from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_UpdateDialog(object):
    def setupUi(self, UpdateDialog):
        UpdateDialog.setObjectName("UpdateDialog")
        UpdateDialog.resize(512, 320)
        self.layoutMain = QtWidgets.QVBoxLayout(UpdateDialog)
        self.layoutMain.setContentsMargins(0, 0, 0, 0)
        self.layoutMain.setSpacing(0)
        self.layoutMain.setObjectName("layoutMain")
        self.frameDialog = QtWidgets.QFrame(parent=UpdateDialog)
        self.frameDialog.setMinimumSize(QtCore.QSize(512, 320))
        self.frameDialog.setStyleSheet("QFrame#frameDialog {\n"
"    background-color: rgb(245, 249, 254);\n"
"    border-radius: 25px;\n"
"}")
        self.frameDialog.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frameDialog.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frameDialog.setObjectName("frameDialog")
        self.layoutDialog = QtWidgets.QHBoxLayout(self.frameDialog)
        self.layoutDialog.setContentsMargins(0, 0, 0, 0)
        self.layoutDialog.setSpacing(12)
        self.layoutDialog.setObjectName("layoutDialog")
        self.layoutContent = QtWidgets.QVBoxLayout()
        self.layoutContent.setContentsMargins(9, 9, 9, 9)
        self.layoutContent.setSpacing(0)
        self.layoutContent.setObjectName("layoutContent")
        self.widgetHeader = QtWidgets.QWidget(parent=self.frameDialog)
        self.widgetHeader.setMinimumSize(QtCore.QSize(0, 0))
        self.widgetHeader.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.widgetHeader.setStyleSheet("QWidget#widgetHeader {\n"
"    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,\n"
"                                      stop:0 rgb(105, 27, 253), \n"
"                                      stop:1 rgb(200, 160, 240));\n"
"    border-radius: 16px;\n"
"    color: rgb(255, 255, 255);\n"
"}")
        self.widgetHeader.setObjectName("widgetHeader")
        self.layoutHeader = QtWidgets.QHBoxLayout(self.widgetHeader)
        self.layoutHeader.setContentsMargins(18, 18, 18, 18)
        self.layoutHeader.setSpacing(18)
        self.layoutHeader.setObjectName("layoutHeader")
        self.layoutTitleContent = QtWidgets.QHBoxLayout()
        self.layoutTitleContent.setObjectName("layoutTitleContent")
        self.layoutDialogElements = QtWidgets.QVBoxLayout()
        self.layoutDialogElements.setSpacing(0)
        self.layoutDialogElements.setObjectName("layoutDialogElements")
        self.lblTitle = QtWidgets.QLabel(parent=self.widgetHeader)
        font = QtGui.QFont()
        font.setPointSize(22)
        font.setBold(True)
        self.lblTitle.setFont(font)
        self.lblTitle.setStyleSheet("QLabel#lblTitle {\n"
"    color: rgba(222, 255, 255, 255);\n"
"    qproperty-alignment: \'AlignCenter\';\n"
"    margin-bottom: 12px;\n"
"}")
        self.lblTitle.setObjectName("lblTitle")
        self.layoutDialogElements.addWidget(self.lblTitle)
        self.lblContent = QtWidgets.QLabel(parent=self.widgetHeader)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(False)
        self.lblContent.setFont(font)
        self.lblContent.setStyleSheet("QLabel#lblContent {\n"
"    color: rgb(250, 250, 250);\n"
"}")
        self.lblContent.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeading|QtCore.Qt.AlignmentFlag.AlignLeft|QtCore.Qt.AlignmentFlag.AlignTop)
        self.lblContent.setObjectName("lblContent")
        self.layoutDialogElements.addWidget(self.lblContent)
        self.layoutButtons = QtWidgets.QHBoxLayout()
        self.layoutButtons.setContentsMargins(-1, -1, 6, -1)
        self.layoutButtons.setSpacing(12)
        self.layoutButtons.setObjectName("layoutButtons")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.layoutButtons.addItem(spacerItem)
        self.btnCancel = QtWidgets.QPushButton(parent=self.widgetHeader)
        self.btnCancel.setMinimumSize(QtCore.QSize(88, 30))
        self.btnCancel.setMaximumSize(QtCore.QSize(88, 30))
        self.btnCancel.setStyleSheet("QPushButton#btnCancel {\n"
"    background-color: rgba(250, 250, 250, 100);\n"
"    color: white;\n"
"    border: none;\n"
"    border-radius: 8px;\n"
"    font-family: \'Microsoft YaHei\';\n"
"    font-size: 12px;\n"
"}\n"
"\n"
"QPushButton#btnCancel:hover {\n"
"    background-color: rgba(250, 250, 250, 130);\n"
"}\n"
"\n"
"QPushButton#btnCancel:pressed {\n"
"    background-color: rgba(250, 250, 250, 180);\n"
"}")
        self.btnCancel.setObjectName("btnCancel")
        self.layoutButtons.addWidget(self.btnCancel)
        self.btnDownload = QtWidgets.QPushButton(parent=self.widgetHeader)
        self.btnDownload.setMinimumSize(QtCore.QSize(88, 30))
        self.btnDownload.setMaximumSize(QtCore.QSize(88, 30))
        self.btnDownload.setStyleSheet("QPushButton#btnDownload {\n"
"    background-color: rgba(105, 27, 253, 180);\n"
"    color: white;\n"
"    border: none;\n"
"    border-radius: 8px;\n"
"    font-family: \'Microsoft YaHei\';\n"
"    font-size: 12px;\n"
"}\n"
"\n"
"QPushButton#btnDownload:hover {\n"
"    background-color: rgba(105, 27, 253, 120);\n"
"}\n"
"\n"
"QPushButton#btnDownload:pressed {\n"
"    background-color: rgba(105, 27, 253, 250);\n"
"}")
        self.btnDownload.setObjectName("btnDownload")
        self.layoutButtons.addWidget(self.btnDownload)
        self.layoutDialogElements.addLayout(self.layoutButtons)
        self.layoutDialogElements.setStretch(0, 1)
        self.layoutDialogElements.setStretch(1, 3)
        self.layoutDialogElements.setStretch(2, 1)
        self.layoutTitleContent.addLayout(self.layoutDialogElements)
        self.layoutHeader.addLayout(self.layoutTitleContent)
        self.layoutHeader.setStretch(0, 5)
        self.layoutContent.addWidget(self.widgetHeader)
        self.layoutContent.setStretch(0, 9)
        self.layoutDialog.addLayout(self.layoutContent)
        self.layoutDialog.setStretch(0, 4)
        self.layoutMain.addWidget(self.frameDialog)

        self.retranslateUi(UpdateDialog)
        QtCore.QMetaObject.connectSlotsByName(UpdateDialog)

    def retranslateUi(self, UpdateDialog):
        _translate = QtCore.QCoreApplication.translate
        UpdateDialog.setWindowTitle(_translate("UpdateDialog", "Dialog"))
        self.lblTitle.setText(_translate("UpdateDialog", "Dialog Title"))
        self.lblContent.setText(_translate("UpdateDialog", "Dialog content"))
        self.btnCancel.setText(_translate("UpdateDialog", "暂不更新"))
        self.btnDownload.setText(_translate("UpdateDialog", "立即下载"))
