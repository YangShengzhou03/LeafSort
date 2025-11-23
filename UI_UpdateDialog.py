"""
更新对话框UI模块

该模块定义了Ui_UpdateDialog类，用于管理应用程序的更新对话框界面。
包含标题、内容显示和操作按钮等UI组件。
"""

from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_UpdateDialog(object):
    """更新对话框UI类"""
    
    def setupUi(self, UpdateDialog):
        """设置更新对话框UI
        
        Args:
            UpdateDialog: 更新对话框实例
        """
        UpdateDialog.setObjectName("UpdateDialog")
        UpdateDialog.resize(512, 320)
        
        # 主布局
        self.layoutMain = QtWidgets.QVBoxLayout(UpdateDialog)
        self.layoutMain.setContentsMargins(0, 0, 0, 0)
        self.layoutMain.setSpacing(0)
        self.layoutMain.setObjectName("layoutMain")
        
        # 对话框框架
        self.frameDialog = QtWidgets.QFrame(parent=UpdateDialog)
        self.frameDialog.setMinimumSize(QtCore.QSize(512, 320))
        self.frameDialog.setStyleSheet(self._get_frame_style())
        self.frameDialog.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frameDialog.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frameDialog.setObjectName("frameDialog")
        
        # 对话框布局
        self.layoutDialog = QtWidgets.QHBoxLayout(self.frameDialog)
        self.layoutDialog.setContentsMargins(0, 0, 0, 0)
        self.layoutDialog.setSpacing(12)
        self.layoutDialog.setObjectName("layoutDialog")
        
        # 内容布局
        self.layoutContent = QtWidgets.QVBoxLayout()
        self.layoutContent.setContentsMargins(9, 9, 9, 9)
        self.layoutContent.setSpacing(0)
        self.layoutContent.setObjectName("layoutContent")
        
        # 头部组件
        self._setup_header_widget()
        
        # 添加到布局
        self.layoutContent.addWidget(self.widgetHeader)
        self.layoutContent.setStretch(0, 9)
        self.layoutDialog.addLayout(self.layoutContent)
        self.layoutDialog.setStretch(0, 4)
        self.layoutMain.addWidget(self.frameDialog)

        self.retranslateUi(UpdateDialog)
        QtCore.QMetaObject.connectSlotsByName(UpdateDialog)
    
    def _get_frame_style(self):
        """获取框架样式"""
        return """QFrame#frameDialog {
    background-color: rgb(245, 249, 254);
    border-radius: 25px;
}"""
    
    def _setup_header_widget(self):
        """设置头部组件"""
        self.widgetHeader = QtWidgets.QWidget(parent=self.frameDialog)
        self.widgetHeader.setMinimumSize(QtCore.QSize(0, 0))
        self.widgetHeader.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.widgetHeader.setStyleSheet(self._get_header_style())
        self.widgetHeader.setObjectName("widgetHeader")
        
        # 头部布局
        self.layoutHeader = QtWidgets.QHBoxLayout(self.widgetHeader)
        self.layoutHeader.setContentsMargins(18, 18, 18, 18)
        self.layoutHeader.setSpacing(18)
        self.layoutHeader.setObjectName("layoutHeader")
        
        # 标题内容布局
        self.layoutTitleContent = QtWidgets.QHBoxLayout()
        self.layoutTitleContent.setObjectName("layoutTitleContent")
        
        # 对话框元素布局
        self.layoutDialogElements = QtWidgets.QVBoxLayout()
        self.layoutDialogElements.setSpacing(0)
        self.layoutDialogElements.setObjectName("layoutDialogElements")
        
        # 添加标题和内容标签
        self._add_title_label()
        self._add_content_label()
        self._add_button_layout()
        
        # 设置布局拉伸比例
        self.layoutDialogElements.setStretch(0, 1)
        self.layoutDialogElements.setStretch(1, 3)
        self.layoutDialogElements.setStretch(2, 1)
        
        self.layoutTitleContent.addLayout(self.layoutDialogElements)
        self.layoutHeader.addLayout(self.layoutTitleContent)
        self.layoutHeader.setStretch(0, 5)
    
    def _get_header_style(self):
        """获取头部样式"""
        return """QWidget#widgetHeader {
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                      stop:0 rgb(105, 27, 253), 
                                      stop:1 rgb(200, 160, 240));
    border-radius: 16px;
    color: rgb(255, 255, 255);
}"""
    
    def _add_title_label(self):
        """添加标题标签"""
        self.lblTitle = QtWidgets.QLabel(parent=self.widgetHeader)
        font = QtGui.QFont()
        font.setPointSize(22)
        font.setBold(True)
        self.lblTitle.setFont(font)
        self.lblTitle.setStyleSheet(self._get_title_style())
        self.lblTitle.setObjectName("lblTitle")
        self.layoutDialogElements.addWidget(self.lblTitle)
    
    def _get_title_style(self):
        """获取标题样式"""
        return """QLabel#lblTitle {
    color: rgba(222, 255, 255, 255);
    qproperty-alignment: 'AlignCenter';
    margin-bottom: 12px;
}"""
    
    def _add_content_label(self):
        """添加内容标签"""
        self.lblContent = QtWidgets.QLabel(parent=self.widgetHeader)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(False)
        self.lblContent.setFont(font)
        self.lblContent.setStyleSheet(self._get_content_style())
        self.lblContent.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeading|QtCore.Qt.AlignmentFlag.AlignLeft|QtCore.Qt.AlignmentFlag.AlignTop)
        self.lblContent.setObjectName("lblContent")
        self.layoutDialogElements.addWidget(self.lblContent)
    
    def _get_content_style(self):
        """获取内容样式"""
        return """QLabel#lblContent {
    color: rgb(250, 250, 250);
}"""
    
    def _add_button_layout(self):
        """添加按钮布局"""
        self.layoutButtons = QtWidgets.QHBoxLayout()
        self.layoutButtons.setContentsMargins(-1, -1, 6, -1)
        self.layoutButtons.setSpacing(12)
        self.layoutButtons.setObjectName("layoutButtons")
        
        # 添加弹性空间
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.layoutButtons.addItem(spacerItem)
        
        # 添加取消按钮
        self._add_cancel_button()
        
        # 添加下载按钮
        self._add_download_button()
        
        self.layoutDialogElements.addLayout(self.layoutButtons)
    
    def _add_cancel_button(self):
        """添加取消按钮"""
        self.btnCancel = QtWidgets.QPushButton(parent=self.widgetHeader)
        self.btnCancel.setMinimumSize(QtCore.QSize(88, 30))
        self.btnCancel.setMaximumSize(QtCore.QSize(88, 30))
        self.btnCancel.setStyleSheet(self._get_cancel_button_style())
        self.btnCancel.setObjectName("btnCancel")
        self.layoutButtons.addWidget(self.btnCancel)
    
    def _get_cancel_button_style(self):
        """获取取消按钮样式"""
        return """QPushButton#btnCancel {
    background-color: rgba(250, 250, 250, 100);
    color: white;
    border: none;
    border-radius: 8px;
    font-family: 'Microsoft YaHei';
    font-size: 12px;
}

QPushButton#btnCancel:hover {
    background-color: rgba(250, 250, 250, 130);
}

QPushButton#btnCancel:pressed {
    background-color: rgba(250, 250, 250, 180);
}"""
    
    def _add_download_button(self):
        """添加下载按钮"""
        self.btnDownload = QtWidgets.QPushButton(parent=self.widgetHeader)
        self.btnDownload.setMinimumSize(QtCore.QSize(88, 30))
        self.btnDownload.setMaximumSize(QtCore.QSize(88, 30))
        self.btnDownload.setStyleSheet(self._get_download_button_style())
        self.btnDownload.setObjectName("btnDownload")
        self.layoutButtons.addWidget(self.btnDownload)
    
    def _get_download_button_style(self):
        """获取下载按钮样式"""
        return """QPushButton#btnDownload {
    background-color: rgba(105, 27, 253, 180);
    color: white;
    border: none;
    border-radius: 8px;
    font-family: 'Microsoft YaHei';
    font-size: 12px;
}

QPushButton#btnDownload:hover {
    background-color: rgba(105, 27, 253, 120);
}

QPushButton#btnDownload:pressed {
    background-color: rgba(105, 27, 253, 250);
}"""
    
    def retranslateUi(self, UpdateDialog):
        """翻译UI文本"""
        _translate = QtCore.QCoreApplication.translate
        UpdateDialog.setWindowTitle(_translate("UpdateDialog", "Dialog"))
        self.lblTitle.setText(_translate("UpdateDialog", "Dialog Title"))
        self.lblContent.setText(_translate("UpdateDialog", "Dialog content"))
        self.btnCancel.setText(_translate("UpdateDialog", "暂不更新"))
        self.btnDownload.setText(_translate("UpdateDialog", "立即下载"))