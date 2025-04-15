from contextlib import contextmanager
import traceback

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import josepy as jose
import OpenSSL

from acme import challenges
from acme import client
from acme import crypto_util
from acme import errors
from acme import messages
from acme import standalone
import socket

import requests
from app.config.constants import BASE_URL, DIRECTORY_URL_ZEROSSL, ZEROSSL_EAB_URL, DIRECTORY_URL_LE
from app.utils.logger import setup_logger

logger = setup_logger("cert_manager")

USER_AGENT = 'mailtunnel'
ACC_KEY_BITS = 2048
CERT_PKEY_BITS = 2048

def new_csr_comp(domain_name, pkey_pem=None):
    try:
        logger.debug(f"Создание CSR для домена {domain_name}")
        
        if pkey_pem is None:
            logger.debug("Генерация нового приватного ключа")
            pkey = rsa.generate_private_key(public_exponent=65537, key_size=CERT_PKEY_BITS)
            pkey_pem = pkey.private_bytes(encoding=serialization.Encoding.PEM,
                                         format=serialization.PrivateFormat.PKCS8,
                                         encryption_algorithm=serialization.NoEncryption())
        
        csr_pem = crypto_util.make_csr(pkey_pem, [domain_name])
        logger.debug("CSR успешно создан")
        
        return pkey_pem, csr_pem
    except Exception as e:
        logger.error(f"Ошибка при создании CSR: {str(e)}", exc_info=True)
        raise RuntimeError(f"Не удалось создать CSR для домена {domain_name}: {str(e)}")


def select_http01_chall(orderr):
    try:
        logger.debug("Поиск HTTP-01 challenge в авторизациях")
        authz_list = orderr.authorizations

        for authz in authz_list:
            for i in authz.body.challenges:
                if isinstance(i.chall, challenges.HTTP01):
                    logger.debug("HTTP-01 challenge найден")
                    return i
        
        logger.error("HTTP-01 challenge не был найден")
        raise Exception('HTTP-01 challenge was not offered by the CA server.')
    except Exception as e:
        if 'HTTP-01 challenge was not offered' in str(e):
            logger.error(f"Ошибка: {str(e)}")
            raise
        else:
            logger.error(f"Ошибка при выборе HTTP-01 challenge: {str(e)}", exc_info=True)
            raise RuntimeError(f"Не удалось выбрать HTTP-01 challenge: {str(e)}")


def send_verification_data(token, url_token, validation_token):
    try:
        logger.info("Отправка данных верификации на сервер")
        response = requests.post(
            f"{BASE_URL}/verify_subdomain", 
            json={
                "token": token,
                "url_token": url_token,
                "validation_token": validation_token
            },
            timeout=30
        )
        
        if response.status_code != 200:
            logger.error(f"Сервер вернул код {response.status_code}: {response.text}")
            response.raise_for_status()
            
        logger.debug("Данные верификации о сертификате успешно отправлены")
        return response
    except requests.RequestException as e:
        logger.error(f"Ошибка при отправке данных верификации: {str(e)}", exc_info=True)
        raise RuntimeError(f"Не удалось отправить данные верификации: {str(e)}")


