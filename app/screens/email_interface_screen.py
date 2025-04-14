from Qt import QtWidgets, QtCore, QtGui

from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineSettings

import webbrowser
import html
import time
import random
from app.screens.settings_screen import SettingsScreen
from app.config.constants import FUNNY_EMAILS
from app.utils.logger import setup_logger


# перехват ссылок, чтобы можно было открывать ссылки в пользовательском браузере
class ExternalBrowserPage(QWebEnginePage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = setup_logger(f"{self.__class__.__name__}")
        
    def acceptNavigationRequest(self, url, _type, isMainFrame):
        try:
            if _type == QWebEnginePage.NavigationType.NavigationTypeLinkClicked:  
                url_str = url.toString()
                # открываем ссылку в системном браузере
                webbrowser.open(url_str)
                return False
        except Exception as e:
            self.logger.error(f"Ошибка при обработке внешней ссылки: {str(e)}", exc_info=True)
            
        return True


class EmailInterfaceScreen(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = setup_logger(f"{self.__class__.__name__}")
        
        self.parent = parent
        self.subdomain = None
        
        try:
            self.setup_ui()
            self.logger.debug("Интерфейс электронной почты успешно инициализирован")
        except Exception as e:
            self.logger.error(f"Ошибка при инициализации интерфейса почты: {str(e)}", exc_info=True)
            QtWidgets.QMessageBox.critical(
                self,
                "Ошибка инициализации",
                f"Не удалось инициализировать интерфейс почты: {str(e)}"
            )
        
    def setup_ui(self):
        try:
            self.logger.debug("Настройка UI интерфейса электронной почты")
            self.layout = QtWidgets.QVBoxLayout(self)
            self.layout.setContentsMargins(0, 0, 0, 0)
            self.layout.setSpacing(0)
            
            # Верхняя панель
            self.top_frame = QtWidgets.QFrame()
            self.top_frame.setFixedHeight(40)
            self.top_frame.setFrameShape(QtWidgets.QFrame.NoFrame)
            self.top_frame.setStyleSheet("background-color: #292929;")
            
            self.top_bar = QtWidgets.QHBoxLayout(self.top_frame)
            self.top_bar.setContentsMargins(10, 0, 10, 0)
            self.top_bar.setSpacing(10)

            # Кнопка для настроек
            self.settings_button = QtWidgets.QPushButton("⋮")
            self.settings_button.setFixedWidth(30)
            self.settings_button.setFont(QtGui.QFont('Arial', 16))
            self.settings_button.setStyleSheet("""
                QPushButton {
                    background-color: #333333;
                    color: #e0e0e0;
                    border: none;
                    border-radius: 4px;
                    padding: 2px;
                }
                QPushButton:hover {
                    background-color: #444444;
                }
                QPushButton:pressed {
                    background-color: #555555;
                }
            """)
            self.settings_button.clicked.connect(self.open_settings)
            self.top_bar.addWidget(self.settings_button)
            
            # контейнер для почтового адреса
            self.email_container = QtWidgets.QWidget()
            email_layout = QtWidgets.QHBoxLayout(self.email_container)
            email_layout.setContentsMargins(0, 0, 0, 0)
            email_layout.setSpacing(2)

            # Поле ввода для части до @
            self.email_input = QtWidgets.QLineEdit(random.choice(FUNNY_EMAILS))
            self.email_input.setFont(QtGui.QFont('Arial', 12))
            self.email_input.setStyleSheet("""
                QLineEdit {
                    background-color: #333333;
                    color: #e0e0e0;
                    border: 1px solid #444444;
                    border-radius: 3px;
                    padding: 2px 5px;
                    max-width: 100px;
                }
                QLineEdit:focus {
                    border: 1px solid #3498db;
                }
            """)
            
            # Предотвращение автоматической фокусировки на поле ввода
            self.email_input.setFocusPolicy(QtCore.Qt.ClickFocus)
            
            self.email_input.setMaxLength(60)
            
            # Только буквы, цифры, точки, - и _ для почтового адреса
            rx = QtCore.QRegExp('^[a-zA-Z0-9][a-zA-Z0-9._-]*$')
            validator = QtGui.QRegExpValidator(rx)
            self.email_input.setValidator(validator)
            
            email_layout.addWidget(self.email_input)

            # Метка с @ и доменом
            self.domain_label = QtWidgets.QLabel("@загрузка...")
            self.domain_label.setFont(QtGui.QFont('Arial', 12))
            self.domain_label.setStyleSheet("color: #e0e0e0; font-weight: bold;")
            email_layout.addWidget(self.domain_label)

            # Кнопка копирования
            self.copy_button = QtWidgets.QPushButton("Копировать")
            self.copy_button.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 5px 10px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
                QPushButton:pressed {
                    background-color: #1f618d;
                }
            """)
            self.copy_button.clicked.connect(self.copy_email_address)
            email_layout.addWidget(self.copy_button)
            email_layout.addStretch()

            self.top_bar.addWidget(self.email_container)
            
            self.top_bar.addStretch()
            
            # TTL indicator
            self.ttl_label = QtWidgets.QLabel("Осталось: загрузка...")
            self.ttl_label.setFont(QtGui.QFont('Arial', 12))
            self.ttl_label.setStyleSheet("color: #2ecc71;")
            self.ttl_label.setAlignment(QtCore.Qt.AlignVCenter)

            self.top_bar.addWidget(self.ttl_label)

            # "Удалить почту"
            self.delete_button = QtWidgets.QPushButton("Удалить почту")
            self.delete_button.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 5px 10px;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
                QPushButton:pressed {
                    background-color: #a93226;
                }
            """)
            self.delete_button.clicked.connect(self.confirm_delete_mail)
            self.top_bar.addWidget(self.delete_button)
            
            self.layout.addWidget(self.top_frame)
            
            # сплиттер
            main_container = QtWidgets.QWidget()
            main_layout = QtWidgets.QVBoxLayout(main_container)
            main_layout.setContentsMargins(10, 10, 10, 10)
            
            self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
            
            # Левая панель - контейнер для списка писем и сообщения о пустом списке
            email_list_container = QtWidgets.QWidget()
            email_list_layout = QtWidgets.QVBoxLayout(email_list_container)
            email_list_layout.setContentsMargins(0, 0, 0, 0)
            email_list_layout.setSpacing(0)
            
            # Список писем
            self.email_list = QtWidgets.QListWidget()
            self.email_list.setMinimumWidth(350)
            self.email_list.setStyleSheet("""
                QListWidget {
                    background-color: #1e1e1e;
                    color: #e0e0e0;
                    border: 1px solid #3d3d3d;
                    border-radius: 6px;
                    padding: 5px;
                }
                QListWidget::item {
                    border-bottom: 1px solid #3d3d3d;
                    padding: 5px;
                }
                QListWidget::item:selected {
                    background-color: #2c3e50;
                    color: #ffffff;
                }
                QListWidget::item:hover {
                    background-color: #232323;
                }
            """)
            self.email_list.currentItemChanged.connect(self.display_email)
            
            # "Тут пока пусто..."
            self.empty_list_label = QtWidgets.QLabel("Тут пока пусто...")
            self.empty_list_label.setAlignment(QtCore.Qt.AlignCenter)
            self.empty_list_label.setFont(QtGui.QFont('Arial', 12))
            self.empty_list_label.setStyleSheet("""
                color: #808080;
                background-color: #1e1e1e;
                opacity: 0.5; 
                border: 1px solid #3d3d3d; 
                border-radius: 6px; 
                padding: 5px;
                min-height: 300px;
            """)
            self.empty_list_label.setMinimumWidth(350)

            # cписок и метка в контейнер
            email_list_layout.addWidget(self.email_list)
            email_list_layout.addWidget(self.empty_list_label)
            
            # только один виджет виден
            self.email_list.hide()
            self.empty_list_label.show()

            # правая панель 
            right_panel = QtWidgets.QWidget()
            right_layout = QtWidgets.QVBoxLayout(right_panel)
            right_layout.setContentsMargins(0, 0, 0, 5)
            right_layout.setSpacing(10)
            
            # заголовк письма
            self.email_header_widget = QtWidgets.QWidget()
            self.email_header_widget.setObjectName("email_header_widget")
            self.email_header_widget.setStyleSheet("""
            QWidget#email_header_widget {
                    background-color: #1e1e1e;
                    color: #e0e0e0;
                    border: 1px solid #3d3d3d;
                    border-radius: 6px;
                    padding: 10px;
            }
            """)

            self.email_header_layout = QtWidgets.QVBoxLayout(self.email_header_widget)
            self.email_header_layout.setSpacing(10)
            
            self.email_subject_label = QtWidgets.QLabel()
            self.email_subject_label.setFont(QtGui.QFont('Arial', 14, QtGui.QFont.Bold))
            self.email_subject_label.setStyleSheet("color: #3498db; margin-bottom: 0px;")
            
            self.email_subject_label.setWordWrap(True)
            
            self.email_sender_label = QtWidgets.QLabel()
            self.email_sender_label.setFont(QtGui.QFont('Arial', 11))
            
            self.email_date_label = QtWidgets.QLabel()
            self.email_date_label.setFont(QtGui.QFont('Arial', 11))
            self.email_date_label.setStyleSheet("color: #ababab;")
            
            self.email_header_layout.addWidget(self.email_subject_label)
            self.email_header_layout.addWidget(self.email_sender_label)
            self.email_header_layout.addWidget(self.email_date_label)

            self.email_subject_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
            self.email_sender_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
            self.email_date_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
            
            # webview для содержимого письма
            self.email_content = QWebEngineView()
            self.email_content.setMinimumHeight(300)
            
            # перехват ссылок
            try:
                custom_page = ExternalBrowserPage(self.email_content)
                self.email_content.setPage(custom_page)
            except Exception as e:
                self.logger.error(f"Ошибка при установке обработчика ссылок: {str(e)}", exc_info=True)
            
            # безопасный рендеринг html и css
            try:
                # Fix settings.setAttribute calls
                settings = self.email_content.settings()
                settings.setAttribute(QWebEngineSettings.AutoLoadImages, True)
                settings.setAttribute(QWebEngineSettings.JavascriptEnabled, False)
                settings.setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, False)
                settings.setAttribute(QWebEngineSettings.PluginsEnabled, False)
                self.logger.debug("Настроены параметры безопасности WebEngine")
            except Exception as e:
                self.logger.error(f"Ошибка при настройке параметров WebEngine: {str(e)}", exc_info=True)
            
            # темный фон
            self.email_content.setStyleSheet("background-color: #1e1e1e;")
            
            # добавляем все элементы в правую панель
            right_layout.addWidget(self.email_header_widget)
            right_layout.addWidget(self.email_content, 1)  # webview, растяжимое пространство
            
            # скрываем заголовок
            self.email_header_widget.hide()
            
            self.initial_webview_message()
            
            self.splitter.addWidget(email_list_container)  
            self.splitter.addWidget(right_panel)
            self.splitter.setStretchFactor(0, 1)
            self.splitter.setStretchFactor(1, 2)
            
            main_layout.addWidget(self.splitter)
            self.layout.addWidget(main_container)
            
            self.logger.debug("Настройка UI интерфейса электронной почты завершена")
        except Exception as e:
            self.logger.error(f"Ошибка при настройке UI: {str(e)}", exc_info=True)
            raise


    def initial_webview_message(self):
        try:
            initial_html = """
            <!DOCTYPE html>
            <html lang="ru">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body {
                        font-family: 'Arial', sans-serif;
                        background-color: #1a1a1a;
                        color: #ffffff;
                        max-width: 700px;
                        margin: 40px auto;
                        padding: 20px;
                        line-height: 1.6;
                    }
                    h1 {
                        font-size: 24px;
                        text-align: center;
                        margin-bottom: 20px;
                    }
                    h3 {
                        font-size: 18px;
                        text-align: center;
                        font-weight: normal
                        margin-bottom: 25px;
                    }
                    ul {
                        margin-left: 20px;
                    }
                    li {
                        margin-bottom: 15px;
                    }
                </style>
            </head>
            <body>
                <h1>Добро пожаловать в почтовый клиент tunnel.email</h1>
                <h3>Краткий экскурс по интерфейсу:</h2>
                <ul>
                    <li>Нажмите на <b>⋮</b>, чтобы перейти к дополнительным функциям</li>
                    <li>Нажмите на <b>Копировать</b>, чтобы скопировать ваш адрес электронной почты</li>
                    <li>Вы можете ввести любую строку до <b>@</b> — это не имеет значения. Письмо все равно придет в ваш временный ящик</li>
                    <li>Справа показывается оставшееся время и кнопка удаления почты</li>
                </ul>
            </body>
            </html>
            """
            self.email_content.setHtml(initial_html)
        except Exception as e:
            self.logger.error(f"Ошибка при установке начального сообщения в WebView: {str(e)}", exc_info=True)

    def open_settings(self):
        try:
            self.logger.info("Открытие окна настроек")
            self.settings_window = SettingsScreen(self.parent)
            self.settings_window.show()
        except Exception as e:
            self.logger.error(f"Ошибка при открытии окна настроек: {str(e)}", exc_info=True)
            QtWidgets.QMessageBox.warning(
                self,
                "Ошибка настроек",
                f"Не удалось открыть окно настроек: {str(e)}"
            )
    
    def copy_email_address(self):
        try:
            if self.subdomain:
                username = self.email_input.text()
                full_address = f"{username}@{self.subdomain}"
                
                clipboard = QtWidgets.QApplication.clipboard()
                clipboard.setText(full_address)
                
                self.copy_button.setText("Скопировано!")
                QtWidgets.QApplication.processEvents()
                
                # вернуть прежний текст через 2 секунды
                def reset_button_text():
                    self.copy_button.setText("Копировать")
                
                QtCore.QTimer.singleShot(2000, reset_button_text)
            else:
                self.logger.warning("Попытка копирования адреса без поддомена")
        except Exception as e:
            self.logger.error(f"Ошибка при копировании адреса: {str(e)}", exc_info=True)
    
    def setup_with_data(self, subdomain):
        try:
            self.subdomain = subdomain
            self.domain_label.setText(f"@{self.subdomain}")
        except Exception as e:
            self.logger.error(f"Ошибка при настройке данных поддомена: {str(e)}", exc_info=True)
    

    def update_ttl_display(self, ttl):
        try:
            if ttl < 0:
                ttl = 0

            hours = ttl // 3600
            minutes = (ttl % 3600) // 60
            seconds = ttl % 60
            
            time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            self.ttl_label.setText(f"Осталось: {time_str}")
            
            if ttl < 180:
                self.ttl_label.setStyleSheet("color: #ff5252; font-weight: bold;")
            elif ttl < 420:
                self.ttl_label.setStyleSheet("color: #ffb300; font-weight: bold;")
            else:
                self.ttl_label.setStyleSheet("color: #2ecc71;")

        except Exception as e:
            self.logger.error(f"Ошибка при обновлении отображения TTL: {str(e)}", exc_info=True)
    
    def show_ttl_error(self, error_msg):
        try:
            error_msg = error_msg[:20] + "..."
            self.logger.error(f"Ошибка TTL: {error_msg}")
            self.ttl_label.setText(f"Ошибка: {error_msg}")
            self.ttl_label.setStyleSheet("color: #ff5252;")
        except Exception as e:
            self.logger.error(f"Ошибка при отображении сообщения об ошибке TTL: {str(e)}", exc_info=True)
    
    def add_email_to_list(self, email, index):
        try:
            # нужно ли скрывать метку пустого списка?
            if self.email_list.count() == 0:
                self.empty_list_label.hide()
                self.email_list.show()
                self.logger.debug("Первое письмо в списке, замена пустого сообщения на список")
            
            # добавление письма
            item = QtWidgets.QListWidgetItem()
            item_widget = QtWidgets.QWidget()

            item_widget.setStyleSheet("background-color: transparent;")
            item_layout = QtWidgets.QVBoxLayout(item_widget)
            item_layout.setContentsMargins(5, 8, 5, 15)
            
            sender_label = QtWidgets.QLabel(email["sender"])
            sender_label.setFont(QtGui.QFont('Arial', 10, QtGui.QFont.Bold))
            sender_label.setStyleSheet("color: #e0e0e0;")
            
            subject_label = QtWidgets.QLabel(email["subject"])
            subject_label.setFont(QtGui.QFont('Arial', 9))
            subject_label.setStyleSheet("color: #cccccc;")
            
            timestamp_label = QtWidgets.QLabel(email["timestamp"])
            timestamp_label.setFont(QtGui.QFont('Arial', 8))
            timestamp_label.setStyleSheet("color: #808080;")
            
            item_layout.addWidget(sender_label)
            item_layout.addWidget(subject_label)
            item_layout.addWidget(timestamp_label)
            
            item_widget.setFixedHeight(80)
            
            item.setSizeHint(item_widget.sizeHint())
            self.email_list.addItem(item)
            self.email_list.setItemWidget(item, item_widget)
            
            item.setData(QtCore.Qt.UserRole, index)
            self.logger.debug(f"Письмо добавлено в список с индексом {index}")
            
            # автоматически выбираем первое письмо
            if self.email_list.count() == 1:
                self.email_list.setCurrentItem(item)
        except Exception as e:
            self.logger.error(f"Ошибка при добавлении письма в список: {str(e)}", exc_info=True)
    
    def display_email(self, current, previous):
        try:
            if current:
                # получение индекса письма из данных элемента
                email_idx = current.data(QtCore.Qt.UserRole)
                
                if not hasattr(self.parent, 'emails') or email_idx >= len(self.parent.emails):
                    self.logger.error(f"Индекс письма {email_idx} вне диапазона или список писем не существует")
                    return
                    
                email = self.parent.emails[email_idx]
                
                # обновляем pyqt виджеты заголовка письма
                self.email_subject_label.setText(f"Тема: {email['subject']}")
                self.email_sender_label.setText(f"От: {email['sender']}")
                self.email_date_label.setText(f"Дата: {email['timestamp']}")
                self.email_header_widget.show()  # Показываем заголовок письма
                
                # есть ли html контент в письме?
                html_body = email.get('html_content', None)
                
                # нет html контента => используем простой текст, экранируя его
                if not html_body:
                    body_content = self.text_to_html(email['body'])
                    self.logger.debug("Использование простого текста для отображения")
                else:
                    body_content = html_body
                    self.logger.debug("Использование HTML контента для отображения")
                
                # упрощенный html шаблон
                full_html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <style>
                        body {{
                            background-color: #1e1e1e;
                            color: #e0e0e0;
                            font-family: Arial, sans-serif;
                        }}

                    </style>
                </head>
                <body>
                    {body_content}
                </body>
                </html>
                """
                
                # отображение html в webview
                self.email_content.setHtml(full_html)
        except Exception as e:
            self.logger.error(f"Ошибка при отображении письма: {str(e)}", exc_info=True)
    
    def text_to_html(self, text):
        try:
            escaped_text = html.escape(text)
            html_text = escaped_text.replace('\n', '<br>')
            return html_text
        except Exception as e:
            self.logger.error(f"Ошибка при конвертации текста в HTML: {str(e)}", exc_info=True)
            return "<p>Ошибка отображения содержимого письма</p>"
        
    def confirm_delete_mail(self):
        try:
            self.logger.debug("Запрос подтверждения на удаление почты")
            # создаем диалог подтверждения
            confirm_dialog = QtWidgets.QMessageBox()
            confirm_dialog.setWindowTitle("Подтверждение удаления")
            confirm_dialog.setText("Вы уверены, что хотите удалить почту сейчас? Все полученные письма будут потеряны")
            confirm_dialog.setIcon(QtWidgets.QMessageBox.Warning)
            confirm_dialog.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            confirm_dialog.setDefaultButton(QtWidgets.QMessageBox.No)
            
            # показываем диалог и получаем результат
            result = confirm_dialog.exec_()
            
            # пользователь подтвердил действие => удаляем почту
            if result == QtWidgets.QMessageBox.Yes:
                self.logger.debug("Пользователь подтвердил удаление почты")
                try:
                    self.email_list.clear()
                    self.email_header_widget.hide()
                    self.initial_webview_message()
                    # после очистки списка показываем метку тут пусто
                    self.email_list.hide()
                    self.empty_list_label.show()

                    # удаляем туннель
                    self.parent.deleteTunnel()

                    self.logger.info("Почта успешно удалена")
                except Exception as e:
                    self.logger.error(f"Ошибка при удалении почты: {str(e)}", exc_info=True)
                    QtWidgets.QMessageBox.critical(
                        self,
                        "Ошибка удаления",
                        f"Произошла ошибка при удалении почты: {str(e)}"
                    )
            else:
                self.logger.debug("Пользователь отменил удаление почты")
        except Exception as e:
            self.logger.error(f"Ошибка при запросе подтверждения удаления: {str(e)}", exc_info=True)
