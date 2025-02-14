# Database

Questo modulo permette di connettersi al Database, fare le query ed avere il risultato nel formato JSON.

**DATABASE SUPPORTATI**:
- MySQL
- PostgreSQL

## Esempio di utilizzo

Ecco un esempio di codice sull'utilizzo del modulo:

```python
from Nezuki import Database

# Creazione di un oggetto Database per MySQL
db = Database(database="monitoring", db_type="mysql")

# Impostazione dei parametri di connessione
db.connection_params(host="localhost", user="myuser", password="mypassword")

# Esecuzione di una query
query = "SELECT * FROM my_table WHERE id = %s"
params = (123, )
result = db.doQuery(query, params)
print(result)
```

### Output
Il metodo `doQuery` ritorna un dizionario contenente:
- `ok`: True se la query è stata eseguita con successo.
- `results`: Una lista di tuple con i risultati della query.
- `rows_affected`: Numero di righe interessate.
- `error`: Una stringa di errore (se presente).
- `lastrowid`: L'ID dell'ultima riga inserita (se applicabile).