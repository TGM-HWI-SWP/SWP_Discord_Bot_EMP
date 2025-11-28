from discord_bot.contracts.ports import DatabasePort, FunFactPort

class FunFactSelector(FunFactPort):
    def __init__(self, dbms: DatabasePort):
        self.dbms = dbms

    def execute_function(self) -> str:
        fun_fact = self.dbms.get_random_entry(table="fun_facts")
        return fun_fact #dict
    
if __name__ == "__main__":
    from discord_bot.adapters.db import DBMS
    
    fun_fact_selector = FunFactSelector(dbms=DBMS())
    print(fun_fact_selector.execute_function())