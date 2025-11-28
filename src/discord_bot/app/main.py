from discord_bot.business_logic.fun_fact_selector import FunFactSelector
from discord_bot.adapters.db import DBMS

if __name__ == "__main__":
    fun_fact_selector = FunFactSelector(dbms=DBMS())
    print(fun_fact_selector.execute_function())