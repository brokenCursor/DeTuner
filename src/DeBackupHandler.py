# -*- coding: utf-8 -*-
import sqlite3
import os
from DeBackup import DeBackup
from decryptor.iphone_backup import EncryptedBackup


class DeBackupHandler:
    ''' Class for performing decryption of a backup and extracting of data from it '''

    def __init__(self, backup: DeBackup, locale: dict):
        ''' Setup DeBackupHandler
            args:
                backup (DeBackup): a backup to be used for all operations 
                locale (dict): a dictionary with all required strings '''
        self.__backup = backup
        self.__locale = locale

    def set_output_directory(self, path: str):
        ''' Set directory for writing results to '''

        self.__output_dir = path + os.sep + \
            self.__locale["backup_dir_prefix"] + self.__backup.backup_id()

    def decrypt(self, passcode, **_) -> bool:
        ''' Decrypt backup with provided passcode '''

        try:
            self.__enc_backup = EncryptedBackup(
                backup_directory=self.__backup.get_path(), passphrase=passcode)
            self.__enc_backup.test_decryption()
        except Exception as e:
            return False

        # Save backup's Manifest.db path
        self.__decrypted_manifest_db = \
            self.__enc_backup._temp_decrypted_manifest_db_path
        return True

    def extract_camera_roll(self, **kwargs):
        ''' Extract all images and videos found in device's Camera Roll '''

        # Get strings from locale
        strings = self.__locale["camera_roll"]

        # Set output path
        path = self.__output_dir + os.sep + strings["directory"]
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
                if file_type == 1:  # If file is file and not something else
                    # Get file from backup and store at path
                    self.__enc_backup.extract_file(
                        relative_path=relativePath,
                        output_filename=path + '/' + relativePath)
            except Exception as e:
                raise Exception(f"Unable to extract file {relativePath}: {e}")

            # If progress callback provided, emit progress
            if 'progress_callback' in kwargs.keys():
                processed_files += 1
                progress = processed_files * 100 // file_count
                if prev_progress != progress:  # Used to limit amount of calls to main thread
                    prev_progress = progress
                    kwargs['progress_callback'].emit(('camera_roll', progress))
        else:
            # TODO: non-encrypted backups
            pass

    def extract_voice_memos(self, **kwargs):
        ''' Extract all recordings form Voice Memos app '''

        # Get strings from locale
        strings = self.__locale["voice_memos"]

        # Set output path
        path = self.__output_dir + os.sep + strings["directory"]
        if self.__backup.is_encrypted():
            # Connect to Manifest.db
            try:
                conn = sqlite3.connect(self.__decrypted_manifest_db)
            except Exception as e:
                raise Exception(f"Unable to connect to database: {e}")

            # Get files
            c = conn.cursor()
            query = '''SELECT relativePath, flags FROM Files 
                    WHERE Files.relativePath 
                    LIKE \'%Recordings/%.m4a\''''
            c.execute(query)

            # If progress callback provided
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

            # Extract files
            for file_data in c:
                relativePath = file_data[0]
                file_type = file_data[1]
                try:
                    if file_type == 1:  # If file is file and not something else
                        file_name = relativePath.rsplit('/', 1)[-1]
                        # Get file from backup and store at path
                        self.__enc_backup.extract_file(
                            relative_path=relativePath,
                            output_filename=path + '/' + file_name)
                except Exception as e:
                    raise Exception(
                        f"Unable to extract file {relativePath}: {e}")

                # If progress callback provided, emit progress
                if 'progress_callback' in kwargs.keys():
                    processed_files += 1
                    progress = processed_files * 100 // file_count
                    if prev_progress != progress:  # Used to limit amount of calls to main thread
                        prev_progress = progress
                        kwargs['progress_callback'].emit(
                            ('voice_memos', progress))
        else:
            # TODO: non-encrypted backups
            pass

    def extract_contacts(self, **kwargs):
        ''' Extract all contacts '''

        # Get strings from locale
        strings = self.__locale["contacts"]

        # Set output path
        path = self.__output_dir + os.sep + strings["directory"]
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

            # Connect to AddressBook DB
            try:
                addr_db_conn = sqlite3.connect(addr_db_path)
            except Exception as e:
                raise Exception(
                    f"Unable to connect to AddressBook database: {e}")

            # Get list of contacts
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

            # If progress callback provided
            if 'progress_callback' in kwargs.keys():
                # Get contacts count
                row_count_cursor = addr_db_conn.cursor()
                query = '''SELECT count(*) as id FROM ABPerson'''
                row_count = row_count_cursor.execute(query).fetchone()[0]
                prev_progress = 0
                processed_count = 0

            # Setup file header
            header = ['ID', 'Dispaly Name', 'First Name', 'Second Name',
                      'Last Name', 'Nickname', 'Organization',
                      'Department', 'Job Title', 'Note', 'Birthday',
                      'Phone Number', 'Email', 'Social Profile', 'URL',
                      'Created']

            # Write contacts to file
            with open(path + os.sep + strings["file_name"] + '.txt', 'w', encoding="UTF-16") as f:
                f.write('\t'.join(header) + '\n')
                for contact in addr_db:
                    f.write(
                        '\t'.join([str(val) for val in contact]) + '\n')

                    # If progress callback provided, emit progress
                    if 'progress_callback' in kwargs.keys():
                        processed_count += 1
                        progress = processed_count * 100 // row_count
                        if prev_progress != progress:  # Used to limit amount of calls to main thread
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
        ''' Extract history of call form Phone app '''

        # Get strings from locale
        strings = self.__locale["call_history"]

        # Set output path
        path = self.__output_dir + os.sep + strings["directory"]
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

            # Connect to CallHistory DB
            try:
                call_db_conn = sqlite3.connect(call_db_path)
            except Exception as e:
                raise Exception(
                    f"Unable to connect to CallHistory database: {e}")

            # Get call history
            call_db = call_db_conn.cursor()
            query = '''SELECT  ZCALLRECORD.Z_PK,
                    ZCALLRECORD.ZADDRESS,
                    datetime(ZCALLRECORD.ZDATE+978307200, 'unixepoch', 'localtime'),
                    ZCALLRECORD.ZDURATION
                    FROM ZCALLRECORD
                    ORDER BY ZCALLRECORD.ZDATE'''
            call_db.execute(query)

            # If progress callback provided
            if 'progress_callback' in kwargs.keys():
                # Get call count
                count = call_db_conn.cursor()
                count_query = '''SELECT count(*) FROM ZCALLRECORD'''
                count.execute(count_query)
                call_count = count.fetchone()[0]
                processed_calls = 0
                prev_progress = 0

            # Write call history to file to file
            header = strings["header"]
            with open(path + os.sep + strings["file_name"] + '.txt', 'w') as f:
                f.write('\t'.join(header) + '\n')
                for contact in call_db:
                    f.write(
                        '\t'.join([str(val) for val in contact]) + '\n')

                    # If progress callback provided, emit progress
                    if 'progress_callback' in kwargs.keys():
                        processed_calls += 1
                        progress = processed_calls * 100 // call_count
                        if prev_progress != progress:  # Used to limit amount of calls to main thread
                            prev_progress = progress
                            kwargs['progress_callback'].emit(
                                ('call_history', progress))
                f.close()

            # Close and delete temporary database
            call_db_conn.close()
            os.remove(call_db_path)
        else:
            # TODO: non-encrypted backups
            pass

    def extract_calendar(self, **kwargs):
        ''' Extract all events form Calendar app '''

        # Get strings from locale
        strings = self.__locale["calendar"]

        # Set output path
        path = self.__output_dir + os.sep + strings["directory"]
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

            # Temporarily save Calendar database
            calendar_db_path = path + '/Calendar'
            self.__enc_backup.extract_file(relative_path=c.fetchone()[0],
                                           output_filename=calendar_db_path)

            # Connect to Calendar DB
            try:
                calendar_db_conn = sqlite3.connect(calendar_db_path)
            except Exception as e:
                raise Exception(
                    f"Unable to connect to Calendar database: {e}")

            # Get list of events
            calendar_db = calendar_db_conn.cursor()
            query = '''SELECT CalendarItem.summary, 
                    datetime(CalendarItem.start_date+978307200, 'unixepoch', 'localtime'),
                    datetime(CalendarItem.end_date+978307200, 'unixepoch', 'localtime'),
                    CalendarItem.all_day,
                    CalendarItem.description
                    FROM CalendarItem
                    ORDER BY CalendarItem.start_date'''
            calendar_db.execute(query)

            # If progress callback is provided
            if 'progress_callback' in kwargs.keys():
                # Get event count
                count = calendar_db_conn.cursor()
                count_query = '''SELECT count(*) FROM CalendarItem'''
                count.execute(count_query)
                event_count = count.fetchone()[0]
                processed_events = 0
                prev_progress = 0

            # Write events to file
            with open(path + os.sep + strings["file_name"] +'.txt', 'w') as f:
                for event_data in calendar_db:
                    summary, start_date, end_date, \
                        all_day_flag, description = event_data
                    # Generate event string
                    event = ''
                    event += strings["templates"]["summary"].format(
                        summ=summary)
                    event += strings["templates"]["start"].format(
                        start=start_date)
                    if all_day_flag:
                        event += strings["templates"]["all_day"]
                    else:
                        event += strings["templates"]["end"].format(
                            end=end_date)
                    if description:
                        event += strings["templates"]["description"].format(
                            desc=description)
                    else:
                        event += '\n\n'
                    f.write(event)

                    # If progress callback provided, emit progress
                    if 'progress_callback' in kwargs.keys():
                        processed_events += 1
                        progress = processed_events * 100 // event_count
                        if prev_progress != progress:  # Used to limit amount of calls to main thread
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
        ''' Extract notes from Notes app '''

        # Get strings from locale
        strings = self.__locale["notes"]

        # Set output path
        path = self.__output_dir + os.sep + strings["directory"]
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

            # Connect to Notes DB
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

                if title:
                    note_string = strings["templates"]["title"].format(
                        title=title)
                else:
                    note_string = strings["templates"]["no_title"]
                note_string += strings["templates"]["created"].format(
                    date=created)

                note_string += strings["templates"]["last_modified"].format(
                    date=modified)

                if summary:
                    note_string += strings["templates"]["summary"].format(
                        summ=summary)
                else:
                    note_string += strings["templates"]["no_summary"]

                note_string += strings["templates"]["is_deleted"].format(
                    val=bool(deleted_flag))
                note_string += strings["templates"]["content"].format(
                    cont=content)

                note_path = path + os.sep + \
                    title if title else strings["no_title_file_name"] + '.txt'

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

            if 'progress_callback' in kwargs.keys() and processed_files == 0:
                kwargs['progress_callback'].emit(
                    ('notes', 100))

            # Close and delete temporary database
            notes_db_conn.close()
            os.remove(notes_db_path)
        else:
            # TODO: non-encrypted backups
            pass

    def extract_sms_imessage(self, **kwargs):
        """ Extract SMS and iMessage chat history """

        # Get strings from locale
        strings = self.__locale["sms_imessage"]

        # Set output path
        path = self.__output_dir + os.sep + strings["directory"]

        if self.__backup.is_encrypted():
            # Find SMS database
            try:
                conn = sqlite3.connect(self.__decrypted_manifest_db)
            except Exception as e:
                raise Exception(f"Unable to connect to database: {e}")
            c = conn.cursor()
            query = '''SELECT relativePath FROM Files 
                    WHERE relativePath LIKE \'%sms.db\'
                    LIMIT 1'''
            c.execute(query)

            # Temporarily save SMS database
            sms_db_path = path + '/SMS'
            self.__enc_backup.extract_file(relative_path=c.fetchone()[0],
                                           output_filename=sms_db_path)

            # Connect to SMS db
            try:
                sms_db_conn = sqlite3.connect(sms_db_path)
            except Exception as e:
                raise Exception(f"Unable to connect to SMS database: {e}")

            # Get chat list
            chat_list = sms_db_conn.cursor()
            query = '''SELECT  chat.ROWID, 
                    handle.id,
                    handle.uncanonicalized_id,
                    handle.service
                    FROM chat
                    LEFT JOIN handle ON handle.ROWID = chat.ROWID'''
            chat_list.execute(query)

            if 'progress_callback' in kwargs.keys():
                # Get message count
                count = sms_db_conn.cursor()
                query = '''SELECT count(*) FROM message'''
                count.execute(query)
                msg_count = count.fetchone()[0]
                processed_messages = 0
                prev_progress = 0

            for chat in chat_list:
                # Extract chat info
                chat_id, handle_id, handle_raw_id, service = chat
                # Get messages in chat
                messages = sms_db_conn.cursor()
                query = '''SELECT chat_message_join.message_id,
                        message.text,
                        message.is_from_me,
                        datetime(message.date+978307200, 'unixepoch', 'localtime'),
                        datetime(message.date_delivered+978307200, 'unixepoch', 'localtime'),
                        datetime(message.date_read+978307200, 'unixepoch', 'localtime')
                        FROM chat_message_join
                        LEFT JOIN message ON message.ROWID = chat_message_join.message_id
                        WHERE chat_message_join.chat_id = ?'''
                messages.execute(query, [chat_id])

                # Create chat directory
                chat_path = path + \
                    f'/{handle_raw_id if handle_raw_id else handle_id} ({service})'
                os.makedirs(chat_path)
                # Create attachments directory
                attachments_path = chat_path + os.sep + \
                    strings["attachments_directory"]
                os.makedirs(attachments_path)

                # Save messages

                for msg in messages:
                    # Extract message data
                    msg_id, text, is_from_me, date, date_delivered, date_read = msg
                    # Generate message string
                    msg_string = strings["templates"]["id"].format(id=msg_id)

                    if is_from_me:
                        msg_string += strings["templates"]["from_me"]
                    else:
                        msg_string += strings["templates"]["from"].format(
                            handle=handle_id)

                    if date:
                        msg_string += strings["templates"]["date"].format(
                            date=date)

                    msg_string += strings["templates"]["delivered"].format(
                        date=date_delivered)
                    msg_string += strings["templates"]["read"].format(
                        date=date_read)
                    msg_string += strings["templates"]["content"].format(
                        text=text)

                    # Write to file
                    with open(chat_path + os.sep + strings["chat_file_name"] + '.txt', 'a', encoding='UTF-16') as f:
                        f.write(msg_string)
                    f.close()

                    # Extract message attachments
                    attachments = sms_db_conn.cursor()
                    query = '''SELECT attachment.filename
                            FROM attachment
                            LEFT JOIN message_attachment_join on attachment.ROWID = message_attachment_join.attachment_id
                            WHERE message_attachment_join.message_id = ?'''
                    attachments.execute(query, [msg_id])
                    for att in attachments:
                        file_path = att[0]
                        filename = file_path.split('/')[-1]
                        if file_path.startswith('~'):
                            file_path = file_path.lstrip('~/')
                            self.__enc_backup.extract_file(relative_path=file_path,
                                                           output_filename=attachments_path
                                                           + '/' + filename)
                    if 'progress_callback' in kwargs.keys():
                        processed_messages += 1
                        progress = processed_messages * 100 // msg_count
                        if prev_progress != progress:
                            prev_progress = progress
                            kwargs['progress_callback'].emit(
                                ('sms_imessage', progress))

            sms_db_conn.close()
            os.remove(sms_db_path)

    def extract_voicemail(self, **kwargs):
        """ Extact voicemail recordings and metadata """
        # Get strings from locale
        strings = self.__locale["notes"]

        # Set output path
        path = self.__output_dir + os.sep + strings["directory"]
        if self.__backup.is_encrypted():
            # Connect to manifest.db
            try:
                conn = sqlite3.connect(self.__decrypted_manifest_db)
            except Exception as e:
                raise Exception(f"Unable to connect to database: {e}")

            # Find voicemail database
            c = conn.cursor()
            query = '''SELECT relativePath FROM Files 
                    WHERE Files.relativePath 
                    LIKE '%voicemail.db'
                    LIMIT 1'''
            c.execute(query)

            # Temporarily save voicemail metadata db
            voicemail_db_path = path + '/Voicemail'
            self.__enc_backup.extract_file(relative_path=c.fetchone()[0],
                                           output_filename=voicemail_db_path)

            # Get voicemail metadata
            try:
                voicemail_db_conn = sqlite3.connect(voicemail_db_path)
            except Exception as e:
                raise Exception(
                    f"Unable to connect to voicemail metadata database: {e}")
            voicemail_db_cursor = voicemail_db_conn.cursor()
            query = '''SELECT voicemail.ROWID as id,
                    voicemail.sender,
                    voicemail.duration,
                    datetime(voicemail.date+978307200, 'unixepoch', 'localtime') as 'date'
					FROM voicemail
					ORDER BY voicemail.date'''
            voicemail_db_cursor.execute(query)

            # Get voicemail file list
            file_cursor = conn.cursor()
            query = '''SELECT relativePath, flags FROM Files 
                        WHERE Files.relativePath LIKE \'%Voicemail/%.amr\''''
            file_cursor.execute(query)

            # Get voicemail file count
            if 'progress_callback' in kwargs.keys():
                count = conn.cursor()
                count_query = '''SELECT count(*) FROM Files 
                                WHERE Files.relativePath 
                                LIKE \'%Voicemail/%.amr\''''
                count.execute(count_query)
                file_count = count.fetchone()[0]
                processed_files = 0
                prev_progress = 0

            # Save to path
            for file_data, metadata in zip(file_cursor, voicemail_db_cursor):
                relativePath = file_data[0]
                file_type = file_data[1]

                # Extract voicemail file
                try:
                    if file_type == 1:
                        new_path = relativePath.rsplit('/', 1)[-1]
                        self.__enc_backup.extract_file(
                            relative_path=relativePath,
                            output_filename=path + '/' + new_path)
                except Exception as e:
                    raise Exception(
                        f"Unable to extract file {relativePath}: {e}")

                # Generate metadata string
                sender, duration, date = metadata
                metadata_string = strings["templates"]["sender"].format(
                    sender=sender)
                metadata_string += strings["templates"]["date"].format(
                    date=date)
                metadata_string += strings["templates"]["duration"].format(
                    dur=duration)

                # Save metadata string to file
                with open(path + os.sep + strings["file_name"] + '.txt', 'w') as f:
                    f.write(metadata_string)
                    f.close

                # If progress callback provided, emit progress
                if 'progress_callback' in kwargs.keys():
                    processed_files += 1
                    progress = processed_files * 100 // file_count
                    if prev_progress != progress:
                        prev_progress = progress
                        kwargs['progress_callback'].emit(
                            ('voicemail', progress))

            if 'progress_callback' in kwargs.keys() and processed_files == 0:
                kwargs['progress_callback'].emit(
                    ('voicemail', 100))

            voicemail_db_conn.close()
            os.remove(voicemail_db_path)
        else:
            # TODO: non-encrypted backups
            pass
