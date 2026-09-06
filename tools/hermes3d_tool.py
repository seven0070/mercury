from crewai_tools import BaseTool
from components.hermes3d import Hermes3D

class Hermes3DTool(BaseTool):
    name: str = "hermes3d"
    description: str = "Generate a link/iframe to the 3D office where agents work (or return a text summary)."

    def _run(self, processed_json: str) -> str:
        hermes = Hermes3D()
        return hermes.visualize(processed_json)
