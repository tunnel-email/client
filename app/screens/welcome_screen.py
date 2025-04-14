from Qt import QtWidgets, QtCore, QtGui


class WelcomeScreen(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()
        
    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # добавление заголовка
        title_label = QtWidgets.QLabel('tunnel.email')
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        title_label.setFont(QtGui.QFont('Arial', 24, QtGui.QFont.Bold))
        title_label.setStyleSheet("color: #e0e0e0; margin-bottom: 30px;")
        layout.addWidget(title_label)
        
        description = QtWidgets.QLabel('Самая безопасная временная электронная почта.\nСоздавайте почтовые туннели одним кликом')
        description.setAlignment(QtCore.Qt.AlignCenter)
        description.setStyleSheet("color: #a0a0a0; font-size: 16px; margin-bottom: 50px;")
        layout.addWidget(description)
        
        # кнопка старт
        start_button = QtWidgets.QPushButton('Начать')
        start_button.setFixedSize(200, 50)
        start_button.setFont(QtGui.QFont('Arial', 12))
        start_button.clicked.connect(self.parent.startAuthentication)
        
        # чтобы кнопка по центру была
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(start_button)
        button_layout.addStretch()
        
        layout.addStretch()
        layout.addLayout(button_layout)
        layout.addStretch()
