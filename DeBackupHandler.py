import sqlite3
import os
from DeBackup import DeBackup
from decryptor.iphone_backup import EncryptedBackup


class DeBackupHandler:

    def __init__(self, backup: DeBackup, output_dir: str):
        self.__backup = backup
        self.__output_dir = output_dir + '/Backup_' + self.__backup.backup_id()

    def decrypt(self, passcode, **kwargs) -> bool:
        ''' Decrypt backup with provided passcode '''
        try:
            self.__enc_backup = EncryptedBackup(
                backup_directory=self.__backup.get_path(), passphrase=passcode)
            self.__enc_backup.test_decryption()
        except Exception as e:
            return False

        self.__decrypted_manifest_db = \
            self.__enc_backup._temp_decrypted_manifest_db_path

        return True

    def extract_camera_roll(self, **kwargs):
        # Set output path
        path = self.__output_dir + '/Camera Roll'
        if self.__backup.is_encrypted():
            # Connect to Manifest.db
            try:
                conn = sqlite3.connect(self.__decrypted_manifest_db)
            except Exception as e:
                raise Exception(f"Unable to connect to database: {e}")

            # Get file list
            c = conn.cursor()
            query = '''SELECT relativePath, flags FROM Files
                    WHERE Files.relativePath LIKE 'Media/DCIM/___APPLE/%.%'
                    AND domain = "CameraRollDomain"'''
            c.execute(query)

            # If progress callback provided
            if 'progress_callback' in kwargs.keys():
                # Get file count
                count = conn.cursor()
                count_query = '''SELECT count(*) FROM Files 
                            WHERE Files.relativePath LIKE 'Media/DCIM/___APPLE/%.%' 
                            AND domain = "CameraRollDomain"'''
                count.execute(count_query)
                file_count = count.fetchone()[0]
                processed_files = 0
                prev_progress = 0

            # Extract files
        for file_data in c:
            relativePath = file_data[0]
            file_type = file_data[1]
            try:
                if file_type == 1:
                    self.__enc_backup.extract_file(
                        relative_path=relativePath,
                        output_filename=path + '/' + relativePath)
            except Exception as e:
                raise Exception(f"Unable to extract file {relativePath}: {e}")

            # If progress callback provided, emit progress
            if 'progress_callback' in kwargs.keys():
                processed_files += 1
                progress = processed_files * 100 // file_count
                if prev_progress != progress:
                    prev_progress = progress
                    kwargs['progress_callback'].emit(('camera_roll', progress))
        else:
            # TODO: non-encrypted backups
            pass

    def extract_voice_memos(self, **kwargs):
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

            if 'progress_callback' in kwargs.keys():
                # Get file count
                count = conn.cursor()
                count_query = '''SELECT count(*) FROM Files 
                                WHERE Files.relativePath 
                                LIKE \'%Recordings/%.m4a\''''
                count.execute(count_query)
                file_count = count.fetchone()[0]
                processed_files = 0
                prev_progress = 0

            for file_data in c:
                relativePath = file_data[0]
                file_type = file_data[1]
                try:
                    if file_type == 1:
                        new_path = relativePath.rsplit('/', 1)[-1]
                        self.__enc_backup.extract_file(
                            relative_path=relativePath,
                            output_filename=path + '/' + new_path)
                except Exception as e:
                    raise Exception(
                        f"Unable to extract file {relativePath}: {e}")

                # If progress callback provided, emit progress
                if 'progress_callback' in kwargs.keys():
                    processed_files += 1
                    progress = processed_files * 100 // file_count
                    if prev_progress != progress:
                        prev_progress = progress
                        kwargs['progress_callback'].emit(
                            ('voice_memos', progress))
        else:
            # TODO: non-encrypted backups
            pass

    def extract_contacts(self, **kwargs):
        path = self.__output_dir + '/Contacts'
        if self.__backup.is_encrypted():
            # Find AddressBook database
            try:
                conn = sqlite3.connect(self.__decrypted_manifest_db)
            except Exception as e:
                raise Exception(f"Unable to connect to database: {e}")
            c = conn.cursor()
            query = '''SELECT relativePath FROM Files 
                    WHERE relativePath LIKE \'%AddressBook.sqlitedb\'
                    LIMIT 1'''
            c.execute(query)

            # Temporarily save AddressBook database
            addr_db_path = path + '/AdressBook'
            self.__enc_backup.extract_file(relative_path=c.fetchone()[0],
                                           output_filename=addr_db_path)

            # Exctract contacts
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

            # Get contacts count
            if 'progress_callback' in kwargs.keys():
                row_count_cursor = addr_db_conn.cursor()
                query = '''SELECT count(*) as id FROM ABPerson'''
                row_count = row_count_cursor.execute(query).fetchone()[0]
                prev_progress = 0
                processed_count = 0

            # Write contacts to file
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
                    if 'progress_callback' in kwargs.keys():
                        processed_count += 1
                        progress = processed_count * 100 // row_count
                        if prev_progress != progress:
                            prev_progress = progress
                            kwargs['progress_callback'].emit(
                                ('contacts', progress))
                f.close()

            # Close and delete temporary database
            addr_db_conn.close()
            os.remove(addr_db_path)
        else:
            # TODO: non-encrypted backups
            pass

    def extract_call_history(self, **kwargs):
        path = self.__output_dir + '/Call History'
        if self.__backup.is_encrypted():
            # Find CallHistory database
            try:
                conn = sqlite3.connect(self.__decrypted_manifest_db)
            except Exception as e:
                raise Exception(f"Unable to connect to database: {e}")
            c = conn.cursor()
            query = '''SELECT relativePath FROM Files 
                    WHERE relativePath LIKE \'%CallHistory.storedata\'
                    LIMIT 1'''
            c.execute(query)

            # Temporarily save CallHistory database
            call_db_path = path + '/CallHistory'
            self.__enc_backup.extract_file(relative_path=c.fetchone()[0],
                                           output_filename=call_db_path)

            # Exctract contacts
            try:
                call_db_conn = sqlite3.connect(call_db_path)
            except Exception as e:
                raise Exception(
                    f"Unable to connect to CallHistory database: {e}")
            call_db = call_db_conn.cursor()
            query = '''SELECT  ZCALLRECORD.Z_PK,
                    ZCALLRECORD.ZADDRESS,
                    datetime(ZCALLRECORD.ZDATE+978307200, 'unixepoch', 'localtime'),
                    ZCALLRECORD.ZDURATION
                    FROM ZCALLRECORD
                    ORDER BY ZCALLRECORD.ZDATE'''
            call_db.execute(query)

            if 'progress_callback' in kwargs.keys():
                # Get file count
                count = call_db_conn.cursor()
                count_query = '''SELECT count(*) FROM ZCALLRECORD'''
                count.execute(count_query)
                call_count = count.fetchone()[0]
                processed_calls = 0
                prev_progress = 0

            # Write contacts to file
            header = ['ID', 'Phone Number', 'Date', 'Duration']
            with open(path + '/Call History.txt', 'w') as f:
                f.write('\t'.join(header) + '\n')
                for contact in call_db:
                    # If progress callback provided, emit progress
                    if 'progress_callback' in kwargs.keys():
                        processed_calls += 1
                        progress = processed_calls * 100 // call_count
                        if prev_progress != progress:
                            prev_progress = progress
                            kwargs['progress_callback'].emit(
                                ('call_history', progress))
                    f.write(
                        '\t'.join([str(val) for val in contact]) + '\n')
                f.close()

            # Close and delete temporary database
            call_db_conn.close()
            os.remove(call_db_path)
        else:
            # TODO: non-encrypted backups
            pass

    def extract_calendar(self, **kwargs):
        path = self.__output_dir + '/Calendar'
        if self.__backup.is_encrypted():
            # Find Calendar database
            try:
                conn = sqlite3.connect(self.__decrypted_manifest_db)
            except Exception as e:
                raise Exception(f"Unable to connect to database: {e}")
            c = conn.cursor()
            query = '''SELECT relativePath FROM Files 
                    WHERE relativePath LIKE \'%Calendar.sqlitedb\'
                    LIMIT 1'''
            c.execute(query)

            # Temporarily save CallHistory database
            calendar_db_path = path + '/Calendar'
            self.__enc_backup.extract_file(relative_path=c.fetchone()[0],
                                           output_filename=calendar_db_path)

            # Exctract contacts
            try:
                calendar_db_conn = sqlite3.connect(calendar_db_path)
            except Exception as e:
                raise Exception(
                    f"Unable to connect to Calendar database: {e}")
            calendar_db = calendar_db_conn.cursor()
            query = '''SELECT CalendarItem.summary, 
                    datetime(CalendarItem.start_date+978307200, 'unixepoch', 'localtime'),
                    datetime(CalendarItem.end_date+978307200, 'unixepoch', 'localtime'),
                    CalendarItem.all_day,
                    CalendarItem.description
                    FROM CalendarItem
                    ORDER BY CalendarItem.start_date'''
            calendar_db.execute(query)

            if 'progress_callback' in kwargs.keys():
                # Get file count
                count = calendar_db_conn.cursor()
                count_query = '''SELECT count(*) FROM CalendarItem'''
                count.execute(count_query)
                event_count = count.fetchone()[0]
                processed_events = 0
                prev_progress = 0

            # Write events to file
            with open(path + '/Calendar.txt', 'w') as f:
                for event_data in calendar_db:
                    summary, start_date, end_date, \
                        all_day_flag, description = event_data
                    event = f'Summary: {summary}\n'
                    event += f'Start: {start_date}\n'
                    event += f'End: {end_date}\n' if all_day_flag else 'All day\n'
                    event += f'Description:\n{description}\n\n' if description else '\n'
                    f.write(event)

                    # If progress callback provided, emit progress
                    if 'progress_callback' in kwargs.keys():
                        processed_events += 1
                        progress = processed_events * 100 // event_count
                        if prev_progress != progress:
                            prev_progress = progress
                            kwargs['progress_callback'].emit(
                                ('calendar', progress))
                f.close()

            # Close and delete temporary database
            calendar_db_conn.close()
            os.remove(calendar_db_path)
        else:
            # TODO: non-encrypted backups
            pass

    def extract_notes(self, **kwargs):
        path = self.__output_dir + '/Notes'
        if self.__backup.is_encrypted():
            # Find Notes database
            try:
                conn = sqlite3.connect(self.__decrypted_manifest_db)
            except Exception as e:
                raise Exception(f"Unable to connect to database: {e}")
            c = conn.cursor()
            query = '''SELECT relativePath FROM Files 
                    WHERE relativePath LIKE \'%notes.sqlite\'
                    LIMIT 1'''
            c.execute(query)

            # Temporarily save Notes database
            notes_db_path = path + '/Notes'
            self.__enc_backup.extract_file(relative_path=c.fetchone()[0],
                                           output_filename=notes_db_path)

            # Exctract notes
            try:
                notes_db_conn = sqlite3.connect(notes_db_path)
            except Exception as e:
                raise Exception(
                    f"Unable to connect to notes database: {e}")
            notes_db = notes_db_conn.cursor()
            query = '''SELECT ZNOTE.ZBODY, 
						ZNOTE.ZTITLE,
						ZNOTE.ZSUMMARY,
						ZNOTEBODY.ZCONTENT,
						ZNOTE.ZDELETEDFLAG,
						datetime(ZNOTE.ZCREATIONDATE+978307200, 'unixepoch', 'localtime'),
						datetime(ZNOTE.ZMODIFICATIONDATE+978307200, 'unixepoch', 'localtime')
					FROM ZNOTE INNER JOIN ZNOTEBODY ON ZNOTE.Z_PK = ZNOTEBODY.ZOWNER
					ORDER BY ZNOTE.ZCREATIONDATE'''
            notes_db.execute(query)

            if 'progress_callback' in kwargs.keys():
                # Get file count
                count = notes_db_conn.cursor()
                count_query = '''SELECT count(*) FROM ZNOTE'''
                count.execute(count_query)
                file_count = count.fetchone()[0]
                processed_files = 0
                prev_progress = 0

            # Write notes to files
            for note in c.fetchall():
                # Build note
                note_id, title, summary, content, \
                    deleted_flag, created, modified = note
                note_string = 'Title: ' + title + '\n' if title else 'Title: No title\n'
                note_string += 'Created: ' + created + '\n'
                note_string += 'Last modified: ' + modified + '\n'
                note_string += 'Summary: ' + summary + '\n' if summary else 'Title: No summary\n'
                note_string += 'Is deleted:' + 'True\n' if deleted_flag else 'False\n'
                note_string += 'Content:\n' + content + '\n'
                note_path = path + title + '.txt' if title else 'No_title.txt'

                # Write note to file
                with open(note_path, 'w') as f:
                    f.write(note_string)
                f.close()

                # If progress callback provided, emit progress
                if 'progress_callback' in kwargs.keys():
                    processed_files += 1
                    progress = processed_files * 100 // file_count
                    if prev_progress != progress:
                        prev_progress = progress
                        kwargs['progress_callback'].emit(
                            ('notes', progress))

            # Close and delete temporary database
            notes_db_conn.close()
            os.remove(notes_db_path)
        else:
            # TODO: non-encrypted backups
            pass

    def extract_sms_imessage(self):
        pass

    def extract_voicemail(self, **kwargs):
        path = self.__output_dir + '/Voicemail'
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

            if 'progress_callback' in kwargs.keys():
                # Get file count
                count = conn.cursor()
                count_query = '''SELECT count(*) FROM Files 
                                WHERE Files.relativePath 
                                LIKE \'%Recordings/%.m4a\''''
                count.execute(count_query)
                file_count = count.fetchone()[0]
                processed_files = 0
                prev_progress = 0

            for file_data in c:
                relativePath = file_data[0]
                file_type = file_data[1]
                try:
                    if file_type == 1:
                        new_path = relativePath.rsplit('/', 1)[-1]
                        self.__enc_backup.extract_file(
                            relative_path=relativePath,
                            output_filename=path + '/' + new_path)
                except Exception as e:
                    raise Exception(
                        f"Unable to extract file {relativePath}: {e}")

                # If progress callback provided, emit progress
                if 'progress_callback' in kwargs.keys():
                    processed_files += 1
                    progress = processed_files * 100 // file_count
                    if prev_progress != progress:
                        prev_progress = progress
                        kwargs['progress_callback'].emit(
                            ('voice_memos', progress))
        else:
            # TODO: non-encrypted backups
            pass

