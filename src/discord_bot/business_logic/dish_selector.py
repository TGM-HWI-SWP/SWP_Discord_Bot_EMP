from discord_bot.contracts.ports import DatabasePort, DishPort
from discord_bot.business_logic.model import Model

class DishSelector(Model, DishPort):
    def __init__(self, dbms: DatabasePort, **kwargs):
        super().__init__(**kwargs)
        self.dbms = dbms

    def execute_function(self, category: str) -> str:
        dish = self.dbms.get_random_entry("dishes", category)
        if not dish:
            self.logging("No dish found.")
            return ""
        result = dish.get("dish") or str(dish)
        self.logging(f'Dish selected: {result}')
        return result

if __name__ == "__main__":
    from discord_bot.adapters.db import DBMS
    db = DBMS()
    db.connect()
    dish_selector = DishSelector(dbms=db)
    print(dish_selector.execute_function("Italian"))
    