import sys
import os
from ui.DeMainUILayout import DeMainUILayout
from DeBackup import DeBackup, InvalidBackupException
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QListWidgetItem
from PyQt5.QtGui import QIcon


class DeMainUI(QMainWindow, DeMainUILayout):

    __backups = []

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        backup_paths = self.get_backup_list()
        for p in backup_paths:
            self.import_backup(p)
        self.update_table()
        self.add_backup_button.clicked.connect(self.add_external_backup)

    def get_backup_list(self) -> list:
        path = os.path.expanduser(
            '~') + r'\AppData\Roaming\Apple Computer\MobileSync\Backup'
        backup_paths = [path + '\\' + b for b in os.listdir(path)]
        return backup_paths

    def import_backup(self, path):
        try:
            backup = DeBackup(path)
            if backup in self.__backups:
                print('hit')
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
            item_text = b.get_display_name() + '\n' + \
                b.get_last_backup_date()
            icon_filename = b.get_product_type().replace(',', '')
            item_icon = QIcon(f"./assets/device_icons/{icon_filename}")
            self.backup_table.addItem(
                QListWidgetItem(item_icon, item_text))

    def add_external_backup(self):
        path = self.get_dir_path()
        if not path:
            print(self.show_warning("No backup selected!"))
            return
        try:
            self.import_backup(path)
        except:
            self.show_error("Unable to import external backup")
        else:
            self.update_table()

    def get_dir_path(self) -> str | None:
        ''' Return path to a directory '''
        path = QFileDialog.getExistingDirectory(
            self, 'Select Backup Directory')
        return path if path else None

    def show_message(self, message: str = "An unknown error ocurred!",
                     icon: QMessageBox.Icon = QMessageBox.Critical,
                     title: str = 'Unknown Error',
                     buttons: QMessageBox.StandardButtons = QMessageBox.Ok,
                     details=None) -> str | None:
        ''' Show a QMessageBox with provided parameters 
        Parameters:
            message (str): A string to show as message body. 
            Default: \'An An unknown error ocurred!\' 

            icon (QMessageBox.Icon): An icon to display in message box. 
            Default: \'Critical\'

            title (str): Window title. Deafult: \'Unknown Error\'

            buttons (QMessageBox.StandartButtons): a list of buttons to be shown in a message.
            Default: QMessageBox.Ok

            details (str): a detailed description for message
            Default: None'''

        func_result = None

        def result_hook(i):
            global func_result
            func_result = i.text()

        msg = QMessageBox()
        msg.setIcon(icon)
        msg.setText(message)
        if details:
            msg.setDetailedText(details)
        msg.setWindowTitle(title)
        msg.setStandardButtons(buttons)
        msg.buttonClicked.connect(result_hook)
        _ = msg.exec_()  # idk why, but that's how it works

        return func_result  # TODO: fix returning of clicked button

    def show_warning(self, message, details=None):
        ''' A wrapper for show_message function'''
        return self.show_message(message, QMessageBox.Warning, 'Warning', details=details)

    def show_error(self, message, details=None):
        ''' A wrapper for show_message function'''
        return self.show_message(message, QMessageBox.Critical, 'Error!', details=details)

    def show_info(self, message, details) -> None:
        return self.show_message(message, QMessageBox.Information, 'Info', details=details)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = DeMainUI()
    ex.show()
    sys.exit(app.exec_())
