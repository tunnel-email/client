from PyQt5.QtCore import QUrl, Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QPushButton, 
    QProgressBar, QDialog, QMessageBox, QLineEdit
)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEnginePage, QWebEngineSettings
from PyQt5.QtNetwork import QNetworkProxy
from app.config.constants import PROXY_HOST, PROXY_PORT
from app.utils.logger import setup_logger


class ZeroSSLBrowser(QDialog):
    # cигнал, который отправится, когда пользователь получит токен
    token_received = pyqtSignal()
    
    def __init__(self, zerossl_url, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.logger = setup_logger(f"{self.__class__.__name__}")
        self.logger.info("Инициализация браузера ZeroSSL")
        
        self.setWindowTitle("ZeroSSL - Получение Developer Token")
        self.resize(1200, 800)
        self.setMinimumSize(800, 600)
        
        try:
            self.setup_proxy()
            self.setup_ui()
            
            # загрузка страницы для входа в ZeroSSL
            self.load_url(zerossl_url)
        except Exception as e:
            self.logger.error(f"Ошибка инициализации браузера ZeroSSL: {str(e)}", exc_info=True)
            QMessageBox.critical(
                self,
                "Ошибка браузера",
                f"Не удалось инициализировать браузер: {str(e)}"
            )

    def setup_proxy(self):
        try:
            # отдельный профиль для браузера
            self.profile = QWebEngineProfile("zerossl_browser")
            
            # socks5 прокси для доступа к ZeroSSL
            self.logger.info(f"Настройка прокси: {PROXY_HOST}:{PROXY_PORT}")
            proxy = QNetworkProxy(QNetworkProxy.Socks5Proxy, PROXY_HOST, PROXY_PORT)
            QNetworkProxy.setApplicationProxy(proxy)
            self.logger.debug("Прокси настроен успешно")
        except Exception as e:
            self.logger.error(f"Ошибка настройки прокси: {str(e)}")
            raise

    def setup_ui(self):
        try:
            layout = QVBoxLayout(self)
            layout.setSpacing(5)
            layout.setContentsMargins(5, 5, 5, 5)
            
            # верхняя панель
            control_panel = QHBoxLayout()
            
            # кнопки навигации
            self.back_btn = QPushButton("Назад")
            self.back_btn.clicked.connect(lambda: self.browser_view.back())
            
            self.forward_btn = QPushButton("Вперед")
            self.forward_btn.clicked.connect(lambda: self.browser_view.forward())
            
            self.reload_btn = QPushButton("Обновить")
            self.reload_btn.clicked.connect(lambda: self.browser_view.reload())
            
            # поле с url
            self.url_field = QLineEdit()
            self.url_field.setReadOnly(True) # чтобы нельзя было редактировать

            self.url_field.setMaximumWidth(300)
            self.url_field.setMinimumWidth(300) 
            self.url_field.setMinimumHeight(30)
            self.url_field.setMaximumHeight(30)

            self.url_field.setStyleSheet("font-size: 15px; font-weight: 300;")
            self.url_field.setAlignment(Qt.AlignCenter)
            
            # "я получил токен"
            self.done_btn = QPushButton("Я получил токен")
            self.done_btn.clicked.connect(self.close_browser)
            
            control_panel.addWidget(self.back_btn)
            control_panel.addWidget(self.forward_btn)
            control_panel.addWidget(self.reload_btn)
            control_panel.addStretch()
            control_panel.addWidget(self.url_field)
            control_panel.addStretch()
            control_panel.addWidget(self.done_btn)
            
            # webview
            self.browser_view = QWebEngineView()
            
            self.page = QWebEnginePage(self.profile, self.browser_view)
            self.browser_view.setPage(self.page)
            
            self.browser_view.loadProgress.connect(self.update_progress)
            self.browser_view.loadFinished.connect(lambda: self.progress_bar.hide())
            self.browser_view.loadStarted.connect(lambda: self.progress_bar.show())
            
            # обновление поля при изменении url
            self.page.urlChanged.connect(self.update_url_field)
            
            # progress-bar
            self.progress_bar = QProgressBar()
            self.progress_bar.setTextVisible(False)
            self.progress_bar.setMaximumHeight(2)
            self.progress_bar.hide()
            
            layout.addLayout(control_panel)
            layout.addWidget(self.progress_bar)
            layout.addWidget(self.browser_view)
            
            self.logger.debug("UI браузера ZeroSSL настроен успешно")
        except Exception as e:
            self.logger.error(f"Ошибка в setup_ui браузера: {str(e)}", exc_info=True)
            raise

    def update_url_field(self, url):
        try:
            self.url_field.setText(url.toString())
            self.logger.debug(f"URL обновлен: {url.toString()}")
        except Exception as e:
            self.logger.error(f"Ошибка при обновлении URL: {str(e)}")

    def load_url(self, url):
        try:
            self.logger.info(f"Загрузка URL: {url}")
            qurl = QUrl(url)
            self.browser_view.load(qurl)
            # обновляем поле url при начальной загрузке
            self.url_field.setText(url)
        except Exception as e:
            self.logger.error(f"Ошибка при загрузке URL: {str(e)}", exc_info=True)
            QMessageBox.critical(
                self, 
                "Ошибка соединения", 
                f"Не удалось подключиться к серверу\n"
                f"Пожалуйста, проверьте подключение к интернету.\n\n"
                f"Детали: {str(e)}"
            )

    def update_progress(self, progress):
        try:
            self.progress_bar.setValue(progress)
            if progress % 25 == 0:  # Логируем только каждые 25%
                self.logger.debug(f"Прогресс загрузки: {progress}%")
        except Exception as e:
            self.logger.error(f"Ошибка при обновлении прогресса: {str(e)}")

    def close_browser(self):
        try:
            self.logger.info("Закрытие браузера по запросу пользователя")
            # возврат к вводу токена
            self.token_received.emit()
            self.accept()
        except Exception as e:
            self.logger.error(f"Ошибка при закрытии браузера: {str(e)}")
            self.accept()  # Все равно пытаемся закрыть
        
    def closeEvent(self, event):
        try:
            # освобождение ресурсов браузера при закрытии
            self.logger.info("Закрытие окна браузера")
            if hasattr(self, 'browser_view'):
                self.browser_view.setPage(None)

                if hasattr(self, 'page'):
                    self.page.deleteLater()

                self.browser_view.deleteLater()

            super().closeEvent(event)
        except Exception as e:
            self.logger.error(f"Ошибка при обработке closeEvent: {str(e)}", exc_info=True)
            super().closeEvent(event)
    
    def accept(self):
        try:
            # переопределяем accept
            self.logger.info("Вызов accept() для браузера ZeroSSL")
            if hasattr(self, 'browser_view'):
                self.browser_view.setPage(None)

                if hasattr(self, 'page'):
                    self.page.deleteLater()

                self.browser_view.deleteLater()

            super().accept()
        except Exception as e:
            self.logger.error(f"Ошибка при вызове accept: {str(e)}", exc_info=True)
            super().accept()
