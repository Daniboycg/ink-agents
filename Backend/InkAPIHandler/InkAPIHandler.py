from agency_swarm.agents import Agent
from agency_swarm.tools import FileSearch


class InkAPIHandler(Agent):
    def __init__(self):
        super().__init__(
            name="InkAPIHandler",
            model="gpt-40-mini",
            description="Handles all interactions with the Ink Innovations API. Traverses the API to fetch, manage, and process flight data.",
            instructions="./instructions.md",
            files_folder="./files",
            schemas_folder="./schemas",
            tools=[FileSearch],
            tools_folder="./tools",
            temperature=0.3,
            max_prompt_tokens=30000,
        )

    def response_validator(self, message):
        return message
