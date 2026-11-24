# repoqa

Ask questions about any GitHub repo and get answers that cite file and line ranges.

## Why this exists
Onboarding onto an unfamiliar codebase means hours of grepping. repoqa indexes a repo locally and answers questions grounded in the actual code, with citations you can verify.

## Quick start
```bash
pip install -e .
export ANTHROPIC_API_KEY=sk-ant-...
repoqa index https://github.com/pallets/flask
repoqa serve   # open http://localhost:8000
```

## How it works
1. **Index**: shallow-clone, split text files into overlapping 40-line chunks, store in SQLite FTS5.
2. **Retrieve**: BM25 search over chunks for the question's keywords.
3. **Answer**: Claude answers only from retrieved snippets and cites `[path:start-end]`.

## Design note
Retrieval starts as keyword search (BM25) so setup has zero heavy dependencies. Swapping `indexer.search` for embeddings plus `sqlite-vec` is the natural next step, and hybrid retrieval would likely beat either alone.

## Roadmap
- [ ] Embedding-based and hybrid retrieval
- [ ] Syntax-aware chunking (functions/classes)
- [ ] Streaming answers
- [ ] Multi-repo support

## License
MIT
