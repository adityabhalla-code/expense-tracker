from datetime import date
from db import handleDb
import re

db_handler = handleDb()


class ValidateExpense:

    def __init__(self,user_date,category,amount,description):
        self.user_date = user_date
        self.category = category
        self.amount = amount
        self.description = description

    def is_validate_date(self,date_str):
        "YYYY-MM-DD"
        pattern = r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[0-1])$"
        return bool(re.match(pattern,date_str))

    def match_dates(self,date_1,date_2):
        if self.is_validate_date(date_1) and self.is_validate_date(date_2):
            return date_1==date_2

    def is_valid(self):
        today = str(date.today())
        date_ = self.user_date if self.is_validate_date(self.user_date) and self.match_dates(today,self.user_date) else today
        return date_,self.category,self.amount,self.description


if __name__ == "__main__":
    print("----Expenses---")
    user_date = input("Enter date in format YYYY-MM-DD:")
    get_exist_categories = db_handler.handle_category()
    get_exist_categories = [x for x in get_exist_categories if x!="-"]
    category = input(f"Enter the category from :{get_exist_categories}") or "-"
    db_handler.handle_category(category)
    amount = input("Enter the amount:") or "-"
    description = input("Enter the description:") or "-"
    user_date,category,amount,description  = ValidateExpense(user_date,category,amount,description).is_valid()
    db_handler.add_entry(user_date,category,amount,description)
    db_handler.display_db()
