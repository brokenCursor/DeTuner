import sys
import os
from DeWorker import DeWorker
from ui.DeMainUILayout import DeMainUILayout
from DeBackup import DeBackup, InvalidBackupException
from DeBackupHandler import DeBackupHandler
from PyQt5.QtWidgets import QApplication, QLineEdit, QMainWindow, QFileDialog, QMessageBox, QListWidgetItem, QInputDialog, QProgressBar
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QThreadPool
from easter_egg import *


class DeMainUI(QMainWindow, DeMainUILayout):

    def __init__(self):
        # Setup UI
        super().__init__()
        self.setupUi(self)

        # Insert progress_bar into status_bar
        self.progress_bar = QProgressBar()
        self.status_bar.addPermanentWidget(self.progress_bar)
        self.progress_bar.hide()
        self.bind_buttons()

        # Define important variables
        self.__backups = []
        self.__progress = {}

        self.import_default_backups()

        if not self.__backups:
            self.show_warning("No backups found!")
        self.__threadpool = QThreadPool().globalInstance()

    def bind_buttons(self):
        self.add_backup_button.clicked.connect(self.add_external_backup)
        self.backup_table.itemSelectionChanged.connect(
            self.update_selected_backup_info)
        self.start_button.clicked.connect(self.start_extraction)

    def import_default_backups(self):
        backup_paths = self.get_backup_list()
        if backup_paths:
            for path in backup_paths:
                self.import_backup(path)
        self.update_table()

    def update_selected_backup_info(self):
        # Get backup from list by index
        backup = self.get_selected_backup()

        # Fill in device info
        self.device_name_label.setText('**' + backup.device_name() + '**')
        self.model_label.setText("Model: " + backup.product_name())
        self.ios_version_label.setText(
            "iOS Version: " + backup.ios_version())
        self.serial_number_label.setText("S/N: " + backup.serial_number())
        self.imei_label.setText("IMEI: " + backup.imei())
        icon_filename = backup.product_type().replace(',', '')
        pixmap = QPixmap(f"./assets/device_icons/{icon_filename}", ).scaled(
            80, 130, aspectRatioMode=1)
        self.device_image.setPixmap(pixmap)

        # Fill in backup info
        self.backup_date_label.setText(
            "Date: " + backup.last_backup_date())
        self.backup_itunes_ver_label.setText(
            "iTunes version: " + backup.itunes_version())
        self.backup_is_encrypted_label.setText("Encrypted: " +
                                               str(backup.is_encrypted()))
        self.backup_passcode_set_label.setText("Passcode set: " +
                                               str(backup.is_passcode_set()))

        # Enable UI elements
        self.start_button.setEnabled(True)
        self.set_checkboxes_enabled(True)

    def set_checkboxes_enabled(self, enable: bool = True):
        ''' Enable/disable checkboxes '''

        self.sms_checkbox.setEnabled(enable)
        self.notes_checkbox.setEnabled(enable)
        self.calendar_checkbox.setEnabled(enable)
        self.contacts_checkbox.setEnabled(enable)
        self.voicemail_checkbox.setEnabled(enable)
        self.voice_memos_checkbox.setEnabled(enable)
        self.camera_roll_checkbox.setEnabled(enable)
        self.call_history_checkbox.setEnabled(enable)

    def set_ui_enabled(self, enabled: True):
        self.set_checkboxes_enabled(enabled)
        self.start_button.setEnabled(enabled)
        self.add_backup_button.setEnabled(enabled)
        self.backup_table.setEnabled(enabled)
        self.menubar.setEnabled(enabled)

    def get_checkboxes_states(self) -> dict:
        states = {
            'call_history': self.call_history_checkbox.isChecked(),
            'calendar': self.calendar_checkbox.isChecked(),
            'camera_roll': self.camera_roll_checkbox.isChecked(),
            'contacts': self.contacts_checkbox.isChecked(),
            'notes': self.notes_checkbox.isChecked(),
            'sms': self.sms_checkbox.isChecked(),
            'voice_memos': self.voice_memos_checkbox.isChecked(),
            'voicemail': self.voicemail_checkbox.isChecked()
        }
        return states

    def get_backup_list(self) -> list | None:
        path = os.path.expanduser(
            '~') + r'\AppData\Roaming\Apple Computer\MobileSync\Backup'
        if os.path.exists(path):
            backup_paths = [path + '\\' + b for b in os.listdir(path)]
            return backup_paths
        else:
            return None

    def import_backup(self, path: str):
        ''' Import backup from path and add to __backups '''

        try:
            if path in [b.get_path() for b in self.__backups]:
                self.show_info("This backup has already been added")
            else:
                self.__backups.append(DeBackup(path))
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
            item_text = b.display_name() + '\n' + b.last_backup_date()
            icon_filename = b.product_type().replace(',', '')
            item_icon = QIcon(f"./assets/device_icons/{icon_filename}")
            self.backup_table.addItem(
                QListWidgetItem(item_icon, item_text))

    def add_external_backup(self):
        ''' Add backup from user-provided location '''

        path = self.get_dir_path("Select backup directory")
        if path:
            try:
                self.import_backup(path)
            except Exception as e:
                self.show_error("Unable to import external backup", details=e)
            else:
                self.update_table()
        else:
            self.show_warning("No backup selected!")

    def get_dir_path(self, title) -> str | None:
        ''' Return path to a directory '''

        path = QFileDialog.getExistingDirectory(
            self, title)
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
        msg.setWindowIcon(QIcon('./assets/icon24'))
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
        ''' A warning wrapper for show_message function'''

        return self.show_message(message, QMessageBox.Warning,
                                 'Warning', **kwargs)

    def show_error(self, message, **kwargs) -> None | str:
        ''' An error wrapper for show_message function'''

        return self.show_message(message, QMessageBox.Critical,
                                 'Error!', **kwargs)

    def show_info(self, message, **kwargs) -> None | str:
        ''' An info wrapper for show_message function'''

        return self.show_message(message, QMessageBox.Information,
                                 'Info', **kwargs)

    def get_selected_backup(self) -> DeBackup | None:
        ''' Get selected backup '''

        index = self.backup_table.currentRow()
        return self.__backups[index] if index != -1 else None

    def get_passcode(self) -> tuple:
        dialog = QInputDialog()
        dialog.setTextEchoMode(QLineEdit.EchoMode.Password)
        passcode, result = dialog.getText(
            self, 'Enter passcode',
            'This backup requires passcode for extraction',
            QLineEdit.EchoMode.Password)
        return passcode, result

    def easter_egg(self, passcode):
        pass

    def handle_export_error(self, *args, **kwargs):
        pass

    def get_worker_progress(self, data):
        name, progress = data[0], data[1]
        if name in self.__progress.keys():
            self.__progress[name] += progress - self.__progress[name]
        else:
            self.__progress[name] = progress
        print(sum([item[1] for item in self.__progress.items()]) //
              self.__thread_count)
        self.progress_bar.setValue(
            sum([item[1] for item in self.__progress.items()]) // self.__thread_count)

    def finish_extraction(self, force: bool = False):
        if not self.__threadpool.activeThreadCount() or force:
            del self.__handler
            self.progress_bar.reset()
            self.progress_bar.hide()
            self.show_info("Extraction completed")
            self.set_ui_enabled(True)

    def start_extraction(self):
        # Get backup from table
        backup = self.get_selected_backup()
        if not backup:
            self.show_warning("No backup selected!")
            return

        # Get passcode
        if backup.is_passcode_set():
            # self.statusbar
            while True:
                passcode, result = self.get_passcode()
                if not result:
                    self.show_info('Extraction canceled')
                    return
                elif passcode == '':
                    self.show_warning('Empty passcode provided!')
                else:
                    break
            self.easter_egg(passcode)

        # Get output directory
        output_dir = self.get_dir_path("Select output directory")
        if not output_dir:
            self.show_info('Extraction canceled')
            return

        # Disable UI
        self.set_ui_enabled(False)

        # Extract data
        self.progress_bar.show()
        settings = self.get_checkboxes_states()
        self.__handler = DeBackupHandler(backup, output_dir)
        if backup.is_encrypted():
            decryption_result = None

            def get_decryption_result(result: bool):
                nonlocal decryption_result
                decryption_result = result

            worker = DeWorker(self.__handler.decrypt, passcode)
            worker.signals.error.connect(self.handle_export_error)
            worker.signals.result.connect(get_decryption_result)

            self.__threadpool.start(worker)

            # Yes, that's not how it supposed to be done, but it works
            while self.__threadpool.activeThreadCount():
                QApplication.processEvents()

            print(decryption_result)
            if not decryption_result:
                self.show_error(
                    "Unable to decrypt backup: incorrect password?")
                self.finish_extraction(force=True)
                return
        self.__thread_count = sum([item[1] * 1 for item in settings.items()])

        def start_thread(func):
            try:
                worker = DeWorker(func)
                worker.signals.error.connect(self.handle_export_error)
                worker.signals.progress.connect(self.get_worker_progress)
                worker.signals.finished.connect(self.finish_extraction)
                self.__threadpool.start(worker)
            except Exception as e:
                self.show_error(
                    "Critical error while starting thread", details=e)

        try:
            if settings['camera_roll']:
                start_thread(self.__handler.extract_camera_roll)
            if settings['voice_memos']:
                start_thread(self.__handler.extract_voice_memos)
            if settings['contacts']:
                start_thread(self.__handler.extract_contacts)
            if settings['calendar']:
                self.__handler.extract_calendar()
            if settings['notes']:
                start_thread(self.__handler.extract_notes)
            if settings['sms']:
                self.__handler.extract_sms_imessage()
            if settings['voicemail']:
                self.__handler.extract_voicemail()
            if settings['call_history']:
                start_thread(self.__handler.extract_call_history)
        except Exception as e:
            self.show_error(
                "Critical error while starting extraction", details=e)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = DeMainUI()
    ex.show()
    sys.exit(app.exec_())
