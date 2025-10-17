"""Example: basic imports and Qdrant connectivity check.

This script demonstrates how to import `google-generativeai` and
`qdrant-client`. It does not call any paid API by default — the
Google generative client usage is commented and requires a valid key.

Run locally with the project's Python interpreter.
"""

import os
import sys
import httpx

try:
    import google.generativeai as genai  # optional: used when
    # GOOGLE_API_KEY is set
except Exception as e:
    genai = None
    print("google-generativeai not available:", e)

try:
    from qdrant_client import QdrantClient
except Exception as e:
    QdrantClient = None
    print("qdrant-client not available:", e)


def qdrant_check():
    # Attempt to connect to local Qdrant (default at localhost:6333)
    # Set QDRANT_URL env var to override, e.g. http://localhost:6333
    qdrant_url = os.getenv('QDRANT_URL', 'http://localhost:6333')
    print(f"Attempting to connect to Qdrant at {qdrant_url} ...")
    try:
        # quick HTTP probe with a short timeout to avoid long hangs
        probe_url = qdrant_url.rstrip('/') + '/collections'
        resp = httpx.get(probe_url, timeout=5.0)
        resp.raise_for_status()
        info = resp.json()
        print("Qdrant collections (HTTP probe):", info)
        # optional: use client to interact further if needed
        if QdrantClient is not None:
            try:
                client = QdrantClient(url=qdrant_url)
                col_info = client.get_collections()
                print("Qdrant collections (via client):", col_info)
            except Exception as e:
                print("Connected but qdrant-client call failed:", e)
    except Exception as e:
        # Print short, actionable error message
        print("Qdrant connection failed (quick probe).\n",
              "Check that Qdrant is running and reachable at the URL shown.\n",
              f"Error: {e}")


if __name__ == '__main__':
    print('Environment: ', sys.executable)
    # Example: set GOOGLE_API_KEY in env to enable genai usage
    if os.getenv('GOOGLE_API_KEY') and genai is not None:
        print('Google API key found (genai available).')
        # Example usage (uncomment and adapt when ready):
        # genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
    # response = genai.generate_text(
    #     model='models/text-bison-001', input='Hello'
    # )
    else:
        print('No Google API key set; skipping genai example.')

    qdrant_check()
