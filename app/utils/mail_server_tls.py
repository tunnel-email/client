import asyncio
import ssl
import email
import threading
import time
import os
from aiosmtpd.controller import Controller
from aiosmtpd.smtp import SMTP
from email.policy import default
from email.utils import parseaddr

from app.config.constants import SMTPD_LOGGING

from Qt import QtCore 
import logging, sys


def configure_smtpd_logging():
    stderr_handler = logging.StreamHandler(sys.stderr)
    logger = logging.getLogger("mail.log")
    fmt = "[%(asctime)s %(levelname)s] %(message)s"
    datefmt = None
    formatter = logging.Formatter(fmt, datefmt, "%")
    stderr_handler.setFormatter(formatter)
    logger.addHandler(stderr_handler)
    logger.setLevel(logging.DEBUG)

if SMTPD_LOGGING:
    configure_smtpd_logging()


class EmailSignals(QtCore.QObject):
    new_email_received = QtCore.Signal(dict)

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

    fc_path = os.path.join(certs_path, "fullchain.pem")
    pk_path = os.path.join(certs_path, "privkey.pem")

    ssl_context.load_cert_chain(fc_path, pk_path)

    # запуск
    controller = Controller(
        EmailHandler(),
        hostname='0.0.0.0',
        port=port,
        server_kwargs={
            'tls_context': ssl_context,
            'require_starttls': True,
            'timeout': 15
        }
    )
    
    # запуск в отдельном потоке
    server_thread = threading.Thread(target=run_server, args=(controller,), daemon=True)
    server_thread.start()
    
    return controller, email_signals

def run_server(controller):
    controller.start()
    try:
        while True:
            time.sleep(1)
    except Exception as e:
        print(f"Ошибка сервера: {e}")
    finally:
        controller.stop()

