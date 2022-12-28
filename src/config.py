import sqlite3
import sys
import time

from .books import Book, BookMaster
from .users import User
from .utils import welcome_message, setup_db


def check_admin_setup(db):

    """
    Check if the admin has been set up
    """

    try:
        res = db.execute("""select * from users where id=1""").fetchone()
        if res[2] is not None:
            return True
        return False
    except sqlite3.OperationalError:
        return False


def startup_func():

    """
    Startup function to set up all initial configs, is a one time thing
    """

    print(welcome_message)

    db = setup_db("library.db")
    if check_admin_setup(db):
        print("\nAdmin User Found, Redirecting ...")
        main()
    db.execute("PRAGMA foreign_keys = ON")
    print(f"\nDatabase : library.db set up successfully")

    print(f"\nAdmin user not configured.....")

    print("\nPlease follow the following setup procedure (THIS IS ONE TIME ONLY) ")

    print("\nPlease provide the admin details")
    username = input("\nEnter your username: ")
    secret_key = input("Enter your secret key:(DO NOT FORGET) ")

    # setup user table
    user = User()
    user.setup_user()
    # setup book table
    book = Book()
    book.setup_book()

    # setup borrow table
    book_master = BookMaster()
    book_master.setup_book_master()

    db.cursor().execute("""insert into users(username, secret_key) values (?, ?)""", (username, secret_key))
    db.commit()

    print("\nThank you for the admin setup, you can now browse the system")

    main()


def main():

    """
    Main function that acts as a communicator between startup and menu function
    """

    db = setup_db("library.db")
    print("\nPlease enter your admin credentials below : ")
    username = input("Username : ")
    secret_key = input("Secret Key : ")

    res = db.cursor().execute(
        """select * from users where username=? and secret_key=?""", (username, secret_key)).fetchone()

    if res is None:
        print("Admin credentials didn't match")
        print("What do you want to do ?")
        choice = int(input(
            """
            (1). Try again
            (2). Exit
            """
        ))
        if choice == 1:
            main()
        elif choice == 2:
            print("Thank you for trying Library System")
            sys.exit()
        else:
            print("Invalid choice, Please try again")
            main()
    else:
        print("\n Admin Config Matched successfully ")
        library_menu()


def library_menu():

    """
    Library Persistent Menu for our system
    """

    # time sleep scheduler for deploying the usual response
    # so that menu doesn't override the console screen instantly
    time.sleep(1)

    print(
        """
    Program Options :

    (1). Add book
    (2). Print library books
    (3). Print books by prefix
    (4). Add user
    (5). Borrow book
    (6). Return book
    (7). Print users borrowed book
    (8). Print users
    (q). Quit

    """)

    book = Book()
    book_master = BookMaster()
    user = User()

    choice = input("Enter your choice (from 1 to 8 ) : ")

    if choice == "1":

        """
        Add a book to the library
        """

        book.add_book()
        print("Book added successfully")
        library_menu()

    elif choice == "2":

        """
        Print all library books
        """

        book_list = book.list_books()
        print("\nHere are the list of all library books")
        for book in book_list:
            print(f"""
            id: {book[0]}, Name: {book[1]}, qty: {book[2]}
            """)
        library_menu()

    elif choice == "3":

        """
        Search a book by a prefix letter or name
        @example: Li -> Life of Pi 
        """

        books = book.search_book_by_name()
        for book in books:
            print(f"""
                  id: {book[0]}, Name: {book[1]}, qty: {book[2]}
                  """)
        library_menu()

    elif choice == "4":

        """
        Add a user into the system
        """

        user.add_user()
        print("User added successfully")
        library_menu()

    elif choice == "5":

        """
        Borrow a book from the system
        """

        book_master.borrow_book()
        library_menu()

    elif choice == "6":

        """
        Return a book to the inventory
        """

        book_master.return_book()
        library_menu()

    elif choice == "7":

        """
        Prints all the users that have borrowed a specific book
        """

        user_list = book_master.list_users_by_book_name()
        if user_list is None:
            print("There are no users who have borrowed this book at the present")
            library_menu()
        else:
            print("Here are the users who borrowed this book: ")
            for user in user_list:
                print(f"""{user}""")
            library_menu()

    elif choice == "8":

        """
        Prints all the users of the system, excluding admin
        """

        user_list = user.list_users()
        print(user_list)
        if user_list:
            print("\n Here is the list of users: ")
            for user in user_list[1:]:
                print(f"""
                      id: {user[0]}, Name: {user[1]}
                      """)
            library_menu()

        else:
            print("\n No users have borrowed this book")
            library_menu()

    elif choice == "q":

        """
        Quit the system
        """

        print("\nThank you for using me, See you again")
        sys.exit()

    else:

        """
        Not a valid choice, redirects to the menu
        """

        print("\nInvalid Choice, Please try again! ")
        library_menu()
