import os
import json

class Hermes3D:
    def __init__(self):
        self.office_url = os.getenv("HERMES3D_OFFICE_URL", "http://localhost:3000/office")
        self.enabled = os.getenv("HERMES3D_ENABLED", "false").lower() == "true"

    def visualize(self, processed_json: str) -> str:
        """Return an iframe to the 3D office or a text summary."""
        if self.enabled:
            return f'<iframe src="{self.office_url}" width="100%" height="600"></iframe>'
        else:
            data = json.loads(processed_json)
            headlines = data.get("headlines", [])
            return f"3D Office not enabled. Processed {len(headlines)} items: " + ", ".join(headlines[:3])
