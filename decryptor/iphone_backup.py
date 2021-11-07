import os.path
import shutil
import sqlite3
import struct
import tempfile

import biplist

from . import google_iphone_dataprotection

__all__ = ["EncryptedBackup", "RelativePath", "RelativePathsLike"]


class RelativePath:
    """Relative paths for commonly accessed files."""

    # Standard iOS file locations:
    ADDRESS_BOOK = "Library/AddressBook/AddressBook.sqlitedb"
    TEXT_MESSAGES = "Library/SMS/sms.db"
    CALL_HISTORY = "Library/CallHistoryDB/CallHistory.storedata"
    NOTES = "Library/Notes/notes.sqlite"
    HEALTH = "Health/healthdb.sqlite"
    HEALTH_SECURE = "Health/healthdb_secure.sqlite"

    # Very common external files:
    WHATSAPP_MESSAGES = "ChatStorage.sqlite"
    WHATSAPP_CONTACTS = "ContactsV2.sqlite"


class RelativePathsLike:
    """Relative path wildcards for commonly accessed groups of files."""

    # Standard iOS file locations:
    CAMERA_ROLL = "Media/DCIM/%APPLE/IMG%.%"
    SMS_ATTACHMENTS = "Library/SMS/Attachments/%.%"

    # WhatsApp paths, which contain "."s and so must search for ".jpg" and ".mp4" individually:
    WHATSAPP_ATTACHED_IMAGES = "Message/Media/%.jpg"
    WHATSAPP_ATTACHED_VIDEOS = "Message/Media/%.mp4"


