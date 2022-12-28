from .utils import setup_db


class User:

    """
    Users class
    """

    def __init__(self):
        self.db = setup_db("library.db")
        self.cursor = self.db.cursor()

    def setup_user(self):
        user_ddl = """
        create table if not exists users(
        id integer primary key not null,
        username varchar(50) not null,
        secret_key varchar(50) null,
        unique(username)
        )"""

        self.cursor.execute(user_ddl)
        self.db.commit()

    def get_user(self):
        user_id = int(input("Enter the user id: "))
        return self.cursor.execute(f"""select * from users where id = {user_id}""").fetchone()

    def add_user(self):
        username = str(input("Enter your username: "))
        self.cursor.execute("""insert into users (username, secret_key) values(?,?)""", (username, None))
        self.db.commit()

    def list_users(self):
        return self.cursor.execute("""select * from users""").fetchall()

    def delete_user(self):
        user_id = int(input("Enter the user id : "))
        self.cursor.execute(f"""delete from users where id={user_id}""")
