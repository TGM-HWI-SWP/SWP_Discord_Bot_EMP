from gradio import gradio as gr
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
        """Render and launch the Gradio web interface.
        
        Args:
            data: Configuration dictionary containing:
                - title (str): The title of the interface. Defaults to "Interface".
                - port (int): The port number to run the server on. Defaults to 7860.
                - share (bool): Whether to create a public shareable link. Defaults to False.
        
        Returns:
            str: A status message indicating successful launch with port information.
        """
        title = data.get("title", "Interface")
        port = data.get("port", 7860)
        share = data.get("share", False)
        
        with gr.Blocks() as interface:
            gr.Markdown(f"# {title}")
            message_input = gr.Textbox(label="Enter your message")
            test_btn = gr.Button("Send")
            output = gr.Textbox(label="Output", interactive=False)
            
            test_btn.click(
                fn=self.controller.handle_message,
                inputs=[0, 0, message_input],
                outputs=output
            )
            
            test_btn.click(test_btn, inputs=message_input, outputs=output)
            interface.launch(port=port, share=share)
            return f"Interface rendered successfully.(port: {port})"
    
    def get_user_input(self, interactable_element: str) -> str:
        """Get user input from a specific interactable element.
        
        Args:
            interactable_element: The name or ID of the UI element to retrieve input from.
        
        Returns:
            str: The user input value from the specified element.
        """
        return self.inputs.get(interactable_element, "")


if __name__ == "__main__":
    view = DiscordBotView(controller=None)
    view.render_interface({
        "title": "Test Bot Admin",
        "port": 7860,
        "share": False
    })