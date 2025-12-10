from discord_bot.contracts.ports import ControllerPort, DishPort, FunFactPort, TranslatePort

class Controller(ControllerPort):
    def __init__(self, dish_selector: DishPort, fun_fact_selector: FunFactPort, translator: TranslatePort):
        self.dish_selector = dish_selector
        self.fun_fact_selector = fun_fact_selector
        self.translator = translator

    def get_fun_fact(self) -> str:
        return self.fun_fact_selector.execute_function()

    def get_dish_suggestion(self, category: str) -> str:
        return self.dish_selector.execute_function(category)

    def translate_text(self, text: str) -> str:
        return self.translator.execute_function(text)

    def auto_translate_text(self, text: str, user_id: int) -> str:
        return self.translator.execute_function(text, user_id)
