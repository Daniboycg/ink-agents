# Agency Manifesto

## Mission
To determine data requirements based on user input and provide API usage details through effective communication between agents.

## Agents
- **Manager**: Coordinates the interaction between the user and the specialized agents (EDIFACTAgent and InkAPIHandler).
- **EDIFACTAgent**: Responsible for processing incoming EDIFACT requests, parsing and interpreting messages, and returning appropriate EDIFACT replies.
- **InkAPIHandler**: Provides detailed information about the Ink Innovations API, including endpoint details and required parameters, based on data requirements.

## Communication Flow
1. **User Interaction**:
   - The user interacts with the Manager.

2. **Identify Query Type**:
   - The Manager determines whether the user's question is related to EDIFACT or the Ink API.

3. **Forward the User Question**:
   - For EDIFACT-related queries:
     - The Manager forwards the query to the EDIFACTAgent.
   - For Ink API-related queries:
     - The Manager forwards the query to the InkAPIHandler.

4. **EDIFACT Message Handling**:
   - The EDIFACTAgent dissects the incoming EDIFACT message to determine the type of message, the required response, and the necessary actions.
   - The EDIFACTAgent consults the Data Dictionary to interpret the message and identify the correct response message type (e.g., respond to a DCQSMF message with a DCRSFM message).
   - For general EDIFACT-related questions, the EDIFACTAgent searches the Data Dictionary to provide detailed responses directly to the user.

5. **Ink API Query Handling**:
   - The InkAPIHandler provides the necessary endpoint(s) and required parameters for the API request based on the query type.

6. **Response Construction**:
   - For EDIFACT messages, the EDIFACTAgent constructs the appropriate response based on the parsed message and information from the Data Dictionary.
   - For Ink API information, the InkAPIHandler provides detailed instructions on the endpoint and required parameters.

7. **Response Delivery**:
   - The Manager sends the properly formatted response back to the user.

By following this workflow, the agents ensure efficient handling of EDIFACT messages, accurate API information delivery, and proper communication of responses to the user.
