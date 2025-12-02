from discord_bot.business_logic.fun_fact_selector import FunFactSelector
from discord_bot.business_logic.dish_selector import DishSelector
from discord_bot.adapters.db import DBMS

if __name__ == "__main__":
    db = DBMS()
    db.connect()

    # TESTING FUN FACT SELECTOR
    fun_fact_selector = FunFactSelector(dbms=db)
    print(fun_fact_selector.execute_function())

    # TESTING DISH SELECTOR
    dish_selector = DishSelector(dbms=db)
    print(dish_selector.execute_function(category="Italian"))

    # TESTING TRANSLATOR
    
