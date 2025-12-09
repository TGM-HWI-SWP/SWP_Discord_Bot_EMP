import gradio as gr
import discord
from discord_bot.contracts.ports import ViewPort, DatabasePort, DishPort, FunFactPort, TranslatePort




ADMIN_PANEL_CSS = """
.gradio-container {
    font-family: 'Whitney', 'Helvetica Neue', Helvetica, Arial, sans-serif;
}
.admin-header {
    background: linear-gradient(135deg, #5865F2 0%, #4752C4 100%);
    color: white;
    padding: 30px;
    border-radius: 12px;
    text-align: center;
    margin-bottom: 25px;
    box-shadow: 0 8px 24px rgba(88, 101, 242, 0.4);
}
.admin-header h1 {
    margin: 0;
    font-size: 2.8em;
    font-weight: 700;
    text-shadow: 2px 2px 8px rgba(0,0,0,0.3);
}
.stat-card {
    background: linear-gradient(135deg, #2C2F33 0%, #23272A 100%);
    color: white;
    padding: 25px;
    border-radius: 12px;
    text-align: center;
    box-shadow: 0 4px 12px rgba(0,0,0,0.4);
    border: 3px solid #5865F2;
}
.stat-number {
    font-size: 3em;
    font-weight: 700;
    color: white;
}
.stat-label {
    font-size: 1.2em;
    color: #99AAB5;
    text-transform: uppercase;
}

/* Override Gradio orange colors with Discord blue */
button.primary, .gr-button-primary {
    background: #5865F2 !important;
    border-color: #5865F2 !important;
}
button.primary:hover, .gr-button-primary:hover {
    background: #4752C4 !important;
    border-color: #4752C4 !important;
}
.tabs button[aria-selected="true"] {
    border-bottom-color: #5865F2 !important;
    color: #5865F2 !important;
}
"""

