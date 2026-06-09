# Evaluation Harness

See [docs/EVALUATION_HARNESS.md](../docs/EVALUATION_HARNESS.md).

```bash
pip install -r requirements-eval.txt
python evaluation/evaluate.py --model mock --jsonl-only --limit 5
streamlit run evaluation/dashboard.py
```
