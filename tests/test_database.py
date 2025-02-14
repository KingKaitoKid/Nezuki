import pytest
from nezuki.Database import Database

@pytest.fixture
def db():
    """Crea un'istanza del Database senza connessione attiva"""
    return Database(database="test_db", db_type="mysql")

def test_init(db):
    """Verifica che l'istanza venga creata correttamente"""
    assert db.database == "test_db"
    assert db.db_type == "mysql"
    assert db.auto_load is False
    assert db.errorDBConnection is False

def test_connection_params(mocker, db):
    """Testa la configurazione dei parametri di connessione"""
    mocker.patch.object(db, "start_connection", return_value="mock_connection")
    
    db.connection_params("localhost", "user", "password")
    
    assert db.configJSONNew["database"] == "test_db"
    assert db.configJSONNew["host"] == "localhost"
    assert db.configJSONNew["user"] == "user"
    assert db.configJSONNew["password"] == "password"
    assert db.connection == "mock_connection"

def test_do_query_select(mocker, db):
    """Simula una query di SELECT"""
    mock_cursor = mocker.Mock()
    mock_cursor.fetchall.return_value = [{"id": 1, "name": "test"}]
    mock_cursor.with_rows = True  # Simulazione MySQL
    mock_cursor.rowcount = 1  # Aggiunto valore numerico
    mock_connection = mocker.Mock()
    mock_connection.cursor.return_value = mock_cursor

    db.connection = mock_connection

    query = "SELECT * FROM users"
    result = db.doQuery(query)

    assert result["ok"] is True
    assert result["results"] == [{"id": 1, "name": "test"}]
    assert result["rows_affected"] >= 0  # Ora il valore sarà numerico

def test_do_query_insert(mocker, db):
    """Simula una query di INSERT"""
    mock_cursor = mocker.Mock()
    mock_cursor.rowcount = 1
    mock_cursor.lastrowid = 42
    mock_cursor.with_rows = False
    mock_connection = mocker.Mock()
    mock_connection.cursor.return_value = mock_cursor

    db.connection = mock_connection

    query = "INSERT INTO users (name) VALUES (%s)"
    result = db.doQuery(query, ("test_user",))

    assert result["ok"] is True
    assert result["rows_affected"] == 1
    assert result["lastrowid"] == 42