from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

import requests
from string import ascii_lowercase, digits
from secrets import choice

from app.utils.api import yandex_login
from app.config.constants import BASE_URL, TOKEN_LENGTH
from app.utils.logger import setup_logger


class AuthScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = setup_logger(f"{self.__class__.__name__}")
        
        self.parent = parent
        self.auth_token = None

        try:
            self.setup_ui()
            self.logger.debug("Интерфейс экрана авторизации настроен успешно")
        except Exception as e:
            self.logger.error(f"Ошибка при инициализации экрана авторизации: {str(e)}", exc_info=True)
            QMessageBox.critical(
                self, 
                "Ошибка инициализации", 
                f"Не удалось настроить экран авторизации: {str(e)}"
            )
        
    def setup_ui(self):
        try:
            layout = QVBoxLayout(self)
            layout.setContentsMargins(20, 20, 20, 20)
            
            auth_label = QLabel('Авторизация через Яндекс')
            auth_label.setAlignment(Qt.AlignCenter)
            auth_label.setFont(QFont('Arial', 18))
            auth_label.setStyleSheet("color: #e0e0e0; margin-bottom: 30px;")
            layout.addWidget(auth_label)
            
            info_label = QLabel('Сейчас откроется браузер для входа через Яндекс.\nПожалуйста, завершите процесс авторизации.')
            info_label.setAlignment(Qt.AlignCenter)
            info_label.setStyleSheet("color: #a0a0a0; font-size: 14px; margin-bottom: 20px;")
            layout.addWidget(info_label)
            
            # текст для отображения ошибок
            self.auth_error_label = QLabel('')
            self.auth_error_label.setAlignment(Qt.AlignCenter)
            self.auth_error_label.setStyleSheet("color: #ff5252; font-size: 14px;")
            layout.addWidget(self.auth_error_label)
            
            # кнопка завершения
            complete_button = QPushButton('Я завершил авторизацию')
            complete_button.setFixedSize(250, 50)
            complete_button.setFont(QFont('Arial', 12))
            complete_button.clicked.connect(self.complete_authentication_safe)
            
            button_layout = QHBoxLayout()
            button_layout.addStretch()
            button_layout.addWidget(complete_button)
            button_layout.addStretch()
            
            layout.addStretch()
            layout.addLayout(button_layout)
            layout.addStretch()
            
            # повтор
            retry_button = QPushButton('Повторить')
            retry_button.clicked.connect(self.start_auth)
            
            retry_layout = QHBoxLayout()
            retry_layout.addStretch()
            retry_layout.addWidget(retry_button)
            retry_layout.addStretch()
            
            layout.addLayout(retry_layout)
            
        except Exception as e:
            self.logger.error(f"Ошибка в setup_ui: {str(e)}", exc_info=True)
            raise

    def generate_secret(self, length):
        secret = ''.join(choice(ascii_lowercase + digits) for i in range(length))

        return secret
        
    def complete_authentication_safe(self):
        try:    
            if not self.auth_token:
                self.logger.warning("Попытка завершить авторизацию без токена")
                self.auth_error_label.setText("Сначала необходимо начать процесс авторизации")
                return
                
            self.parent.completeAuthentication()
            self.logger.info("Процесс авторизации завершен")
        except Exception as e:
            self.logger.error(f"Ошибка при завершении авторизации: {str(e)}", exc_info=True)
            self.auth_error_label.setText(f"Ошибка: {str(e)}")
            
    def start_auth(self):
        try:
            self.auth_error_label.setText("")  # очистка предыдущих ошибок

            self.auth_token = self.generate_secret(TOKEN_LENGTH)
            
            # открытие браузера для аутентификации
            try:
                yandex_login(self.auth_token)
                self.logger.debug("Браузер для аутентификации и успешно запущен")
            except requests.RequestException as req_error:
                self.logger.error(f"Ошибка сетевого запроса при авторизации: {str(req_error)}", exc_info=True)

                self.auth_error_label.setText(f"Ошибка сетевого запроса: {str(req_error)}")
            except Exception as e:
                self.logger.error(f"Непредвиденная ошибка при авторизации: {str(e)}", exc_info=True)
                self.auth_error_label.setText(f"Ошибка авторизации: {str(e)}")
        
        except Exception as e:
            self.logger.critical(f"Критическая ошибка в процессе авторизации: {str(e)}", exc_info=True)
            self.auth_error_label.setText(f"Критическая ошибка: {str(e)}")
            QMessageBox.critical(
                self, 
                "Ошибка авторизации", 
                f"Произошла неожиданная ошибка при авторизации: {str(e)}"
            )
