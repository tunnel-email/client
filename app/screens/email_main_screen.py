from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from app.utils.logger import setup_logger


class EmailMainScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = setup_logger(f"{self.__class__.__name__}")
        
        self.parent = parent
        
        try:
            self.setup_ui()
        except Exception as e:
            self.logger.error(f"Ошибка при инициализации главного экрана почты: {str(e)}", exc_info=True)
            QMessageBox.critical(
                self, 
                "Ошибка инициализации", 
                f"Не удалось настроить главный экран почты: {str(e)}"
            )
        
    def setup_ui(self):
        try:
            layout = QVBoxLayout(self)
            layout.setContentsMargins(20, 20, 20, 20)
            
            # заголовок
            title_label = QLabel('tunnel.email')
            title_label.setAlignment(Qt.AlignCenter)
            title_label.setFont(QFont('Arial', 18, QFont.Bold))
            title_label.setStyleSheet("color: #e0e0e0; margin-bottom: 20px;")
            layout.addWidget(title_label)
            
            # кнопка создания нового туннеля
            create_button = QPushButton('Создать новую почту')
            create_button.clicked.connect(self.parent.createTunnel)
            create_button.setFixedSize(250, 50)
            create_button.setFont(QFont('Arial', 12))
            
            button_layout = QHBoxLayout()
            button_layout.addStretch()
            button_layout.addWidget(create_button)
            button_layout.addStretch()
            layout.addLayout(button_layout)
            layout.addSpacing(30)
            
    
            placeholder = QLabel("Нажмите 'Создать новую почту' для начала работы")
            placeholder.setAlignment(Qt.AlignCenter)
            placeholder.setStyleSheet("color: #a0a0a0; font-size: 16px;")
            layout.addWidget(placeholder)
        except Exception as e:
            self.logger.error(f"Ошибка в setup_ui: {str(e)}", exc_info=True)
            raise
