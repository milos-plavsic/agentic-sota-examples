# Data Sources

## Public APIs Used in Keyless CI

- Wikipedia REST Summary API  
  `https://en.wikipedia.org/api/rest_v1/page/summary/{topic}`
- Semantic Scholar Graph API  
  `https://api.semanticscholar.org/graph/v1/paper/search`
- GitHub Repositories API  
  `https://api.github.com/repos/{owner}/{repo}`
- HuggingFace Datasets API  
  `https://huggingface.co/api/datasets/{dataset_id}`
- UCI Dataset API  
  `https://archive.ics.uci.edu/api/dataset/list`

## Reliability and Reproducibility

- All adapters use timeout and retry behavior.
- JSON responses are cached under `.cache/sources/`.
- Every run records `source`, `used_fallback`, and latency metadata.
- Deterministic fallback fixtures ensure CI remains green when endpoints are unreachable.

## Legal and Operational Notes

- APIs listed are public endpoints intended for metadata retrieval.
- Respect provider rate limits in local high-volume runs.
- Avoid storing sensitive payloads in artifacts; keep reports metadata-focused.

## Nightly Extensions

- When secrets are available, nightly workflow enables provider-backed runs.
- Supported secrets: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`.
