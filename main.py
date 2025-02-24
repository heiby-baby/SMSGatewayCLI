import socket
import tomllib
import sys
import json
import base64
import logging

logging.basicConfig(
    level=logging.DEBUG,
    filename="SMSGatewayCLI.log",
    filemode="w",
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-32"
)
logger = logging.getLogger(__name__)


class HttpRequest:
    def __init__(self, method, url, headers, body):
        self.method = method
        self.url = url
        self.headers = headers
        self.body = body

    def to_bytes(self):
        headers_str = "\r\n".join([f"{k}: {v}" for k, v in self.headers.items()])
        path = self.__extract_path__(self.url)
        request_line = f"{self.method} {path} HTTP/1.1"
        return f"{request_line}\r\n{headers_str}\r\n\r\n{self.body}".encode()

    @classmethod
    def from_bytes(cls, binary_data):
        data = binary_data.decode()
        headers_end = data.find("\r\n\r\n")

        headers_part = data[:headers_end]
        body = data[headers_end + 4:]

        headers_lines = headers_part.split("\r\n")
        request_line = headers_lines[0]
        method, url, _ = request_line.split()

        headers = {}
        for line in headers_lines[1:]:
            if ": " in line:
                key, value = line.split(": ", 1)
                headers[key] = value

        return cls(method, url, headers, body)

    @classmethod
    def __extract_path__(self, url):
        if '://' in url:
            url = url.split('://', 1)[1]
        if '/' in url:
            url = url.split('/', 1)[1]
        return '/' + url if url else '/'

class HttpResponse:
    def __init__(self, status_code, headers, body):
        self.status_code = status_code
        self.headers = headers
        self.body = body

    @classmethod
    def from_bytes(cls, binary_data):
        data = binary_data.decode()
        headers_end = data.find("\r\n\r\n")
        headers = data[:headers_end].split("\r\n")
        status_code = int(headers[0].split()[1])
        headers_dict = {k: v for k, v in (line.split(": ") for line in headers[1:])}
        body = data[headers_end + 4:]
        return cls(status_code, headers_dict, body)

    @classmethod
    def to_bytes(cls, response):
        status_line = f"HTTP/1.1 {response.status_code}\r\n"
        headers = "\r\n".join(f"{k}: {v}" for k, v in response.headers.items())
        http_response = f"{status_line}{headers}\r\n\r\n{response.body}"
        return http_response.encode()


def send_sms(config: dict, sender: str, recipient: str, message: str) -> HttpResponse:
    address = config["address"]
    username = config["username"]
    password = config["password"]

    credentials = base64.b64encode((f"{username}:{password}").encode()).decode()

    body = json.dumps({
        "sender": sender,
        "recipient": recipient,
        "message": message
    })

    headers = {
        "Host": address.split('://')[1].split('/')[0],
        "Content-Type": "application/json",
        "Authorization": f"Basic {credentials}",
        "Content-Length": len(body)
    }

    request = HttpRequest("POST", address, headers, body)
    request_bytes = request.to_bytes()
    host_port = address.split('://')[1].split('/')[0]
    host, port = host_port.split(':')
    port = int(port)

    logger.debug(f"Подключение к {host}:{port}")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(request_bytes)
        response_bytes = s.recv(4096)
        logger.debug(f"Ответ от сервера: {response_bytes}")
        return HttpResponse.from_bytes(response_bytes)


def main():
    logger.debug("Программа запущена")

    if len(sys.argv) != 4:
        logger.critical(f"Количество введённых переменных: {len(sys.argv)}")
        print("Используйте формат: python SMSGatewayCLI.py <sender> <recipient> <message>")
        exit(1)

    sender = sys.argv[1]
    recipient = sys.argv[2]
    message = sys.argv[3]

    logger.debug(f"Введенные переменные: '{sender}' '{recipient}' '{message}'")

    try:
        with open("config.toml", "rb") as f:
            config = tomllib.load(f)
        logger.debug("Конфигурационный файл успешно загружен")
    except Exception as e:
        logger.error(f"Ошибка при загрузке конфигурационного файла: {e}")
        exit(1)

    response = send_sms(config, sender, recipient, message)

    logger.info(f"Код статуса: {response.status_code}")
    logger.info(f"Голова ответа: {json.dumps(response.headers, indent=4)}")
    logger.info(f"Тело ответа: {response.body}")

    print(f"Код статуса: {response.status_code}")
    print(f"Голова ответа: {json.dumps(response.headers, indent=4)}")
    print(f"Тело ответа: {response.body}")


if __name__ == '__main__':
    main()