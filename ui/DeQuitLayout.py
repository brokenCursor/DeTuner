# -*- coding: utf-8 -*-




from PyQt5 import QtCore, QtGui, QtWidgets


class DeQuitLayout(object):
    def setupUi(self, DeQuitLayout):
        DeQuitLayout.setObjectName("DeQuitLayout")
        DeQuitLayout.resize(171, 97)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(DeQuitLayout.sizePolicy().hasHeightForWidth())
        DeQuitLayout.setSizePolicy(sizePolicy)
        DeQuitLayout.setMinimumSize(QtCore.QSize(171, 97))
        DeQuitLayout.setMaximumSize(QtCore.QSize(171, 97))
        self.centralwidget = QtWidgets.QWidget(DeQuitLayout)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(0, 10, 161, 80))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label.setTextFormat(QtCore.Qt.MarkdownText)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.quit_button = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.quit_button.setObjectName("quit_button")
        self.horizontalLayout_3.addWidget(self.quit_button)
        self.cancel_button = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.cancel_button.setObjectName("cancel_notton")
        self.horizontalLayout_3.addWidget(self.cancel_button)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        DeQuitLayout.setCentralWidget(self.centralwidget)

        self.retranslateUi(DeQuitLayout)
        QtCore.QMetaObject.connectSlotsByName(DeQuitLayout)

    def retranslateUi(self, DeQuitLayout):
        _translate = QtCore.QCoreApplication.translate
        DeQuitLayout.setWindowTitle(_translate("DeQuitLayout", "Quit DeTuner?"))
        self.label.setText(_translate("DeQuitLayout", "# Quit DeTuner?"))
        self.quit_button.setText(_translate("DeQuitLayout", "Quit"))
        self.cancel_button.setText(_translate("DeQuitLayout", "Canccel"))
