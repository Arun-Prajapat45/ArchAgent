# Two-minute Demo Recording Checklist

This checklist is intentionally reproducible. Do not splice in a checked-in fixture or claim that an edited response is a live run.

1. Start from a clean clone and show the repository URL and commit SHA.
2. Copy `.env.example` to `.env`; add credentials off-camera so they are never recorded.
3. Run `docker compose up --build`.
4. Show `/health`, `/ready`, and the Streamlit UI.
5. Submit the prompt from `examples/sample-request.json`.
6. Keep the recording uncut while the request executes.
7. Show the requirements, HLD, Mermaid source/rendering, critique count, and pricing disclaimer.
8. Run `pytest` and briefly show the offline evaluation result.
9. State the current limitations: model fallibility, no public authentication, no live benchmark, and approximate pricing.
10. Publish the video with the commit SHA, model IDs, date, runtime, and measured request latency in the description.
