import gradio as gr

from discord_bot.contracts.ports import ViewPort, DatabasePort, ControllerPort


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
        controller: ControllerPort,
        host: str = "0.0.0.0",
        port: int = 7860
    ):
        self.dbms = dbms
        self.controller = controller
        self.host = host
        self.port = port
        self.app = None
    
    def get_user_input(self, interactable_element: str) -> str:
        return ""
    
    def build_interface(self) -> gr.Blocks:
        with gr.Blocks(title="Discord Bot Admin Panel") as app:
            
            gr.HTML("""
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
                    
                    refresh_button = gr.Button("Refresh Status", size="lg")
                    
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
                    
                    refresh_button.click(fn=load_dashboard, outputs=[bot_status, servers_stat, users_stat, bot_info])
                    app.load(fn=load_dashboard, outputs=[bot_status, servers_stat, users_stat, bot_info])
                
                with gr.Tab("Bot Control"):
                    gr.Markdown("### Discord Bot Management")
                    
                    with gr.Row():
                        with gr.Column():
                            gr.Markdown("#### Server Management")
                            server_list = gr.Dropdown(label="Select Server", choices=[], interactive=True)
                            refresh_servers_button = gr.Button("Refresh Servers")
                            leave_server_button = gr.Button("Leave Server")
                            server_status = gr.Markdown("")
                        
                        with gr.Column():
                            gr.Markdown("#### User Management")
                            user_id_input = gr.Textbox(label="User ID")
                            block_user_button = gr.Button("Block User")
                            unblock_user_button = gr.Button("Unblock User")
                            user_status = gr.Markdown("")
                    
                    gr.Markdown("#### Send Custom Message")
                    with gr.Row():
                        channel_id_input = gr.Textbox(label="Channel ID")
                        message_input = gr.Textbox(label="Message", lines=3)
                    send_message_button = gr.Button("Send Message")
                    message_status = gr.Markdown("")
                    
                    gr.Markdown("#### Bot Settings")
                    with gr.Row():
                        with gr.Column():
                            bot_prefix = gr.Textbox(label="Command Prefix", value="!")
                            bot_status_text = gr.Textbox(label="Status Text", value="Playing")
                        with gr.Column():
                            auto_reply = gr.Checkbox(label="Auto Reply", value=False)
                            log_messages = gr.Checkbox(label="Log Messages", value=True)
                    update_settings_button = gr.Button("Update Settings")
                    settings_status = gr.Markdown("")
                    
                    def placeholder_refresh_servers():
                        return "Placeholder: Refresh servers"
                    
                    def placeholder_leave_server():
                        return "Placeholder: Leave server"
                    
                    def placeholder_block_user():
                        return "Placeholder: Block user"
                    
                    def placeholder_unblock_user():
                        return "Placeholder: Unblock user"
                    
                    def placeholder_send_message():
                        return "Placeholder: Send message"
                    
                    def placeholder_update_settings():
                        return "Placeholder: Update settings"
                    
                    refresh_servers_button.click(fn=placeholder_refresh_servers, outputs=server_status)
                    leave_server_button.click(fn=placeholder_leave_server, outputs=server_status)
                    block_user_button.click(fn=placeholder_block_user, outputs=user_status)
                    unblock_user_button.click(fn=placeholder_unblock_user, outputs=user_status)
                    send_message_button.click(fn=placeholder_send_message, outputs=message_status)
                    update_settings_button.click(fn=placeholder_update_settings, outputs=settings_status)
                
                with gr.Tab("Database"):
                    with gr.Tabs():
                        with gr.Tab("Dishes"):
                            with gr.Row():
                                with gr.Column():
                                    gr.Markdown("### Search & View")
                            search_query = gr.Textbox(label="Search", placeholder="Enter dish name...")
                            search_category = gr.Dropdown(
                                choices=["All", "Italian", "German", "Austrian", "Mexican", "Chinese", 
                                        "Japanese", "Indian", "American", "French", "Spanish", "Greek",
                                        "Turkish", "Thai", "Korean", "British", "African", "Middle Eastern",
                                        "Vegan", "Dessert", "Seafood"],
                                value="All",
                                label="Category"
                            )
                            search_button = gr.Button("Search")
                            results = gr.Dataframe(headers=["ID", "Category", "Dish"])
                        
                        with gr.Column():
                            gr.Markdown("### Add New Dish")
                            new_category = gr.Dropdown(
                                choices=["Italian", "German", "Austrian", "Mexican", "Chinese", 
                                        "Japanese", "Indian", "American", "French", "Spanish", "Greek",
                                        "Turkish", "Thai", "Korean", "British", "African", "Middle Eastern",
                                        "Vegan", "Dessert", "Seafood"],
                                value="Italian",
                                label="Category"
                            )
                            new_name = gr.Textbox(label="Dish Name")
                            add_button = gr.Button("Add")
                            add_status = gr.Markdown("")
                                    
                            gr.Markdown("### Delete Dish")
                            delete_id = gr.Number(label="Dish ID", precision=0)
                            delete_button = gr.Button("Delete")
                            delete_status = gr.Markdown("")                            
                            gr.Markdown("### Test Random Dish")
                            test_category = gr.Dropdown(
                                choices=["Italian", "German", "Austrian", "Mexican", "Chinese", 
                                        "Japanese", "Indian", "American", "French", "Spanish", "Greek",
                                        "Turkish", "Thai", "Korean", "British", "African", "Middle Eastern",
                                        "Vegan", "Dessert", "Seafood"],
                                value="Italian"
                            )
                            test_button = gr.Button("Get Random")
                            test_result = gr.Textbox(label="Result", interactive=False)
                    
                            def search_dishes(query, category):
                                filter_query = {} if category == "All" else {"category": category}
                                data = self.dbms.get_data("dishes", filter_query)
                                if query:
                                    data = [dish for dish in data if query.lower() in dish.get("dish", "").lower()]
                                return [[dish.get("id"), dish.get("category"), dish.get("dish")] for dish in data]
                            
                            def add_dish(category, name):
                                if not name:
                                    return "Error: Enter a dish name"
                                all_dishes = self.dbms.get_data("dishes", {})
                                next_id = max([dish.get("id", 0) for dish in all_dishes], default=0) + 1
                                success = self.dbms.insert_data("dishes", {"id": next_id, "category": category, "dish": name})
                                return f"Success: Added {name}" if success else "Error: Failed"
                            
                            def delete_dish(dish_id):
                                if not dish_id or dish_id <= 0:
                                    return "Error: Invalid ID"
                                success = self.dbms.delete_data("dishes", {"id": int(dish_id)})
                                return f"Success: Deleted ID {int(dish_id)}" if success else "Error: Failed"
                            
                            def test_dish(category):
                                return self.controller.get_dish_suggestion(category)
                            
                            search_button.click(fn=search_dishes, inputs=[search_query, search_category], outputs=results)
                            add_button.click(fn=add_dish, inputs=[new_category, new_name], outputs=add_status)
                            delete_button.click(fn=delete_dish, inputs=delete_id, outputs=delete_status)
                            test_button.click(fn=test_dish, inputs=test_category, outputs=test_result)
                        
                        with gr.Tab("Fun Facts"):
                            with gr.Row():
                                with gr.Column():
                                    gr.Markdown("### Search")
                                    fact_query = gr.Textbox(label="Search", placeholder="Keywords...")
                                    fact_search_button = gr.Button("Search")
                                    fact_results = gr.Dataframe(headers=["ID", "Fun Fact"])
                                
                                with gr.Column():
                                    gr.Markdown("### Add New")
                                    new_fact = gr.Textbox(label="Fun Fact", lines=3)
                                    fact_add_button = gr.Button("Add")
                                    fact_add_status = gr.Markdown("")
                                    
                                    gr.Markdown("### Delete")
                                    fact_delete_id = gr.Number(label="Fact ID", precision=0)
                                    fact_delete_button = gr.Button("Delete")
                                    fact_delete_status = gr.Markdown("")
                    
                            gr.Markdown("### Test Random Fun Fact")
                            fact_test_button = gr.Button("Get Random")
                            fact_test_result = gr.Textbox(label="Result", interactive=False, lines=3)
                    
                            def search_facts(query):
                                data = self.dbms.get_data("fun_facts", {})
                                if query:
                                    data = [fact for fact in data if query.lower() in fact.get("fun_fact", "").lower()]
                                return [[fact.get("id"), fact.get("fun_fact")] for fact in data]
                            
                            def add_fact(text):
                                if not text:
                                    return "Error: Enter a fun fact"
                                all_facts = self.dbms.get_data("fun_facts", {})
                                next_id = max([fact.get("id", 0) for fact in all_facts], default=0) + 1
                                success = self.dbms.insert_data("fun_facts", {"id": next_id, "fun_fact": text})
                                return "Success: Added" if success else "Error: Failed"
                            
                            def delete_fact(fact_id):
                                if not fact_id or fact_id <= 0:
                                    return "Error: Invalid ID"
                                success = self.dbms.delete_data("fun_facts", {"id": int(fact_id)})
                                return f"Success: Deleted ID {int(fact_id)}" if success else "Error: Failed"
                            
                            def test_fact():
                                return self.controller.get_fun_fact()
                            
                            fact_search_button.click(fn=search_facts, inputs=fact_query, outputs=fact_results)
                            fact_add_button.click(fn=add_fact, inputs=new_fact, outputs=fact_add_status)
                            fact_delete_button.click(fn=delete_fact, inputs=fact_delete_id, outputs=fact_delete_status)
                            fact_test_button.click(fn=test_fact, outputs=fact_test_result)
                        
                        with gr.Tab("Translator"):
                            gr.Markdown("### Translate Text")
                            
                            with gr.Row():
                                translate_input = gr.Textbox(label="Input", lines=5, placeholder="Enter text...")
                                translate_output = gr.Textbox(label="Output", lines=5, interactive=False)
                            
                            translate_button = gr.Button("Translate", size="lg")
                            
                            def translate(text):
                                if not text:
                                    return "Enter text"
                                return self.controller.translate_text(text)
                            
                            translate_button.click(fn=translate, inputs=translate_input, outputs=translate_output)
                        
                        with gr.Tab("Statistics"):
                            gr.Markdown("### Database Statistics")
                            
                            refresh_stats_button = gr.Button("Refresh Stats", size="lg")
                            
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
                                
                                for category in categories:
                                    count = self.dbms.get_table_size("dishes", category)
                                    if count > 0:
                                        stats["dishes"][category] = count
                                        stats["total_dishes"] += count
                                
                                stats["total_fun_facts"] = self.dbms.get_table_size("fun_facts", None)
                                
                                dishes_md = f'<div class="stat-card"><div class="stat-label">Total Dishes</div><div class="stat-number">{stats["total_dishes"]}</div></div>'
                                facts_md = f'<div class="stat-card"><div class="stat-label">Fun Facts</div><div class="stat-number">{stats["total_fun_facts"]}</div></div>'
                                cats_md = f'<div class="stat-card"><div class="stat-label">Categories</div><div class="stat-number">{len(stats["dishes"])}</div></div>'
                                
                                return dishes_md, facts_md, cats_md, stats
                            
                            refresh_stats_button.click(fn=load_stats, outputs=[dishes_stat, facts_stat, categories_stat, stats_json])
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
            css=ADMIN_PANEL_CSS
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
        controller=controller
    )
    panel.launch()
