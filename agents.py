from crewai import Agent
from tools.surfsense_tool import SurfSenseTool
from tools.ghostpepper_tool import GhostPepperTool
from tools.hermes3d_tool import Hermes3DTool

surf_tool = SurfSenseTool()
pepper_tool = GhostPepperTool()
hermes_tool = Hermes3DTool()

data_collector = Agent(
    role='Data Collector',
    goal='Gather raw web data relevant to the user request.',
    backstory='You are an expert at searching the web and returning structured data.',
    tools=[surf_tool],
    verbose=True
)

processor = Agent(
    role='Data Processor',
    goal='Process raw data and extract key insights.',
    backstory='You transform noisy data into clean, structured information.',
    tools=[pepper_tool],
    verbose=True
)

visualizer = Agent(
    role='3D Visualizer',
    goal='Create a 3D representation of the processed data.',
    backstory='You turn structured data into intuitive 3D scenes.',
    tools=[hermes_tool],
    verbose=True
)