class AdminPanel(ViewPort):
    def __init__(
        self,
        dbms: DatabasePort,
        discord_bot: discord.Client | None = None,
        dish_selector: DishPort | None = None,
        fun_fact_selector: FunFactPort | None = None,
        translator: TranslatePort | None = None,
        host: str = "0.0.0.0",
        port: int = 7860
    ):
        self.dbms = dbms
        self.discord_bot = discord_bot
        self.dish_selector = dish_selector
        self.fun_fact_selector = fun_fact_selector
        self.translator = translator
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
        with gr.Blocks(title="Discord Bot Admin Panel") as app:
            
            
            gr.HTML(f"""
                <style>
                {ADMIN_PANEL_CSS}
                </style>
                <div class="admin-header">
                    <h1>Discord Bot Admin Panel</h1>
                    <p style="font-size: 1.2em; margin-top: 10px; opacity: 0.9;">
                        Bot Control & Database Management
                    </p>
                </div>
            """)
            
            with gr.Tabs():
                
                with gr.Tab("Dashboard"):
                    gr.Markdown("### Discord Bot Status")
                    
                    refresh_btn = gr.Button("Refresh Status", size="lg")
                    
                    with gr.Row():
                        bot_status = gr.Markdown("### Loading...")
                        servers_stat = gr.Markdown("### Loading...")
                        users_stat = gr.Markdown("### Loading...")
                    
                    bot_info = gr.JSON(label="Bot Information")
                    
                    def load_dashboard():
                        status = {"status": "online", "servers": 0, "users": 0}
                        
                        status_md = f'<div class="stat-card"><div class="stat-label">Status</div><div class="stat-number">Online</div></div>'
                        servers_md = f'<div class="stat-card"><div class="stat-label">Servers</div><div class="stat-number">{status["servers"]}</div></div>'
                        users_md = f'<div class="stat-card"><div class="stat-label">Users</div><div class="stat-number">{status["users"]}</div></div>'
                        
                        return status_md, servers_md, users_md, status
                    
                    refresh_btn.click(fn=load_dashboard, outputs=[bot_status, servers_stat, users_stat, bot_info])
                    app.load(fn=load_dashboard, outputs=[bot_status, servers_stat, users_stat, bot_info])
                
                with gr.Tab("Bot Control"):
                    gr.Markdown("### Discord Bot Management")
                    
                    with gr.Row():
                        with gr.Column():
                            gr.Markdown("#### Server Management")
                            server_list = gr.Dropdown(label="Select Server", choices=[], interactive=True)
                            refresh_servers_btn = gr.Button("Refresh Servers")
                            leave_server_btn = gr.Button("Leave Server")
                            server_status = gr.Markdown("")
                        
                        with gr.Column():
                            gr.Markdown("#### User Management")
                            user_id_input = gr.Textbox(label="User ID")
                            block_user_btn = gr.Button("Block User")
                            unblock_user_btn = gr.Button("Unblock User")
                            user_status = gr.Markdown("")
                    
                    gr.Markdown("#### Send Custom Message")
                    with gr.Row():
                        channel_id_input = gr.Textbox(label="Channel ID")
                        message_input = gr.Textbox(label="Message", lines=3)
                    send_message_btn = gr.Button("Send Message")
                    message_status = gr.Markdown("")
                    
                    gr.Markdown("#### Bot Settings")
                    with gr.Row():
                        with gr.Column():
                            bot_prefix = gr.Textbox(label="Command Prefix", value="!")
                            bot_status_text = gr.Textbox(label="Status Text", value="Playing")
                        with gr.Column():
                            auto_reply = gr.Checkbox(label="Auto Reply", value=False)
                            log_messages = gr.Checkbox(label="Log Messages", value=True)
                    update_settings_btn = gr.Button("Update Settings")
                    settings_status = gr.Markdown("")
                    
                    
                    def refresh_server_list():
                        if not self.check_available():
                            return gr.update(), "No discord bot instance"
                        
                        if not self.check_connection():
                            return gr.update(), "Bot offline"
                            
                        servers = self.discord_bot.get_servers()
                        if not servers:
                            return gr.update(), "No servers found"
                            
                        choices = [f'{server["name"]} ({server["id"]})' for server in servers]
                        return gr.update(choices=choices), f"Found {len(servers)} servers"
                    
                    def leave_server(server_selection: str):
                        if not self.check_available():
                            return gr.update(), "No discord bot instance"
                        if not self.check_connection():
                            return gr.update(), "Bot offline"
                        if not server_selection:
                            return gr.update(), "Please select a server"
                        try:
                            server_id = int(server_selection.split('(')[-1].rstrip(')'))
                        except (ValueError, IndexError):
                            return gr.update(), "Invalid server selection"
                        
                        success = self.discord_bot.leave_server(server_id)
                        if success:
                            return refresh_server_list()
                        else:
                            return gr.update(), f"Failed to leave server (ID: {server_id})"
                    
                    def block_user(user_id: str):
                        if not self.check_available():
                            return "No discord bot instance"
                        
                        if not self.check_connection():
                            return "Bot offline"
                        
                        if not user_id:
                            return "Please enter a User ID"
                        
                        try:
                            user_id_int = int(user_id)
                        except ValueError:
                            return "Invalid User ID (must be a number)"
                        
                        success = self.discord_bot.block_user(user_id_int)
                        if success:
                            return f"Successfully blocked user (ID: {user_id_int})"
                        else:
                            return f"Failed to block user (ID: {user_id_int})"
                    
                    def unblock_user(user_id: str):
                        if not self.check_available():
                            return "No discord bot instance"
                        
                        if not self.check_connection():
                            return "Bot offline"
                        
                        if not user_id:
                            return "Please enter a User ID"
                        
                        try:
                            user_id_int = int(user_id)
                        except ValueError:
                            return "Invalid User ID (must be a number)"
                        
                        success = self.discord_bot.unblock_user(user_id_int)
                        if success:
                            return f"Successfully unblocked user (ID: {user_id_int})"
                        else:
                            return f"Failed to unblock user (ID: {user_id_int})"
                    
                    def send_message(channel_id: str, message: str):
                        if not self.check_available():
                            return "No discord bot instance"
                            
                        if not self.check_connection():
                            return "Bot offline"
                            
                        if not all([channel_id, message]):  
                            return "Channel ID and message required"
            
                        try:
                            channel_id = int(channel_id)
                        except ValueError:
                            return "Invalid channel ID"
                            
                        success = self.discord_bot.send_message(0, channel_id, message)
                        return "Message sent successfully" if success else "Failed to send message"
                    
                    def placeholder_update_settings():
                        return "Placeholder: Update settings"
                    
                    refresh_servers_btn.click(fn=refresh_server_list, outputs=[server_list, server_status])
                    leave_server_btn.click(fn=leave_server, inputs=[server_list], outputs=[server_list, server_status])
                    block_user_btn.click(fn=block_user, inputs=[user_id_input], outputs=user_status)
                    unblock_user_btn.click(fn=unblock_user, inputs=[user_id_input], outputs=user_status)
                    send_message_btn.click(fn=send_message, inputs=[channel_id_input, message_input], outputs=message_status)
                    update_settings_btn.click(fn=placeholder_update_settings, outputs=settings_status)
                
                with gr.Tab("Servers"):
                    gr.Markdown("### Discord Servers")
                    gr.Markdown("All servers where the bot is currently active")
                    
                    refresh_server_view_btn = gr.Button("Refresh Server List", size="lg")
                    
                    server_table = gr.Dataframe(
                        headers=["Server ID", "Server Name", "Member Count"],
                        label="Connected Servers",
                        interactive=False
                    )
                    
                    server_view_status = gr.Markdown("")
                    
                    def load_server_list():
                        if not self.check_available():
                            return [], "Discord bot not available (runs in separate container)"
                        
                        if not self.check_connection():
                            return [], "Bot is offline"
                        
                        try:
                            servers = self.discord_bot.get_servers()
                            if not servers:
                                return [], "No servers found"
                            
                            server_data = []
                            for server in servers:
                                server_id = server.get("id", "N/A")
                                server_name = server.get("name", "Unknown")
                                
                                member_count = "N/A"
                                try:
                                    guild = self.discord_bot.client.get_guild(server_id)
                                    if guild:
                                        member_count = guild.member_count
                                except:
                                    pass
                                
                                server_data.append([server_id, server_name, member_count])
                            
                            return server_data, f"Found {len(servers)} server(s)"
                        except Exception as e:
                            return [], f"Error loading servers: {str(e)}"
                    
                    refresh_server_view_btn.click(fn=load_server_list, outputs=[server_table, server_view_status])
                    app.load(fn=load_server_list, outputs=[server_table, server_view_status])
                
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
                                return self.translator.execute_function(text) if self.translator else "N/A"
                            
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
            share=share
        )

if __name__ == "__main__":
    from discord_bot.adapters.db import DBMS
    from discord_bot.business_logic.dish_selector import DishSelector
    from discord_bot.business_logic.fun_fact_selector import FunFactSelector
    from discord_bot.business_logic.translator import Translator
    
    db = DBMS()
    db.connect()
    
    dish_selector = DishSelector(dbms=db)
    fun_fact_selector = FunFactSelector(dbms=db)
    translator = Translator()
    
    panel = AdminPanel(
        dbms=db,
        dish_selector=dish_selector,
        fun_fact_selector=fun_fact_selector,
        translator=translator,
        port=7861  
    )
    panel.launch()
