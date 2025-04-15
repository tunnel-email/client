import json
import threading
import time
import traceback
from Qt import QtWidgets, QtCore

from app.screens.welcome_screen import WelcomeScreen
from app.screens.auth_screen import AuthScreen
from app.screens.dev_token_screen import DevTokenScreen
from app.screens.email_main_screen import EmailMainScreen
from app.screens.email_interface_screen import EmailInterfaceScreen
from app.screens.loading_screen import LoadingScreen

from app.utils.worker import Worker
from app.utils.api import get_ttl, script_path
from app.utils.tunnel import (create_tunnel, delete_tunnel,
                             save_certificate, save_token, load_secrets,
                             save_developer_token, add_tunnel_to_rathole, Rathole)
from app.utils.logger import setup_logger

import app.utils.mail_server_tls as mailserv
from app.utils.cert_manager import get_certificate

from requests.exceptions import ConnectionError
from app.config.constants import BASE_DOMAIN
import os.path


class EmailTunnelApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
    
        self.logger = setup_logger(f"{self.__class__.__name__}")
        self.logger.info("Инициализация основного приложения EmailTunnelApp")
        
        self.token = None
        self.tunnel_id = None
        self.subdomain = None
        self.tunnel_setup_failed = False
        self.emails = []
    
        try:
            self.initUI()
            self.loadToken()
            self.logger.info("Приложение успешно инициализировано")
        except Exception as e:
            self.logger.critical(f"Критическая ошибка при инициализации приложения: {str(e)}", exc_info=True)
            QtWidgets.QMessageBox.critical(
                self, 
                "Ошибка инициализации", 
                f"Не удалось запустить приложение: {str(e)}"
            )


    def initUI(self):
        try:
            self.setWindowTitle('tunnel.email')
            self.setGeometry(100, 100, 1000, 700)
            
            # стек экранов
            self.stacked_widget = QtWidgets.QStackedWidget()
            self.setCentralWidget(self.stacked_widget)
            

            self.welcome_screen = WelcomeScreen(self)
            self.auth_screen = AuthScreen(self)
            self.dev_token_screen = DevTokenScreen(self)
            self.email_main_screen = EmailMainScreen(self)
            self.email_interface_screen = EmailInterfaceScreen(self)
            self.loading_screen = LoadingScreen(self)
            
            self.stacked_widget.addWidget(self.welcome_screen)
            self.stacked_widget.addWidget(self.auth_screen)
            self.stacked_widget.addWidget(self.dev_token_screen)
            self.stacked_widget.addWidget(self.email_main_screen)
            self.stacked_widget.addWidget(self.email_interface_screen)
            self.stacked_widget.addWidget(self.loading_screen)
            
            self.logger.debug("Интерфейс успешно настроен")
        except Exception as e:
            self.logger.error(f"Ошибка при инициализации интерфейса: {str(e)}", exc_info=True)
            raise
    
    def loadToken(self):
        self.logger.debug("Загрузка сохраненных токенов")
        try:
            self.token, self.dev_token = load_secrets()
            
            if self.token and self.dev_token:
                self.logger.info("Найдены оба токена, переход к главному экрану")
                self.stacked_widget.setCurrentWidget(self.email_main_screen)
            elif self.token and not self.dev_token:
                self.logger.info("Найден только токен авторизации, требуется developer токен")
                self.stacked_widget.setCurrentWidget(self.dev_token_screen)
            else:
                self.logger.info("Токены не найдены, отображение приветственного экрана")
                self.stacked_widget.setCurrentWidget(self.welcome_screen)
        except FileNotFoundError:
            self.logger.warning("Файл secrets.json не найден, отображение приветственного экрана")
            self.stacked_widget.setCurrentWidget(self.welcome_screen)
        except json.JSONDecodeError:
            self.logger.error("Ошибка декодирования JSON в secrets.json")
            self.stacked_widget.setCurrentWidget(self.welcome_screen)
        except Exception as e:
            self.logger.error(f"Неожиданная ошибка при загрузке токена: {str(e)}", exc_info=True)
            self.stacked_widget.setCurrentWidget(self.welcome_screen)
    
    def startAuthentication(self):
        try:
            self.logger.info("Запуск процесса аутентификации")

            self.stacked_widget.setCurrentWidget(self.auth_screen)
            self.auth_screen.start_auth()
        except Exception as e:
            self.logger.error(f"Ошибка при старте аутентификации: {str(e)}", exc_info=True)
            self.showError(f"Не удалось начать аутентификацию: {str(e)}")


    def completeAuthentication(self):
        try:
            if self.auth_screen.auth_token:
                self.token = self.auth_screen.auth_token
                self.logger.info("Аутентификация успешна, сохранение токена")
                
                try:
                    save_token(self.auth_screen.auth_token)
                    self.stacked_widget.setCurrentWidget(self.dev_token_screen)
                except Exception as save_error:
                    self.logger.error(f"Ошибка при сохранении токена: {str(save_error)}", exc_info=True)
                    raise save_error
            else:
                self.logger.warning("Аутентификация не удалась, токен не получен")
                self.auth_screen.auth_error_label.setText("Ошибка: Не удалось получить токен")
        except Exception as e:
            self.logger.error(f"Ошибка при завершении аутентификации: {str(e)}", exc_info=True)
            self.showError(f"Ошибка аутентификации: {str(e)}")


    def submitDeveloperToken(self):
        try:
            self.dev_token = self.dev_token_screen.token_input.text()
            if self.dev_token:
                try:
                    save_developer_token(self.dev_token)

                    self.stacked_widget.setCurrentWidget(self.email_main_screen)
                    self.logger.debug("Developer токен успешно сохранен")
                except Exception as save_error:
                    self.logger.error(f"Ошибка при сохранении developer токена: {str(save_error)}", exc_info=True)
                    self.showError(f"Не удалось сохранить developer токен: {str(save_error)}")
            else:
                self.logger.warning("Пустой developer токен, показ предупреждения")
                self.dev_token_screen.show_warning()
        except Exception as e:
            self.logger.error(f"Ошибка при обработке developer токена: {str(e)}", exc_info=True)
            self.showError(f"Ошибка при обработке developer токена: {str(e)}")


    def createTunnel(self):
        try:
            self.logger.info("Запуск процесса создания туннеля")

            # показ экрана загрузки
            self.stacked_widget.setCurrentWidget(self.loading_screen)
            
            # создание туннеля в отдельном потоке
            self.tunnel_worker = Worker(self.setupTunnel)
            self.tunnel_worker.finished.connect(self.tunnelCreated)
            self.tunnel_worker.error.connect(self.showError)
            self.tunnel_worker.start()
        except Exception as e:
            self.logger.error(f"Ошибка при инициализации создания туннеля: {str(e)}", exc_info=True)
            self.showError(f"Не удалось начать создание туннеля: {str(e)}")


    def deleteTunnel(self):
        try:
            self.logger.info(f"Удаление туннеля")
            try:
                delete_tunnel(self.token)
                self.logger.debug("API-запрос на удаление туннеля выполнен")
            except Exception as tunnel_error:
                self.logger.warning(f"Ошибка при удалении туннеля через API: {str(tunnel_error)}")

            if hasattr(self, "mail_controller"):
                try:
                    self.logger.debug("Остановка почтового контроллера")
                    self.mail_controller.stop()
                except Exception as mail_error:
                    self.logger.warning(f"Ошибка при остановке почтового сервера: {str(mail_error)}")
            
            if hasattr(self, 'ttl_timer') and self.ttl_timer.isActive():
                try:
                    self.logger.debug("Остановка TTL таймера")
                    self.ttl_timer.stop()
                except Exception as timer_error:
                    self.logger.warning(f"Ошибка при остановке TTL таймера: {str(timer_error)}")

            # останавливаем rathole
            if hasattr(self, 'rathole'): # если сущ-т
                try:
                    self.logger.debug("Остановка rathole")

                    self.rathole.stop()
                except Exception as rh_error:
                    self.logger.warning(f"Ошибка при остановке rathole: {str(rh_error)}")

            self.stacked_widget.setCurrentWidget(self.email_main_screen)
            self.logger.info("Туннель успешно удален")
        except Exception as e:
            self.logger.error(f"Ошибка при удалении туннеля: {str(e)}", exc_info=True)
            self.showError(f"Произошла ошибка при удалении туннеля: {str(e)}")

            # возвращение на главный экран
            self.stacked_widget.setCurrentWidget(self.email_main_screen)


    def setupTunnel(self, should_stop):
        try:
            try:
                delete_tunnel(self.token)
                self.logger.debug("Успешно удален туннель")
            except ConnectionError:
                self.logger.debug("Невозможно подключиться к серверу")
                self.tunnel_worker.error.emit("Сервер временно недоступен")
                self.tunnel_setup_failed = True
                return
            except Exception as delete_error:
                self.logger.error(f"Ошибка при удалении предыдущего туннеля: {str(delete_error)}")
                self.tunnel_worker.error.emit("Что-то пошло не так при удалении предыдущего туннеля...")
                self.tunnel_setup_failed = True
                return
                
            
            # создание нового туннеля

            self.subdomain, self.tunnel_id, tunnel_secret = create_tunnel(self.token)
            self.logger.info(f"Туннель создан: {self.subdomain}")
            
            self.logger.debug("Запрос сертификата")

            fullchain, privkey = get_certificate(self.token, self.dev_token, self.subdomain)

            self.logger.debug("Сертификат получен, сохранение")
            save_certificate(self.subdomain, fullchain, privkey)
            
            try:
                self.logger.debug("Создание конфига для rathole")
                add_tunnel_to_rathole(self.tunnel_id, tunnel_secret)
            except Exception as config_error:
                self.logger.error(f"Ошибка при создании конфигурационного файла: {str(config_error)}")
                raise config_error
            
            # запуск rathole в отдельном потоке
            self.logger.debug("Запуск rathole в фоновом режиме")

            self.rathole = Rathole()

            threading.Thread(target=self.rathole.run, daemon=True).start()
            
            # запуск почтового сервера и получение сигналов
            self.logger.debug(f"Запуск почтового сервера с сертификатами для {self.subdomain}")

            certs_path = os.path.join(script_path(".certs"), self.subdomain)
            self.mail_controller, self.email_signals = mailserv.start(certs_path)
            
            # подключаем сигнал о новых письмах к обработчику
            self.email_signals.new_email_received.connect(self.handle_new_email)
            self.tunnel_setup_failed = False
        except Exception as e:
            self.logger.error(f"Ошибка в setupTunnel: {str(e)}", exc_info=True)
            self.tunnel_setup_failed = True
            self.tunnel_worker.error.emit(f"Ошибка при настройке туннеля: {str(e)}")


    def closeEvent(self, event):
        self.logger.info("Закрытие приложения")

        try:
            # удаление туннеля при закрытии
            if self.token:
                try:
                    delete_tunnel(self.token)
                except Exception as tunnel_error:
                    self.logger.warning(f"Не удалось удалить туннель при выходе: {str(tunnel_error)}")

            # остановка таймера
            if hasattr(self, 'ttl_timer') and self.ttl_timer.isActive(): # если сущ-т
                try:
                    self.logger.debug("Остановка TTL таймера")

                    self.ttl_timer.stop()
                except Exception as timer_error:
                    self.logger.warning(f"Ошибка при остановке таймера: {str(timer_error)}")

            # останавливаем почтовый сервер
            if hasattr(self, 'mail_controller'): # если сущ-т
                try:
                    self.logger.debug("Остановка почтового сервера")

                    self.mail_controller.stop()
                except Exception as mail_error:
                    self.logger.warning(f"Ошибка при остановке почтового сервера: {str(mail_error)}")

            # останавливаем rathole
            if hasattr(self, 'rathole'): # если сущ-т
                try:
                    self.logger.debug("Остановка rathole")

                    self.rathole.stop()
                except Exception as rh_error:
                    self.logger.warning(f"Ошибка при остановке rathole: {str(rh_error)}")
        except Exception as e:
            self.logger.error(f"Неожиданная ошибка при закрытии приложения: {str(e)}", exc_info=True)
        
        self.logger.info("Приложение завершено")
        event.accept()


    def tunnelCreated(self):
        try:
            if self.tunnel_setup_failed:
                return
            self.logger.info("Туннель создан успешно")
            # настройка экрана интерфейса почты
            self.email_interface_screen.setup_with_data(self.subdomain)
            
            # экран почтового интерфейса
            self.stacked_widget.setCurrentWidget(self.email_interface_screen)
            
            self.current_ttl = 0  
            self.seconds_counter = 0 
            
            self.updateTTL()
            
            # таймер
            self.ttl_timer = QtCore.QTimer()
            self.ttl_timer.timeout.connect(self.decrementTTL)
            self.ttl_timer.start(1000)
            self.logger.debug("TTL таймер запущен")
        except Exception as e:
            self.logger.error(f"Ошибка при настройке интерфейса после создания туннеля: {str(e)}", exc_info=True)
            self.showError(f"Туннель создан, но произошла ошибка при настройке интерфейса: {str(e)}")


    def updateTTL(self):
        # получение актуального ttl
        try:
            self.logger.debug(f"Запрос текущего TTL для туннеля {self.tunnel_id}")
            self.current_ttl = get_ttl(self.tunnel_id)
            self.email_interface_screen.update_ttl_display(self.current_ttl)
            self.seconds_counter = 0  # Сбрасываем счетчик секунд
            self.logger.debug(f"Текущий TTL: {self.current_ttl} секунд")
        except ConnectionError:
            self.logger.warning(f"Невозможно подключиться к серверу при updateTTL")
            self.email_interface_screen.show_ttl_error("сервер временно недоступен")
        except Exception as e:
            self.logger.warning(f"Ошибка при получении TTL: {str(e)}")
            self.email_interface_screen.show_ttl_error(str(e))


    def decrementTTL(self):
        try:
            self.seconds_counter += 1
            
            # синхронизация с сервером
            if self.seconds_counter >= 60:
                self.updateTTL()
                return

            if self.current_ttl > 0:
                self.current_ttl -= 1
                self.email_interface_screen.update_ttl_display(self.current_ttl)
                
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Ошибка при decrementTTL: {error_msg}")
    

    def addEmail(self, sender, subject, body, html_content=None):
        try:
            email = {
                "sender": sender,
                "subject": subject,
                "body": body,
                "html_content": html_content,  # м.б. None
                "timestamp": time.strftime("%d.%m.%Y %H:%M")
            }
            
            self.emails.append(email)
            
            self.email_interface_screen.add_email_to_list(email, len(self.emails) - 1)
            self.logger.debug(f"Письмо добавлено успешно, всего писем: {len(self.emails)}")
        except Exception as e:
            self.logger.error(f"Ошибка при добавлении письма: {str(e)}", exc_info=True)

    def handle_new_email(self, email_data):
        # обработчик нового письма
        try:
            self.logger.info(f"Получено новое письмо от: {email_data.get('sender', 'unknown')}")
            # добавляем письмо в интерфейс
            self.addEmail(
                email_data["sender"],
                email_data["subject"],
                email_data["body"],
                email_data.get("html_content", None)
            )
        except KeyError as ke:
            self.logger.error(f"Ошибка в структуре данных письма - отсутствует поле {str(ke)}", exc_info=True)
        except Exception as e:
            self.logger.error(f"Ошибка при обработке нового письма: {str(e)}", exc_info=True)

    
    def showError(self, error_msg):
        # отображение ошибки пользователю
        try:
            
            msg_box = QtWidgets.QMessageBox(self)
            msg_box.setIcon(QtWidgets.QMessageBox.Critical)
            msg_box.setWindowTitle("Ошибка")
            msg_box.setText(error_msg)
            msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
            
            msg_box.setStyleSheet("""
                QMessageBox {
                    /* background-color: #1e1e1e; */
                    color: #e0e0e0;
                }
                QMessageBox QLabel {
                    color: #e0e0e0;
                }
                QPushButton {
                    /* background-color: #3498db; */
                    color: white;
                    border: none;
                    padding: 5px 15px;
                    border-radius: 3px;
                }
            """)
            
            msg_box.exec_()
            self.stacked_widget.setCurrentWidget(self.email_main_screen)
        except Exception as e:
            # ошибка в отображении ошибки => логируем без вызова showError
            self.logger.critical(f"Критическая ошибка при отображении сообщения об ошибке: {str(e)}", exc_info=True)
            # пытаемся вернуться на главный экран
            try:
                self.stacked_widget.setCurrentWidget(self.email_main_screen)
            except:
                pass
