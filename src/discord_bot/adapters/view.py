import gradio as gr
import discord
from discord_bot.contracts.ports import ViewPort, DatabasePort, DishPort, FunFactPort, TranslatePort, ControllerPort
#import datetime




# ADMIN_PANEL_CSS = """
# .gradio-container {
#     font-family: 'Whitney', 'Helvetica Neue', Helvetica, Arial, sans-serif;
# }
# .admin-header {
#     background: linear-gradient(135deg, #5865F2 0%, #4752C4 100%);
#     color: white;
#     padding: 30px;
#     border-radius: 12px;
#     text-align: center;
#     margin-bottom: 25px;
#     box-shadow: 0 8px 24px rgba(88, 101, 242, 0.4);
# }
# .admin-header h1 {
#     margin: 0;
#     font-size: 2.8em;
#     font-weight: 700;
#     text-shadow: 2px 2px 8px rgba(0,0,0,0.3);
# }
# .stat-card {
#     background: linear-gradient(135deg, #2C2F33 0%, #23272A 100%);
#     color: white;
#     padding: 25px;
#     border-radius: 12px;
#     text-align: center;
#     box-shadow: 0 4px 12px rgba(0,0,0,0.4);
#     border: 3px solid #5865F2;
# }
# .stat-number {
#     font-size: 3em;
#     font-weight: 700;
#     color: white;
# }
# .stat-label {
#     font-size: 1.2em;
#     color: #99AAB5;
#     text-transform: uppercase;
# }

# /* Override Gradio orange colors with Discord blue */
# button.primary, .gr-button-primary {
#     background: #5865F2 !important;
#     border-color: #5865F2 !important;
# }
# button.primary:hover, .gr-button-primary:hover {
#     background: #4752C4 !important;
#     border-color: #4752C4 !important;
# }
# .tabs button[aria-selected="true"] {
#     border-bottom-color: #5865F2 !important;
#     color: #5865F2 !important;
# }
# """



