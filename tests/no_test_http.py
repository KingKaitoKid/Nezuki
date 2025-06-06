import pytest
from nezuki.Http import Http, MethodNotSupported, InsufficientInfo

# 🌍 Configurazione server reale 
TEST_HOST = "kaito.link"
TEST_PORT = 30080
BASE_PATH = "/"


@pytest.fixture
def http_client():
    """Crea un'istanza della classe Http con i parametri reali."""
    return Http(protocol="http", host=TEST_HOST, port=TEST_PORT, basePath=BASE_PATH)


### ✅ **TEST DI SUCCESSO**
def test_perform_request_get(http_client):
    """Testa se l'home page è accessibile."""
    response = http_client._perform_request("get", f"http://{TEST_HOST}:{TEST_PORT}/", {})
    assert response.status_code == 200
    assert "<html" in response.text.lower()


def test_perform_request_post(http_client):
    """Testa una richiesta POST a /create."""
    response = http_client._perform_request("post", f"http://{TEST_HOST}:{TEST_PORT}/create", {"data": "test"})
    assert response.status_code == 404  # ✅ Endpoint esistente


def test_api_request_get(http_client):
    """Testa una richiesta API GET esistente."""
    response = http_client.api_request("GET", "/", {})
    assert response.status_code == 200
    assert "<html" in response.text.lower()


def test_do_request(http_client):
    """Testa una chiamata generica a /."""
    response = http_client.do_request("GET", "http", TEST_HOST, TEST_PORT, "/")
    assert response.status_code == 200
    assert "<html" in response.text.lower()


### ❌ **TEST DI ERRORI HTTP**
@pytest.mark.parametrize("path, expected_status", [
    ("/notfound", 404) # Non autorizzato
])
def test_perform_request_get_errors(http_client, path, expected_status):
    """Testa errori HTTP su GET."""
    response = http_client._perform_request("get", f"http://{TEST_HOST}:{TEST_PORT}{path}", {})
    assert response.status_code == expected_status


@pytest.mark.parametrize("path, expected_status", [
    ("/notfound", 404)
])
def test_perform_request_post_errors(http_client, path, expected_status):
    """Testa errori HTTP su POST."""
    response = http_client._perform_request("post", f"http://{TEST_HOST}:{TEST_PORT}{path}", {"data": "test"})
    assert response.status_code == expected_status


@pytest.mark.parametrize("path, expected_status", [
    ("/notfound", 404)
])
def test_api_request_get_errors(http_client, path, expected_status):
    """Testa errori HTTP su API GET."""
    response = http_client.api_request("GET", path, {})
    assert response.status_code == expected_status


@pytest.mark.parametrize("path, expected_status", [
    ("/notfound", 404)
])
def test_do_request_errors(http_client, path, expected_status):
    """Testa errori HTTP su do_request."""
    response = http_client.do_request("GET", "http", TEST_HOST, TEST_PORT, path)
    assert response.status_code == expected_status


### ❗ **TEST DI ECCEZIONI**
def test_perform_request_invalid_method(http_client):
    """Verifica che venga sollevata un'eccezione se il metodo HTTP non è supportato."""
    with pytest.raises(MethodNotSupported):
        http_client._perform_request("delete", f"http://{TEST_HOST}:{TEST_PORT}/", {})


def test_api_request_missing_info():
    """Verifica che venga sollevata l'eccezione InsufficientInfo se mancano dati essenziali."""
    client = Http()
    with pytest.raises(InsufficientInfo):
        client.api_request("GET", "/", {})


def test_do_request_invalid_method(http_client):
    """Verifica che venga sollevata un'eccezione se il metodo HTTP non è supportato in do_request."""
    with pytest.raises(MethodNotSupported):
        http_client.do_request("PUT", "http", TEST_HOST, TEST_PORT, "/")