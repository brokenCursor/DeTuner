# -*- coding: utf-8 -*-
import os
import plistlib


class DeBackup:

    def __init__(self, path_to_backup):
        self.__path = path_to_backup
        if os.path.isfile(self.__path + '/Info.plist'):
            with open(self.__path + '/Info.plist', 'rb') as f:
                try:
                    self.__info = plistlib.load(f)
                except Exception:
                    raise InvalidBackupException("Invalid Info.plist file!")
        else:
            raise InvalidBackupException("No Info.plist file found!")

        if os.path.isfile(self.__path + '/Manifest.plist'):
            with open(self.__path + '/Manifest.plist', 'rb') as f:
                try:
                    self.__manifest = plistlib.load(f, fmt=plistlib.FMT_BINARY)
                except Exception:
                    raise InvalidBackupException(
                        "Invalid Manifest.plist file!")
        else:
            raise InvalidBackupException("No Manifest.plist file found!")

        if not os.path.isfile(self.__path + '/Manifest.db'):
            raise InvalidBackupException("No Manifest.db file!")

    def get_path(self) -> str:
        return self.__path

    def is_encrypted(self) -> bool:
        return self.__manifest['IsEncrypted']

    def is_passcode_set(self) -> bool:
        return self.__manifest['WasPasscodeSet']

    def build_version(self) -> str:
        return self.__info['Build Version']

    def device_name(self) -> str:
        return self.__info['Device Name'].strip()

    def display_name(self) -> str:
        return self.__info['Display Name']

    def guid(self) -> str:
        return self.__info['GUID']

    def iccid(self) -> str:
        return self.__info['ICCID']

    def imei(self) -> str:
        return self.__info['IMEI']

    def last_backup_date(self) -> str:
        return self.__info['Last Backup Date'].strftime("%d-%m-%Y")

    def product_name(self) -> str:
        return self.__info['Product Name']

    def product_type(self) -> str:
        return self.__info['Product Type']

    def ios_version(self) -> str:
        return self.__info['Product Version']

    def backup_id(self) -> str:
        return self.__info['Target Identifier']

    def serial_number(self) -> str:
        return self.__info['Serial Number']

    def itunes_version(self) -> str:
        return self.__info['iTunes Version']

    def __str__(self) -> str:
        return self.backup_id()

    def __repr__(self) -> str:
        return self.__str__()


class InvalidBackupException(Exception):
    ''' Raised when backup structure and/or data is invalid '''

    def __init__(self, message) -> None:
        super().__init__(message)
