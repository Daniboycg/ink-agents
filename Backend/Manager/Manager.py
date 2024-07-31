from agency_swarm.agents import Agent


class Manager(Agent):
    def __init__(self):
        super().__init__(
            name="Manager",
            description="Handles the reception, processing, and information retrieval of user EDIFACT queries.",
            instructions="./instructions.md",
            files_folder="./files",
            schemas_folder="./schemas",
            tools=[],
            tools_folder="./tools",
            temperature=0,
            max_prompt_tokens=25000,
            model="gpt-4o-mini"
        )

    def response_validator(self, message):
        return message
