import os
import json
import requests

class SurfSense:
    def __init__(self):
        self.api_url = os.getenv("SURFSENSE_API_URL", "https://api.surfsense.com")
        self.workspace_id = os.getenv("SURFSENSE_WORKSPACE_ID", "")
        self.api_key = os.getenv("SURFSENSE_API_KEY", "")
        self.enabled = bool(self.api_key and self.workspace_id)

    def gather(self, query: str, connector: str = "google_search") -> str:
        """
        Gather data from SurfSense connectors.
        Falls back to mock data if API not configured or call fails.
        """
        if not self.enabled:
            return self._mock_gather(query)

        endpoint = f"{self.api_url}/workspaces/{self.workspace_id}/scrapers/{connector}/scrape"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {"query": query}

        try:
            resp = requests.post(endpoint, json=payload, headers=headers, timeout=30)
            resp.raise_for_status()
            data = resp.json()

            # Normalize response (assumes "results" key with "title" and "snippet")
            items = []
            for item in data.get("results", []):
                items.append({
                    "title": item.get("title", ""),
                    "content": item.get("snippet", item.get("content", ""))
                })

            return json.dumps({
                "source": connector,
                "query": query,
                "items": items
            })
        except Exception as e:
            print(f"SurfSense API error: {e}")
            return self._mock_gather(query)

    def _mock_gather(self, query: str) -> str:
        """Fallback mock data."""
        return json.dumps({
            "source": "surfsense_mock",
            "query": query,
            "items": [
                {"title": "Sample Result 1", "content": "Some sample content."},
                {"title": "Sample Result 2", "content": "More sample content."}
            ]
        })
