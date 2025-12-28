## Health Endpoint

/health checks:
- API process is running

Does NOT check:
- Embedding model availability
- Vector store completeness
- OpenAI API availability

## Known Failure Modes

1. Embedding model missing
   - Service fails at startup
   - Logged as EMBEDDING_LOAD_ERROR

2. No relevant context
   - Request returns 200 with explicit message

3. OpenAI API failure
   - Request returns 5xx
   - Logged as LLM_TIMEOUT or INTERNAL_ERROR

4. Cold start latency
   - First request may be slow