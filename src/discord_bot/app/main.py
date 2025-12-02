from discord_bot.business_logic.fun_fact_selector import FunFactSelector
from discord_bot.business_logic.dish_selector import DishSelector
from discord_bot.adapters.db import DBMS
from discord_bot.business_logic.translator import Translator

if __name__ == "__main__":
    db = DBMS()
    db.connect()

    # TESTING FUN FACT SELECTOR
    fun_fact_selector = FunFactSelector(dbms=db)
    print("FUN FACT TEST")
    print(fun_fact_selector.execute_function())

    # TESTING DISH SELECTOR
    dish_selector = DishSelector(dbms=db)
    print("DISH SUGGESTION TEST")
    print(dish_selector.execute_function(category="Italian"))

    # TESTING TRANSLATOR
    translator = Translator()
    sample_text = "Hallo, wie geht's?"
    translated_text = translator.execute_function(sample_text)
    print("TRANSLATION TEST")
    print(f"Original: {sample_text}")
    print(f"Translated: {translated_text}")