# Based on https://stackoverflow.com/questions/1498342/how-to-decrypt-an-encrypted-apple-itunes-iphone-backup
# and code sample provided by @andrewdotn in this answer: https://stackoverflow.com/a/13793043
class EncryptedBackup:

    def __init__(self, *, backup_directory, passphrase):
        """
        Decrypt an iOS 13 encrypted backup using the passphrase chosen in iTunes.

        The passphrase and decryption keys will be stored in memory whilst using this code,
        and a temporary decrypted copy of the Manifest database containing a list of all files
        in the backup will be created in a temporary folder. If run on a machine without full-disk
        encryption, this may leak the keys and reduce the overall security of the backup.
        If an exception occurs during program execution, there is a chance this decrypted Manifest
        database will not be removed. Its location is stored in '_temp_decrypted_manifest_db_path'
        which can be printed and manually inspected if desired.

        :param backup_directory:
            The path to the backup directory on disk. On Windows, this is either:
              - '%AppData%\\Apple Computer\\MobileSync\\Backup\\[device-specific-hash]'
              or, for iTunes installed via the Windows Store:
              - '%UserProfile%\\Apple\\MobileSync\\Backup\\[device-specific-hash]'
            The folder should contain 'Manifest.db' and 'Manifest.plist' if it contains a valid backup.
        :param passphrase:
            The passphrase chosen in iTunes when first choosing to encrypt backups.
            If it requires an encoding other than ASCII or UTF-8, a bytes object must be provided.
        """
        # Public state:
        self.decrypted = False
        # Keep track of the backup directory, and more dangerously, keep the backup passphrase as bytes until used:
        self._backup_directory = os.path.expandvars(backup_directory)
        self._passphrase = passphrase if type(passphrase) is bytes else passphrase.encode("utf-8")
        # Internals for unlocking the Keybag:
        self._manifest_plist_path = os.path.join(self._backup_directory, 'Manifest.plist')
        self._manifest_plist = None
        self._manifest_db_path = os.path.join(self._backup_directory, 'Manifest.db')
        self._keybag = None
        self._unlocked = False
        # We need a temporary file for the decrypted database, because SQLite can't open bytes in memory as a database:
        self._temporary_folder = tempfile.mkdtemp()
        self._temp_decrypted_manifest_db_path = os.path.join(self._temporary_folder, 'Manifest.db')
        # We can keep a connection to the index SQLite database open:
        self._temp_manifest_db_conn = None

    def __del__(self):
        self._cleanup()

    def _cleanup(self):
        try:
            if self._temp_manifest_db_conn is not None:
                self._temp_manifest_db_conn.close()
            shutil.rmtree(self._temporary_folder)
        except Exception:
            print("WARN: Cleanup failed. You may want to delete the decrypted temporary file found at:")
            print("    '{}'".format(self._temp_decrypted_manifest_db_path))
            raise

    def _read_and_unlock_keybag(self):
        if self._unlocked:
            return self._unlocked
        # Open the Manifest.plist file to access the Keybag:
        with open(self._manifest_plist_path, 'rb') as infile:
            self._manifest_plist = biplist.readPlist(infile)
        self._keybag = google_iphone_dataprotection.Keybag(self._manifest_plist['BackupKeyBag'])
        # Attempt to unlock the Keybag:
        self._unlocked = self._keybag.unlockWithPassphrase(self._passphrase)
        if not self._unlocked:
            raise ValueError("Failed to decrypt keys: incorrect passphrase?")
        # No need to keep the passphrase any more:
        self._passphrase = None
        return True

    def _open_temp_database(self):
        # Check that we have successfully decrypted the file:
        if not os.path.exists(self._temp_decrypted_manifest_db_path):
            return False
        try:
            # Connect to the decrypted Manifest.db database if necessary:
            if self._temp_manifest_db_conn is None:
                self._temp_manifest_db_conn = sqlite3.connect(self._temp_decrypted_manifest_db_path)
            # Check that it has the expected table structure and a list of files:
            cur = self._temp_manifest_db_conn.cursor()
            cur.execute("SELECT count(*) FROM Files;")
            file_count = cur.fetchone()[0]
            cur.close()
            return file_count > 0
        except sqlite3.Error:
            return False

    def _decrypt_manifest_db_file(self):
        if os.path.exists(self._temp_decrypted_manifest_db_path):
            return
        # Ensure we've already unlocked the Keybag:
        self._read_and_unlock_keybag()
        # Decrypt the Manifest.db index database:
        manifest_key = self._manifest_plist['ManifestKey'][4:]
        with open(self._manifest_db_path, 'rb') as encrypted_db_filehandle:
            encrypted_db = encrypted_db_filehandle.read()
        manifest_class = struct.unpack('<l', self._manifest_plist['ManifestKey'][:4])[0]
        key = self._keybag.unwrapKeyForClass(manifest_class, manifest_key)
        decrypted_data = google_iphone_dataprotection.AESdecryptCBC(encrypted_db, key)
        # Write the decrypted Manifest.db temporarily to disk:
        with open(self._temp_decrypted_manifest_db_path, 'wb') as decrypted_db_filehandle:
            decrypted_db_filehandle.write(decrypted_data)
        # Open the temporary database to verify decryption success:
        if not self._open_temp_database():
            raise ConnectionError("Manifest.db file does not seem to be the right format!")

    def _decrypt_inner_file(self, *, file_id, file_bplist):
        # Ensure we've already unlocked the Keybag:
        self._read_and_unlock_keybag()
        # Extract the decryption key from the PList data:
        plist = biplist.readPlistFromString(file_bplist)
        file_data = plist['$objects'][plist['$top']['root'].integer]
        protection_class = file_data['ProtectionClass']
        if "EncryptionKey" not in file_data:
            return None  # This file is not encrypted; either a directory or empty.
        encryption_key = plist['$objects'][file_data['EncryptionKey'].integer]['NS.data'][4:]
        inner_key = self._keybag.unwrapKeyForClass(protection_class, encryption_key)
        # Find the encrypted version of the file on disk and decrypt it:
        filename_in_backup = os.path.join(self._backup_directory, file_id[:2], file_id)
        with open(filename_in_backup, 'rb') as encrypted_file_filehandle:
            encrypted_data = encrypted_file_filehandle.read()
        # Decrypt the file contents:
        decrypted_data = google_iphone_dataprotection.AESdecryptCBC(encrypted_data, inner_key)
        # Remove any padding introduced by the CBC encryption:
        return google_iphone_dataprotection.removePadding(decrypted_data)

    def test_decryption(self):
        """Validate that the backup can be decrypted successfully."""
        # Ensure that we've initialised everything:
        if self._temp_manifest_db_conn is None:
            self._decrypt_manifest_db_file()
        return True

    def save_manifest_file(self, output_filename):
        """Save a permanent copy of the decrypted Manifest SQLite database."""
        # Ensure that we've decrypted the manifest file:
        self._decrypt_manifest_db_file()
        # Copy the decrypted file to the output:
        output_directory = os.path.dirname(output_filename)
        if output_directory:
            os.makedirs(output_directory, exist_ok=True)
        shutil.copy(self._temp_decrypted_manifest_db_path, output_filename)

    def extract_file_as_bytes(self, relative_path):
        """
        Decrypt a single named file and return the bytes.

        :param relative_path:
            The iOS 'relativePath' of the file to be decrypted. Common relative paths are provided by the
            'RelativePath' class, otherwise these can be found by opening the decrypted Manifest.db file
            and examining the Files table.
        :return: decrypted bytes of the file.
        """
        # Ensure that we've initialised everything:
        if self._temp_manifest_db_conn is None:
            self._decrypt_manifest_db_file()
        # Use Manifest.db to find the on-disk filename and file metadata, including the keys, for the file.
        # The metadata is contained in the 'file' column, as a binary PList file:
        try:
            cur = self._temp_manifest_db_conn.cursor()
            query = """
                SELECT fileID, file
                FROM Files
                WHERE relativePath = ?
                ORDER BY domain, relativePath
                LIMIT 1;
            """
            cur.execute(query, (relative_path,))
            result = cur.fetchone()
        except sqlite3.Error:
            return None
        file_id, file_bplist = result
        # Decrypt the requested file:
        return self._decrypt_inner_file(file_id=file_id, file_bplist=file_bplist)

    def extract_file(self, *, relative_path, output_filename):
        """
        Decrypt a single named file and save it to disk.

        This is a helper method and is exactly equivalent to extract_file_as_bytes(...) and then
        writing that data to a file.

        :param relative_path:
            The iOS 'relativePath' of the file to be decrypted. Common relative paths are provided by the
            'RelativePath' class, otherwise these can be found by opening the decrypted Manifest.db file
            and examining the Files table.
        :param output_filename:
            The filename to write the decrypted file contents to.
        """
        # Get the decrypted bytes of the requested file:
        decrypted_data = self.extract_file_as_bytes(relative_path)
        # Output them to disk:
        output_directory = os.path.dirname(output_filename)
        if output_directory:
            os.makedirs(output_directory, exist_ok=True)
        if decrypted_data is not None:
            with open(output_filename, 'wb') as outfile:
                outfile.write(decrypted_data)

    def extract_files(self, *, relative_paths_like, output_folder):
        """
        Decrypt files matching a relative path query and output them to a folder.

        This method is not really designed to match very loose relative paths like '%' or '%.jpg'.
        Since the folder structure is not preserved, files may be overwritten and/or unclear in origin.
        Use very generic relative path matching at your own risk.

        :param relative_paths_like:
            An iOS 'relativePath' of the files to be decrypted, containing '%' or '_' SQL LIKE wildcards.
            Common relative path wildcards are provided by the 'RelativePathsLike' class, otherwise these can be found
            by opening the decrypted Manifest.db file and examining the Files table.
        :param output_folder:
            The folder to write output files into. Files will be named with their internal iOS filenames and will
            overwrite anything in the output folder with that name.
        """
        # Ensure that we've initialised everything:
        if self._temp_manifest_db_conn is None:
            self._decrypt_manifest_db_file()
        # Use Manifest.db to find the on-disk filename(s) and file metadata, including the keys, for the file(s).
        # The metadata is contained in the 'file' column, as a binary PList file; the filename in 'relativePath':
        try:
            cur = self._temp_manifest_db_conn.cursor()
            query = """
                SELECT fileID, relativePath, file
                FROM Files
                WHERE relativePath LIKE ?
                ORDER BY domain, relativePath;
            """
            cur.execute(query, (relative_paths_like,))
            results = cur.fetchall()
        except sqlite3.Error:
            return None
        # Ensure output destination exists then loop through matches:
        os.makedirs(output_folder, exist_ok=True)
        for file_id, matched_relative_path, file_bplist in results:
            filename = os.path.basename(matched_relative_path)
            output_path = os.path.join(output_folder, filename)
            # Decrypt the file:
            decrypted_data = self._decrypt_inner_file(file_id=file_id, file_bplist=file_bplist)
            # Output to disk:
            if decrypted_data is not None:
                with open(output_path, 'wb') as outfile:
                    outfile.write(decrypted_data)
