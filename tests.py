import os.path
import sqlite3
import unittest
from unittest.mock import MagicMock, Mock


class DBTests(unittest.TestCase):
    """
    Unit Testing For DB connection with Mocks
    """

    def test_sqlite3_connect(self):
        sqlite3.connect = MagicMock(return_value="Connected Successfully")

        dbc = DataBaseClass()
        sqlite3.connect.assert_called_with('library.db')
        self.assertEqual(dbc.connection, 'Connected Successfully')

    def test_sqlite3_connect_fail(self):
        sqlite3.connect = MagicMock(return_value="Connection Failed")

        dbc = DataBaseClass()
        sqlite3.connect.assert_called_with('library.db')
        self.assertEqual(dbc.connection, "Connection Failed")

    def test_sqlite3_connect_with_side_effect(self):
        self._setup_mock_sqlite3_connect()

        dbc = DataBaseClass('good_connection_string')
        self.assertTrue(dbc.connection)
        sqlite3.connect.assert_called_with('good_connection_string')

        dbc = DataBaseClass('bad_connection_string')
        self.assertFalse(dbc.connection)
        sqlite3.connect.assert_called_with('bad_connection_string')

    def _setup_mock_sqlite3_connect(self):
        values = {'good_connection_string': True,
                  'bad_connection_string': False}

        def side_effect(arg):
            return values[arg]

        sqlite3.connect = Mock(side_effect=side_effect)


class DataBaseClass:

    def __init__(self, db_name: str = 'library.db'):
        self.connection = sqlite3.connect(db_name)


class UserTestCase(unittest.TestCase):
    """
    Unit Testing with test DB and no mocks
    """

    def setUp(self) -> None:
        self.db = sqlite3.connect("test.db")
        self.cursor = self.db.cursor()

        # setup user
        self.cursor.execute("""
                create table if not exists users(
                id integer primary key not null,
                username varchar(50) not null,
                secret_key varchar(50) null,
                unique(username)
                )""")
        self.db.commit()

    def test_get_user(self):
        get_test_user = self.db.execute("""select username from users where id=1""").fetchone()
        self.assertIsNone(get_test_user)

    def test_add_user(self):
        self.db.execute("""insert into users (id, username, secret_key) values(?,?,?)""", (1, "test_user1", None))
        self.db.commit()
        get_test_user = self.db.execute("""select username from users where id=1""").fetchone()
        self.assertEqual(get_test_user, ("test_user1",))

    def test_list_users(self):
        user2 = (2, "test_user2", None)
        user3 = (3, "test_user3", None)
        user4 = (4, "test_user4", None)
        self.db.executemany("""insert into users (id, username, secret_key) values(?,?,?)""", [user2, user3, user4])
        self.db.commit()
        lists_users = self.db.execute("""select * from users""").fetchall()
        self.assertEqual(lists_users, [(2, "test_user2", None), (3, "test_user3", None), (4, "test_user4", None)])

    def test_delete_user(self):
        self.db.execute("""delete from users where id=1""")
        self.db.commit()
        self.assertIsNone(self.db.execute("""select * from users where id=1""").fetchone())
        self.db.execute("""delete from users""")
        self.db.commit()
        self.assertEqual(self.db.execute("""select * from users""").fetchmany(10), [])


def runner(test_name):
    unittest.TextTestRunner().run(test_name)


def tearDown():
    if os.path.exists("test.db"):
        os.remove("test.db")


if __name__ == '__main__':
    db_tests = unittest.defaultTestLoader.loadTestsFromTestCase(DBTests)
    user_test = unittest.defaultTestLoader.loadTestsFromTestCase(DBTests)
    runner(db_tests)
    runner(user_test)
    tearDown()
