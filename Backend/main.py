import logging
from pathlib import Path
import os

from agency_swarm import get_openai_client, set_openai_key
from dotenv import load_dotenv

from InkAPIHandler import InkAPIHandler
from EDIFACTAgent import EDIFACTAgent
from Manager import Manager
from AgencyUI import AgencyUI

# Configure logging
logging.basicConfig(level=logging.INFO)

# Load environment variables
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

# Configure OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OpenAI API key is not set. Please set it in the .env file.")
set_openai_key(api_key)

client = get_openai_client()
client.timeout = 60

ink_api_handler = InkAPIHandler()
edifact_agent = EDIFACTAgent()
manager = Manager()

agency = AgencyUI([manager,
                   [manager, ink_api_handler],
                   [manager, edifact_agent],],
        shared_instructions="./agency_manifesto.md",
)

# Create the app
app = agency.custom_demo(server_name="0.0.0.0", server_port=8000)

# Run the app
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
