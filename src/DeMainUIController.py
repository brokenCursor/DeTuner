# -*- coding: utf-8 -*-
import sys
import os
from PyQt5 import QtCore, QtGui, QtWidgets
from DeSettingUIController import DeSetingsUIController
from DeWorker import DeWorker
from ui.DeMainUILayout import DeMainUILayout
from ui.DeQuitDialogLayout import DeQuitDialogLayout
from DeBackup import DeBackup, InvalidBackupException
from DeBackupHandler import DeBackupHandler
from DeSettingsManager import DeSettingsManager
from DeLocaleManager import DeLocaleManager
from easter_egg import *


class DeMainUIController(QtWidgets.QMainWindow, DeMainUILayout):
    ''' The (temporarely) main class of DeTuner app '''

    def __init__(self):
        # Load locale data
        self.__locale_manager = DeLocaleManager()

        # Load settings
        self.__settings_manager = DeSettingsManager()

        # Load locale strings
        system_locale = self.__locale_manager.get_system_locale()
        stored_locale = self.__settings_manager.get_locale()

        if stored_locale:
            self.__locale_manager.set_locale(stored_locale)
        else:
            if system_locale in [loc[0] for loc in
                             self.__locale_manager.get_avaliable_locales()]:
                self.__settings_manager.update_locale(system_locale)
                self.__locale_manager.set_locale(system_locale)
        
        self.locale_strings = self.__locale_manager.get_strings()

        # Setup UI
        super().__init__()
        self.set_locale(self.locale_strings["main_window"])
        self.setupUi(self)

        # Insert progress_bar into status_bar
        self.progress_bar = QtWidgets.QProgressBar()
        self.status_bar.addPermanentWidget(self.progress_bar)
        self.progress_bar.hide()

        # Bind actions and buttons
        self.bind_buttons()
        self.bind_actions()

        # Bind backup_table update signal
        self.backup_table.itemSelectionChanged.connect(
            self.update_selected_backup_info)

        # Setup backup_tables context menu
        self.backup_table.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.backup_table.addActions(
            [self.action_add_backup, self.action_delete_backup])

        # Define important variables
        self.__backups = []
        self.__progress = {}
        self.__threadpool = QtCore.QThreadPool().globalInstance()

        # Import all known backups
        self.import_default_backups()
        self.import_known_external_backups()
        if not self.__backups:
            self.show_warning(
                self.locale_strings["messages"]["no_backups_found"])

    def bind_buttons(self):
        """ Attach button's "clicked" signal to it's function """

        self.add_backup_button.clicked.connect(self.add_external_backup)
        self.start_button.clicked.connect(self.start_extraction)

    def bind_actions(self):
        """ Attach action's "triggered" signal to it's function"""

        self.action_add_backup.triggered.connect(self.add_external_backup)
        self.action_export.triggered.connect(self.start_extraction)
        self.action_exit.triggered.connect(self.close)
        self.action_delete_backup.triggered.connect(
            self.delete_selected_backup)
        self.action_settings.triggered.connect(self.open_settings_window)

    def import_default_backups(self):
        """ Import backups from default iTunes backup path"""

        backup_paths = self.get_backup_list()
        if backup_paths:
            for path in backup_paths:
                self.import_backup(path)
        self.update_table()

    def import_known_external_backups(self):
        """ Import external backups from database"""

        backup_paths = \
            self.__settings_manager.get_external_backups_paths()
        if backup_paths:
            for path in backup_paths:
                try:
                    self.import_backup(path)
                except:
                    continue
        self.update_table()

    def update_selected_backup_info(self):
        """ Update UI elements in accordance to selected backup"""

        # Get backup from list by index
        backup = self.get_selected_backup()
        if not backup:
            self.reset_backup_info()
            return

        # Fill in device info
        dev_strings = self.locale_strings["main_window"]["device_info"]
        self.device_name_label.setText('**' + backup.display_name() + '**')
        self.model_label.setText(
            dev_strings["model"] + " " + backup.product_name())
        self.ios_version_label.setText(
            dev_strings["ios_version"] + " " + backup.ios_version())
        self.serial_number_label.setText("S/N: " + backup.serial_number())
        self.imei_label.setText(dev_strings["imei"] + " " + backup.imei())
        icon_filename = backup.product_type()
        pixmap = QtGui.QPixmap(f"./assets/device_icons/{icon_filename}", ).scaled(
            80, 130, aspectRatioMode=1, transformMode=QtCore.Qt.SmoothTransformation)
        self.device_image.setPixmap(pixmap)

        # Fill in backup info
        backup_strings = self.locale_strings["main_window"]["backup_info"]
        self.backup_date_label.setText(
            backup_strings["date"] + " " + backup.last_backup_date())
        self.backup_itunes_ver_label.setText(
            backup_strings["itunes_version"] + " " + backup.itunes_version())
        self.backup_is_encrypted_label.setText(backup_strings["encrypted"] + " " +
                                               str(backup.is_encrypted()))
        self.backup_passcode_set_label.setText(backup_strings["passcode_set"] + " " +
                                               str(backup.is_passcode_set()))

        # Enable UI elements
        self.start_button.setEnabled(True)
        self.set_checkboxes_enabled(True)

    def reset_backup_info(self):
        """ Reset backup UI elements to their default states """

        # Reset device info
        dev_strings = self.locale_strings["main_window"]["device_info"]
        self.device_name_label.setText(dev_strings["device_name_label"])
        self.model_label.setText(dev_strings["model"])
        self.ios_version_label.setText(dev_strings["ios_version"])
        self.serial_number_label.setText(dev_strings["serial_number"])
        self.imei_label.setText(dev_strings["imei"])
        self.device_image.setText(dev_strings["device_image"])

        # Reset in backup info
        backup_strings = self.locale_strings["main_window"]["backup_info"]
        self.backup_date_label.setText(backup_strings["date"])
        self.backup_itunes_ver_label.setText(backup_strings["itunes_version"])
        self.backup_is_encrypted_label.setText(backup_strings["encrypted"])
        self.backup_passcode_set_label.setText(backup_strings["passcode_set"])

        # Disable UI elements
        self.set_checkboxes_enabled(False)
        self.start_button.setEnabled(False)

    def delete_selected_backup(self):
        """ Delete selected backup if selected backup is external """

        backup = self.get_selected_backup()
        if backup:  # If no backup selected
            backup_path = backup.get_path()
            if r'\AppData\Roaming\Apple Computer\MobileSync\Backup' not in backup_path:
                self.__settings_manager.delete_external_backup(backup_path)
                self.__backups.remove(backup)
                self.update_table()
            else:
                self.show_warning(
                    self.locale_strings["messages"]["unable_to_delete_default"])
        else:
            self.show_warning(
                self.locale_strings["messages"]["unable_to_delete_no_selected"])

    def set_checkboxes_enabled(self, enable: bool = True):
        """ Enable/disable checkboxes """

        self.sms_checkbox.setEnabled(enable)
        self.notes_checkbox.setEnabled(enable)
        self.calendar_checkbox.setEnabled(enable)
        self.contacts_checkbox.setEnabled(enable)
        self.voicemail_checkbox.setEnabled(enable)
        self.voice_memos_checkbox.setEnabled(enable)
        self.camera_roll_checkbox.setEnabled(enable)
        self.call_history_checkbox.setEnabled(enable)

    def set_ui_enabled(self, enabled: True):
        """ Enable/disable all UI elements"""

        self.set_checkboxes_enabled(enabled)
        self.start_button.setEnabled(enabled)
        self.add_backup_button.setEnabled(enabled)
        self.backup_table.setEnabled(enabled)
        self.menubar.setEnabled(enabled)
        self.action_add_backup.setEnabled(enabled)
        self.action_delete_backup.setEnabled(enabled)

    def get_checkboxes_states(self) -> dict:
        """ Get settings for export """

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
        """ Get list of backups in default iTunes backup directory """

        path = os.path.expanduser(
            '~') + r'\AppData\Roaming\Apple Computer\MobileSync\Backup'
        if os.path.exists(path):
            backup_paths = [path + '\\' + b for b in os.listdir(path)]
            return backup_paths
        else:
            return None

    def import_backup(self, path: str):
        ''' Import backup from path backups '''

        try:
            if path in [b.get_path() for b in self.__backups]:
                self.show_info(
                    self.locale_strings["messages"]["backup_already_added"])
            else:
                self.__backups.append(DeBackup(path))
        except InvalidBackupException as e:
            id = path.split('\\')[-1]
            self.show_error(self.locale_strings["messages"]["unable_to_import"].format(
                backup_id=id), details=str(e))
        except Exception as e:
            self.show_error(
                self.locale_strings["messages"]["unknown_import_error"], details=str(e))

    def update_table(self):
        """ Clear and fill in table with list of backups """

        self.backup_table.clear()
        for b in self.__backups:
            item_text = b.display_name() + '\n' + b.last_backup_date()
            icon_filename = b.product_type()
            item_icon = QtGui.QIcon(f"./assets/device_icons/{icon_filename}")
            self.backup_table.addItem(
                QtWidgets.QListWidgetItem(item_icon, item_text))

    def add_external_backup(self):
        ''' Add backup from user-provided location '''

        path = self.get_dir_path(
            self.locale_strings["get_dir_path"]["select_backup_dir"])
        if path:
            try:
                self.import_backup(path)
            except Exception as e:
                self.show_error(
                    self.locale_strings["messages"]["unable_to_import_external"], details=e)
            else:
                self.__settings_manager.add_external_backup(path)
                self.update_table()
        else:
            self.show_warning(
                self.locale_strings["messages"]["no_backup_selected"])

    def get_dir_path(self, title, start: str = '.') -> str | None:
        ''' Return path to a user-selected directory '''

        path = QtWidgets.QFileDialog.getExistingDirectory(
            self, title, start)
        return path if path else None

    def show_message(self, message: str = "An unknown error ocurred!",
                     icon: QtWidgets.QMessageBox.Icon = QtWidgets.QMessageBox.Critical,
                     title: str = 'Unknown Error', **kwargs) -> str | None:
        ''' Show a QMessageBox with provided parameters

        args:
            message (str): A string to show as message body.
            Default: \'An An unknown error ocurred!\'

            icon (QMessageBox.Icon): An icon to display in message box.
            Default: \'Critical\'

            title (str): Window title. 
            Deafult: \'Unknown Error\'

            buttons (QMessageBox.StandartButtons): an object with buttons to be shown
            Default: QMessageBox.Ok

            details (str): a detailed description for message
            Default: None'''

        # Create result hook
        func_result = None

        def result_hook(i):
            global func_result
            func_result = i.text()
        # Setup QMessageBox
        msg = QtWidgets.QMessageBox()
        msg.setIcon(icon)
        msg.setWindowIcon(QtGui.QIcon('./assets/icon24'))
        msg.setText(message)
        if 'details' in kwargs:
            msg.setDetailedText(kwargs['details'])
        msg.setWindowTitle(title)
        if 'button' in kwargs:
            msg.setStandardButtons(kwargs['buttons'])
        else:
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.buttonClicked.connect(result_hook)

        # Show QMessageBox
        _ = msg.exec_()  # idk why, but that's how it works

        return func_result  # TODO: fix returning of clicked button

    def show_warning(self, message, **kwargs) -> None | str:
        ''' A warning wrapper for show_message function'''

        return self.show_message(message, QtWidgets.QMessageBox.Warning,
                                 self.locale_strings["messages"]["codes"]["warning"],
                                 **kwargs)

    def show_error(self, message, **kwargs) -> None | str:
        ''' An error wrapper for show_message function'''

        return self.show_message(message, QtWidgets.QMessageBox.Critical,
                                 self.locale_strings["messages"]["codes"]["error"],
                                 **kwargs)

    def show_info(self, message, **kwargs) -> None | str:
        ''' An info wrapper for show_message function'''

        return self.show_message(message, QtWidgets.QMessageBox.Information,
                                 self.locale_strings["messages"]["codes"]["info"],
                                 **kwargs)

    def get_selected_backup(self) -> DeBackup | None:
        ''' Get selected backup '''

        index = self.backup_table.currentRow()
        self.backup_table.setCurrentRow(index)

        if index == -1:
            return None
        try:
            return self.__backups[index]
        except:
            return None

    def get_passcode(self) -> tuple:
        """ Show a QInputDialog for user to enter encryption passcode """
        strings = self.locale_strings["passcode_dialog"]

        dialog = QtWidgets.QInputDialog()
        dialog.setTextEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        passcode, result = dialog.getText(
            self, strings["title"], strings["body"],
            QtWidgets.QLineEdit.EchoMode.Password)
        return passcode, result

    def easter_egg(self, passcode):
        pass

    def handle_export_error(self, *args, **kwargs):
        pass

    def get_worker_progress(self, data):
        """ Get progress from worker, update progress bar """
        name, progress = data[0], data[1]
        if name in self.__progress.keys():
            self.__progress[name] += progress - self.__progress[name]
        else:
            self.__progress[name] = progress

        # Get overall progress value
        self.progress_bar.setValue(
            sum([item[1] for item in self.__progress.items()]) // self.__thread_count)

    def finish_extraction(self, force: bool = False):
        """ Worker's "finished" signal callback """
        # If last worker is done or "force" is set
        if not self.__threadpool.activeThreadCount() or force:
            del self.__handler
            self.progress_bar.reset()
            self.progress_bar.hide()
            self.show_info(
                self.locale_strings["messages"]["extraction_completed"])
            self.set_ui_enabled(True)

    def start_extraction(self):
        """ Setup and start extraction of selected backup """
        # Get backup from table
        backup = self.get_selected_backup()
        if not backup:
            self.show_warning(
                self.locale_strings["messages"]["no_backup_selected"])
            return

        # Get passcode
        if backup.is_encrypted():
            while True:
                passcode, result = self.get_passcode()
                if not result:  # If user canceled/closed window
                    self.show_info(
                        self.locale_strings["messages"]["extraction_canceled"])
                    return
                elif passcode == '':
                    self.show_warning(
                        self.locale_strings["messages"]["empty_passcode"])
                else:
                    break
            self.easter_egg(passcode)

        # Disable UI
        self.set_ui_enabled(False)

        # Extract data
        self.progress_bar.show()
        settings = self.get_checkboxes_states()
        self.__handler = DeBackupHandler(
            backup, self.locale_strings["handler"])

        # Decrypt, if backup is encrypted
        if backup.is_encrypted():
            self.status_bar.showMessage('Decrypting...')

            decryption_result = None

            # Decryption result callback
            def get_decryption_result(result: bool):
                nonlocal decryption_result
                decryption_result = result

            # Create and setup worker
            worker = DeWorker(self.__handler.decrypt, passcode)
            worker.signals.error.connect(self.handle_export_error)
            worker.signals.result.connect(get_decryption_result)

            self.__threadpool.start(worker)

            # Yes, that's not how it supposed to be done, but it works
            while self.__threadpool.activeThreadCount():
                QtWidgets.QApplication.processEvents()

            if not decryption_result:
                self.show_error(
                    self.locale_strings["messages"]["unable_to_decrypt"])
                self.finish_extraction(force=True)
                return

        # Get output directory
        last_output_dir = self.__settings_manager.get_last_export_path()
        output_dir = self.get_dir_path(
            self.locale_strings["get_dir_path"]["select_output_dir"],
            last_output_dir)
        if not output_dir:
            self.show_info(
                self.locale_strings["messages"]["extraction_canceled"])
            self.set_ui_enabled(True)
            return

        # Save directory to settings as last used for extraction
        self.__settings_manager.update_last_export_path(output_dir)

        self.__handler.set_output_directory(output_dir)

        # Calc thread count
        self.__thread_count = sum([item[1] * 1 for item in settings.items()])

        # Small function for starting threads
        def start_thread(func):
            try:
                worker = DeWorker(func)
                worker.signals.error.connect(self.handle_export_error)
                worker.signals.progress.connect(self.get_worker_progress)
                worker.signals.finished.connect(self.finish_extraction)
                self.__threadpool.start(worker)
            except Exception as e:
                self.show_error(
                    self.locale_strings["messages"]["thread_start_error"], details=e)

        # Start extraction threads
        self.status_bar.showMessage('Extracting...')
        try:
            if settings['camera_roll']:
                start_thread(self.__handler.extract_camera_roll)
            if settings['voice_memos']:
                start_thread(self.__handler.extract_voice_memos)
            if settings['contacts']:
                start_thread(self.__handler.extract_contacts)
            if settings['calendar']:
                start_thread(self.__handler.extract_calendar)
            if settings['notes']:
                start_thread(self.__handler.extract_notes)
            if settings['sms']:
                start_thread(self.__handler.extract_sms_imessage)
            if settings['voicemail']:
                start_thread(self.__handler.extract_voicemail)
            if settings['call_history']:
                start_thread(self.__handler.extract_call_history)
        except Exception as e:
            self.show_error(
                self.locale_strings["messages"]["extraction_start_error"], details=e)

    def open_settings_window(self):
        self.settings_window = DeSetingsUIController(
            self.locale_strings["settings_window"], self.__settings_manager, self.__locale_manager)
    
    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        self.quit_dialog = DeQuitDialogLayout(self,
                                              self.locale_strings["quit_dialog"])
        self.quit_dialog.setupUi(self.quit_dialog)
        if self.quit_dialog.exec():
            event.accept()
        else:
            event.ignore()
        

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = DeMainUIController()
    ex.show()
    sys.exit(app.exec_())
