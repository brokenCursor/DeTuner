# -*- coding: utf-8 -*-


from PyQt5 import QtCore, QtGui, QtWidgets


class DeMainUILayout(object):
    def set_locale(self, locale):
        self.strings = locale

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(680, 483)

        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            MainWindow.sizePolicy().hasHeightForWidth())

        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QtCore.QSize(680, 483))
        MainWindow.setMaximumSize(QtCore.QSize(680, 483))

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("./assets/icon24.png"),
                       QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.add_backup_button = QtWidgets.QPushButton(self.centralwidget)
        self.add_backup_button.setGeometry(QtCore.QRect(10, 390, 260, 41))
        self.add_backup_button.setObjectName("add_backup_button")

        self.backup_table = QtWidgets.QListWidget(self.centralwidget)
        self.backup_table.setGeometry(QtCore.QRect(10, 10, 260, 371))
        self.backup_table.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOff)
        self.backup_table.setEditTriggers(
            QtWidgets.QAbstractItemView.NoEditTriggers)
        self.backup_table.setProperty("showDropIndicator", False)
        self.backup_table.setDragDropOverwriteMode(False)
        self.backup_table.setDefaultDropAction(QtCore.Qt.IgnoreAction)
        self.backup_table.setIconSize(QtCore.QSize(56, 56))
        self.backup_table.setObjectName("backup_table")

        self.device_image = QtWidgets.QLabel(self.centralwidget)
        self.device_image.setGeometry(QtCore.QRect(290, 10, 80, 130))
        self.device_image.setAlignment(QtCore.Qt.AlignCenter)
        self.device_image.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.device_image.setObjectName("device_image")

        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(390, 10, 261, 131))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")

        self.device_info_layout = QtWidgets.QVBoxLayout(
            self.verticalLayoutWidget)
        self.device_info_layout.setContentsMargins(0, 0, 0, 0)
        self.device_info_layout.setObjectName("device_info_layout")

        self.device_name_label = QtWidgets.QLabel(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(14)

        self.device_name_label.setFont(font)
        self.device_name_label.setTextFormat(QtCore.Qt.MarkdownText)
        self.device_name_label.setTextInteractionFlags(
            QtCore.Qt.NoTextInteraction)
        self.device_name_label.setObjectName("device_name_label")
        self.device_info_layout.addWidget(self.device_name_label)
        self.model_label = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.model_label.setTextInteractionFlags(
            QtCore.Qt.TextSelectableByMouse)
        self.model_label.setObjectName("model_label")
        self.device_info_layout.addWidget(self.model_label)
        self.ios_version_label = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.ios_version_label.setTextInteractionFlags(
            QtCore.Qt.TextSelectableByMouse)
        self.ios_version_label.setObjectName("ios_version_label")
        self.device_info_layout.addWidget(self.ios_version_label)
        self.serial_number_label = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.serial_number_label.setTextInteractionFlags(
            QtCore.Qt.TextSelectableByMouse)
        self.serial_number_label.setObjectName("serial_number_label")
        self.device_info_layout.addWidget(self.serial_number_label)
        self.imei_label = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.imei_label.setTextInteractionFlags(
            QtCore.Qt.TextSelectableByMouse)
        self.imei_label.setObjectName("imei_label")
        self.device_info_layout.addWidget(self.imei_label)

        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setGeometry(QtCore.QRect(290, 150, 381, 20))
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.line_2 = QtWidgets.QFrame(self.centralwidget)
        self.line_2.setGeometry(QtCore.QRect(270, 10, 20, 421))
        self.line_2.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.line_3 = QtWidgets.QFrame(self.centralwidget)
        self.line_3.setGeometry(QtCore.QRect(460, 170, 20, 131))
        self.line_3.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_3.setObjectName("line_3")

        self.verticalLayoutWidget_2 = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget_2.setGeometry(
            QtCore.QRect(290, 200, 160, 231))
        self.verticalLayoutWidget_2.setObjectName("verticalLayoutWidget_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(
            self.verticalLayoutWidget_2)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.call_history_checkbox = QtWidgets.QCheckBox(
            self.verticalLayoutWidget_2)
        self.call_history_checkbox.setEnabled(False)
        self.call_history_checkbox.setChecked(True)
        self.call_history_checkbox.setTristate(False)
        self.call_history_checkbox.setObjectName("call_history_checkbox")
        self.verticalLayout_2.addWidget(self.call_history_checkbox)
        self.calendar_checkbox = QtWidgets.QCheckBox(
            self.verticalLayoutWidget_2)
        self.calendar_checkbox.setEnabled(False)
        self.calendar_checkbox.setChecked(True)
        self.calendar_checkbox.setObjectName("calendar_checkbox")
        self.verticalLayout_2.addWidget(self.calendar_checkbox)
        self.camera_roll_checkbox = QtWidgets.QCheckBox(
            self.verticalLayoutWidget_2)
        self.camera_roll_checkbox.setEnabled(False)
        self.camera_roll_checkbox.setChecked(True)
        self.camera_roll_checkbox.setObjectName("camera_roll_checkbox")
        self.verticalLayout_2.addWidget(self.camera_roll_checkbox)
        self.contacts_checkbox = QtWidgets.QCheckBox(
            self.verticalLayoutWidget_2)
        self.contacts_checkbox.setEnabled(False)
        self.contacts_checkbox.setChecked(True)
        self.contacts_checkbox.setObjectName("contacts_checkbox")
        self.verticalLayout_2.addWidget(self.contacts_checkbox)
        self.notes_checkbox = QtWidgets.QCheckBox(self.verticalLayoutWidget_2)
        self.notes_checkbox.setEnabled(False)
        self.notes_checkbox.setChecked(True)
        self.notes_checkbox.setObjectName("notes_checkbox")
        self.verticalLayout_2.addWidget(self.notes_checkbox)
        self.sms_checkbox = QtWidgets.QCheckBox(self.verticalLayoutWidget_2)
        self.sms_checkbox.setEnabled(False)
        self.sms_checkbox.setChecked(True)
        self.sms_checkbox.setObjectName("sms_checkbox")
        self.verticalLayout_2.addWidget(self.sms_checkbox)
        self.voice_memos_checkbox = QtWidgets.QCheckBox(
            self.verticalLayoutWidget_2)
        self.voice_memos_checkbox.setEnabled(False)
        self.voice_memos_checkbox.setChecked(True)
        self.voice_memos_checkbox.setObjectName("voice_memos_checkbox")
        self.verticalLayout_2.addWidget(self.voice_memos_checkbox)
        self.voicemail_checkbox = QtWidgets.QCheckBox(
            self.verticalLayoutWidget_2)
        self.voicemail_checkbox.setEnabled(False)
        self.voicemail_checkbox.setChecked(True)
        self.voicemail_checkbox.setObjectName("voicemail_checkbox")
        self.verticalLayout_2.addWidget(self.voicemail_checkbox)
        self.extract_label = QtWidgets.QLabel(self.centralwidget)
        self.extract_label.setGeometry(QtCore.QRect(290, 170, 158, 23))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.extract_label.setFont(font)
        self.extract_label.setTextFormat(QtCore.Qt.MarkdownText)
        self.extract_label.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.extract_label.setObjectName("extract_label")

        self.line_4 = QtWidgets.QFrame(self.centralwidget)
        self.line_4.setGeometry(QtCore.QRect(480, 300, 191, 20))
        self.line_4.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_4.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_4.setObjectName("line_4")

        self.start_button = QtWidgets.QPushButton(self.centralwidget)
        self.start_button.setEnabled(False)
        self.start_button.setGeometry(QtCore.QRect(460, 390, 211, 41))
        self.start_button.setObjectName("start_button")
        self.layoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget.setGeometry(QtCore.QRect(480, 170, 171, 131))
        self.layoutWidget.setObjectName("layoutWidget")
        self.backup_info_layout = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.backup_info_layout.setContentsMargins(0, 0, 0, 0)
        self.backup_info_layout.setObjectName("backup_info_layout")
        self.backup_info_label = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.backup_info_label.setFont(font)
        self.backup_info_label.setTextFormat(QtCore.Qt.MarkdownText)
        self.backup_info_label.setTextInteractionFlags(
            QtCore.Qt.NoTextInteraction)
        self.backup_info_label.setObjectName("backup_info_label")
        self.backup_info_layout.addWidget(self.backup_info_label)
        self.backup_date_label = QtWidgets.QLabel(self.layoutWidget)
        self.backup_date_label.setTextInteractionFlags(
            QtCore.Qt.TextSelectableByMouse)
        self.backup_date_label.setObjectName("backup_date_label")
        self.backup_info_layout.addWidget(self.backup_date_label)
        self.backup_itunes_ver_label = QtWidgets.QLabel(self.layoutWidget)
        self.backup_itunes_ver_label.setTextInteractionFlags(
            QtCore.Qt.TextSelectableByMouse)
        self.backup_itunes_ver_label.setObjectName("backup_itunes_ver_label")
        self.backup_info_layout.addWidget(self.backup_itunes_ver_label)
        self.backup_is_encrypted_label = QtWidgets.QLabel(self.layoutWidget)
        self.backup_is_encrypted_label.setTextInteractionFlags(
            QtCore.Qt.NoTextInteraction)
        self.backup_is_encrypted_label.setObjectName(
            "backup_is_encrypted_label")
        self.backup_info_layout.addWidget(self.backup_is_encrypted_label)
        self.backup_passcode_set_label = QtWidgets.QLabel(self.layoutWidget)
        self.backup_passcode_set_label.setTextInteractionFlags(
            QtCore.Qt.NoTextInteraction)
        self.backup_passcode_set_label.setObjectName(
            "backup_passcode_set_label")
        self.backup_info_layout.addWidget(self.backup_passcode_set_label)
        MainWindow.setCentralWidget(self.centralwidget)
        self.status_bar = QtWidgets.QStatusBar(MainWindow)
        self.status_bar.setSizeGripEnabled(False)
        self.status_bar.setObjectName("status_bar")
        MainWindow.setStatusBar(self.status_bar)

        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setEnabled(True)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 680, 21))
        self.menubar.setObjectName("menubar")

        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")

        self.menuWindow = QtWidgets.QMenu(self.menubar)
        self.menuWindow.setObjectName("menuWindow")

        MainWindow.setMenuBar(self.menubar)

        self.action_add_backup = QtWidgets.QAction(MainWindow)
        self.action_add_backup.setCheckable(False)
        self.action_add_backup.setObjectName("action_add_backup")

        self.action_export = QtWidgets.QAction(MainWindow)
        self.action_export.setCheckable(False)
        self.action_export.setObjectName("action_export")

        self.action_exit = QtWidgets.QAction(MainWindow)
        self.action_exit.setCheckable(False)
        self.action_exit.setObjectName("action_exit")

        self.action_settings = QtWidgets.QAction(MainWindow)
        self.action_settings.setCheckable(False)
        self.action_settings.setObjectName("action_settings")

        self.action_delete_backup = QtWidgets.QAction(MainWindow)
        self.action_delete_backup.setObjectName("action_delete_backup")

        self.menuFile.addAction(self.action_add_backup)
        self.menuFile.addAction(self.action_delete_backup)
        self.menuFile.addAction(self.action_export)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.action_settings)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.action_exit)

        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "DeTuner"))
        self.add_backup_button.setStatusTip(_translate("MainWindow",
                                                       self.strings["status_tips"]["add_backup_button"]))
        self.add_backup_button.setText(_translate(
            "MainWindow", self.strings["buttons"]["add_backup"]))
        self.backup_table.setStatusTip(_translate(
            "MainWindow", self.strings["status_tips"]["backup_table"]))

        self.device_image.setStatusTip(
            _translate("MainWindow", self.strings["status_tips"]["device_image"]))
        self.device_image.setText(_translate(
            "MainWindow", self.strings["device_info"]["device_image"]))

        self.device_name_label.setStatusTip(_translate(
            "MainWindow", self.strings["status_tips"]["device_name_label"]))
        self.device_name_label.setText(
            _translate("MainWindow", self.strings["device_info"]["device_name_label"]))

        self.model_label.setStatusTip(_translate(
            "MainWindow", self.strings["status_tips"]["model_label"]))
        self.model_label.setText(_translate(
            "MainWindow", self.strings["device_info"]["model"]))

        self.ios_version_label.setStatusTip(
            _translate("MainWindow", self.strings["status_tips"]["ios_version_label"]))
        self.ios_version_label.setText(
            _translate("MainWindow", self.strings["device_info"]["ios_version"]))

        self.serial_number_label.setStatusTip(
            _translate("MainWindow", self.strings["status_tips"]["serial_number_label"]))
        self.serial_number_label.setText(
            _translate("MainWindow", self.strings["device_info"]["serial_number"]))

        self.imei_label.setStatusTip(_translate(
            "MainWindow", self.strings["status_tips"]["imei_label"]))
        self.imei_label.setText(_translate(
            "MainWindow", self.strings["device_info"]["imei"]))

        self.call_history_checkbox.setStatusTip(
            _translate("MainWindow", self.strings["status_tips"]["call_history_checkbox"]))
        self.call_history_checkbox.setText(
            _translate("MainWindow", self.strings["extraction_settings"]["call_history"]))

        self.calendar_checkbox.setStatusTip(
            _translate("MainWindow", self.strings["status_tips"]["calendar_checkbox"]))
        self.calendar_checkbox.setText(_translate(
            "MainWindow", self.strings["extraction_settings"]["calendar"]))

        self.camera_roll_checkbox.setStatusTip(
            _translate("MainWindow", self.strings["status_tips"]["camera_roll_checkbox"]))
        self.camera_roll_checkbox.setText(
            _translate("MainWindow", self.strings["extraction_settings"]["camera_roll"]))

        self.contacts_checkbox.setStatusTip(
            _translate("MainWindow", self.strings["status_tips"]["contacts_checkbox"]))
        self.contacts_checkbox.setText(_translate(
            "MainWindow", self.strings["extraction_settings"]["contacts"]))

        self.notes_checkbox.setStatusTip(
            _translate("MainWindow", self.strings["status_tips"]["notes_checkbox"]))
        self.notes_checkbox.setText(_translate(
            "MainWindow", self.strings["extraction_settings"]["notes"]))

        self.sms_checkbox.setStatusTip(_translate(
            "MainWindow", self.strings["status_tips"]["sms_checkbox"]))
        self.sms_checkbox.setText(_translate(
            "MainWindow", self.strings["extraction_settings"]["sms"]))

        self.voice_memos_checkbox.setStatusTip(
            _translate("MainWindow", self.strings["status_tips"]["voice_memos_checkbox"]))
        self.voice_memos_checkbox.setText(
            _translate("MainWindow", self.strings["extraction_settings"]["voice_memos"]))

        self.voicemail_checkbox.setStatusTip(
            _translate("MainWindow", self.strings["status_tips"]["voicemail_checkbox"]))
        self.voicemail_checkbox.setText(
            _translate("MainWindow", self.strings["extraction_settings"]["voicemail"]))

        self.extract_label.setText(_translate(
            "MainWindow", self.strings["extraction_settings"]["extract"]))

        self.start_button.setStatusTip(
            _translate("MainWindow", self.strings["status_tips"]["start_button"]))
        self.start_button.setText(_translate(
            "MainWindow", self.strings["buttons"]["extract"]))

        self.backup_info_label.setText(
            _translate("MainWindow", self.strings["backup_info"]["backup_info"]))

        self.backup_date_label.setStatusTip(
            _translate("MainWindow", self.strings["status_tips"]["backup_date_label"]))
        self.backup_date_label.setText(_translate(
            "MainWindow", self.strings["backup_info"]["date"]))

        self.backup_itunes_ver_label.setStatusTip(
            _translate("MainWindow", self.strings["status_tips"]["backup_itunes_ver_label"]))
        self.backup_itunes_ver_label.setText(
            _translate("MainWindow", self.strings["backup_info"]["itunes_version"]))

        self.backup_is_encrypted_label.setStatusTip(
            _translate("MainWindow", self.strings["status_tips"]["backup_is_encrypted_label"]))
        self.backup_is_encrypted_label.setText(
            _translate("MainWindow", self.strings["backup_info"]["encrypted"]))

        self.backup_passcode_set_label.setStatusTip(
            _translate("MainWindow", self.strings["status_tips"]["backup_passcode_set_label"]))
        self.backup_passcode_set_label.setText(
            _translate("MainWindow", self.strings["backup_info"]["passcode_set"]))

        self.menuFile.setTitle(_translate(
            "MainWindow", self.strings["menubar"]["file"]))

        self.action_add_backup.setText(_translate(
            "MainWindow", self.strings["actions"]["add_backup"]))
        self.action_add_backup.setStatusTip(_translate(
            "MainWindow", self.strings["status_tips"]["action_add_backup"]))
        self.action_add_backup.setShortcut(_translate("MainWindow", "Ctrl+I"))

        self.action_export.setText(_translate(
            "MainWindow", self.strings["actions"]["extract"]))
        self.action_export.setStatusTip(
            _translate("MainWindow", self.strings["status_tips"]["action_export"]))
        self.action_export.setShortcut(_translate("MainWindow", "Ctrl+E"))

        self.action_exit.setText(_translate(
            "MainWindow", self.strings["actions"]["exit"]))
        self.action_exit.setStatusTip(_translate(
            "MainWindow", self.strings["status_tips"]["action_exit"]))

        self.action_delete_backup.setText(
            _translate("MainWindow", self.strings["actions"]["delete_backup"]))
        self.action_delete_backup.setStatusTip(_translate(
            "MainWindow", self.strings["status_tips"]["action_delete_backup"]))
        self.action_delete_backup.setShortcut(_translate("MainWindow", "Del"))

        self.action_settings.setText(_translate(
            "MainWindow", self.strings["actions"]["settings"]))
        self.action_settings.setStatusTip(_translate("MainWindow",
                                                     self.strings["status_tips"]["action_settings"]))
