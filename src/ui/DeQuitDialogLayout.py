# -*- coding: utf-8 -*-


from PyQt5 import QtCore, QtGui, QtWidgets
import typing


class DeQuitDialogLayout(QtWidgets.QDialog):
    def __init__(self, parent, locale) -> None:
        super().__init__(parent=parent)
        self.strings = locale

    def setupUi(self, DeQuitDialogLayout):
        DeQuitDialogLayout.setObjectName("DeQuitDialogLayout")
        DeQuitDialogLayout.resize(201, 104)

        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            DeQuitDialogLayout.sizePolicy().hasHeightForWidth())

        DeQuitDialogLayout.setSizePolicy(sizePolicy)
        DeQuitDialogLayout.setMinimumSize(QtCore.QSize(201, 104))
        DeQuitDialogLayout.setMaximumSize(QtCore.QSize(201, 104))

        self.gridLayoutWidget = QtWidgets.QWidget(DeQuitDialogLayout)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(10, 0, 181, 91))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(self.gridLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.quit_button = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.quit_button.setAutoDefault(False)
        self.quit_button.setDefault(False)
        self.quit_button.setObjectName("quit_button")
        self.horizontalLayout_2.addWidget(self.quit_button)
        self.cancel_button = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.cancel_button.setAutoDefault(False)
        self.cancel_button.setDefault(True)
        self.cancel_button.setObjectName("cancel_button")
        self.horizontalLayout_2.addWidget(self.cancel_button)
        self.gridLayout.addLayout(self.horizontalLayout_2, 1, 0, 1, 1)

        self.quit_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.retranslateUi(DeQuitDialogLayout)
        QtCore.QMetaObject.connectSlotsByName(DeQuitDialogLayout)

    def retranslateUi(self, DeQuitDialogLayout):
        _translate = QtCore.QCoreApplication.translate
        DeQuitDialogLayout.setWindowTitle(
            _translate("DeQuitDialogLayout", self.strings["title"]))
        self.label.setText(_translate(
            "DeQuitDialogLayout", self.strings["label"]))
        self.quit_button.setText(_translate(
            "DeQuitDialogLayout", self.strings["quit_button"]))
        self.cancel_button.setText(_translate(
            "DeQuitDialogLayout", self.strings["cancel_button"]))
