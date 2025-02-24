import pytest
from main import HttpRequest, HttpResponse


# Тесты для класса HttpRequest
def test_http_request_to_bytes():
    headers = {"Content-Type": "application/json", "Authorization": "Basic auth"}
    request = HttpRequest("POST", "http://example.com/api", headers, '{"key":"value"}')
    expected = b'POST /api HTTP/1.1\r\nContent-Type: application/json\r\nAuthorization: Basic auth\r\n\r\n{"key":"value"}'
    assert request.to_bytes() == expected


def test_http_request_from_bytes():
    data = b'POST /api HTTP/1.1\r\nContent-Type: application/json\r\nAuthorization: Basic auth\r\n\r\n{"key":"value"}'
    request = HttpRequest.from_bytes(data)
    assert request.method == "POST"
    assert request.url == "/api"
    assert request.headers["Content-Type"] == "application/json"
    assert request.body == '{"key":"value"}'

def test_http_request___extract_path___1():
    data = "http://localhost:4010/send_sms"
    expected = "/send_sms"
    assert HttpRequest.__extract_path__(data) == expected

def test_http_request___extract_path___2():
    data = "http://localhost:4010/"
    expected = "/"
    assert HttpRequest.__extract_path__(data) == expected

# Тесты для класса HttpResponse
def test_http_response_from_bytes():
    data = b'HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n{"status":"ok"}'
    response = HttpResponse.from_bytes(data)
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    assert response.body == '{"status":"ok"}'


def test_http_response_to_bytes():
    response = HttpResponse(200, {"Content-Type": "application/json"}, '{"status":"ok"}')
    expected = b'HTTP/1.1 200\r\nContent-Type: application/json\r\n\r\n{"status":"ok"}'
    assert HttpResponse.to_bytes(response) == expected


if __name__ == "__main__":
    pytest.main()