class AdminPanel(ViewPort):
    def __init__(
        self,
        dbms: DatabasePort,
        discord_bot: discord.Client | None = None,
        dish_selector: DishPort | None = None,
        fun_fact_selector: FunFactPort | None = None,
        translator: TranslatePort | None = None,
        controller: ControllerPort | None = None,
        host: str = "0.0.0.0",
        port: int = 7860
    ):
        self.dbms = dbms
        self.discord_bot = discord_bot
        self.dish_selector = dish_selector
        self.fun_fact_selector = fun_fact_selector
        self.translator = translator
        self.controller = controller
        self.host = host
        self.port = port
        self.app = None
    
    def get_user_input(self, interactable_element: str) -> str:
        return ""
    
    def check_available(self) -> bool:
        return self.discord_bot is not None
                    
    def check_connection(self) -> bool:
        return self.check_available() and getattr(self.discord_bot, 'is_connected', lambda: False)()  
    
    def build_interface(self) -> gr.Blocks:

        with gr.Blocks(title="Leberkas Larry Admin Panel") as app:        
            with gr.Tabs():
                with gr.Tab("Overview"):
                    gr.Markdown("### Bot Status")

                    refresh_btn = gr.Button("Refresh", variant="primary")

                    with gr.Row():
                        with gr.Column():
                            bot_status = gr.Textbox(label="Status", value="Loading...", interactive=False)
                        with gr.Column():
                            server_count = gr.Textbox(
                                label="Servers", value="Loading...", interactive=False)
                        with gr.Column():
                            user_count = gr.Textbox(label="Total Users", value="Loading...", interactive=False)
                    
                    def load_bot_status():
                        if not self.check_available():
                            return "Unavailable", "0", "0"
                        
                        try:
                            stats = self.discord_bot.get_bot_stats()
                            return stats["status"], str(stats["servers"]), f"{stats['users']:,}"
                        except Exception as e:
                            return "Error", "0", "0"
                    
                    refresh_btn.click(fn=load_bot_status, outputs=[bot_status, server_count, user_count])
                    app.load(fn=load_bot_status, outputs=[bot_status, server_count, user_count])
               
               
                # with gr.Tab("Bot Control"):
                    
                #     gr.Markdown("### Discord Bot Management")
                    
                #     with gr.Row():
                #         with gr.Column():
                #             gr.Markdown("#### Server Management")
                #             server_list = gr.Dropdown(label="Select Server", choices=[], interactive=True)
                #             refresh_servers_btn = gr.Button("Refresh Servers")
                #             leave_server_btn = gr.Button("Leave Server")
                #             server_status = gr.Markdown("")
                        
                #         with gr.Column():
                #             gr.Markdown("#### User Management")
                #             user_id_input = gr.Textbox(label="User ID")
                #             block_user_btn = gr.Button("Block User")
                #             unblock_user_btn = gr.Button("Unblock User")
                #             user_status = gr.Markdown("")
                    
                #     gr.Markdown("#### Send Custom Message")
                #     with gr.Row():
                #         channel_id_input = gr.Textbox(label="Channel ID")
                #         message_input = gr.Textbox(label="Message", lines=3)
                #     send_message_btn = gr.Button("Send Message")
                #     message_status = gr.Markdown("")
                    
                #     gr.Markdown("#### Bot Settings")
                #     with gr.Row():
                #         with gr.Column():
                #             bot_prefix = gr.Textbox(label="Command Prefix", value="!")
                #             bot_status_text = gr.Textbox(label="Status Text", value="Playing")
                #         with gr.Column():
                #             auto_reply = gr.Checkbox(label="Auto Reply", value=False)
                #             log_messages = gr.Checkbox(label="Log Messages", value=True)
                #     update_settings_btn = gr.Button("Update Settings")
                #     settings_status = gr.Markdown("")
                    
                    
                #     def refresh_server_list():
                #         if not self.check_available():
                #             return gr.update(), "No discord bot instance"
                        
                #         if not self.check_connection():
                #             return gr.update(), "Bot offline"
                            
                #         servers = self.discord_bot.get_servers()
                #         if not servers:
                #             return gr.update(), "No servers found"
                            
                #         choices = [f'{server["name"]} ({server["id"]})' for server in servers]
                #         return gr.update(choices=choices), f"Found {len(servers)} servers"
                    
                #     def leave_server(server_selection: str):
                #         if not self.check_available():
                #             return gr.update(), "No discord bot instance"
                #         if not self.check_connection():
                #             return gr.update(), "Bot offline"
                #         if not server_selection:
                #             return gr.update(), "Please select a server"
                #         try:
                #             server_id = int(server_selection.split('(')[-1].rstrip(')'))
                #         except (ValueError, IndexError):
                #             return gr.update(), "Invalid server selection"
                        
                #         success = self.discord_bot.leave_server(server_id)
                #         if success:
                #             return refresh_server_list()
                #         else:
                #             return gr.update(), f"Failed to leave server (ID: {server_id})"
                    
                #     def block_user(user_id: str):
                #         if not self.check_available():
                #             return "No discord bot instance"
                        
                #         if not self.check_connection():
                #             return "Bot offline"
                        
                #         if not user_id:
                #             return "Please enter a User ID"
                        
                #         try:
                #             user_id_int = int(user_id)
                #         except ValueError:
                #             return "Invalid User ID (must be a number)"
                        
                #         success = self.discord_bot.block_user(user_id_int)
                #         if success:
                #             return f"Successfully blocked user (ID: {user_id_int})"
                #         else:
                #             return f"Failed to block user (ID: {user_id_int})"
                    
                #     def unblock_user(user_id: str):
                #         if not self.check_available():
                #             return "No discord bot instance"
                        
                #         if not self.check_connection():
                #             return "Bot offline"
                        
                #         if not user_id:
                #             return "Please enter a User ID"
                        
                #         try:
                #             user_id_int = int(user_id)
                #         except ValueError:
                #             return "Invalid User ID (must be a number)"
                        
                #         success = self.discord_bot.unblock_user(user_id_int)
                #         if success:
                #             return f"Successfully unblocked user (ID: {user_id_int})"
                #         else:
                #             return f"Failed to unblock user (ID: {user_id_int})"
                    
                #     def send_message(channel_id: str, message: str):
                #         if not self.check_available():
                #             return "No discord bot instance"
                            
                #         if not self.check_connection():
                #             return "Bot offline"
                            
                #         if not all([channel_id, message]):  
                #             return "Channel ID and message required"
            
                #         try:
                #             channel_id = int(channel_id)
                #         except ValueError:
                #             return "Invalid channel ID"
                            
                #         success = self.discord_bot.send_message(0, channel_id, message)
                #         return "Message sent successfully" if success else "Failed to send message"
                    
                #     def update_settings(prefix: str, status: str, auto_reply_enabled: bool, log_enabled: bool):
                #         if not self.check_available():
                #             return "No discord bot instance"
                #         if not self.check_connection():
                #             return "Bot offline"
                        
                #         success = self.discord_bot.update_settings(prefix, status, auto_reply_enabled, log_enabled)
                        
                #         if success:
                #             return f"Settings updated:\n- Prefix: {prefix}\n- Status: {status}\n- Auto Reply: {'ON' if auto_reply_enabled else 'OFF'}\n- Logging: {'ON' if log_enabled else 'OFF'}"
                #         else:
                #             return "Failed to save settings"
                    
                #     refresh_servers_btn.click(fn=refresh_server_list, outputs=[server_list, server_status])
                #     leave_server_btn.click(fn=leave_server, inputs=[server_list], outputs=[server_list, server_status])
                #     block_user_btn.click(fn=block_user, inputs=[user_id_input], outputs=user_status)
                #     unblock_user_btn.click(fn=unblock_user, inputs=[user_id_input], outputs=user_status)
                #     send_message_btn.click(fn=send_message, inputs=[channel_id_input, message_input], outputs=message_status)
                #     update_settings_btn.click(fn=update_settings, inputs=[bot_prefix, bot_status_text, auto_reply, log_messages], outputs=settings_status)
                
                with gr.Tab("Control Panel"):
                    section_selector = gr.Dropdown(label="Select Section", choices=["Server Management", "User Management", "Custom Messages", "Bot Settings"], value="Server Management",interactive=True)
                    
                   
                    with gr.Row(visible=True) as server_mgmt_section:
                        with gr.Column():
                            gr.Markdown("## Server Management")
                            server_view = gr.Dropdown(label="Select Server to Leave", choices=[], interactive=True)
                            leave_btn = gr.Button("Leave Server", size="lg", interactive=True)
                            refresh_btn = gr.Button("Refresh Servers", size="lg", interactive=True)
                            server_status = gr.Markdown("")
                            
                            def leave_server(server_selection):
                                if not self.check_available():
                                    return "No discord bot instance"
                                if not self.check_connection():
                                    return "Bot offline"
                                if not server_selection:
                                    return "Please select a server"
                                try:
                                    server_id = int(server_selection.split("ID: ")[1].rstrip(")"))
                                    success = self.discord_bot.leave_server(server_id)
                                    if success:
                                        return "Successfully left server"
                                    else:
                                        return "Failed to leave server"
                                except (ValueError, IndexError):
                                    return "Invalid server selection"
                            
                            def refresh_server_list():
                                if not self.check_available():
                                    return gr.update(choices=[]), "No discord bot instance"
                                if not self.check_connection():
                                    return gr.update(choices=[]), "Bot offline"
                                
                                servers = self.discord_bot.get_servers()
                                if not servers:
                                    return gr.update(choices=[]), "No servers found"
                                
                                choices = [f"{server['name']} (ID: {server['id']})" for server in servers]
                                return gr.update(choices=choices), f"Found {len(servers)} servers"
                
                    with gr.Row(visible=False) as user_mgmt_section:
                        with gr.Column():
                            gr.Markdown("## User Management")
                            user_search = gr.Textbox(label="Search User", placeholder="Enter username to search")
                            search_user_btn = gr.Button("Search User", size="lg", interactive=True)
                            user_dropdown = gr.Dropdown(label="Select User to Block/Unblock", choices=[], interactive=True)
                            block_btn = gr.Button("Block User", size="lg", interactive=True)
                            unblock_btn = gr.Button("Unblock User", size="lg", interactive=True)
                            user_status = gr.Markdown("")

                            def search_users(username):
                                if not self.check_available():
                                    return gr.update(choices=[]), "No discord bot instance"
                                if not self.check_connection():
                                    return gr.update(choices=[]), "Bot offline"
                                if not username:
                                    return gr.update(choices=[]), "Please enter a username"
                                
                                try:
                                    servers = self.discord_bot.get_servers()
                                    matching_users = []
                                    
                                    for server in servers:
                                        guild = self.discord_bot.client.get_guild(server['id'])
                                        if guild:
                                            for member in guild.members:
                                                if username.lower() in member.name.lower() or username.lower() in str(member.display_name).lower():
                                                    user_entry = f"{member.name}#{member.discriminator} (ID: {member.id})"
                                                    if user_entry not in matching_users:
                                                        matching_users.append(user_entry)
                                    
                                    if not matching_users:
                                        return gr.update(choices=[]), "No users found"
                                    
                                    return gr.update(choices=matching_users), f"Found {len(matching_users)} user(s)"
                                except Exception as e:
                                    return gr.update(choices=[]), f"Error searching users: {str(e)}"
                            
                            def block_user(user_selection):
                                if not self.check_available():
                                    return "No discord bot instance"
                                if not self.check_connection():
                                    return "Bot offline"
                                if not user_selection:
                                    return "Please select a user"
                                try:
                                    user_id = int(user_selection.split("ID: ")[1].rstrip(")"))
                                    success = self.discord_bot.block_user(user_id)
                                    if success:
                                        return "Successfully blocked user"
                                    else:
                                        return "Failed to block user"
                                except (ValueError, IndexError):
                                    return "Invalid user selection"
                            
                            def unblock_user(user_selection):
                                if not self.check_available():
                                    return "No discord bot instance"
                                if not self.check_connection():
                                    return "Bot offline"
                                if not user_selection:
                                    return "Please select a user"
                                try:
                                    user_id = int(user_selection.split("ID: ")[1].rstrip(")"))
                                    success = self.discord_bot.unblock_user(user_id)
                                    if success:
                                        return "Successfully unblocked user"
                                    else:
                                        return "Failed to unblock user"
                                except (ValueError, IndexError):
                                    return "Invalid user selection"
                    
                    with gr.Row(visible=False) as custom_msg_section:
                        with gr.Column():
                            gr.Markdown("## Custom Messages")
                            channel_id_input = gr.Textbox(label="Channel ID", placeholder="Enter Discord Channel ID")
                            message_input = gr.Textbox(label="Message", placeholder="Enter message to send", lines=3)
                            send_message_btn = gr.Button("Send Message", size="lg", interactive=True)
                            message_status = gr.Markdown("")
                            
                            def send_custom_message(channel_id, message):
                                if not self.check_available():
                                    return "No discord bot instance"
                                if not self.check_connection():
                                    return "Bot offline"
                                if not channel_id or not message:
                                    return "Channel ID and message required"
                                try:
                                    channel_id_int = int(channel_id)
                                    success = self.discord_bot.send_message(0, channel_id_int, message)
                                    if success:
                                        return "Message sent successfully"
                                    else:
                                        return "Failed to send message"
                                except ValueError:
                                    return "Invalid channel ID (must be a number)"
                    
                    with gr.Row(visible=False) as bot_settings_section:
                        with gr.Column():
                            gr.Markdown("## Bot Settings")
                            
                            with gr.Group():
                                gr.Markdown("### Translation Settings")
                                auto_translate_checkbox = gr.Checkbox(label="Auto Translate", value=False, interactive=True, info="Automatically translate all incoming messages")
                                input_translate_language = gr.Dropdown(label="Target Language", choices=["en", "de", "es", "fr", "it", "ja", "zh-CN"], value="de", interactive=True,info="Language to translate messages to")
                            
                            with gr.Group():
                                gr.Markdown("### Command Settings")
                                log_messages_checkbox = gr.Checkbox(label="Log Messages", value=True, interactive=True)
                                
                            
                            save_settings_btn = gr.Button("Save Settings", variant="primary", size="lg", interactive=True)
                            settings_status = gr.Markdown("")
                            
                            def save_bot_settings(auto_translate_enabled, target_language, log_messages):
                                if not self.check_available():
                                    return "No discord bot instance"
                                if not self.check_connection():
                                    return "Bot offline"
                                
                                success = True
                                if hasattr(self.discord_bot, 'update_auto_translate'):
                                    success = self.discord_bot.update_auto_translate(auto_translate_enabled, target_language)
                                
                                if hasattr(self.discord_bot, 'update_log_messages'):
                                    log_success = self.discord_bot.update_log_messages(log_messages)
                                    success = success and log_success
                             
                                try:
                                    from discord_bot.init.config_loader import DiscordConfigLoader
                                                
                                    DiscordConfigLoader.TARGET_LANGUAGE = target_language
                                    
                                    self.logging(f"Updated DiscordConfigLoader.TARGET_LANGUAGE = {target_language}")
                                except Exception as e:
                                    self.logging(f"Error updating config_loader: {e}")
                                    success = False
                                
                                if success:
                                    status_parts = [
                                        f"**Settings saved successfully!**",
                                        f"\n- Auto Translate: **{'ON' if auto_translate_enabled else 'OFF'}**",
                                        f"\n- Target Language: **{target_language.upper()}**" if auto_translate_enabled else "",
                                        f"\n- Log Messages: **{'ON' if log_messages else 'OFF'}**",
                                    ]
                                    status_message = "".join(status_parts)
                                    
                                    return f"**Settings saved successfully!**\n\n{status_message}"
                                else:
                                    return "**Failed to save settings.**\n\nPlease check the bot connection."
                                            
                    def switch_section(section):
                        if section == "Server Management":
                            return gr.update(visible=True), gr.update(visible=False), gr.update(visible=False), gr.update(visible=False)
                        elif section == "User Management":
                            return gr.update(visible=False), gr.update(visible=True), gr.update(visible=False), gr.update(visible=False)
                        elif section == "Custom Messages":
                            return gr.update(visible=False), gr.update(visible=False), gr.update(visible=True), gr.update(visible=False)
                        elif section == "Bot Settings":
                            return gr.update(visible=False), gr.update(visible=False), gr.update(visible=False), gr.update(visible=True)
                        else:
                            return gr.update(visible=False), gr.update(visible=False), gr.update(visible=False), gr.update(visible=False)
                    
                    gr.on(
                        triggers=[section_selector.change],
                        fn=switch_section,
                        inputs=section_selector,
                        outputs=[
                            server_mgmt_section,
                            user_mgmt_section,
                            custom_msg_section,
                            bot_settings_section,
                        ],
                    )
                    
                    # Event handlers AFTER all sections are closed
                    refresh_btn.click(fn=refresh_server_list, outputs=[server_view, server_status])
                    leave_btn.click(fn=leave_server, inputs=[server_view], outputs=[server_status])
                    
                    search_user_btn.click(fn=search_users, inputs=[user_search], outputs=[user_dropdown, user_status])
                    block_btn.click(fn=block_user, inputs=[user_dropdown], outputs=[user_status])
                    unblock_btn.click(fn=unblock_user, inputs=[user_dropdown], outputs=[user_status])
                    
                    send_message_btn.click(fn=send_custom_message, inputs=[channel_id_input, message_input], outputs=[message_status])
                    
                    save_settings_btn.click(fn=save_bot_settings, inputs=[auto_translate_checkbox, input_translate_language, log_messages_checkbox], outputs=[settings_status])

                        
              
                with gr.Tab("Database"):
                    with gr.Tabs():
                        with gr.Tab("Dishes"):
                            with gr.Row():
                                with gr.Column():
                                    gr.Markdown("### Search & View")
                                    search_query = gr.Textbox(label="Search", placeholder="Enter dish name...")
                                    search_cat = gr.Dropdown(
                                        choices=["All", "Italian", "German", "Austrian", "Mexican", "Chinese", 
                                                "Japanese", "Indian", "American", "French", "Spanish", "Greek",
                                                "Turkish", "Thai", "Korean", "British", "African", "Middle Eastern",
                                                "Vegan", "Dessert", "Seafood"],
                                        value="All",
                                        label="Category"
                                    )
                                    search_btn = gr.Button("Search")
                                    results = gr.Dataframe(headers=["ID", "Category", "Dish"])
                                
                                with gr.Column():
                                    gr.Markdown("### Add New Dish")
                                    new_cat = gr.Dropdown(
                                        choices=["Italian", "German", "Austrian", "Mexican", "Chinese", 
                                                "Japanese", "Indian", "American", "French", "Spanish", "Greek",
                                                "Turkish", "Thai", "Korean", "British", "African", "Middle Eastern",
                                                "Vegan", "Dessert", "Seafood"],
                                        value="Italian",
                                        label="Category"
                                    )
                                    new_name = gr.Textbox(label="Dish Name")
                                    add_btn = gr.Button("Add")
                                    add_status = gr.Markdown("")
                                    
                                    gr.Markdown("### Delete Dish")
                                    del_id = gr.Number(label="Dish ID", precision=0)
                                    del_btn = gr.Button("Delete")
                                    del_status = gr.Markdown("")
                    
                            gr.Markdown("### Test Random Dish")
                            test_cat = gr.Dropdown(
                                choices=["Italian", "German", "Austrian", "Mexican", "Chinese", 
                                        "Japanese", "Indian", "American", "French", "Spanish", "Greek",
                                        "Turkish", "Thai", "Korean", "British", "African", "Middle Eastern",
                                        "Vegan", "Dessert", "Seafood"],
                                value="Italian"
                            )
                            test_btn = gr.Button("Get Random")
                            test_result = gr.Textbox(label="Result", interactive=False)
                    
                            def search_dishes(query, cat):
                                filter_query = {} if cat == "All" else {"category": cat}
                                data = self.dbms.get_data("dishes", filter_query)
                                if query:
                                    data = [d for d in data if query.lower() in d.get("dish", "").lower()]
                                return [[d.get("id"), d.get("category"), d.get("dish")] for d in data]
                            
                            def add_dish(cat, name):
                                if not name:
                                    return "Error: Enter a dish name"
                                all_dishes = self.dbms.get_data("dishes", {})
                                next_id = max([d.get("id", 0) for d in all_dishes], default=0) + 1
                                success = self.dbms.insert_data("dishes", {"id": next_id, "category": cat, "dish": name})
                                return f"Success: Added {name}" if success else "Error: Failed"
                            
                            def delete_dish(dish_id):
                                if not dish_id or dish_id <= 0:
                                    return "Error: Invalid ID"
                                success = self.dbms.delete_data("dishes", {"id": int(dish_id)})
                                return f"Success: Deleted ID {int(dish_id)}" if success else "Error: Failed"
                            
                            def test_dish(cat):
                                if self.controller:
                                    return self.controller.get_dish_suggestion(cat)
                                return self.dish_selector.execute_function(cat) if self.dish_selector else "N/A"
                            
                            search_btn.click(fn=search_dishes, inputs=[search_query, search_cat], outputs=results)
                            add_btn.click(fn=add_dish, inputs=[new_cat, new_name], outputs=add_status)
                            del_btn.click(fn=delete_dish, inputs=del_id, outputs=del_status)
                            test_btn.click(fn=test_dish, inputs=test_cat, outputs=test_result)
                        
                        with gr.Tab("Fun Facts"):
                            with gr.Row():
                                with gr.Column():
                                    gr.Markdown("### Search")
                                    fact_query = gr.Textbox(label="Search", placeholder="Keywords...")
                                    fact_search_btn = gr.Button("Search")
                                    fact_results = gr.Dataframe(headers=["ID", "Fun Fact"])
                                
                                with gr.Column():
                                    gr.Markdown("### Add New")
                                    new_fact = gr.Textbox(label="Fun Fact", lines=3)
                                    fact_add_btn = gr.Button("Add")
                                    fact_add_status = gr.Markdown("")
                                    
                                    gr.Markdown("### Delete")
                                    fact_del_id = gr.Number(label="Fact ID", precision=0)
                                    fact_del_btn = gr.Button("Delete")
                                    fact_del_status = gr.Markdown("")
                    
                            gr.Markdown("### Test Random Fun Fact")
                            fact_test_btn = gr.Button("Get Random")
                            fact_test_result = gr.Textbox(label="Result", interactive=False, lines=3)
                    
                            def search_facts(query):
                                data = self.dbms.get_data("fun_facts", {})
                                if query:
                                    data = [f for f in data if query.lower() in f.get("fun_fact", "").lower()]
                                return [[f.get("id"), f.get("fun_fact")] for f in data]
                            
                            def add_fact(text):
                                if not text:
                                    return "Error: Enter a fun fact"
                                all_facts = self.dbms.get_data("fun_facts", {})
                                next_id = max([f.get("id", 0) for f in all_facts], default=0) + 1
                                success = self.dbms.insert_data("fun_facts", {"id": next_id, "fun_fact": text})
                                return "Success: Added" if success else "Error: Failed"
                            
                            def delete_fact(fact_id):
                                if not fact_id or fact_id <= 0:
                                    return "Error: Invalid ID"
                                success = self.dbms.delete_data("fun_facts", {"id": int(fact_id)})
                                return f"Success: Deleted ID {int(fact_id)}" if success else "Error: Failed"
                            
                            def test_fact():
                                if self.controller:
                                    return self.controller.get_fun_fact()
                                return self.fun_fact_selector.execute_function() if self.fun_fact_selector else "N/A"
                            
                            fact_search_btn.click(fn=search_facts, inputs=fact_query, outputs=fact_results)
                            fact_add_btn.click(fn=add_fact, inputs=new_fact, outputs=fact_add_status)
                            fact_del_btn.click(fn=delete_fact, inputs=fact_del_id, outputs=fact_del_status)
                            fact_test_btn.click(fn=test_fact, outputs=fact_test_result)
                        
                        with gr.Tab("Translator"):
                            gr.Markdown("### Translate Text")
                            
                            with gr.Row():
                                trans_input = gr.Textbox(label="Input", lines=5, placeholder="Enter text...")
                                trans_output = gr.Textbox(label="Output", lines=5, interactive=False)
                            
                            trans_btn = gr.Button("Translate", size="lg")
                            
                            def translate(text):
                                if not text:
                                    return "Enter text"
                                if self.controller:
                                    return self.controller.translate_text(text)
                                elif self.translator:
                                    return self.translator.execute_function(text)
                                return "N/A"
                            
                            trans_btn.click(fn=translate, inputs=trans_input, outputs=trans_output)
                        
                        with gr.Tab("Statistics"):
                            gr.Markdown("### Database Statistics")
                            
                            refresh_stats_btn = gr.Button("Refresh Stats", size="lg")
                            
                            with gr.Row():
                                dishes_stat = gr.Markdown("### Loading...")
                                facts_stat = gr.Markdown("### Loading...")
                                categories_stat = gr.Markdown("### Loading...")
                            
                            stats_json = gr.JSON(label="Detailed Statistics")
                            
                            def load_stats():
                                categories = ["Italian", "German", "Austrian", "Mexican", "Chinese", 
                                            "Japanese", "Indian", "American", "French", "Spanish", 
                                            "Greek", "Turkish", "Thai", "Korean", "British", "African",
                                            "Middle Eastern", "Vegan", "Dessert", "Seafood"]
                                
                                stats = {"dishes": {}, "total_dishes": 0, "total_fun_facts": 0}
                                
                                for cat in categories:
                                    count = self.dbms.get_table_size("dishes", cat)
                                    if count > 0:
                                        stats["dishes"][cat] = count
                                        stats["total_dishes"] += count
                                
                                stats["total_fun_facts"] = self.dbms.get_table_size("fun_facts", None)
                                
                                dishes_md = f'<div class="stat-card"><div class="stat-label">Total Dishes</div><div class="stat-number">{stats["total_dishes"]}</div></div>'
                                facts_md = f'<div class="stat-card"><div class="stat-label">Fun Facts</div><div class="stat-number">{stats["total_fun_facts"]}</div></div>'
                                cats_md = f'<div class="stat-card"><div class="stat-label">Categories</div><div class="stat-number">{len(stats["dishes"])}</div></div>'
                                
                                return dishes_md, facts_md, cats_md, stats
                            
                            refresh_stats_btn.click(fn=load_stats, outputs=[dishes_stat, facts_stat, categories_stat, stats_json])
                            app.load(fn=load_stats, outputs=[dishes_stat, facts_stat, categories_stat, stats_json])
            
            gr.HTML("""
                <div style="text-align: center; padding: 20px; color: #99AAB5; margin-top: 20px;">
                    <p>Discord Bot Admin Panel v1.0</p>
                </div>
            """)
        
        self.app = app
        return app
    
    def launch(self, share: bool = False):
        if not self.app:
            self.build_interface()
        
        self.app.launch(
            server_name=self.host,
            server_port=self.port,
            share=share,
            theme=gr.themes.Soft(primary_hue="blue")
        )

if __name__ == "__main__":
    from discord_bot.adapters.db import DBMS
    from discord_bot.business_logic.dish_selector import DishSelector
    from discord_bot.business_logic.fun_fact_selector import FunFactSelector
    from discord_bot.business_logic.translator import Translator
    from discord_bot.adapters.controller.controller import Controller
    
    db = DBMS()
    db.connect()
    
    dish_selector = DishSelector(dbms=db)
    fun_fact_selector = FunFactSelector(dbms=db)
    translator = Translator()
    
    controller = Controller(
        dish_selector=dish_selector,
        fun_fact_selector=fun_fact_selector,
        translator=translator
    )
    
    panel = AdminPanel(
        dbms=db,
        dish_selector=dish_selector,
        fun_fact_selector=fun_fact_selector,
        translator=translator,
        controller=controller,
        port=7861  
    )
    panel.launch()
