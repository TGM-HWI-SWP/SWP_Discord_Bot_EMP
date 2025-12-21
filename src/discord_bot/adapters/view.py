"""This File contains the gradio Web-Interface."""

import gradio as gr

from discord_bot.business_logic.discord_logic import DiscordLogic
from discord_bot.contracts.ports import ViewPort, DatabasePort, DishPort, FunFactPort, TranslatePort, ControllerPort
from discord_bot.init.db_loader import DBLoader

class AdminPanel(ViewPort):
    """Admin panel for managing the Discord bot via a web interface."""
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

            def _bot_guard() -> str | None:
                """Check if the Discord bot instance is available and online.

                Returns:
                    str | None: An error message if the bot is unavailable or offline, otherwise None.
                """
                if not self.check_available():
                    return "No discord bot instance"
                if not self.check_connection():
                    return "Bot offline"
                return None

            def _parse_positive_int(value) -> int | None:
                """Parse a value into a positive integer.

                Args:
                    value (Any): The value to parse.

                Returns:
                    int | None: The parsed positive integer, or None if parsing fails or value is not positive.
                """
                if value is None:
                    return None
                raw = str(value).strip()
                if raw == "":
                    return None
                try:
                    parsed = int(float(raw))
                except (TypeError, ValueError):
                    return None
                return parsed if parsed > 0 else None

            def _next_numeric_id(table_name: str) -> int:
                """Generate the next numeric ID for a given database table.

                Args:
                    table_name (str): The name of the database table.

                Returns:
                    int: The next available numeric ID.
                """
                docs = self.dbms.get_data(table_name, {})
                ids: list[int] = []
                for doc in docs:
                    try:
                        ids.append(int(doc.get("id")))
                    except (TypeError, ValueError):
                        continue
                return max(ids, default=0) + 1

            def _id_query(id_value: int) -> dict:
                """Create a query to match a document by ID, allowing both int and string formats.

                Args:
                    id_value (int): The ID value to query.

                Returns:
                    dict: A MongoDB-style query dictionary to match the ID.
                """
                return {"$or": [{"id": id_value}, {"id": str(id_value)}]}
                
            with gr.Tabs():
                with gr.Tab("Overview"):
                    
                    gr.HTML("""
                        <div style="width:100%;margin-bottom:18px;display:flex;justify-content:center;">
                            <div style="width:calc(100% - 48px);max-width:1200px;background:#2F71F0;color:white;border-radius:14px;padding:18px 24px;display:flex;align-items:center;justify-content:center;box-shadow:0 6px 16px rgba(47,113,240,0.18);">
                                <div style="text-align:center;font-size:32px;font-weight:700;letter-spacing:0.4px;">
                                    Discord Bot Admin Panel
                                </div>
                            </div>
                        </div>
                    """)

                    gr.Markdown("### Bot Status")
                    refresh_btn = gr.Button("Refresh", variant="primary")
                    refresh_status = gr.Markdown("")

                    with gr.Row():
                        with gr.Column():
                            bot_status = gr.Textbox(label="Status", value="Loading...", interactive=False)
                        with gr.Column():
                            guild_count = gr.Textbox(
                                label="Guilds", value="Loading...", interactive=False)
                        with gr.Column():
                            user_count = gr.Textbox(label="Total Users", value="Loading...", interactive=False)

                    def load_bot_status_initial():
                        """Load the initial status of the Discord bot.

                        Returns:
                            tuple[str, str, str, str]: A tuple containing:
                                - Bot status as a string.
                                - Number of guilds as a string.
                                - Number of users formatted with commas as a string.
                                - An additional info message as a string.
                        """
                        if not self.check_available():
                            return ("No discord bot instance", "0", "0", "")
                        try:
                            stats = self.discord_bot.get_bot_stats()
                            return (stats.get("status", "Offline"), str(stats.get("guilds", 0)), "{:,}".format(stats.get("users", 0)), "")
                        except Exception:
                            return ( "Error", "0", "0", "")

                    def load_bot_status():
                        """Refresh and load the current status of the Discord bot.

                        Returns:
                            tuple[gr.update | str, gr.update | str, gr.update | str, str]: A tuple containing:
                                - Bot status (string or Gradio update object).
                                - Number of guilds (string or Gradio update object).
                                - Number of users formatted with commas (string or Gradio update object).
                                - A message indicating success or error of the refresh.
                        """
                        if not self.check_available():
                            return (gr.update(value="No discord bot instance"), gr.update(value="0"), gr.update(value="0"), "No discord bot instance")

                        try:
                            stats = self.discord_bot.get_bot_stats()
                            return (stats.get("status", "Offline"), str(stats.get("guilds", 0)), "{:,}".format(stats.get("users", 0)), "Refresh successful")
                        except Exception:
                            return (gr.update(value="Error"), gr.update(value="0"), gr.update(value="0"), "Error while refreshing")
                        
                    refresh_btn.click(fn=load_bot_status, outputs=[bot_status, guild_count, user_count, refresh_status])
                    app.load(fn=load_bot_status_initial, outputs=[bot_status, guild_count, user_count, refresh_status])

                with gr.Tab("Control Panel"):
                    section_selector = gr.Dropdown(label="Select Section", choices=["Guild Management", "Custom Messages"], value="Guild Management",interactive=True)
                   
                    with gr.Row(visible=True) as guild_mgmt_section:
                        with gr.Column():
                            gr.Markdown("## Guild Management")
                            guild_view = gr.Dropdown(label="Select Guild to Leave", choices=[], interactive=True)
                            leave_btn = gr.Button("Leave Guild", size="lg", interactive=True)
                            refresh_btn = gr.Button("Refresh Guilds", size="lg", interactive=True)
                            guild_status = gr.Markdown("")
                            
                            def leave_guild(guild_selection):
                                """Leave a selected Discord guild.

                                Args:
                                    guild_selection (str): The selected guild string, expected in the format "Name (ID: 123456)".

                                Returns:
                                    str: A message indicating the result of the operation:
                                        - Error messages if no selection, invalid format, or bot issues occur.
                                        - Success or failure message after attempting to leave the guild.
                                """
                                if not guild_selection:
                                    return "Please select a guild"

                                guard = _bot_guard()
                                if guard:
                                    return guard

                                try:
                                    guild_id = int(guild_selection.split("ID: ")[1].rstrip(")"))
                                except (ValueError, IndexError):
                                    return "Invalid guild selection"

                                return ("Successfully left guild" if self.discord_bot.leave_guild(guild_id) else "Failed to leave guild")
                            
                            def refresh_guild_list():
                                """Refresh the list of Discord guilds for the bot.

                                Returns:
                                    tuple[gr.update, str]: 
                                        - gr.update: Updated choices for the guild selection component.
                                        - str: A message indicating the result of the refresh, such as errors or the number of guilds found.
                                """
                                if not self.check_available():
                                    return (gr.update(choices=[]), "No discord bot instance")
                                if not self.check_connection():
                                    return (gr.update(choices=[]), "Bot offline")
                                
                                guilds = self.discord_bot.get_guilds()
                                if not guilds:
                                    return (gr.update(choices=[]), "No guilds found")
                                
                                choices = ["{} (ID: {})".format(guild['name'], guild['id']) for guild in guilds]
                                return (gr.update(choices=choices), "Found {} guilds".format(len(guilds)))

                    with gr.Row(visible=False) as custom_msg_section:
                        with gr.Column():
                            gr.Markdown("## Custom Messages")
                            channel_dropdown = gr.Dropdown(label="Select Channel", choices=[], interactive=True)
                            message_input = gr.Textbox(label="Message", placeholder="Enter message to send", lines=3)
                            send_message_btn = gr.Button("Send Message", size="lg", interactive=True)
                            refresh_channels_btn = gr.Button("Refresh Channels")
                            message_status = gr.Markdown("")
                            channel_status = gr.Markdown("")
                            
                            def refresh_channel_list():
                                """Refresh the list of Discord channels for the bot.

                                Returns:
                                    tuple[gr.update, str]: 
                                        - gr.update: Updated choices for the channel selection component.
                                        - str: A message indicating the result of the refresh, such as errors or the number of channels found.
                                """
                                if not self.check_available():
                                    return (gr.update(choices=[]), "No discord bot instance")

                                channels = []

                                for guild in self.discord_bot.client.guilds:
                                    for channel in guild.text_channels:
                                        perms = channel.permissions_for(guild.me)
                                        if perms.send_messages:
                                            channels.append(f'{guild.name} / #{channel.name} (ID: {channel.id})')

                                if not channels:
                                    return (gr.update(choices=[]), "No channels found")

                                return (gr.update(choices=channels), f'Loaded {len(channels)} channels')

                            def send_custom_message(channel_selection: str, message: str) -> str:
                                """Send a custom message to a selected Discord channel.

                                Args:
                                    channel_selection (str): The selected channel string, expected in the format "Name (ID: 123456)".
                                    message (str): The message text to send.

                                Returns:
                                    str: A message indicating the result of the operation:
                                        - Error messages if the bot is unavailable, the channel is invalid, or the message is empty.
                                        - Success or failure message after attempting to send the message.
                                """
                                guard = _bot_guard()
                                if guard:
                                    return guard

                                if not channel_selection:
                                    return "Select a channel"

                                try:
                                    channel_id = int(channel_selection.split("ID: ")[1].rstrip(")"))
                                    channel_obj = self.discord_bot.client.get_channel(channel_id)
                                    if not channel_obj:
                                        return "Channel not found"
                                    guild_id = channel_obj.guild.id
                                except (ValueError, IndexError):
                                    return "Invalid channel selection"

                                message_text = (message or "").strip()
                                if not message_text:
                                    return "Message required"

                                success = self.discord_bot.send_message(guild_id, channel_id, message_text)
                                return ("Message sent successfully" if success else "Failed to send message")
                   
                    def switch_section(section: str):
                        """Switch visibility between different UI sections in the app.

                        Args:
                            section (str): The name of the section to display. Supported values:
                                - "Guild Management"
                                - "Custom Messages"

                        Returns:
                            tuple[gr.update, gr.update]: Two Gradio update objects controlling visibility of:
                                - The Guild Management section.
                                - The Custom Messages section.
                        """
                        if section == "Guild Management":
                            return (gr.update(visible=True), gr.update(visible=False))
                        elif section == "Custom Messages":
                            return (gr.update(visible=False), gr.update(visible=True))
                        else:
                            return (gr.update(visible=False), gr.update(visible=False))
                    
                    gr.on(
                        triggers=[section_selector.change],
                        fn=switch_section,
                        inputs=section_selector,
                        outputs=[
                            guild_mgmt_section,
                            custom_msg_section
                        ]
                    )
                    
                    # Event handlers AFTER all sections are closed
                    refresh_btn.click(fn=refresh_guild_list, outputs=[guild_view, guild_status])
                    leave_btn.click(fn=leave_guild, inputs=[guild_view], outputs=[guild_status])

                    refresh_channels_btn.click(fn=refresh_channel_list, outputs=[channel_dropdown, channel_status])
                    send_message_btn.click(fn=send_custom_message, inputs=[channel_dropdown, message_input], outputs=[message_status])

                    app.load(fn=refresh_channel_list, outputs=[channel_dropdown, channel_status])

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
                                    dishes_reset_btn = gr.Button("Reset to Initial Data")
                                    dishes_reset_status = gr.Markdown("")
                                
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
                    
                            def search_dishes(query: str, cat: str) -> list[list]:
                                """Search for dishes in the database, optionally filtering by category and query text.

                                Args:
                                    query (str): A search string to filter dish names. Empty string means no filtering.
                                    cat (str): The category to filter by. Use "All" to include all categories.

                                Returns:
                                    list[list]: A list of dishes matching the search, each represented as [id, category, dish name].
                                """
                                filter_query = {} if cat == "All" else {"category": cat}
                                data = self.dbms.get_data("dishes", filter_query)
                                if query:
                                    data = [d for d in data if query.lower() in d.get("dish", "").lower()]
                                return [[d.get("id"), d.get("category"), d.get("dish")] for d in data]
                            
                            def add_dish(cat: str, name: str) -> str:
                                """Add a new dish to the database.

                                Args:
                                    cat (str): The category of the dish.
                                    name (str): The name of the dish.

                                Returns:
                                    str: A message indicating success or failure of the operation.
                                """
                                dish_name = (name or "").strip()
                                if not dish_name:
                                    return "Error: Enter a dish name"
                                if not cat:
                                    return "Error: Select a category"

                                try:
                                    next_id = _next_numeric_id("dishes")
                                    ok = self.dbms.insert_data("dishes", {"id": next_id, "category": str(cat), "dish": dish_name})
                                    return (f'Success: Added {dish_name}' if ok else "Error: Failed to insert")
                                
                                except Exception as error:
                                    return f'Error: {error}'
                            
                            def delete_dish(dish_id: int) -> str:
                                """Delete a dish from the database by its ID.

                                Args:
                                    dish_id (int): The ID of the dish to delete.

                                Returns:
                                    str: A message indicating success or failure of the deletion.
                                """
                                dish_id_int = _parse_positive_int(dish_id)
                                if dish_id_int is None:
                                    return "Error: Invalid ID"

                                try:
                                    query = _id_query(dish_id_int)
                                    if not self.dbms.get_data("dishes", query):
                                        return "Error: ID not found"
                                    return f'Success: Deleted ID {dish_id_int}' if self.dbms.delete_data("dishes", query) else "Error: Failed to delete"
                                
                                except Exception as error:
                                    return f'Error: {error}'
                            
                            def reset_dishes() -> str:
                                """Reset the dishes table to its initial data using the database loader.

                                Returns:
                                    str: A message indicating success or any errors that occurred.
                                """
                                if not self.db_loader:
                                    return "Error: DB loader not available"
                                try:
                                    self.dbms.delete_data("dishes", {})
                                    self.db_loader.import_tables(force_reload=True, specific_table="dishes")
                                    return "Dish table reset to initial data"
                                
                                except Exception as error:
                                    return f'Error: {error}'
                            
                            def test_dish(cat: str) -> str:
                                """Get a dish suggestion for a given category.

                                Args:
                                    cat (str): The category to get a dish suggestion from.

                                Returns:
                                    str: The suggested dish, or "N/A" if no controller or selector is available.
                                """
                                if self.controller:
                                    return self.controller.get_dish_suggestion(cat)
                                return (self.dish_selector.execute_function(cat) if self.dish_selector else "N/A")
                            
                            search_btn.click(fn=search_dishes, inputs=[search_query, search_cat], outputs=results)
                            add_btn.click(fn=add_dish, inputs=[new_cat, new_name], outputs=add_status)
                            del_btn.click(fn=delete_dish, inputs=del_id, outputs=del_status)
                            test_btn.click(fn=test_dish, inputs=test_cat, outputs=test_result)
                            dishes_reset_btn.click(fn=reset_dishes, outputs=dishes_reset_status)
                        
                        with gr.Tab("Fun Facts"):
                            with gr.Row():
                                with gr.Column():
                                    gr.Markdown("### Search")
                                    fact_query = gr.Textbox(label="Search", placeholder="Keywords...")
                                    fact_search_btn = gr.Button("Search")
                                    fact_results = gr.Dataframe(headers=["ID", "Fun Fact"])

                                    gr.Markdown("### Reset Fun Facts Table")
                                    funfacts_reset_btn = gr.Button("Reset to Initial Data")
                                    funfacts_reset_status = gr.Markdown("")
                                
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
                    
                            def search_facts(query: str) -> list[list]:
                                """Search for fun facts in the database, optionally filtering by a query string.

                                Args:
                                    query (str): A search string to filter fun facts. Empty string means no filtering.

                                Returns:
                                    list[list]: A list of fun facts matching the search, each represented as [id, fun_fact].
                                """
                                data = self.dbms.get_data("fun_facts", {})
                                if query:
                                    data = [f for f in data if query.lower() in f.get("fun_fact", "").lower()]
                                return [[f.get("id"), f.get("fun_fact")] for f in data]
                            
                            def add_fact(text: str) -> str:
                                """Add a new fun fact to the database.

                                Args:
                                    text (str): The text of the fun fact.

                                Returns:
                                    str: A message indicating success or failure of the insertion.
                                """
                                fact_text = (text or "").strip()
                                if not fact_text:
                                    return "Error: Enter a fun fact"
                                try:
                                    next_id = _next_numeric_id("fun_facts")
                                    ok = self.dbms.insert_data("fun_facts", {"id": next_id, "fun_fact": fact_text})
                                    return ("Success: Added" if ok else "Error: Failed")
                               
                                except Exception as error:
                                    return f'Error: {error}'
                            
                            def delete_fact(fact_id: int) -> str:
                                """Delete a fun fact from the database by its ID.

                                Args:
                                    fact_id (int): The ID of the fun fact to delete.

                                Returns:
                                    str: A message indicating success or failure of the deletion.
                                """
                                fact_id_int = _parse_positive_int(fact_id)
                                if fact_id_int is None:
                                    return "Error: Invalid ID"

                                try:
                                    query = _id_query(fact_id_int)
                                    if not self.dbms.get_data("fun_facts", query):
                                        return "Error: ID not found"
                                    return (f'Success: Deleted ID {fact_id_int}' if self.dbms.delete_data("fun_facts", query) else "Error: Failed")
                                
                                except Exception as error:
                                    return f'Error: {error}'
                            
                            def reset_fun_facts() -> str:
                                """Reset the fun facts table to its initial data using the database loader.

                                Returns:
                                    str: A message indicating success or any errors that occurred.
                                """
                                if not self.db_loader:
                                    return "Error: DB loader not available"
                                try:
                                    self.dbms.delete_data("fun_facts", {})
                                    self.db_loader.import_tables(force_reload=True, specific_table="fun_facts")
                                    return "Fun facts table reset to initial data"
                                
                                except Exception as error:
                                    return f'Error: {error}'

                            def test_fact() -> str:
                                """Get a fun fact suggestion.

                                Returns:
                                    str: A fun fact retrieved from the controller or selector, or "N/A" if unavailable.
                                """
                                if self.controller:
                                    return self.controller.get_fun_fact()
                                return (self.fun_fact_selector.execute_function() if self.fun_fact_selector else "N/A")
                            
                            fact_search_btn.click(fn=search_facts, inputs=fact_query, outputs=fact_results)
                            fact_add_btn.click(fn=add_fact, inputs=new_fact, outputs=fact_add_status)
                            fact_del_btn.click(fn=delete_fact, inputs=fact_del_id, outputs=fact_del_status)
                            funfacts_reset_btn.click(fn=reset_fun_facts, outputs=funfacts_reset_status)
                            fact_test_btn.click(fn=test_fact, outputs=fact_test_result)
                        
                        with gr.Tab("Translator"):
                            gr.Markdown("### Translate Text")
                            
                            with gr.Row():
                                trans_input = gr.Textbox(label="Input", lines=5, placeholder="Enter text...")
                                trans_output = gr.Textbox(label="Output", lines=5, interactive=False)
                            
                            trans_btn = gr.Button("Translate", size="lg")
                            
                            def translate(text: str) -> str:
                                """Translate a given text using the controller or translator component.

                                Args:
                                    text (str): The text to translate.

                                Returns:
                                    str: The translated text, or an error message if text is empty or no translation component is available.
                                """
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
                            refresh_stats_status = gr.Markdown("")
                            
                            with gr.Row():
                                dishes_stat = gr.Markdown("### Loading...")
                                facts_stat = gr.Markdown("### Loading...")
                                categories_stat = gr.Markdown("### Loading...")
                            
                            stats_json = gr.JSON(label="Detailed Statistics")
                            
                            def load_stats_initial() -> tuple[str, str, str, dict, str]:
                                """Load initial statistics for dishes and fun facts.

                                Returns:
                                    tuple[str, str, str, dict, str]: A tuple containing:
                                        - HTML string for total dishes.
                                        - HTML string for number of dish categories.
                                        - HTML string for total fun facts.
                                        - A dictionary with detailed statistics.
                                        - An additional info message (empty string initially).
                                """
                                categories = dish_categories

                                stats = {"dishes": {}, "total_dishes": 0, "total_fun_facts": 0}

                                for cat in categories:
                                    count = self.dbms.get_table_size("dishes", cat)
                                    if count > 0:
                                        stats["dishes"][cat] = count
                                        stats["total_dishes"] += count

                                stats["total_fun_facts"] = self.dbms.get_table_size("fun_facts", None)

                                dishes_md = '<div class="stat-card"><div class="stat-label">Total Dishes</div><div class="stat-number">{}</div></div>'.format(stats["total_dishes"])
                                cats_md = '<div class="stat-card"><div class="stat-label">Dish Categories</div><div class="stat-number">{}</div></div>'.format(len(stats["dishes"]))
                                facts_md = '<div class="stat-card"><div class="stat-label">Fun Facts</div><div class="stat-number">{}</div></div>'.format(stats["total_fun_facts"])
                                
                                return (dishes_md, cats_md, facts_md, stats, "")
                        
                            def load_stats() -> tuple[str, str, str, dict, str]:
                                """Refresh and load the current statistics for dishes and fun facts.

                                Returns:
                                    tuple[str, str, str, dict, str]: A tuple containing:
                                        - HTML string for total dishes.
                                        - HTML string for number of dish categories.
                                        - HTML string for total fun facts.
                                        - A dictionary with detailed statistics.
                                        - A message indicating success or error of the refresh.
                                """
                                try:
                                    categories = dish_categories

                                    stats = {"dishes": {}, "total_dishes": 0, "total_fun_facts": 0}

                                    for cat in categories:
                                        count = self.dbms.get_table_size("dishes", cat)
                                        if count > 0:
                                            stats["dishes"][cat] = count
                                            stats["total_dishes"] += count

                                    stats["total_fun_facts"] = self.dbms.get_table_size("fun_facts", None)

                                    dishes_md = '<div class="stat-card"><div class="stat-label">Total Dishes</div><div class="stat-number">{}</div></div>'.format(stats["total_dishes"])
                                    cats_md = '<div class="stat-card"><div class="stat-label">Dish Categories</div><div class="stat-number">{}</div></div>'.format(len(stats["dishes"]))
                                    facts_md = '<div class="stat-card"><div class="stat-label">Fun Facts</div><div class="stat-number">{}</div></div>'.format(stats["total_fun_facts"])
                                    
                                    return (dishes_md, cats_md, facts_md, stats, "Refresh successful")
                                
                                except Exception:
                                    return ("Error", "Error", "Error", {}, "Error while refreshing")
                            
                            refresh_stats_btn.click(fn=load_stats, outputs=[dishes_stat, facts_stat, categories_stat, stats_json, refresh_stats_status])
                            app.load(fn=load_stats_initial, outputs=[dishes_stat, facts_stat, categories_stat, stats_json, refresh_stats_status])
            
            gr.HTML("""
                <div style="text-align: center; padding: 20px; color: #99AAB5; margin-top: 20px;">
                    <p>Discord Bot Admin Panel v1.2</p>
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
