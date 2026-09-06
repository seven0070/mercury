from crewai import Task
from agents import data_collector, processor, visualizer

collect_task = Task(
    description='Fetch the latest web data about {goal}.',
    expected_output='JSON string with raw web data.',
    agent=data_collector
)

process_task = Task(
    description='Process the raw data to extract headlines, word counts, and top terms.',
    expected_output='JSON string with processed insights.',
    agent=processor,
    context=[collect_task]
)

visualize_task = Task(
    description='Generate a 3D visualization from the processed data.',
    expected_output='HTML iframe or text description.',
    agent=visualizer,
    context=[process_task]
)
