from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class WelcomeScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # добавление заголовка
        title_label = QLabel('tunnel.email')
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont('Arial', 24, QFont.Bold))
        title_label.setStyleSheet("color: #e0e0e0; margin-bottom: 30px;")
        layout.addWidget(title_label)
        
        description = QLabel('Самая безопасная временная электронная почта.\nСоздавайте почтовые туннели одним кликом')
        description.setAlignment(Qt.AlignCenter)
        description.setStyleSheet("color: #a0a0a0; font-size: 16px; margin-bottom: 50px;")
        layout.addWidget(description)
        
        # кнопка старт
        start_button = QPushButton('Начать')
        start_button.setFixedSize(200, 50)
        start_button.setFont(QFont('Arial', 12))
        start_button.clicked.connect(self.parent.startAuthentication)
        
        # чтобы кнопка по центру была
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(start_button)
        button_layout.addStretch()
        
        layout.addStretch()
        layout.addLayout(button_layout)
        layout.addStretch()
