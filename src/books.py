import sys

from .utils import setup_db


class Book:

    """
    Books class
    """

    def __init__(self):
        self.db = setup_db("library.db")
        self.cursor = self.db.cursor()

    def setup_book(self):
        book_ddl = """
        create table if not exists books(
        id integer primary key not null,
        name varchar(255) not null,
        qty integer not null default 1,
        unique(name)
        )"""

        self.cursor.execute(book_ddl)
        self.db.commit()

    def get_book(self):
        book_id = int(input("Enter the book id: "))
        self.cursor.execute(f"""select * from books where id = {book_id}""")

        return self.cursor.fetchone()

    def add_book(self):
        name = str(input("Enter the book name: "))
        qty = str(input("Enter the book qty: "))
        self.cursor.execute("""insert into books (name, qty) values(?,?)""", (name, qty))
        self.db.commit()

    def list_books(self):
        self.cursor.execute("""select * from books""")
        return self.cursor.fetchall()

    def delete_book(self):
        book_id = int(input("Enter the book id : "))
        self.cursor.execute(f"""delete from users where id={book_id}""")
        self.db.commit()

    def search_book_by_name(self):
        keyword = input("Enter the book name or prefix: ")
        return self.cursor.execute("""select * from books where name like ?""", (keyword + '%',)).fetchall()

    def get_book_by_name(self):
        book_name = input("Enter the book name : ")
        return self.cursor.execute("""select * from books where lower(name)=?""", (book_name.lower(),)).fetchone()


class BookMaster:

    """
    BookMaster class, handles both borrow and return operation
    """

    def __init__(self):
        self.db = setup_db("library.db")
        self.cursor = self.db.cursor()

    def setup_book_master(self):
        book_master_ddl = """
        create table if not exists book_master(
        id integer primary key not null,
        book_id integer,
        user_id integer,
        is_returned boolean default false,
        foreign key (book_id) references books(id),
        foreign key (user_id) references users(id)
        )"""

        self.cursor.execute(book_master_ddl)
        self.db.commit()

    def get_borrow_detail_by_id(self):
        borrow_id = int(input("Enter the borrow id: "))
        return self.cursor.execute("""select * from book_master where id = ?""", (borrow_id,)).fetchone()

    def borrow_book(self):
        name = str(input("Enter the book name: "))
        res = self.cursor.execute("""select * from books where lower(name)=?""", (name.lower(),)).fetchone()
        if res is None:
            print(f"\nBook with this name : {name} not found")
            print("What do you want to do ?")
            choice = int(input(
                """
                (1). Try again
                (2). Exit
                """
            ))
            if choice == 1:
                self.borrow_book()
            elif choice == 2:
                print("Thank you for trying Library System")
                sys.exit()
            else:
                print("Invalid choice, Please try again")
        else:
            print(f"you requested to borrow this book : {res[1]}")
            confirm = str(input("Is this book choice correct ? (yes/no) :"))
            if confirm.lower() == "yes":
                username = str(input("Enter the username who wants to borrow this book : "))
                user_obj = self.cursor.execute("""select * from users where lower(username)=?""",
                                               (username.lower(),)).fetchone()
                if user_obj is None:
                    print(f"User with this username : {username} not found")
                    self.borrow_book()
                self.cursor.execute("""insert into book_master (book_id, user_id) values(?,?)""", (res[0], user_obj[0]))
                self.cursor.execute("""update books set qty=qty-1 where id=?""", (res[0],))
                self.db.commit()
                print("Book borrowed successfully")
            else:
                self.borrow_book()

    def list_borrowed_books(self):
        return self.cursor.execute("""select * from book_master where is_returned = false""").fetchall()

    # lists all who borrowed this book by book name
    def list_users_by_book_name(self):
        book_name = input("Enter the book name : ")
        book_obj = self.cursor.execute("""select * from books where lower(name)=?""", (book_name.lower(),)).fetchone()

        if book_obj is None:
            print(f"Book with this name : {book_name} not found")
            print("What do you want to do ?")
            choice = int(input(
                """
                (1). Try again
                (2). Exit
                """
            ))
            if choice == 1:
                self.list_users_by_book_name()
            elif choice == 2:
                print("Thank you for trying Library System")
                sys.exit()
            else:
                print("Invalid choice, Please try again")

        else:
            user_list = self.cursor.execute("""select user_id from
             book_master where book_id=? and is_returned=false""", (book_obj[0],)).fetchall()
            users = []
            if user_list:
                for user in user_list:
                    res = self.cursor.execute("select username from users where id=?", (user[0],)).fetchone()
                    users.append(res[0])
                return users
            else:
                return []

    def return_book(self):
        book = Book()
        book_obj = book.get_book_by_name()
        if book_obj is None:
            print(f"Book with this name not found")
            print("What do you want to do ?")
            choice = int(input(
                """
                (1). Try again
                (2). Exit
                """
            ))
            if choice == 1:
                self.return_book()
            elif choice == 2:
                print("Thank you for trying Library System")
                sys.exit()
            else:
                print("Invalid choice, Please try again")
        else:
            print(f"you requested to borrow this book : {book_obj[1]}")
            confirm = str(input("Is this book choice correct ? (yes/no) :"))
            if confirm.lower() == "yes":
                username = str(input("Enter the username who wants to return this book : "))
                user_obj = self.cursor.execute("""select * from users where lower(username)=?""",
                                               (username.lower(),)).fetchone()
                if user_obj is None:
                    print(f"User with this username : {username} not found")
                    self.return_book()
                else:
                    book_master_obj = self.cursor.execute("""select * from book_master where user_id=? 
                                                            and book_id=? and is_returned=False""",
                                                          (user_obj[0], book_obj[0])).fetchone()
                    if book_master_obj is None:
                        print(f"This user has not borrowed any books at the present")
                        self.return_book()
                    else:
                        self.cursor.execute("""update book_master set is_returned = True where id=?""",
                                            (book_master_obj[0],))
                        self.cursor.execute("""update books set qty=qty+1 where id=?""", (book_obj[0],))
                        self.db.commit()
                        print("Book returned successfully")
            else:
                self.return_book()
