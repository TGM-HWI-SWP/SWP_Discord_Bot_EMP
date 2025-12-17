"""This File contains the gradio Web-Interface."""

import gradio as gr

from discord_bot.business_logic.discord_logic import DiscordLogic
from discord_bot.contracts.ports import ViewPort, DatabasePort, DishPort, FunFactPort, TranslatePort, ControllerPort
from discord_bot.init.db_loader import DBLoader

class AdminPanel(ViewPort):
    def __init__(
        self,
        dbms: DatabasePort,
        discord_bot: DiscordLogic | None = None,
        dish_selector: DishPort | None = None,
        fun_fact_selector: FunFactPort | None = None,
        translator: TranslatePort | None = None,
        controller: ControllerPort | None = None,
        db_loader: DBLoader | None = None,
        host: str = "0.0.0.0",
        port: int = 7860
    ):
        self.dbms = dbms
        self.discord_bot = discord_bot
        self.dish_selector = dish_selector
        self.fun_fact_selector = fun_fact_selector
        self.translator = translator
        self.controller = controller
        self.db_loader = db_loader
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
            with gr.Tabs():
                with gr.Tab("Overview"):
                    gr.Markdown("### Bot Status")

                    refresh_btn = gr.Button("Refresh", variant="primary")

                    with gr.Row():
                        with gr.Column():
                            bot_status = gr.Textbox(label="Status", value="Loading...", interactive=False)
                        with gr.Column():
                            guild_count = gr.Textbox(
                                label="Guilds", value="Loading...", interactive=False)
                        with gr.Column():
                            user_count = gr.Textbox(label="Total Users", value="Loading...", interactive=False)
                    
                    def load_bot_status():
                        if not self.check_available():
                            return "Unavailable", "0", "0"
                        
                        try:
                            stats = self.discord_bot.get_bot_stats()
                            return stats["status"], str(stats["Guilds"]), f'{stats['users']:,}'
                        except Exception as error:
                            return "Error", "0", "0"
                    
                    refresh_btn.click(fn=load_bot_status, outputs=[bot_status, guild_count, user_count])
                    app.load(fn=load_bot_status, outputs=[bot_status, guild_count, user_count])

                with gr.Tab("Control Panel"):
                    section_selector = gr.Dropdown(label="Select Section", choices=["Guild Management", "Custom Messages", "Bot Settings"], value="Guild Management",interactive=True)
                   
                    with gr.Row(visible=True) as guild_mgmt_section:
                        with gr.Column():
                            gr.Markdown("## Guild Management")
                            guild_view = gr.Dropdown(label="Select Guild to Leave", choices=[], interactive=True)
                            leave_btn = gr.Button("Leave Guild", size="lg", interactive=True)
                            refresh_btn = gr.Button("Refresh Guilds", size="lg", interactive=True)
                            guild_status = gr.Markdown("")
                            
                            def leave_guild(guild_selection):
                                if not self.check_available():
                                    return "No discord bot instance"
                                if not self.check_connection():
                                    return "Bot offline"
                                if not guild_selection:
                                    return "Please select a guild"
                                try:
                                    guild_id = int(guild_selection.split("ID: ")[1].rstrip(")"))
                                    success = self.discord_bot.leave_guild(guild_id)
                                    if success:
                                        return "Successfully left guild"
                                    else:
                                        return "Failed to leave guild"
                                except (ValueError, IndexError):
                                    return "Invalid guild selection"
                            
                            def refresh_guild_list():
                                if not self.check_available():
                                    return gr.update(choices=[]), "No discord bot instance"
                                if not self.check_connection():
                                    return gr.update(choices=[]), "Bot offline"
                                
                                guilds = self.discord_bot.get_guilds()
                                if not guilds:
                                    return gr.update(choices=[]), "No guilds found"
                                
                                choices = [f'{guild['name']} (ID: {guild['id']})' for guild in guilds]
                                return gr.update(choices=choices), f'Found {len(guilds)} guilds'

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
                                gr.Markdown("### Command Settings")
                                log_messages_checkbox = gr.Checkbox(label="Log Messages", value=True, interactive=True)
                                
                            save_settings_btn = gr.Button("Save Settings", variant="primary", size="lg", interactive=True)
                            settings_status = gr.Markdown("")
                            
                            def save_bot_settings(log_messages):
                                if not self.check_available():
                                    return "No discord bot instance"
                                if not self.check_connection():
                                    return "Bot offline"
                                
                                success = True
                                if hasattr(self.discord_bot, 'update_log_messages'):
                                    log_success = self.discord_bot.update_log_messages(log_messages)
                                    success = success and log_success
                            
                                if success:
                                    status_parts = [
                                        f'**Settings saved successfully!**',
                                        f'\n- Log Messages: **{'ON' if log_messages else 'OFF'}**',
                                    ]
                                    status_message = "".join(status_parts)
                                    
                                    return f'**Settings saved successfully!**\n\n{status_message}'
                                else:
                                    return "**Failed to save settings.**\n\nPlease check the bot connection."
                                            
                    def switch_section(section):
                        if section == "Guild Management":
                            return gr.update(visible=True), gr.update(visible=False), gr.update(visible=False), gr.update(visible=False)
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
                            guild_mgmt_section,
                            custom_msg_section,
                            bot_settings_section
                        ],
                    )
                    
                    # Event handlers AFTER all sections are closed
                    refresh_btn.click(fn=refresh_guild_list, outputs=[guild_view, guild_status])
                    leave_btn.click(fn=leave_guild, inputs=[guild_view], outputs=[guild_status])

                    send_message_btn.click(fn=send_custom_message, inputs=[channel_id_input, message_input], outputs=[message_status])
                    
                    save_settings_btn.click(fn=save_bot_settings, inputs=[log_messages_checkbox], outputs=[settings_status])

                with gr.Tab("Database"):
                    with gr.Tabs():
                        with gr.Tab("Dishes"):
                            with gr.Row():
                                with gr.Column():
                                    gr.Markdown("### Search & View")
                                    dish_categories = self.dbms.get_distinct_values("dishes", "category")
                                    search_query = gr.Textbox(label="Search", placeholder="Enter dish name...")
                                    search_cat = gr.Dropdown(
                                        choices=["All"] + dish_categories,
                                        value="All",
                                        label="Category"
                                    )
                                    search_btn = gr.Button("Search")
                                    results = gr.Dataframe(headers=["ID", "Category", "Dish"])

                                    gr.Markdown("### Reset Dishes Table")
                                    reset_btn = gr.Button("Reset to Initial Data")
                                    reset_status = gr.Markdown("")
                                
                                with gr.Column():
                                    gr.Markdown("### Add New Dish")
                                    new_cat = gr.Dropdown(
                                        choices=dish_categories,
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
                                choices=dish_categories,
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
                                return f'Success: Added {name}' if success else "Error: Failed"
                            
                            def delete_dish(dish_id):
                                if not dish_id or dish_id <= 0:
                                    return "Error: Invalid ID"
                                success = self.dbms.delete_data("dishes", {"id": int(dish_id)}) # broken
                                return f'Success: Deleted ID {int(dish_id)}' if success else "Error: Failed"
                            
                            def reset_dishes():
                                self.dbms.delete_data() # broken 
                                self.db_loader.import_tables(force_reload=True, specific_table="dishes")
                                return "Dish table reset to initial data"
                            
                            def test_dish(cat):
                                if self.controller:
                                    return self.controller.get_dish_suggestion(cat)
                                return self.dish_selector.execute_function(cat) if self.dish_selector else "N/A"
                            
                            search_btn.click(fn=search_dishes, inputs=[search_query, search_cat], outputs=results)
                            add_btn.click(fn=add_dish, inputs=[new_cat, new_name], outputs=add_status)
                            del_btn.click(fn=delete_dish, inputs=del_id, outputs=del_status)
                            test_btn.click(fn=test_dish, inputs=test_cat, outputs=test_result)
                            reset_btn.click(fn=reset_dishes, outputs=reset_status)
                        
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
                                return f'Success: Deleted ID {int(fact_id)}' if success else "Error: Failed"
                            
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
                                categories = dish_categories
                                
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
                    <p>Discord Bot Admin Panel v1.1</p>
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
    # Outdated test code - ignore
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
    )

    panel.launch()
