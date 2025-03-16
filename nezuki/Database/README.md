# Database - Modulo Nezuki

Il modulo **Database** di Nezuki consente di connettersi a un database MySQL o PostgreSQL ed eseguire query in modo sicuro ed efficiente.

## ✨ **Caratteristiche**
- Supporta **MySQL** e **PostgreSQL**  
- Connessione sicura e gestione automatica degli errori  
- Supporta query parametrizzate per prevenire SQL Injection  
- Possibilità di ottenere i risultati in due formati:  
  - **Lista di valori** (senza nomi delle colonne)  
  - **Lista di dizionari** (con nomi delle colonne)  
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

# Creazione di un oggetto Database per PostgreSQL
db = Database(database="monitoring", db_type="postgresql")

# Impostazione dei parametri di connessione
db.connection_params(host="localhost", user="myuser", password="mypassword")

# Esecuzione di una query di selezione
query = "SELECT * FROM my_table WHERE id = %s"
params = (123,)

# Metodo che restituisce solo i valori (senza nomi delle colonne)
result = db.doQuery(query, params)

# Metodo che restituisce un dizionario con i nomi delle colonne
result_named = db.doQueryNamed(query, params)
```

### 🔹 **Differenza tra i metodi**
#### `doQuery()`: Restituisce solo i valori, senza nomi delle colonne
```json
{
    "ok": true,
    "results": [
        [123, "Mario Rossi", "mario@example.com"]
    ],
    "rows_affected": 1,
    "error": null,
    "lastrowid": null
}
```

#### `doQueryNamed()`: Restituisce un dizionario con i nomi delle colonne
```json
{
    "ok": true,
    "results": [
        {
            "id": 123,
            "nome": "Mario Rossi",
            "email": "mario@example.com"
        }
    ],
    "rows_affected": 1,
    "error": null,
    "lastrowid": null
}
```

Il metodo **doQueryNamed()** è utile quando si vuole ottenere un output strutturato e leggibile, mentre **doQuery()** è più leggero e veloce per elaborazioni che non necessitano di nomi di colonne.

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
- `port`: Porta del database (opzionale, default 3306 per MySQL e 5432 per PostgreSQL)  

Se la connessione ha successo, il database sarà pronto per eseguire query.

---

## 🔄 **Eseguire Query**
I due metodi disponibili per eseguire query sono:

### **1⃣ doQuery()**
Restituisce i risultati come lista di liste, senza nomi delle colonne.

```python
query = "SELECT id, nome, email FROM utenti WHERE id = %s"
params = (42,)

result = db.doQuery(query, params)
print(result)
```

### **Output**
```json
{
    "ok": true,
    "results": [
        [42, "Luca Verdi", "luca@example.com"]
    ],
    "rows_affected": 1,
    "error": null,
    "lastrowid": null
}
```

---

### **2⃣ doQueryNamed()**
Restituisce i risultati come lista di dizionari, includendo i nomi delle colonne.

```python
query = "SELECT id, nome, email FROM utenti WHERE id = %s"
params = (42,)

result_named = db.doQueryNamed(query, params)
print(result_named)
```

### **Output**
```json
{
    "ok": true,
    "results": [
        {
            "id": 42,
            "nome": "Luca Verdi",
            "email": "luca@example.com"
        }
    ],
    "rows_affected": 1,
    "error": null,
    "lastrowid": null
}
```

Entrambi i metodi supportano query **INSERT**, **UPDATE** e **DELETE**, con la gestione di `lastrowid` quando disponibile.

---

## ⚙ **Stored Procedure (CALL)**
Puoi eseguire stored procedure con entrambi i metodi:

```python
call_query = "CALL nome_procedura(%s, %s)"
params = (123, "valore")

result = db.doQuery(call_query, params)
```

Se la stored procedure restituisce un set di dati, usa `doQueryNamed()` per ottenere i nomi delle colonne.

---

## ❗ **Gestione degli Errori**
Se si verifica un errore (ad esempio, tabella inesistente o errore di connessione), il dizionario di risposta avrà `ok: false` e includerà il messaggio di errore:

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

## 📚 **Supporto e Contributi**
Se hai suggerimenti o bug da segnalare, apri un **issue** su [GitHub](https://github.com/KingKaitoKid/Nezuki).

---

📌 **Autore:** *Sergio Catacci*  
📌 **Versione:** *2.2.0*  
📌 **Licenza:** *MIT*  

---

📌 **Se ti è utile, lascia una ⭐ su [GitHub](https://github.com/KingKaitoKid/Nezuki)!** 😊