from Qt import QtWidgets, QtCore, QtGui
from app.config.constants import BASE_URL, ZEROSSL_LOGIN
from app.utils.logger import setup_logger
import webbrowser


class DevTokenScreen(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.logger = setup_logger(f"{self.__class__.__name__}")
        
        try:
            self.setup_ui()
        except Exception as e:
            self.logger.error(f"Ошибка инициализации интерфейса токена: {str(e)}", exc_info=True)
            QtWidgets.QMessageBox.critical(
                self,
                "Ошибка инициализации",
                f"Не удалось инициализировать экран токена: {str(e)}"
            )
        
    def setup_ui(self):
        try:
            layout = QtWidgets.QVBoxLayout(self)
            layout.setContentsMargins(20, 20, 20, 20)
            
            title_label = QtWidgets.QLabel('Необходим Developer Token')
            title_label.setAlignment(QtCore.Qt.AlignCenter)
            title_label.setFont(QtGui.QFont('Arial', 18))
            title_label.setStyleSheet("color: #e0e0e0; margin-bottom: 30px;") 
            layout.addWidget(title_label)
            
            instruction_label = QtWidgets.QLabel('<b>Не работает в России.</b><br>Зарегистрируйтесь на ZeroSSL, после успешного входа зайдите во вкладку Developer и скопируйте токен')
            instruction_label.setAlignment(QtCore.Qt.AlignCenter)
            instruction_label.setStyleSheet("color: #a0a0a0; font-size: 14px; margin-bottom: 20px;")
            layout.addWidget(instruction_label)
            
            register_button = QtWidgets.QPushButton('Открыть сайт ZeroSSL')
            register_button.clicked.connect(lambda: webbrowser.open(ZEROSSL_LOGIN))
            register_button.setFixedSize(300, 40)
            
            button_layout = QtWidgets.QHBoxLayout()
            button_layout.addStretch()
            button_layout.addWidget(register_button)
            button_layout.addStretch()
            layout.addLayout(button_layout)
            
            token_layout = QtWidgets.QHBoxLayout()
            token_label = QtWidgets.QLabel('Developer Token:')
            token_label.setFixedWidth(120)
            token_label.setStyleSheet("color: #e0e0e0;")
            self.token_input = QtWidgets.QLineEdit()
            self.token_input.setMinimumWidth(300)
            self.token_input.setPlaceholderText("Введите ваш Developer Token")
            self.token_input.setStyleSheet("""
                QLineEdit {
                    background-color: #2d2d2d;
                    color: #e0e0e0;
                    border: 1px solid #3d3d3d;
                    border-radius: 4px;
                    padding: 8px;
                }
                QLineEdit:focus {
                    border: 1px solid #3498db;
                }
            """)
            token_layout.addStretch()
            token_layout.addWidget(token_label)
            token_layout.addWidget(self.token_input)
            token_layout.addStretch()
            
            layout.addStretch()
            layout.addLayout(token_layout)
            layout.addSpacing(20)
            
            submit_button = QtWidgets.QPushButton('Cохранить')
            submit_button.clicked.connect(self.parent.submitDeveloperToken)
            submit_button.setFixedSize(200, 40)
            
            button_layout2 = QtWidgets.QHBoxLayout()
            button_layout2.addStretch()
            button_layout2.addWidget(submit_button)
            button_layout2.addStretch()
            
            layout.addLayout(button_layout2)
            layout.addStretch()
            
            # "вернуться назад"
            back_button = QtWidgets.QPushButton('← Назад', self)
            back_button.clicked.connect(self.go_back)
            back_button.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border: none;
                    color: #0d6efd;
                    font-weight: bold;
                    padding: 5px;
                    text-align: left;
                }
                QPushButton:hover {
                    color: #0b5ed7;
                    background: transparent;
                }
                QPushButton:pressed {
                    color: #084298;
                    background: transparent;
                }
            """)
            back_button.setGeometry(20, 20, 100, 30)
            
            self.logger.debug("UI экрана токена настроен успешно")
        except Exception as e:
            self.logger.error(f"Ошибка в setup_ui: {str(e)}", exc_info=True)
            raise
    
    def go_back(self):
        try:
            self.logger.debug("Нажата кнопка 'Вернуться назад'")
            self.parent.go_back_from_dev_token_screen()
        except Exception as e:
            self.logger.error(f"Ошибка при возврате назад: {str(e)}", exc_info=True)
    
    def focus_on_token_input(self):
        try:
            self.logger.debug("Установка фокуса на поле ввода токена")
            self.token_input.setFocus()
        except Exception as e:
            self.logger.error(f"Ошибка при установке фокуса: {str(e)}")
        
    def show_warning(self):
        try:
            self.logger.warning("Отображение предупреждения о пустом токене")
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.setWindowTitle("Предупреждение")
            msg.setText("Пожалуйста, введите Developer Token")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: #1e1e1e;
                    color: #e0e0e0;
                }
                QMessageBox QLabel {
                    color: #e0e0e0;
                }
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    padding: 5px 15px;
                    border-radius: 3px;
                }
            """)
            msg.exec_()
        except Exception as e:
            self.logger.error(f"Ошибка при отображении предупреждения: {str(e)}")
