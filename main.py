import sqlite3

from src.config import startup_func, library_menu

if __name__ == '__main__':

    """
    Main Python module, Startup func points to the setup and menu functionalities
    """

    try:
        startup_func()
    except TypeError:
        library_menu()
    except sqlite3.OperationalError as e:
        print("Error due to : ", str(e))
    except InterruptedError:
        print("Interrupted the system, Thank you for using Library System, Please use again!!")
    except Exception as e:
        print("Exception due to :", str(e))
