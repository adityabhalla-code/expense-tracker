from operator import index
from unicodedata import category

from utils import print_waring , print_update
from contextlib import contextmanager
from datetime import date
import pandas as pd
import  sqlite3
import os

db_name = "expense.db"
today = str(date.today())
month = today.split("-")[1]


class handleDb:

    def __init__(self):
        with self.session_scope() as session:
                session.execute(
                    """
                    CREATE TABLE IF NOT EXISTS expense(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE,
                    category TEXT NOT NULL,
                    amount INTEGER,
                    description TEXT)
                    """
                )
                session.execute(
                    """
                    CREATE TABLE IF NOT EXISTS categories(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL)
                    """
                )
                session.execute(
                    """
                    CREATE TABLE IF NOT EXISTS tracker(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE,
                    budget INTEGER)
                    """
                )


    @contextmanager
    def session_scope(self,commit=True):
        self.connection = sqlite3.connect(db_name)
        try:
            yield self.connection.cursor()
            if commit:
                self.connection.commit()
                # print(f"Data committed to db")
        except Exception as e:
            print(f"Exception occured in db connection, rolling back -- {e}")
            self.connection.rollback()
            raise
        finally:
            self.connection.close()


    def add_entry(self,category,amount,description):
        with self.session_scope() as session:
            session.execute("""
            INSERT INTO expense (date , category , amount , description)
            VALUES (?,?,?,?)
            """,(today,category,amount,description))

    def display_db(self):
        with self.session_scope(False) as session:
            session.execute('SELECT * FROM expense')
            rows = session.fetchall()
            df = pd.DataFrame(rows, columns=['ID', 'Date', 'Category', 'Amount', 'Description'])
            if df.empty:
                print_waring("---NO DATA !! PLEASE ADD AN EXPENSE")
            else:
                print("="*100)
                print(df)
                print("="*100)

    def save_db(self):
        with self.session_scope() as session:
            rows = session.execute('SELECT * FROM expense').fetchall()
            df = pd.DataFrame(rows, columns=['ID', 'Date', 'Category', 'Amount', 'Description'])
            if not df.empty:
                file_name = os.path.join(os.getcwd(),f'expense_report_{today}.csv')
                df.to_csv(file_name,index=False)
                print_update(f"DATA WRITTEN TO DIRECTORY---{os.getcwd()}")
                print_update(f"FILE NAME--{file_name}")

            else:
                print_waring(f"PLEASE ADD AN EXPENSE TO SAVE DATA !!")


    def handle_category(self,category=None):

        with self.session_scope() as session:
            db_categories = session.execute('SELECT * FROM categories').fetchall()
            db_categories = [x[1] for x in db_categories]

            if category is not None and category not in db_categories:
                session.execute(
                    """
                    INSERT INTO categories(category)
                    VALUES (?)
                    """,(category,)
                )
                return
            return db_categories

    def check_budget(self):
        with self.session_scope(False) as session:
            existing_budget = session.execute(f"""
                SELECT budget 
                FROM tracker 
                WHERE strftime('%Y-%m', '{today}') = strftime('%Y-%m', date)
                """).fetchone()
            if existing_budget:
                print_update(f"FOR THE MONTH--{month}\nEXISTING BUDGET FOUND ----{existing_budget[0]}")
                total_expense = session.execute('SELECT SUM(Amount) FROM expense').fetchone()[0]
                if total_expense:
                    print_update(f"TOTAL EXPENSES INCURRED---{total_expense}")
                    return True
                else:
                    print(f"NO EXPENSES ADDED!!")
                    return True
            else:
                print_waring(f"NO EXISTING BUDGET FOUND FOR THE MONTH---{month}")
                return  False


    def update_budget(self,user_budget):
        # total_rows = session.execute('SELECT COUNT(Amount) FROM expense').fetchall()
        # print(f"Total rows in db--{type(total_rows[0])}")
        # print(f"Total rows in db--{total_rows[0][0]}")
        # total_expense = session.execute('SELECT SUM(Amount) FROM expense').fetchone()[0]
        # print(f"Total amount so far--{type(total_expense[0])}")
        # print(f"Total expenses so far--{total_expense}")
        if self.check_budget():
            with self.session_scope() as session:
                print_update(f"UPDATTING BUDGET FOR THE MONTH--{month}---{user_budget}")
                session.execute(
                    """
                    UPDATE tracker 
                    SET budget = ?
                    WHERE date = ?
                    """, (user_budget, today)
                )
                print_update(f"BUDGET ADDED ! ")
                return
        else:
            with self.session_scope() as session:
                print_update(f"UPDATTING BUDGET FOR THE MONTH--{month}")
                session.execute(
                    """
                    INSERT INTO tracker ( date,budget)
                    VALUES (?,?)
                    """,(today,user_budget,)
                )
                print_update(f"BUDGET ADDED ! ")

    def build_db_from_csv(self,file_path):
        df = pd.read_csv(file_path)
        print_update("DATA RECEIVED TO BE ADDED TO DB")
        print(df)
        for index, row in df.iterrows():
            category = row['Category']
            self.handle_category(category)
            try:
                with self.session_scope() as session:
                    session.execute('''
                    INSERT INTO expense (ID, Date, Category, Amount, Description)
                    VALUES (?, ?, ?, ?, ?)
                    ''', (row['ID'], row['Date'], row['Category'], row['Amount'], row['Description']))
            except sqlite3.IntegrityError:
                print(f"Duplicate entry for {row['Date']}, {row['Category']}, {row['Amount']} not inserted.")
            except KeyError:
                print_waring(f"Kindly please check the file, the columns should be [ID Date Category  Amount Description]")


