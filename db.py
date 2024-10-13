import  sqlite3
from contextlib import contextmanager

db_name = "expense.db"
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

    @contextmanager
    def session_scope(self,commit=True):
        self.connection = sqlite3.connect(db_name)
        try:
            yield self.connection.cursor()
            if commit:
                self.connection.commit()
                print(f"Data committed to db")
        except Exception as e:
            print(f"Exception occured in db connection, rolling back -- {e}")
            self.connection.rollback()
            raise
        finally:
            self.connection.close()


    def add_entry(self,user_date,category,amount,description):
        with self.session_scope() as session:
            session.execute("""
            INSERT INTO expense (date , category , amount , description)
            VALUES (?,?,?,?)
            """,(user_date,category,amount,description))

    def display_db(self):
        with self.session_scope() as session:
            session.execute('SELECT * FROM expense')
            rows = session.fetchall()
            for row in rows:
                print(row)

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




