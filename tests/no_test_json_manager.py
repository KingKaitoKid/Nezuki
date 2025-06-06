import pytest
import json
from nezuki.JsonManager import JsonManager


@pytest.fixture
def sample_json():
    """JSON di esempio per i test."""
    return {
        "utente": {
            "nome": "Sergio",
            "età": 28
        },
        "hobby": ["programmazione", "anime", "gaming"]
    }


@pytest.fixture
def json_manager(sample_json):
    """Istanzia un JsonManager con il JSON di esempio."""
    return JsonManager(sample_json)


def test_init_empty():
    """Verifica l'inizializzazione con JSON vuoto."""
    manager = JsonManager()
    assert manager.data == {}


def test_init_dict(sample_json):
    """Verifica l'inizializzazione con un dizionario."""
    manager = JsonManager(sample_json)
    assert manager.data == sample_json


def test_load_data_from_string():
    """Verifica il caricamento del JSON da stringa."""
    json_str = '{"chiave": "valore", "numero": 42}'
    manager = JsonManager(json_str)
    assert manager.data == {"chiave": "valore", "numero": 42}


def test_load_data_invalid():
    """Verifica il comportamento con JSON non valido."""
    manager = JsonManager("{chiave: valore}")  # JSON non valido
    assert manager.data == {}  # Deve restituire un JSON vuoto


def test_retrieve_existing_key(json_manager):
    """Test per il recupero di una chiave esistente."""
    assert json_manager.retrieveKey("$.utente.nome") == "Sergio"


def test_retrieve_non_existing_key(json_manager):
    """Test per il recupero di una chiave inesistente."""
    assert json_manager.retrieveKey("$.utente.cognome") == []


def test_update_existing_key(json_manager):
    """Test per aggiornare una chiave esistente."""
    assert json_manager.updateKey("$.utente.nome", "Andrea") is True
    assert json_manager.retrieveKey("$.utente.nome") == "Andrea"


def test_update_non_existing_key(json_manager):
    """Test per aggiornare una chiave inesistente."""
    assert json_manager.updateKey("$.utente.cognome", "Rossi") is False


def test_read_json_file(mocker):
    """Test per leggere un file JSON."""
    json_mock = '{"chiave": "valore"}'
    mocker.patch("builtins.open", mocker.mock_open(read_data=json_mock))
    mocker.patch("os.path.exists", return_value=True)

    manager = JsonManager("dummy.json")
    assert manager.data == {"chiave": "valore"}


def test_read_json_file_not_found(mocker):
    """Test per il caso in cui il file JSON non esiste."""
    mocker.patch("os.path.exists", return_value=False)
    
    manager = JsonManager("non_esiste.json")
    assert manager.data == {}


def test_read_json_file_invalid_json(mocker):
    """Test per il caso di un file JSON non valido."""
    mocker.patch("builtins.open", mocker.mock_open(read_data="{chiave: valore}"))
    mocker.patch("os.path.exists", return_value=True)

    manager = JsonManager("invalid.json")
    assert manager.data == {}


def test_update_key_with_nested_json():
    """Test per aggiornare un valore annidato."""
    json_data = {
        "config": {
            "theme": "dark",
            "language": "it"
        }
    }
    manager = JsonManager(json_data)
    assert manager.updateKey("$.config.language", "en") is True
    assert manager.retrieveKey("$.config.language") == "en"


def test_update_key_with_list():
    """Test per aggiornare un valore in una lista JSON."""
    json_data = {
        "items": [
            {"id": 1, "name": "Item1"},
            {"id": 2, "name": "Item2"}
        ]
    }
    manager = JsonManager(json_data)
    assert manager.updateKey("$.items[0].name", "UpdatedItem") is True
    assert manager.retrieveKey("$.items[0].name") == "UpdatedItem"