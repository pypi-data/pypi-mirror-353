import os
import re
import logging
from base64 import b64encode
from os.path import basename
from requests import post
from dotenv import load_dotenv

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Whats77:
    COUNTRY_CODE = "55"
    EXPECTED_LENGTH_NUMBER = 11
    STATE_NUMBER = '9'
    WHATSAPP_NUMBER_PATTERN = r'^55\d{11}$|^\d{12}$'

    SEND_TEXT = "/send-text"
    SEND_AUDIO = "/send-audio"
    SEND_DOCUMENT = "/send-document"
    SEND_IMAGE = "/send-image"

    def __init__(self, instance_id=None, token=None, security_token=None):
        load_dotenv()
        self.instance_id = instance_id or os.getenv("INSTANCE_ID")
        self.token = token or os.getenv("TOKEN")
        self.security_token = security_token or os.getenv("SECURITY_TOKEN")
        self.base_url_api = None
        self._validate_credentials()
        self._set_base_url_api()

    def _validate_credentials(self):
        if not self.instance_id:
            raise ValueError("O 'instance_id' não foi configurado.")
        if not self.token:
            raise ValueError("O 'token' não foi configurado.")

    def _set_base_url_api(self):
        self.base_url_api = f"https://api.z-api.io/instances/{self.instance_id}/token/{self.token}"
        logger.info(f"Base URL configurada: {self.base_url_api}")

    @staticmethod
    def normalize_phone_number(number: str) -> str:
        clean_number = re.sub(r'\D', '', number)
        if len(clean_number) == 10:
            clean_number = Whats77.STATE_NUMBER + clean_number
        elif len(clean_number) == Whats77.EXPECTED_LENGTH_NUMBER and not clean_number.startswith(Whats77.COUNTRY_CODE):
            clean_number = Whats77.COUNTRY_CODE + clean_number
        return clean_number

    @staticmethod
    def is_valid_whatsapp_number(number: str) -> bool:
        return re.match(Whats77.WHATSAPP_NUMBER_PATTERN, number) is not None

    def send_text(self, phone_number: str, message: str) -> None:
        url = f"{self.base_url_api}{self.SEND_TEXT}"
        payload = {"phone": phone_number, "message": message}
        self._send_request(url, payload)

    def send_audio(self, phone_number: str, base64_audio: str) -> None:
        url = f"{self.base_url_api}{self.SEND_AUDIO}"
        payload = {"phone": phone_number, "audio": base64_audio}
        self._send_request(url, payload)

    @staticmethod
    def parse_to_base64(file_path: str) -> str:
        with open(file_path, 'rb') as file:
            return b64encode(file.read()).decode()

    def send_document(self, phone_number: str, file_path: str, document_type: str = 'pdf', caption: str = None) -> None:
        file_name = basename(file_path)
        base64_file = self.parse_to_base64(file_path)
        payload = {
            'phone': phone_number,
            'document': f"data:application/{document_type};base64,{base64_file}",
            'fileName': file_name,
            'caption': caption
        }
        url = f"{self.base_url_api}{self.SEND_DOCUMENT}/{document_type}"
        self._send_request(url, payload)

    def send_image(self, phone_number: str, image_path_or_url: str, caption: str = None, view_once: bool = False, is_base64: bool = False) -> None:
        if is_base64:
            extension = image_path_or_url.split('.')[-1].lower()
            mime_type = f"image/{extension if extension != 'jpg' else 'jpeg'}"
            base64_image = self.parse_to_base64(image_path_or_url)
            image_data = f"data:{mime_type};base64,{base64_image}"
        else:
            image_data = image_path_or_url

        payload = {
            "phone": phone_number,
            "image": image_data,
            "caption": caption,
            "viewOnce": view_once
        }

        url = f"{self.base_url_api}{self.SEND_IMAGE}"
        self._send_request(url, payload)

    def _send_request(self, url: str, payload: dict) -> None:
        headers = {'Client-Token': self.security_token}
        try:
            response = post(url, json=payload, headers=headers)
            response.raise_for_status()
            logger.info(f"Envio para {payload.get('phone')} bem-sucedido: {response.json()}")
        except Exception as e:
            logger.error(f"Erro ao enviar para {payload.get('phone')}: {e}")
