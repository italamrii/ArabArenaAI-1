# Local RAG Prototype (Phase 5.3)

Minimal retrieval-augmented generation over **manual seed documents only** in `knowledge/documents/`.

## What this does

1. Chunks eligible Saudi Knowledge Pack seed markdown
2. Retrieves top-k chunks with keyword + semantic-lite scoring
3. Builds a context prompt for the existing Ollama/Qwen runner
4. Evaluates benchmarks and stores results separately as `evaluation/results/rag_*.json`
5. Compares against the latest matching non-RAG calibrated baseline

## What this does not do

- No web scraping
- No vector database
- No training or fine-tuning
- No use of blocked/rejected manifest sources

## Usage

```bash
# Preview indexed chunks and sample retrieval
python rag/evaluate_rag.py --model qwen --preview-retrieval

# Run RAG evaluation (10 benchmarks, calibrated scoring)
python rag/evaluate_rag.py --model qwen --limit 10 --scoring calibrated
```

## Layout

```
rag/
├── chunker.py          Markdown chunking with metadata
├── index.py            In-memory index builder
├── retriever.py        Keyword / overlap retrieval
├── rag_runner.py       Prompt builder + runner wrapper
├── pipeline.py         RAG evaluation pipeline
├── storage.py          rag_{run_id}.json persistence
├── evaluate_rag.py     CLI
└── README.md
```

Comparison reports: `evaluation/reports/rag_comparison_{run_id}.json`

Dashboard section: **RAG Experiments**
