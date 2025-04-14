from Qt import QtWidgets, QtCore, QtGui
from app.utils.logger import setup_logger


class EmailMainScreen(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = setup_logger(f"{self.__class__.__name__}")
        
        self.parent = parent
        
        try:
            self.setup_ui()
        except Exception as e:
            self.logger.error(f"Ошибка при инициализации главного экрана почты: {str(e)}", exc_info=True)
            QtWidgets.QMessageBox.critical(
                self, 
                "Ошибка инициализации", 
                f"Не удалось настроить главный экран почты: {str(e)}"
            )
        
    def setup_ui(self):
        try:
            layout = QtWidgets.QVBoxLayout(self)
            layout.setContentsMargins(20, 20, 20, 20)
            
            # заголовок
            title_label = QtWidgets.QLabel('tunnel.email')
            title_label.setAlignment(QtCore.Qt.AlignCenter)
            title_label.setFont(QtGui.QFont('Arial', 18, QtGui.QFont.Bold))
            title_label.setStyleSheet("color: #e0e0e0; margin-bottom: 20px;")
            layout.addWidget(title_label)
            
            # кнопка создания нового туннеля
            create_button = QtWidgets.QPushButton('Создать новую почту')
            create_button.clicked.connect(self.parent.createTunnel)
            create_button.setFixedSize(250, 50)
            create_button.setFont(QtGui.QFont('Arial', 12))
            
            button_layout = QtWidgets.QHBoxLayout()
            button_layout.addStretch()
            button_layout.addWidget(create_button)
            button_layout.addStretch()
            layout.addLayout(button_layout)
            layout.addSpacing(30)
            
    
            placeholder = QtWidgets.QLabel("Нажмите 'Создать новую почту' для начала работы")
            placeholder.setAlignment(QtCore.Qt.AlignCenter)
            placeholder.setStyleSheet("color: #a0a0a0; font-size: 16px;")
            layout.addWidget(placeholder)
        except Exception as e:
            self.logger.error(f"Ошибка в setup_ui: {str(e)}", exc_info=True)
            raise
