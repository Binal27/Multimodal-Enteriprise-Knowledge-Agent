<<<<<<< HEAD
# Multimodal Enterprise Knowledge Agent — Prototype v1 (plain RAG baseline)

This is a deliberately simple, single-pass RAG system over PDF and PPTX
documents. It is **not** the agentic version — it has no verification,
no conflict detection, no multi-hop retrieval. That's the point: this
prototype exists to demonstrate *why* those things are needed, by showing
what happens without them.

## What's included

- `make_sample_data.py` — generates two small sample documents with a
  realistic, deliberate conflict: a PDF quarterly report states GAAP
  revenue ($4.20M), a PPTX investor deck states a non-GAAP adjusted
  figure for the *same quarter* ($4.60M). This mirrors how real
  companies often report two different numbers for one period.
- `ingest.py` — parses every PDF/PPTX in `data/`, extracts text and
  tables, chunks it, and builds a TF-IDF (keyword-based) retrieval index.
- `ask.py` — takes a question, retrieves the most relevant chunks, and
  asks Claude to answer using only those chunks, with citations.

## Setup

```bash
pip install -r requirements.txt

# Generate the sample conflict dataset (or skip this and drop your own
# PDFs/PPTX into data/ instead — see "Using real data" below)
python make_sample_data.py

# Build the retrieval index
python ingest.py

# Set your API key (needed only for ask.py's answer-generation step;
# retrieval works and can be inspected without it)
export ANTHROPIC_API_KEY="your-key-here"

# Ask a question
python ask.py "What was our Q3 revenue?"
```

Without an API key, `ask.py` still runs retrieval and prints the exact
prompt that would have been sent — useful for checking retrieval quality
on its own.

## What to expect when you run it

Retrieval correctly pulls passages from **both** documents — you'll see
both the $4.20M (GAAP, from the PDF) and $4.60M (non-GAAP, from the
slide) passages retrieved for the same question. That part works fine.

What happens next depends on the LLM, and that's exactly the point:
this baseline has **no dedicated step that checks whether retrieved
sources agree**. Sometimes the model will happen to mention both
figures; sometimes it will just pick one and answer confidently. Either
way, that behavior is incidental, not designed — there's no guarantee,
and no structured way for the system to flag "these sources disagree"
or ask a clarifying question. That reliability gap — turning "the model
might happen to notice" into "the system always checks" — is exactly
what the next phase (agentic self-verification and conflict handling)
is being built to close.

## Using real data instead of the sample documents

Drop any PDF and PPTX files into `data/` and re-run `ingest.py` —
the pipeline doesn't care where they came from. For a more authentic
version of this same demo:

1. Go to [SEC EDGAR](https://www.sec.gov/edgar/search/) and pull a real
   company's latest **10-Q** filing (PDF).
2. Find that same company's **investor earnings presentation** (usually
   a PDF or PPTX on their investor-relations website).
3. Look for a GAAP vs. non-GAAP revenue figure, or a preliminary vs.
   restated figure — these real discrepancies exist in most large
   companies' actual filings and are a stronger, more defensible example
   than a synthetic one.

## Known limitations of this v1 (intentional, for scoping reasons)

- **Retrieval is TF-IDF (keyword-based), not dense embeddings.** This
  avoids needing a downloaded embedding model or an API key just to
  index documents. Swapping in dense embeddings (e.g.
  `sentence-transformers` or an embedding API) is a planned upgrade.
- **No chart/image understanding yet.** Slide charts and scanned images
  are not yet processed by a vision model — only extractable text and
  tables. This is the next multimodal upgrade.
- **No verification, conflict handling, multi-hop retrieval, tool use,
  or clarification-seeking.** These are the four agentic capabilities
  planned for the next phase, on top of this working baseline.
=======
# Multimodal-Enteriprise-Knowledge-Agent
>>>>>>> 8965a89df30416eef53c34e5c350424b2f3be8e5
