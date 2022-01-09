from PyQt5 import QtWidgets, QtCore, QtGui
from DeLocaleManager import DeLocaleManager
from ui.DeSettingsLayout import DeSettingsLayout
from ui.DeSettingsQuitDialogLayout import DeSettingsQuitDialogLayout
from DeSettingsManager import DeSettingsManager


class DeSetingsUIController(QtWidgets.QWidget, DeSettingsLayout):
    def __init__(self, locale: list, settings_manager: DeSettingsManager, locale_manager: DeLocaleManager):
        self.strings = locale
        self.settings_manager = settings_manager
        self.locale_manager = locale_manager
        self.restart_required = False
        self.changes = dict()

        super().__init__()
        self.setWindowModality(QtCore.Qt.ApplicationModal)

        # Setup UI
        self.set_locale(locale)
        self.setupUi(self)

        self.setup_tabs()
        self.bind_buttons()

        self.show()

    def bind_buttons(self):
        """ Bind buttons to their functions"""

        self.cancel_button.clicked.connect(self.close)
        self.save_button.clicked.connect(self.save_changes)

    def save_changes(self):
        """ Save changes to settings_manager"""

        # Show message if restart is required
        if self.restart_required:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Information)
            msg.setWindowIcon(QtGui.QIcon('./assets/icon24'))
            msg.setText(self.strings["restart_required"])
            msg.setWindowTitle(self.strings["restart_required_title"])
            _ = msg.exec_()  # idk why, but that's how it works

        # Store every change
        for key in self.changes.keys():
            match key:
                case "locale":
                    self.settings_manager.update_locale(self.changes[key])

        # Clear changes list and close the menu
        self.changes = None
        self.close()

    def setup_tabs(self):
        """ Setup tabs in tabWidget"""

        # Setup "General" tab
        locales = self.locale_manager.get_avaliable_locales()
        for locale in locales:
            self.lang_select_box.addItem(locale[1])
            self.lang_select_box.setItemData(locales.index(locale), locale[0])
        self.lang_select_box.setCurrentIndex(
            locales.index(self.locale_manager.get_current_locale()))
        self.lang_select_box.currentIndexChanged.connect(self.change_language)

        # Setup "About" tab
        pixmap = QtGui.QPixmap(f"./assets/icon2310.png", ).scaled(
            150, 150, aspectRatioMode=1, transformMode=QtCore.Qt.SmoothTransformation)
        self.logo_label.setPixmap(pixmap)

    def change_language(self, index):
        self.changes["locale"] = self.lang_select_box.itemData(index)
        self.restart_required = True

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        # If any changes were made
        if self.changes:
            self.quit_dialog = DeSettingsQuitDialogLayout(self,
                                                          self.strings["quit_dialog"])
            self.quit_dialog.setupUi(self.quit_dialog)
            # If user wants to save changes
            if self.quit_dialog.exec():
                self.save_changes()
            event.accept()
