from PyQt5 import QtCore, QtGui, QtWidgets


class DeSettingsLayout(object):
    def set_locale(self, locale):
        self.locale = locale

    def setupUi(self, settings_window):
        settings_window.setObjectName("settings_window")
        settings_window.resize(490, 331)
        settings_window.setFocusPolicy(QtCore.Qt.StrongFocus)

        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            settings_window.sizePolicy().hasHeightForWidth())

        settings_window.setSizePolicy(sizePolicy)
        settings_window.setMinimumSize(QtCore.QSize(490, 331))
        settings_window.setMaximumSize(QtCore.QSize(331, 490))
        
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("./assets/icon24.png"),
                       QtGui.QIcon.Normal, QtGui.QIcon.Off)
        settings_window.setWindowIcon(icon)

        self.gridLayoutWidget = QtWidgets.QWidget(settings_window)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(0, 0, 491, 301))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.tabWidget = QtWidgets.QTabWidget(self.gridLayoutWidget)
        self.tabWidget.setObjectName("tabWidget")
        self.general = QtWidgets.QWidget()
        self.general.setObjectName("general")
        self.label = QtWidgets.QLabel(self.general)
        self.label.setGeometry(QtCore.QRect(10, 10, 61, 16))
        self.label.setObjectName("label")
        self.lang_select_box = QtWidgets.QComboBox(self.general)
        self.lang_select_box.setGeometry(QtCore.QRect(10, 30, 141, 22))
        self.lang_select_box.setEditable(False)
        self.lang_select_box.setObjectName("comboBox")
        self.tabWidget.addTab(self.general, "")
        self.about = QtWidgets.QWidget()
        self.about.setObjectName("about")
        self.label_3 = QtWidgets.QLabel(self.about)
        self.label_3.setGeometry(QtCore.QRect(190, 160, 89, 41))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setTextFormat(QtCore.Qt.MarkdownText)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.logo_label = QtWidgets.QLabel(self.about)
        self.logo_label.setGeometry(QtCore.QRect(160, 10, 150, 150))
        self.logo_label.setTextFormat(QtCore.Qt.MarkdownText)
        self.logo_label.setObjectName("label_2")
        self.label_4 = QtWidgets.QLabel(self.about)
        self.label_4.setGeometry(QtCore.QRect(190, 200, 91, 20))
        self.label_4.setObjectName("label_4")
        self.label_5 = QtWidgets.QLabel(self.about)
        self.label_5.setGeometry(QtCore.QRect(170, 230, 131, 16))
        self.label_5.setAlignment(QtCore.Qt.AlignCenter)
        self.label_5.setObjectName("label_5")
        self.tabWidget.addTab(self.about, "")
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)
        self.save_button = QtWidgets.QPushButton(settings_window)
        self.save_button.setGeometry(QtCore.QRect(410, 305, 75, 23))
        self.save_button.setDefault(True)
        self.save_button.setObjectName("save_button")

        self.cancel_button = QtWidgets.QPushButton(settings_window)
        self.cancel_button.setGeometry(QtCore.QRect(320, 305, 75, 23))
        self.cancel_button.setObjectName("cancel_button")

        #self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.retranslateUi(settings_window)
        self.tabWidget.setCurrentIndex(0)

    def retranslateUi(self, settings_window):
        _translate = QtCore.QCoreApplication.translate
        settings_window.setWindowTitle(
            _translate("settings_window", self.locale["title"]))
        self.label.setText(_translate("settings_window", self.locale["language_label"]))
        self.tabWidget.setTabText(self.tabWidget.indexOf(
            self.general), _translate("settings_window", self.locale["general_settings"]))
        self.label_3.setText(_translate("settings_window", "**DeTuner**"))
        self.logo_label.setText(_translate("settings_window", self.locale["image_not_found"]))
        self.label_4.setText(_translate("settings_window", self.locale["version"]))
        self.label_5.setText(_translate("settings_window", self.locale["author"]))
        self.tabWidget.setTabText(self.tabWidget.indexOf(
            self.about), _translate("settings_window", self.locale["about"]))
        self.save_button.setText(_translate("settings_window", self.locale["save_button"]))
        self.cancel_button.setText(_translate("settings_window", self.locale["cancel_button"]))
