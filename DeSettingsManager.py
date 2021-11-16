import sqlite3
import os


class DeSettingsManager:

    def __init__(self, db_path: str = None) -> None:
        self.db_path = os.path.expanduser(
            '~') + '/Documents/DeTuner/detuner.db' \
            if not db_path else db_path

        # Import existing or create new settings.db
        if not self.__check_db():
            self.__create_db()
        self.__import_db()

    def __import_db(self):
        pass

    def __check_db(self):
        ''' Check if settings db already exists '''
        if os.path.exists(self.db_path):
            try:
                sqlite3.connect(self.db_path)
            except:
                print('check failled')
                return False
            else:
                return True
        else:
            return False

    def __create_db(self):
        ''' Create settings db if doesn't exist '''
        try:
            # Create directory structure
            split_path = self.db_path.split('/')
            dir_path = '/'.join(split_path[:len(split_path) - 1])
            os.makedirs(dir_path)

            # Create DB
            conn = sqlite3.connect(self.db_path)
        except Exception as e:
            print(e)
            raise Exception(f'Unable to create db: {e}')
        else:
            query = '''CREATE TABLE external_backups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    backup_id text NOT NULL,
                      path text NOT NULL
                    );'''
            conn.execute(query)

            query = '''CREATE TABLE settings (
                    name TEXT UNIQUE PRIMARY KEY,
                    value TEXT
                    )'''
            conn.execute(query)

            query = '''INSERT INTO settings (name, value)
                    VALUES ('last_export_path', '.');'''
            conn.execute(query)
            conn.commit()

            conn.close()

    def get_setting_value(self, name) -> str | bool:
        ''' Return setting value for provied name '''

        try:
            conn = sqlite3.connect(self.db_path)
        except Exception as e:
            raise Exception(f'Unable to connect to db: {e}')
        else:
            # Check if setting name is valid
            c = conn.cursor()
            query = '''SELECT count(name) FROM settings WHERE name = ?'''
            result = c.execute(query, [name]).fetchone()[0]
            if result != 1:
                return False
            # Get value
            c = conn.cursor()
            query = '''SELECT value FROM settings WHERE name = ?'''
            value = c.execute(query, [name]).fetchone()[0]
            return value

    def get_last_export_path(self) -> str:
        ''' Get last path used for export '''
        return self.get_setting_value('last_export_path')

    def update_setting(self, name: str, value: str):
        try:
            conn = sqlite3.connect(self.db_path)
        except Exception as e:
            raise Exception(f'Unable to connect to db: {e}')
        else:
            # Check if setting name is valid
            c = conn.cursor()
            query = '''SELECT count(name) FROM settings WHERE name = ?'''
            result = c.execute(query, [name]).fetchone()[0]
            if result != 1:
                return False
            query = ''' UPDATE settings 
                    SET value = ?
                    WHERE name = ?'''
            conn.execute(query, [value, name])
            conn.commit()

    def update_last_export_path(self, last_export_path: str):
        ''' Update last path used for export '''
        self.update_setting('last_export_path', last_export_path)
