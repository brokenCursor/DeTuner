import sys
import os
from ui.DeMainUILayout import DeMainUILayout
from DeBackup import DeBackup, InvalidBackupException
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QListWidgetItem
from PyQt5.QtGui import QIcon, QPixmap


class DeMainUI(QMainWindow, DeMainUILayout):

    __backups = []

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.bind_buttons()
        self.import_default_backups()

    def bind_buttons(self):
        self.add_backup_button.clicked.connect(self.add_external_backup)
        self.backup_table.itemSelectionChanged.connect(
            self.update_selected_backup_info)

    def import_default_backups(self):
        backup_paths = self.get_backup_list()
        for path in backup_paths:
            self.import_backup(path)
        self.update_table()

    def update_selected_backup_info(self):
        # Get backup from list by index
        index = self.backup_table.currentRow()
        backup = self.__backups[index]

        # Fill in device info
        self.device_name_label.setText('**' + backup.get_device_name() + '**')
        self.model_label.setText("Model: " + backup.get_product_name())
        self.ios_version_label.setText(
            "iOS Version: " + backup.get_ios_version())
        self.serial_number_label.setText("S/N: " + backup.get_serial_number())
        self.imei_label.setText("IMEI: " + backup.get_imei())
        icon_filename = backup.get_product_type().replace(',', '')
        pixmap = QPixmap(f"./assets/device_icons/{icon_filename}", ).scaled(
            80, 130, aspectRatioMode=1)
        self.device_image.setPixmap(pixmap)

        # Fill in backup info
        self.backup_date_label.setText(
            "Date: " + backup.get_last_backup_date())
        self.backup_itunes_ver_label.setText(
            "iTunes version: " + backup.get_itunes_version())
        self.backup_is_encrypted_label.setText("Encrypted: " +
                                               str(backup.get_is_encrypted()))
        self.backup_passcode_set_label.setText("Passcode set: " +
                                               str(backup.get_is_passcode_set()))

    def get_backup_list(self) -> list:
        path = os.path.expanduser(
            '~') + r'\AppData\Roaming\Apple Computer\MobileSync\Backup'
        backup_paths = [path + '\\' + b for b in os.listdir(path)]
        return backup_paths

    def import_backup(self, path):
        try:
            backup = DeBackup(path)
            if backup.get_backup_id() in [b.get_backup_id() for b in self.__backups]:
                self.show_info("This backup has already been added")
            else:
                self.__backups.append(backup)
        except InvalidBackupException as e:
            id = path.split('\\')[-1]
            self.show_error(
                f"Unable to import backup {id}: invalid backup", details=str(e))
        except Exception as e:
            self.show_error(
                'An unknown error ocurred during backup import', details=str(e))

    def update_table(self):
        self.backup_table.clear()
        for b in self.__backups:
            item_text = b.get_display_name() + '\n' + b.get_last_backup_date()
            icon_filename = b.get_product_type().replace(',', '')
            item_icon = QIcon(f"./assets/device_icons/{icon_filename}")
            self.backup_table.addItem(
                QListWidgetItem(item_icon, item_text))

    def add_external_backup(self):
        path = self.get_dir_path()
        if path:
            try:
                self.import_backup(path)
            except:
                self.show_error("Unable to import external backup")
            else:
                self.update_table()
        else:
            self.show_warning("No backup selected!")

    def get_dir_path(self) -> str | None:
        ''' Return path to a directory '''
        path = QFileDialog.getExistingDirectory(
            self, 'Select Backup Directory')
        return path if path else None

    def show_message(self, message: str = "An unknown error ocurred!",
                     icon: QMessageBox.Icon = QMessageBox.Critical,
                     title: str = 'Unknown Error', **kwargs) -> str | None:
        ''' Show a QMessageBox with provided parameters

        Parameters:
            message (str): A string to show as message body.
            Default: \'An An unknown error ocurred!\'

            icon (QMessageBox.Icon): An icon to display in message box.
            Default: \'Critical\'

            title (str): Window title. Deafult: \'Unknown Error\'

            buttons (QMessageBox.StandartButtons): an object with buttons to be shown
            Default: QMessageBox.Ok

            details (str): a detailed description for message
            Default: None'''

        func_result = None

        def result_hook(i):
            global func_result
            func_result = i.text()

        msg = QMessageBox()
        msg.setIcon(icon)
        # msg.setWindowIcon()
        msg.setText(message)
        if 'details' in kwargs:
            msg.setDetailedText(kwargs['details'])
        msg.setWindowTitle(title)
        if 'button' in kwargs:
            msg.setStandardButtons(kwargs['buttons'])
        else:
            msg.setStandardButtons(QMessageBox.Ok)
        msg.buttonClicked.connect(result_hook)
        _ = msg.exec_()  # idk why, but that's how it works

        return func_result  # TODO: fix returning of clicked button

    def show_warning(self, message, **kwargs) -> None | str:
        ''' A wrapper for show_message function'''
        return self.show_message(message, QMessageBox.Warning,
                                 'Warning', **kwargs)

    def show_error(self, message, **kwargs) -> None | str:
        ''' A wrapper for show_message function'''
        return self.show_message(message, QMessageBox.Critical,
                                 'Error!', **kwargs)

    def show_info(self, message, **kwargs) -> None | str:
        return self.show_message(message, QMessageBox.Information,
                                 'Info', **kwargs)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = DeMainUI()
    ex.show()
    sys.exit(app.exec_())
