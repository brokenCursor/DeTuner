import sqlite3
import os
from DeBackup import DeBackup
from decryptor.iphone_backup import EncryptedBackup


class DeBackupHandler:

    def __init__(self, backup: DeBackup, output_dir: str):
        self.__backup = backup
        self.__output_dir = output_dir + '/Backup_' + self.__backup.backup_id()

    def decrypt(self, passcode):
        ''' Decrypt backup with provided passcode '''

        try:
            self.__enc_backup = EncryptedBackup(
                backup_directory=self.__backup.get_path(), passphrase=passcode)
            self.__enc_backup.test_decryption()
        except Exception as e:
            raise Exception(f"Unable to decrypt backup: {e}")

        self.__decrypted_manifest_db = \
            self.__enc_backup._temp_decrypted_manifest_db_path

    def extract_camera_roll(self):
        path = self.__output_dir + '/Camera Roll'
        if self.__backup.is_encrypted():
            try:
                conn = sqlite3.connect(self.__decrypted_manifest_db)
            except Exception as e:
                raise Exception(f"Unable to connect to database: {e}")
            c = conn.cursor()
            query = '''SELECT relativePath, flags FROM Files 
                    WHERE Files.relativePath LIKE 'Media/DCIM/___APPLE/%.%' 
                    AND domain = "CameraRollDomain"'''
            c.execute(query)
        for file_data in c:
            relativePath = file_data[0]
            file_type = file_data[1]
            try:
                print(path)
                if file_type == 1:
                    self.__enc_backup.extract_file(
                        relative_path=relativePath,
                        output_filename=path + '/' + relativePath)
            except Exception as e:
                raise Exception(f"Unable to extract file {relativePath}: {e}")
        else:
            # TODO: non-encrypted backups
            pass

    def extract_voice_memos(self):
        path = self.__output_dir + '/Voice Memos'
        if self.__backup.is_encrypted():
            try:
                conn = sqlite3.connect(self.__decrypted_manifest_db)
            except Exception as e:
                raise Exception(f"Unable to connect to database: {e}")
            c = conn.cursor()
            query = '''SELECT relativePath, flags FROM Files 
                    WHERE Files.relativePath 
                    LIKE \'%Recordings/%.m4a\''''
            c.execute(query)
            for file_data in c:
                relativePath = file_data[0]
                file_type = file_data[1]
                try:
                    if file_type == 1:
                        new_path = relativePath.rsplit('/', 1)[-1]
                        print(new_path)
                        self.__enc_backup.extract_file(
                            relative_path=relativePath,
                            output_filename=path + '/' + new_path)
                except Exception as e:
                    raise Exception(
                        f"Unable to extract file {relativePath}: {e}")
        else:
            # TODO: non-encrypted backups
            pass

    def extract_contacts(self):
        path = self.__output_dir + '/Contacts'
        if self.__backup.is_encrypted():
            try:
                conn = sqlite3.connect(self.__decrypted_manifest_db)
            except Exception as e:
                raise Exception(f"Unable to connect to database: {e}")
            c = conn.cursor()
            query = '''SELECT relativePath FROM Files 
                    WHERE relativePath LIKE \'%AddressBook.sqlitedb\'
                    LIMIT 1'''
            c.execute(query)
            addr_db_path = path + '/AdressBook'
            self.__enc_backup.extract_file(relative_path=c.fetchone()[
                                           0], output_filename=addr_db_path)
            try:
                addr_db_conn = sqlite3.connect(addr_db_path)
            except Exception as e:
                raise Exception(
                    f"Unable to connect to AddressBook database: {e}")
            addr_db = addr_db_conn.cursor()
            query = '''SELECT ABPerson.ROWID as id,
                        ABPerson.DisplayName,
                        ABPerson.First,
                        ABPerson.Middle,
                        ABPerson.Last,
                        ABPerson.Nickname,
                        ABPerson.Organization,
                        ABPerson.Department,
                        ABPerson.JobTitle,
                        ABPerson.Note,
                        datetime(ABPerson.Birthday+978307200, 'unixpoch', 'localtime') as Birthday,
                        ABPersonFullTextSearch_content.c16Phone,
                        ABPersonFullTextSearch_content.c17Email,
                        ABPersonFullTextSearch_content.c19SocialProfile,
                        ABPersonFullTextSearch_content.c20URL,
                        datetime(ABPerson.CreationDate+978307200, 'unixepoch', 'localtime') AS creation_date
                        FROM ABPerson INNER JOIN ABPersonFullTextSearch_content ON ABPerson.ROWID = ABPersonFullTextSearch_content.docid
                        ORDER BY ABPerson.First'''
            addr_db.execute(query)
            header = ['ID', 'Dispaly Name', 'First Name', 'Second Name',
                      'Last Name', 'Nickname', 'Organization',
                      'Department', 'Job Title', 'Note', 'Birthday',
                      'Phone Number', 'Email', 'Social Profile', 'URL',
                      'Created']
            with open(path + '/Contacts.txt', 'w') as f:
                f.write('\t'.join(header) + '\n')
                for contact in addr_db:
                    f.write(
                        '\t'.join([str(val).replace('\u202a', '').replace('\u2011', '-').
                                   replace('\u202c', '') for val in contact]) + '\n')
                f.close()
            addr_db_conn.close()
            os.remove(addr_db_path)
        else:
            # TODO: non-encrypted backups
            pass

    def __del__(self):
        if self.__enc_backup:
            self.__enc_backup.__del__()
