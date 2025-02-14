# Database - Modulo Nezuki

Il modulo **Database** di Nezuki consente di connettersi a un database MySQL o PostgreSQL ed eseguire query in modo sicuro.

## ✨ **Caratteristiche**
- Supporta **MySQL** e **PostgreSQL**
- Connessione sicura e gestione automatica degli errori
- Supporta query parametrizzate per prevenire SQL Injection
- Recupero risultati in formato JSON
- Supporto per stored procedure (`CALL`)

---

## 📺 **Installazione**
Il modulo è incluso in **Nezuki**, quindi basta installare il pacchetto:

```bash
pip install Nezuki
```

---

## 🚀 **Esempio di utilizzo**

```python
from nezuki.Database import Database

# Creazione di un oggetto Database per MySQL
db = Database(database="monitoring", db_type="mysql")

# Impostazione dei parametri di connessione
db.connection_params(host="localhost", user="myuser", password="mypassword")

# Esecuzione di una query di selezione
query = "SELECT * FROM my_table WHERE id = %s"
params = (123,)
result = db.doQuery(query, params)

print(result)
```

### 🔹 **Output Previsto**
Il metodo `doQuery` ritorna un **dizionario JSON** con la seguente struttura:

```json
{
    "ok": true,
    "results": [
        {"id": 123, "nome": "Esempio", "email": "test@example.com"}
    ],
    "rows_affected": 1,
    "error": null,
    "lastrowid": null
}
```

---

## 🔋 **Connessione e Configurazione**
Prima di eseguire una query, è necessario **configurare la connessione**:

```python
db.connection_params(host="localhost", user="myuser", password="mypassword")
```

**Parametri:**
- `host`: Indirizzo IP o hostname del database
- `user`: Nome utente del database
- `password`: Password dell'utente
- `database`: Nome del database

Se la connessione ha successo, il database sarà pronto per eseguire query.

---

## 🔄 **Eseguire Query**
Il metodo **doQuery()** permette di eseguire query di qualsiasi tipo (SELECT, INSERT, UPDATE, DELETE):

```python
# Esempio di inserimento
insert_query = "INSERT INTO utenti (nome, email) VALUES (%s, %s)"
params = ("Mario Rossi", "mario@example.com")

result = db.doQuery(insert_query, params)
print(result)
```

### **Output**
```json
{
    "ok": true,
    "results": [],
    "rows_affected": 1,
    "error": null,
    "lastrowid": 42
}
```

- Se è una query **SELECT**, `results` conterrà i risultati.
- Se è una query **INSERT**, `lastrowid` conterrà l'ID della riga inserita.

---

## ⚙ **Stored Procedure (CALL)**
Puoi eseguire stored procedure con il metodo **doQuery()**:

```python
call_query = "CALL nome_procedura(%s, %s)"
params = (123, "valore")
result = db.doQuery(call_query, params)
```

---

## ❗ **Gestione degli Errori**
Se si verifica un errore (ad es. tabella inesistente, errore di connessione), il dizionario di risposta avrà `ok: false` e includerà il messaggio di errore:

```json
{
    "ok": false,
    "results": [],
    "rows_affected": -1,
    "error": "Table 'my_table' doesn't exist"
}
```

---

## 🚫 **Chiusura Connessione**
La connessione viene **chiusa automaticamente** alla distruzione dell'oggetto **Database**:

```python
del db  # Chiude la connessione al database
```

---

## 📃 **Supporto e Contributi**
Se hai suggerimenti o bug da segnalare, apri un **issue** su [GitHub](https://github.com/KingKaitoKid/Nezuki).

---

📌 **Autore:** *Sergio Catacci*  
📌 **Versione:** *2.0.2*  
📌 **Licenza:** *MIT*  

---

📌 **Se ti è utile, lascia una ⭐ su [GitHub](https://github.com/KingKaitoKid/Nezuki)!** 😊

