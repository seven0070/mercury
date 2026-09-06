import os
from crewai import Crew, Process
from agents import data_collector, processor, visualizer
from tasks import collect_task, process_task, visualize_task
from components.hermes3d_live import Hermes3DLiveClient
from dotenv import load_dotenv

load_dotenv()

# Initialize Hermes3D live client
hermes_live = Hermes3DLiveClient()
hermes_live.connect()

# Mapping from CrewAI agent roles to Hermes3D agent IDs
AGENT_ID_MAP = {
    "Data Collector": "data_collector",
    "Data Processor": "processor",
    "3D Visualizer": "visualizer"
}

def step_callback(step_output):
    """
    Called after each agent step. Sends status updates to Hermes3D.
    """
    try:
        agent = step_output.agent
        agent_role = agent.role if hasattr(agent, 'role') else str(agent)
        hermes_agent_id = AGENT_ID_MAP.get(agent_role, agent_role.lower().replace(" ", "_"))
        if step_output.output:
            status = "completed"
            message = f"Task completed: {step_output.task.description[:50]}..."
        else:
            status = "working"
            message = f"Working on: {step_output.task.description[:50]}..."
        hermes_live.send_status(hermes_agent_id, status, message)
    except Exception as e:
        print(f"Step callback error: {e}")

crew = Crew(
    agents=[data_collector, processor, visualizer],
    tasks=[collect_task, process_task, visualize_task],
    process=Process.sequential,
    verbose=True,
    step_callback=step_callback
)

def run_crew(goal: str = "latest tech news", connector: str = "google_search") -> str:
    result = crew.kickoff(inputs={"goal": goal, "connector": connector})
    return str(result)

if __name__ == "__main__":
    print(run_crew("latest AI trends"))
