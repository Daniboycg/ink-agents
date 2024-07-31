from agency_swarm.agents import Agent


class EDIFACTAgent(Agent):
    def __init__(self):
        super().__init__(
            name="EDIFACTAgent",
            description="Handles the reception, processing, and construction of EDIFACT messages.",
            instructions="./instructions.md",
            files_folder="./files",
            schemas_folder="./schemas",
            tools=[],
            tools_folder="./tools",
            temperature=0,
            max_prompt_tokens=30000,
            model="gpt-4o-mini"
        )

    def response_validator(self, message):
        return message
