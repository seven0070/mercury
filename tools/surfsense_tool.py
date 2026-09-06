from crewai.tools.base_tool import BaseTool
from components.surfsense import SurfSense

class SurfSenseTool(BaseTool):
    name: str = "surfsense"
    description: str = "Gather live web data from SurfSense for a given query."

    def _run(self, query: str) -> str:
        surf = SurfSense()
        return surf.gather(query)