def get_certificate(token, domain, developer_token=None, ca="le"):
    logger.debug(f"Запуск процесса получения сертификата для домена {domain}")

    if not ca in ["le", "zerossl"]:
        raise ValueError("ca should be either le (Let's Encrypt) or zerossl")
    
    try:
        privkey = rsa.generate_private_key(
            public_exponent=65537,
            key_size=ACC_KEY_BITS,
            backend=default_backend()
        )
        acc_key = jose.JWKRSA(key=privkey)

        try:
            net = client.ClientNetwork(acc_key, user_agent=USER_AGENT)

            if ca == "le":
                directory = client.ClientV2.get_directory(DIRECTORY_URL_LE, net)
            elif ca == "zerossl":
                directory = client.ClientV2.get_directory(DIRECTORY_URL_ZEROSSL, net)

            client_acme = client.ClientV2(directory, net=net)
        except Exception as e:
            logger.error(f"Ошибка при инициализации ACME клиента: {str(e)}", exc_info=True)

            raise RuntimeError(f"Не удалось инициализировать ACME клиент: {str(e)}")

        if ca == "zerossl":
            # получение eab от zerossl
            logger.debug("Запрос EAB credentials от ZeroSSL")

            try:
                eab_response = requests.post(
                    ZEROSSL_EAB_URL,
                    params={"access_key": developer_token},
                    timeout=30  # добавляем таймаут
                )
                
                if eab_response.status_code != 200:
                    logger.error(f"ZeroSSL API вернул код {eab_response.status_code}: {eab_response.text}")
                    eab_response.raise_for_status()
                    
                eab_json = eab_response.json()
                
                if "error" in eab_json:
                    error_msg = eab_json.get("error", {}).get("message", "Unknown error")
                    logger.error(f"ZeroSSL API вернул ошибку: {error_msg}")
                    raise RuntimeError(f"Ошибка ZeroSSL API: {error_msg}")
                    
            except requests.RequestException as e:
                logger.error(f"Ошибка при запросе EAB: {str(e)}", exc_info=True)
                raise RuntimeError(f"Не удалось получить EAB креденшалы от ZeroSSL: {str(e)}")

            # Создание eab
            try:
                eab = messages.ExternalAccountBinding.from_data(
                    acc_key,
                    eab_json["eab_kid"],
                    eab_json["eab_hmac_key"],
                    directory
                )
            except (KeyError, ValueError) as e:
                logger.error(f"Ошибка при создании EAB объекта: {str(e)}", exc_info=True)
                raise RuntimeError(f"Неверный формат EAB данных от ZeroSSL: {str(e)}")


        logger.debug("Регистрация нового ACME аккаунта")

        try:
            if ca == "zerossl":
                regr = client_acme.new_account(
                    messages.NewRegistration.from_data(
                        external_account_binding=eab,
                        terms_of_service_agreed=True
                    )
                )
            elif ca == "le":
                regr = client_acme.new_account(
                    messages.NewRegistration.from_data(
                        terms_of_service_agreed=True
                    )
                )

            logger.debug(f"Аккаунт ACME зарегистрирован: {regr.uri}")
        except errors.Error as e:
            logger.error(f"Ошибка при регистрации ACME аккаунта: {str(e)}", exc_info=True)
            raise RuntimeError(f"Не удалось зарегистрировать ACME аккаунт: {str(e)}")


        pkey_pem, csr_pem = new_csr_comp(domain)

        logger.debug("Создание нового запроса сертификата")

        try:
            orderr = client_acme.new_order(csr_pem)

            logger.debug(f"Заказ сертификата создан: {orderr.uri}")
        except errors.Error as e:
            logger.error(f"Ошибка при создании заказа сертификата: {str(e)}", exc_info=True)
            raise RuntimeError(f"Не удалось создать заказ сертификата: {str(e)}")

        # http-01 challenge
        logger.debug("Выбор HTTP-01 challenge")
        challb = select_http01_chall(orderr)

        url_token = challb.chall.encode("token")

        response, validation_token = challb.response_and_validation(client_acme.net.key)

        logger.debug("Отправка данных верификации")
        send_verification_data(token, url_token, validation_token)
    
        try:
            client_acme.answer_challenge(challb, response)
        except errors.Error as e:
            logger.error(f"Ошибка при ответе на answer_challenge: {str(e)}", exc_info=True)
            raise RuntimeError(f"Не удалось ответить на challenge: {str(e)}")

        logger.debug("Ожидание finalized_orderr сертификата")

        try:
            finalized_orderr = client_acme.poll_and_finalize(orderr)
            logger.debug("Сертификат успешно получен")
        except errors.Error as e:
            logger.error(f"Ошибка при финализации заказа сертификата: {str(e)}", exc_info=True)
            raise RuntimeError(f"Не удалось финализировать заказ сертификата: {str(e)}")

        fullchain_pem = finalized_orderr.fullchain_pem
        
        return fullchain_pem, pkey_pem.decode("utf-8")
    except Exception as e:
        logger.critical(f"Критическая ошибка при получении сертификата для {domain}: {str(e)}", exc_info=True)
        raise RuntimeError(f"Не удалось получить сертификат для {domain}: {str(e)}")
