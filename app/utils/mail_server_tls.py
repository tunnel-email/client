import asyncio
import ssl
import email
import threading
import time
from aiosmtpd.controller import Controller
from aiosmtpd.smtp import SMTP
from email.policy import default
from email.utils import parseaddr

from PyQt5.QtCore import QObject, pyqtSignal

class EmailSignals(QObject):
    new_email_received = pyqtSignal(dict)

email_signals = EmailSignals()

# обработчик писем 
class EmailHandler:
    async def handle_RCPT(self, server, session, envelope, address, rcpt_options):
        envelope.rcpt_tos.append(address)
        return '250 OK'

    async def handle_DATA(self, server, session, envelope):
        # содержимое письма
        message_data = envelope.content.decode('utf-8', errors='replace')
        
        # парсим письмо
        message = email.message_from_string(message_data, policy=default)
        
        html_body, plain_body = self._get_body(message)
        
        # адрес отправителя
        from_header = message.get("From", "")
        sender_name, sender_email = parseaddr(from_header)
        
        sender = sender_email if sender_email else envelope.mail_from
        
        email_data = {
            "sender": sender,
            "sender_name": sender_name,
            "subject": message.get("Subject", "(Без темы)"),
            "body": html_body if html_body else plain_body,  # Приоритет HTML
            "html_content": html_body if html_body else None,
            "plain_content": plain_body,
            "timestamp": message.get("Date", ""),
            "recipients": envelope.rcpt_tos
        }
        
        # сигнал в основной поток
        email_signals.new_email_received.emit(email_data)
        
        return '250 Message accepted for delivery'
    
    def _get_body(self, message):
        # извлекаем html и обычный текст
        html_content = None
        plain_content = None
        
        if message.is_multipart():
            for part in message.walk():
                content_type = part.get_content_type()
                
                if content_type == "text/html" and html_content is None:
                    payload = part.get_payload(decode=True)
                    if payload:
                        html_content = payload.decode('utf-8', errors='replace')
                        
                elif content_type == "text/plain" and plain_content is None:
                    payload = part.get_payload(decode=True)
                    if payload:
                        plain_content = payload.decode('utf-8', errors='replace')
        else:
            content_type = message.get_content_type()
            payload = message.get_payload(decode=True)
            
            if payload:
                decoded_payload = payload.decode('utf-8', errors='replace')
                if content_type == "text/html":
                    html_content = decoded_payload
                elif content_type == "text/plain":
                    plain_content = decoded_payload
                    
        return html_content, plain_content


def start(certs_path, port=8025):
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain(f'{certs_path}/fullchain.pem', f'{certs_path}/privkey.pem')

    # запуск
    controller = Controller(
        EmailHandler(),
        hostname='0.0.0.0',
        port=port,
        server_kwargs={
            'tls_context': ssl_context,
            'require_starttls': True
        }
    )
    
    # запуск в отдельном потоке
    server_thread = threading.Thread(target=run_server, args=(controller,), daemon=True)
    server_thread.start()
    
    return controller, email_signals

def run_server(controller):
    controller.start()
    try:
        # Бесконечный цикл для поддержания работы сервера
        while True:
            time.sleep(1)  # Обычный sleep вместо asyncio
    except Exception as e:
        print(f"Ошибка сервера: {e}")
    finally:
        controller.stop()
