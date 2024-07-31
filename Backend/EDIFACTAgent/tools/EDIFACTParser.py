from agency_swarm.tools import BaseTool
from pydantic import Field
import dotenv
from pydifact.segmentcollection import Interchange

dotenv.load_dotenv()

class EDIFACTParser(BaseTool):
    """
    A tool to parse EDIFACT messages. This tool parses the EDIFACT message,
    validates it, and prints the details of each message and segment.
    """

    edifact_message: str = Field(
        ..., description="The EDIFACT message to be dissected."
    )

    def run(self):
        """
        Parses the EDIFACT message, validates it, and prints the details of each message and segment.
        """
        try:
            interchange = Interchange.from_str(self.edifact_message)
            interchange.validate()

            message_dict = {}

            # Iterate through messages and segments, populating the dictionary
            for message in interchange.get_messages():
                message_header = message.get_header_segment()

                message_dict[message_header.tag] = message_header.elements
                for segment in message.segments:
                    tag = segment.tag
                    if tag not in message_dict:
                        message_dict[tag] = []
                    message_dict[tag].extend(segment.elements)

                message_footer = message.get_footer_segment()

                if message_footer.tag not in message_dict:
                    message_dict[message_footer.tag] = []
                message_dict[message_footer.tag].extend(message_footer.elements)

            # Print the parsed message dictionary
            print("Parsed EDIFACT Message:", message_dict)
            return message_dict
        except Exception as e:
            print(f"Interchange validation error: {e}")
            return f"Interchange validation error: {e}"

# Example usage
if __name__ == "__main__":
    edifact_message = (
        "UNB+IATA:1+W1+ON+240626:1935+0001'"
        "UNH+1+DCQSMF:03:1:IA'"
        "LOR+W1:BOG'"
        "FDQ+1IN+4632+240626+PEI+BOG++1IN+3782+2406261100+2406262330+BOG+PEI'"
        "UNT+4+1'"
        "UNZ+1+0001'"
    )
    tool = EDIFACTParser(edifact_message=edifact_message)
    result = tool.run()
    print(result)
