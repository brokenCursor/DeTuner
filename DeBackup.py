import os
import plistlib
from PyQt5 import QtCore, QtGui, QtWidgets


class DeBackup:

    def __init__(self, path_to_backup):
        self.__path = path_to_backup
        if os.path.isfile(path_to_backup + '/Info.plist'):
            with open(path_to_backup + '/Info.plist', 'rb') as f:
                try:
                    self.__info = plistlib.load(f)
                except Exception:
                    raise InvalidBackupException("Invalid Info.plist file!")
        else:
            raise InvalidBackupException("No Info.plist file found!")

        if os.path.isfile(path_to_backup + '/Manifest.plist'):
            with open(path_to_backup + '/Manifest.plist', 'rb') as f:
                try:
                    self.__manifest = plistlib.load(f, fmt=plistlib.FMT_BINARY)
                except Exception:
                    raise InvalidBackupException(
                        "Invalid Manifest.plist file!")
        else:
            raise InvalidBackupException("No Manifest.plist file found!")

    def get_is_encrypted(self) -> bool:
        return self.__manifest['IsEncrypted']

    def get_is_passcode_set(self) -> bool:
        return self.__manifest['WasPasscodeSet']

    def get_build_version(self) -> str:
        return self.__info['Build Version']

    def get_device_name(self) -> str:
        return self.__info['Device Name']

    def get_display_name(self) -> str:
        return self.__info['Display Name']

    def get_guid(self) -> str:
        return self.__info['GUID']

    def get_iccid(self) -> str:
        return self.__info['ICCID']

    def get_imei(self) -> str:
        return self.__info['IMEI']

    def get_last_backup_date(self) -> str:
        return self.__info['Last Backup Date'].strftime("%d-%m-%Y")

    def get_product_name(self) -> str:
        return self.__info['Product Name']

    def get_product_type(self) -> str:
        return self.__info['Product Type']

    def get_ios_version(self) -> str:
        return self.__info['Product Version']

    def get_backup_id(self) -> str:
        return self.__info['Target Identifier']

    def get_serial_number(self) -> str:
        return self.__info['Serial Number']

    def get_itunes_version(self) -> str:
        return self.__info['iTunes Version']

    def __str__(self) -> str:
        return self.get_backup_id()

    def __repr__(self) -> str:
        return self.__str__()


class InvalidBackupException(Exception):
    ''' Raised when backup structure and/or data is invalid '''

    def __init__(self, message) -> None:
        super().__init__(message)
