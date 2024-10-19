from utils import print_waring , print_update
from datetime import date
from pathlib import Path
from db import handleDb
import re

db_handler = handleDb()

def display_menu():
    print("1: Add expense")
    print("2: View expenses")
    print("3: Track budget")
    print("4: Save expenses")
    print("5: Load Budget from csv")
    print("6: Exit")
    user_input = input("Enter the option of your choice:")
    return user_input

class ValidateExpense:

    def __init__(self,category,amount,description):
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
        # expense can be added for today's date only
        # date_ = self.user_date if self.is_validate_date(self.user_date) and self.match_dates(today,self.user_date) else today
        return self.category,self.amount,self.description


if __name__ == "__main__":
    print("----EXPENSE TRACKER---")
    while True:
        user_input = display_menu()
        if user_input=="1":
            print(f"Enter expense for---{str(date.today())}")
            # user_date = input("Enter to proceed or provide a date of your choice in format YYYY-MM-DD:")
            get_exist_categories = db_handler.handle_category()
            get_exist_categories = [x for x in get_exist_categories if x!="-"]
            category = input(f"Select the category or add new category :{get_exist_categories}") or "-"
            db_handler.handle_category(category)
            amount = input("Enter the amount:") or "-"
            description = input("Enter the description:") or "-"
            category,amount,description  = ValidateExpense(category,amount,description).is_valid()
            db_handler.add_entry(category,amount,description)
        elif user_input == "2":
            db_handler.display_db()
        elif user_input == "3":
            is_true = db_handler.check_budget()
            if is_true:
                user_input = input(f"DO YOU WANT TO OVERRIDE THE BUDGET [y/n]")
                if user_input == "y":
                    user_budget = int(input("PLEASE ENTER THE MONTHLY BUDGET:"))
                    if user_budget  and isinstance(user_budget,int):
                        db_handler.update_budget(user_budget)
                    else:
                        print_waring("INCORRECT FORMAT FOR BUDGET, PLEASE TRY AGAIN !!")
                elif user_input == "n":
                    print_update("RETURNING TO MAIN MENU !!")
                    user_input = display_menu()
            if not is_true:
                user_budget = int(input("PLEASE ENTER THE MONTHLY BUDGET:"))
                if user_budget and isinstance(user_budget,int):
                    db_handler.update_budget(user_budget)
                else:
                    print_waring("INCORRECT FORMAT FOR BUDGET, PLEASE TRY AGAIN !!")


        elif user_input == "4":
            db_handler.save_db()
        elif user_input == "5":
            print_waring("MAKE SURE THE FILE CONTAINS FOLLOWING HEADERS-[ID Date Category  Amount Description]")
            file_path = input("please provide file path:")
            path = Path(file_path)
            if path.is_file():
                db_handler.build_db_from_csv(file_path)
        elif user_input == "6":
            break
