import queue
import threading

from agency_swarm import Agency
from agency_swarm.messages import MessageOutput
from agency_swarm.util.streaming import AgencyEventHandler
from openai.types.beta.threads import Message
from openai.types.beta.threads.runs import RunStep
from typing_extensions import override


class AgencyUI(Agency):
    def custom_demo(self, height=450, dark_mode=True, **kwargs):
        """
        Launches a Gradio-based demo interface for the agency chatbot.

        Parameters:
            height (int, optional): The height of the chatbot widget in the Gradio interface. Default is 600.
            dark_mode (bool, optional): Flag to determine if the interface should be displayed in dark mode. Default is True.
            **kwargs: Additional keyword arguments to be passed to the Gradio interface.
        This method sets up and runs a Gradio interface, allowing users to interact with the agency's chatbot. It includes a text input for the user's messages and a chatbot interface for displaying the conversation. The method handles user input and chatbot responses, updating the interface dynamically.
        """

        try:
            import gradio as gr
        except ImportError:
            raise Exception("Please install gradio: pip install gradio")

        js = """function () {
          gradioURL = window.location.href
          if (!gradioURL.endsWith('?__theme={theme}')) {
            window.location.replace(gradioURL + '?__theme={theme}');
          }
        }"""

        if dark_mode:
            js = js.replace("{theme}", "dark")
        else:
            js = js.replace("{theme}", "light")

        message_file_ids = []
        message_file_names = None
        recipient_agents = [agent.name for agent in self.main_recipients]
        recipient_agent = self.main_recipients[0]

        with gr.Blocks(js=js) as demo:
            chatbot_queue = queue.Queue()
            chatbot = gr.Chatbot(height=height)
            with gr.Row():
                with gr.Column(scale=9):
                    dropdown = gr.Dropdown(
                        label="Recipient Agent",
                        choices=recipient_agents,
                        value=recipient_agent.name,
                    )
                    msg = gr.Textbox(label="Your Message", lines=4)
                with gr.Column(scale=1):
                    file_upload = gr.Files(label="Files", type="filepath")
            button = gr.Button(value="Send", variant="primary")

            def handle_dropdown_change(selected_option):
                nonlocal recipient_agent
                recipient_agent = self._get_agent_by_name(selected_option)

            def handle_file_upload(file_list):
                nonlocal message_file_ids
                nonlocal message_file_names
                message_file_ids = []
                message_file_names = []
                if file_list:
                    try:
                        for file_obj in file_list:
                            with open(file_obj.name, "rb") as f:
                                # Upload the file to OpenAI
                                file = self.main_thread.client.files.create(
                                    file=f, purpose="assistants"
                                )
                            message_file_ids.append(file.id)
                            message_file_names.append(file.filename)
                            print(f"Uploaded file ID: {file.id}")
                        return message_file_ids
                    except Exception as e:
                        print(f"Error: {e}")
                        return str(e)

                return "No files uploaded"

            def user(user_message, history):
                if not user_message.strip():
                    return user_message, history

                if history is None:
                    history = []

                original_user_message = user_message

                # Append the user message with a placeholder for bot response
                if recipient_agent:
                    user_message = (
                        f"👤 User 🗣️ @{recipient_agent.name}:\n" + user_message.strip()
                    )
                else:
                    user_message = "👤 User:" + user_message.strip()

                nonlocal message_file_names
                if message_file_names:
                    user_message += "\n\n📎 Files:\n" + "\n".join(message_file_names)

                return original_user_message, history + [[user_message, None]]

            class GradioEventHandler(AgencyEventHandler):
                message_output = None

                @override
                def on_message_created(self, message: Message) -> None:
                    if message.role == "user":
                        full_content = ""
                        for content in message.content:
                            if content.type == "image_file":
                                full_content += (
                                    f"🖼️ Image File: {content.image_file.file_id}\n"
                                )
                                continue

                            if content.type == "image_url":
                                full_content += f"\n{content.image_url.url}\n"
                                continue

                            if content.type == "text":
                                full_content += content.text.value + "\n"

                        self.message_output = MessageOutput(
                            "text",
                            self.agent_name,
                            self.recipient_agent_name,
                            full_content,
                        )

                    else:
                        self.message_output = MessageOutput(
                            "text", self.recipient_agent_name, self.agent_name, ""
                        )

                    chatbot_queue.put("[new_message]")
                    chatbot_queue.put(self.message_output.get_formatted_content())

                @override
                def on_text_delta(self, delta, snapshot):
                    chatbot_queue.put(delta.value)

                @override
                def on_tool_call_created(self, tool_call):
                    # TODO: add support for code interpreter and retirieval tools
                    if tool_call.type == "function":
                        chatbot_queue.put("[new_message]")
                        self.message_output = MessageOutput(
                            "function",
                            self.recipient_agent_name,
                            self.agent_name,
                            str(tool_call.function),
                        )
                        chatbot_queue.put(
                            self.message_output.get_formatted_header() + "\n"
                        )

                @override
                def on_tool_call_done(self, snapshot):
                    self.message_output = None

                    # TODO: add support for code interpreter and retirieval tools
                    if snapshot.type != "function":
                        return

                    chatbot_queue.put(str(snapshot.function))

                    if snapshot.function.name == "SendMessage":
                        try:
                            args = eval(snapshot.function.arguments)
                            recipient = args["recipient"]
                            self.message_output = MessageOutput(
                                "text",
                                self.recipient_agent_name,
                                recipient,
                                args["message"],
                            )

                            chatbot_queue.put("[new_message]")
                            chatbot_queue.put(
                                self.message_output.get_formatted_content()
                            )
                        except Exception:
                            pass

                    self.message_output = None

                @override
                def on_run_step_done(self, run_step: RunStep) -> None:
                    if run_step.type == "tool_calls":
                        for tool_call in run_step.step_details.tool_calls:
                            if tool_call.type != "function":
                                continue

                            if tool_call.function.name == "SendMessage":
                                continue

                            self.message_output = None
                            chatbot_queue.put("[new_message]")

                            self.message_output = MessageOutput(
                                "function_output",
                                tool_call.function.name,
                                self.recipient_agent_name,
                                tool_call.function.output,
                            )

                            chatbot_queue.put(
                                self.message_output.get_formatted_header() + "\n"
                            )
                            chatbot_queue.put(tool_call.function.output)

                @override
                @classmethod
                def on_all_streams_end(cls):
                    cls.message_output = None
                    chatbot_queue.put("[end]")

            def bot(original_message, history):
                if not original_message:
                    return "", history

                nonlocal message_file_ids
                nonlocal message_file_names
                nonlocal recipient_agent
                print("Message files: ", message_file_ids)
                # Replace this with your actual chatbot logic

                completion_thread = threading.Thread(
                    target=self.get_completion_stream,
                    args=(
                        original_message,
                        GradioEventHandler,
                        message_file_ids,
                        recipient_agent,
                    ),
                )
                completion_thread.start()

                message_file_ids = []
                message_file_names = []

                new_message = True
                while True:
                    try:
                        bot_message = chatbot_queue.get(block=True)

                        if bot_message == "[end]":
                            completion_thread.join()
                            break

                        if bot_message == "[new_message]":
                            new_message = True
                            continue

                        if new_message:
                            history.append([None, bot_message])
                            new_message = False
                        else:
                            history[-1][1] += bot_message

                        yield "", history
                    except queue.Empty:
                        break

            button.click(user, inputs=[msg, chatbot], outputs=[msg, chatbot]).then(
                bot, [msg, chatbot], [msg, chatbot]
            )
            dropdown.change(handle_dropdown_change, dropdown)
            file_upload.change(handle_file_upload, file_upload)
            msg.submit(user, [msg, chatbot], [msg, chatbot], queue=False).then(
                bot, [msg, chatbot], [msg, chatbot]
            )

            # Enable queuing for streaming intermediate outputs
            demo.queue()

        # Launch the demo
        demo.launch(**kwargs)
        return demo
