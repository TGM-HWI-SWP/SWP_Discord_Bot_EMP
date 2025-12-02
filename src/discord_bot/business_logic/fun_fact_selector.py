from discord_bot.contracts.ports import DatabasePort, FunFactPort
from discord_bot.business_logic.model import Model

class FunFactSelector(Model, FunFactPort):
    def __init__(self, dbms: DatabasePort, **kwargs):
        super().__init__(**kwargs)
        self.dbms = dbms

    def execute_function(self) -> str:
        fun_fact = self.dbms.get_random_entry(table="fun_facts", category=None)
        if not fun_fact:
            return "No fun fact found."
        return fun_fact.get("fun_fact") or str(fun_fact)

if __name__ == "__main__":
    from discord_bot.adapters.db import DBMS
    db = DBMS()
    db.connect()
    fun_fact_selector = FunFactSelector(dbms=db)
    print(fun_fact_selector.execute_function())
    