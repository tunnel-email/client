from Qt import QtWidgets, QtCore, QtGui
from app.utils.api import check_security
import webbrowser

class SettingsScreen(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Дополнительные функции")
        self.setFixedSize(500, 350)
        self.setup_ui()
        
    def setup_ui(self):
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)
        
        # заголовок
        self.title_label = QtWidgets.QLabel("Безопасность")
        self.title_label.setFont(QtGui.QFont('Arial', 16, QtGui.QFont.Bold))
        self.title_label.setStyleSheet("color: #3498db;")
        self.layout.addWidget(self.title_label)

        # Секция проверки безопасности
        self.security_section = QtWidgets.QWidget()
        security_layout = QtWidgets.QVBoxLayout(self.security_section)
        
        self.security_button = QtWidgets.QPushButton("Проверить безопасность")
        self.security_button.setFont(QtGui.QFont('Arial', 12))
        self.security_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        self.security_button.clicked.connect(self.check_security)
        
        self.security_info = QtWidgets.QLabel("Проверка безопасности позволяет убедиться, что ни у кого, кроме вас, "
                                   "нет доступа к TLS сертификату на поддомен.")
        self.security_info.setWordWrap(True)
        self.security_info.setStyleSheet("color: #cccccc;")
        
        # область для результатов проверки безопасности
        self.security_result = QtWidgets.QLabel("")
        self.security_result.setWordWrap(True)
        self.security_result.setStyleSheet("color: #2ecc71;")
        self.security_result.setOpenExternalLinks(True)
        self.security_result.hide()
        
        security_layout.addWidget(self.security_button)
        security_layout.addWidget(self.security_info)
        security_layout.addWidget(self.security_result)
        
        self.layout.addWidget(self.security_section)
        
        self.layout.addStretch(1)

    def check_security(self):
        try:
            self.security_button.setText("Проверка...")
            self.security_button.setEnabled(False)
            QtWidgets.QApplication.processEvents()  # обновление интерфейса
            
            
            certificates = check_security(self.parent.subdomain)
            
            if len(certificates) == 2:
                self.security_button.setText("Безопасность подтверждена")
                self.security_button.setStyleSheet("""
                    QPushButton {
                        background-color: #2ecc71;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 8px 16px;
                    }
                """)
                
                cert_link = f"https://crt.sh/?q={self.parent.subdomain}"
                
                self.security_result.setText(f"Данные о сертификате доступны по <a href='{cert_link}'>ссылке</a>")
                self.security_result.show()
            elif len(certificates) == 0:
                self.security_button.setText("Проверить безопасность")
                self.security_button.setEnabled(True)
                QtWidgets.QMessageBox.warning(self, "Проверка безопасности",
                                    "Данные о сертификате еще не успели появиться в открытом доступе. "
                                    "Попробуйте ещё раз через пару минут")
            else:
                self.security_button.setText("Проверить безопасность")
                self.security_button.setEnabled(True)
                QtWidgets.QMessageBox.warning(self, "Проверка безопасности", 
                                   "Не удалось подтвердить безопасность. "
                                   "Обнаружены проблемы с сертификатами.")
                
        except Exception as e:
            self.security_button.setText("Проверить безопасность")
            self.security_button.setEnabled(True)
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Произошла ошибка при проверке безопасности: {str(e)}")
