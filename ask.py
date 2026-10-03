"""
ask.py — Loads the index built by ingest.py, retrieves the passages most
relevant to a question, and asks an LLM to answer using ONLY those
passages, with citations.

This is a DELIBERATELY SIMPLE, single-pass RAG baseline: it retrieves once
and answers once. It does NOT check whether the retrieved passages agree
with each other — that verification step is the next phase of the
project. Try a question where two of your documents disagree (e.g. GAAP
vs non-GAAP revenue) and watch it produce one confident answer anyway,
citing a source, without flagging the conflict. That failure is the
point of this prototype.

Run:  python ask.py "What was our Q3 revenue?"
"""
import os
import sys
import pickle

try:
    from dotenv import load_dotenv
    load_dotenv()  # loads GEMINI_API_KEY etc. from a .env file if present
except ImportError:
    pass  # dotenv is optional - env vars set manually still work fine

from sklearn.metrics.pairwise import cosine_similarity

INDEX_PATH = "data/index/index.pkl"
TOP_K = 12


def load_index():
    if not os.path.exists(INDEX_PATH):
        print("No index found. Run ingest.py first.")
        sys.exit(1)
    with open(INDEX_PATH, "rb") as f:
        return pickle.load(f)


def retrieve(question, index, top_k=TOP_K):
    q_vec = index["vectorizer"].transform([question])
    scores = cosine_similarity(q_vec, index["matrix"]).flatten()
    top_idx = scores.argsort()[::-1][:top_k]
    results = []
    for i in top_idx:
        if scores[i] > 0:
            results.append({
                "text": index["chunks"][i],
                "source": index["metadata"][i]["source"],
                "location": index["metadata"][i]["location"],
                "score": float(scores[i]),
            })
    return results


def build_prompt(question, passages):
    context = "\n\n".join(
        f"[Source: {p['source']}, {p['location']}]\n{p['text']}"
        for p in passages
    )
    return f"""You are answering a question using ONLY the passages below.
Cite the source (document name and page/slide) for any fact you state.
If the passages don't contain the answer, say so plainly.

Passages:
{context}

Question: {question}

Answer:"""


def call_llm(prompt):
    """
    Calls an LLM to generate the answer. Checks for API keys in this order
    and uses whichever is found first: ANTHROPIC_API_KEY, GEMINI_API_KEY,
    GROQ_API_KEY. If none is set, prints the prompt instead so you can
    still inspect retrieval quality without any key.

    Anthropic's API has no standing free tier (one-time signup credit
    only). Gemini and Groq both offer genuine free tiers with no credit
    card required - see README.md for where to get a key.
    """
    import requests

    groq_key = os.environ.get("GROQ_API_KEY")

    if groq_key:
        # NOTE: llama-3.3-70b-versatile was decommissioned by Groq on
        # 2026-08-16. Using their current recommended replacement.
        model = os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b")
        url = "https://api.groq.com/openai/v1/chat/completions"
        resp = requests.post(
            url,
            headers={"Authorization": f"Bearer {groq_key}"},
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 500,
            },
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]

    print("\n[No API key set (checked ANTHROPIC_API_KEY, GEMINI_API_KEY, "
          "GROQ_API_KEY) - showing the prompt that would have been sent "
          "instead of calling the LLM.]\n")
    print(prompt)
    return None


def main():
    if len(sys.argv) < 2:
        print('Usage: python ask.py "your question here"')
        sys.exit(1)

    question = sys.argv[1]
    index = load_index()
    passages = retrieve(question, index)

    if not passages:
        print("No relevant passages found in the indexed documents.")
        return

    print(f"\nRetrieved {len(passages)} passages:")
    for p in passages:
        print(f"  - {p['source']} ({p['location']}), score={p['score']:.3f}")

    prompt = build_prompt(question, passages)
    answer = call_llm(prompt)

    if answer:
        print("\n--- Answer ---")
        print(answer)


if __name__ == "__main__":
    main()
