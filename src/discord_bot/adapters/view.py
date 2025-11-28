import gradio as gr
import os
from discord_bot.contracts.ports import ControllerPort, ViewPort

class DiscordBotView(ViewPort):
    """Gradio-based view adapter for Discord bot administration.
    
    This class implements the ViewPort interface to provide a web-based
    user interface using the Gradio framework.
    """
    
    def __init__(self, controller: ControllerPort):
        """Initialize the Discord bot view.
        
        Args:
            controller: The controller port instance for handling bot operations.
        """
        self.controller = controller
        self.interface = None
        self.inputs = {} 
    
    def render_interface(self, data: dict) -> str:
        """ Render and launch the Gradio web interface.
            
            Args:
                data: The data to be used for rendering the interface.
            
            Returns:
                port number where the interface is launched.
        """
        title = data.get("title", "Interface")
        port = int(os.getenv("GRADIO_SERVER_PORT", data.get("port", 7860)))
        share = data.get("share", False)
        server_name = os.getenv("GRADIO_SERVER_NAME", "0.0.0.0")
        
        with gr.Blocks() as interface:
            gr.Markdown(f"# {title}")
            server_choice = gr.Dropdown(label="Server", choices=["Server 1", "Server 2"], interactive=True)
            channel_id = gr.Number(label="Channel ID", value=0, precision=0)
            message_input = gr.Textbox(label="Enter your message")
            test_btn = gr.Button("Send")
            output = gr.Textbox(label="Output", interactive=False)
            
            test_btn.click(
                fn=self.controller.handle_message,
                inputs=[server_choice, channel_id, message_input],
                outputs=output
            )
        
        interface.launch(
            server_port=port,
            share=share,
            server_name=server_name
        )
        return f"Interface rendered successfully (port: {port})"
    
    def get_user_input(self, interactable_element: str) -> str:
        """Get user input from a specific interactable element.
        
        Args:
            interactable_element: The name or ID of the UI element to retrieve input from.
        
        Returns:
            str: The user input value from the specified element.
        """
        return self.inputs.get(interactable_element, "")



if __name__ == "__main__":
    
    class DummyController(ControllerPort):
        def handle_command(self, server_id: int, channel_id: int, command: str, args: list[str]) -> bool:
            return True

        def handle_message(self, server, channel_id: int, message: str) -> bool:
            return f"Handled message: {message}"

        def get_server_info() -> list[dict]:
            return [{"id": 1, "name": "Test Server"}]

    
    view = DiscordBotView(controller=DummyController())
    view.render_interface({
        "title": "Test Bot Admin",
        "port": int(os.getenv("GRADIO_SERVER_PORT", "7860")),
        "share": False
    })