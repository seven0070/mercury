from crewai.tools.base_tool import BaseTool
from components.ghost_pepper import GhostPepper

class GhostPepperTool(BaseTool):
    name: str = "ghost_pepper"
    description: str = "Process meeting transcripts or voice input into structured text (headlines, keywords, word counts)."

    def _run(self, data: str = "") -> str:
        pepper = GhostPepper()
        return pepper.process(data)
