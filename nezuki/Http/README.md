# 🌐 Http - Modulo per Chiamate HTTP

Il modulo **Http** permette di effettuare chiamate HTTP **GET** e **POST** in modo semplice e flessibile.  
Può essere utilizzato sia per chiamate singole, sia per interfacciarsi con API specifiche grazie ai parametri preconfigurabili.  

## 🚀 Installazione

Il modulo **Http** è incluso nel pacchetto **nezuki**. Per installarlo:

```sh
pip install nezuki
```

## 👀 Utilizzo 

### 🔹 Creazione di un'istanza Http

Puoi creare un'istanza per effettuare più chiamate alla stessa API.

```python
from nezuki.Http import Http

http_client = Http(protocol="https", host="api.example.com", port=443, basePath="/v1")
```

| Parametro  | Tipo   | Descrizione |
|------------|--------|-------------|
| `protocol` | str (`http`/`https`) | Protocollo della richiesta |
| `host`     | str    | Host dell'API (es. `api.example.com`) |
| `port`     | int    | Porta del server (80 per HTTP, 443 per HTTPS) |
| `basePath` | str    | Percorso fisso delle API (es. `/v1`) |
| `timeout`  | int    | Timeout della richiesta (default: 30s) |

---

### 🔹 Esecuzione di una chiamata API

#### 🔸 **Metodo `api_request`**  
Effettua una chiamata HTTP utilizzando i parametri dell'istanza.

```python
response = http_client.api_request(
    method="GET",
    path="/users",
    payload={},
    headers={"Authorization": "Bearer TOKEN123"}
)
print(response.json())
```

| Parametro  | Tipo   | Descrizione |
|------------|--------|-------------|
| `method`   | str (`GET`/`POST`) | Metodo della richiesta |
| `path`     | str    | Percorso API (es. `/users`) |
| `payload`  | dict   | Dati da inviare (se `POST`) |
| `headers`  | dict   | Headers opzionali |

---

### 🔹 Esecuzione di una chiamata generica

#### 🔸 **Metodo `do_request`**  
Esegue una richiesta HTTP senza utilizzare parametri preconfigurati.

```python
from nezuki.Http import Http

http_client = Http()

response = http_client.do_request(
    method="POST",
    protocol="https",
    host="api.example.com",
    port=443,
    path="/auth/login",
    payload={"username": "test", "password": "secure"},
    headers={"Content-Type": "application/json"}
)

print(response.status_code, response.json())
```

| Parametro  | Tipo   | Descrizione |
|------------|--------|-------------|
| `method`   | str (`GET`/`POST`) | Metodo della richiesta |
| `protocol` | str (`http`/`https`) | Protocollo della richiesta |
| `host`     | str    | Host della richiesta |
| `port`     | int    | Porta del server |
| `path`     | str    | Percorso API |
| `payload`  | dict   | Dati da inviare (se `POST`) |
| `headers`  | dict   | Headers opzionali |

---

## 🚨 Gestione degli Errori

Se il metodo non è supportato o i parametri sono insufficienti, verranno sollevate le seguenti eccezioni:

- ❌ `MethodNotSupported` → Il metodo HTTP non è tra quelli implementati (`GET`, `POST`).  
- ❌ `InsufficientInfo` → Mancano informazioni obbligatorie (`protocol`, `host`, `port`).  

Esempio di gestione degli errori:

```python
from nezuki.Http import Http, MethodNotSupported, InsufficientInfo

http_client = Http()

try:
    response = http_client.do_request("PUT", "https", "example.com", 443, "/test")
except MethodNotSupported as e:
    print(f"Errore: {e}")
except InsufficientInfo as e:
    print(f"Informazioni mancanti: {e}")
except Exception as e:
    print(f"Errore generico: {e}")
```

---

## 📜 **Conclusione**
Il modulo **Http** semplifica la gestione delle chiamate HTTP, permettendo di interfacciarsi rapidamente con API REST.

💡 *Se hai suggerimenti o segnalazioni, contribuisci al progetto su [GitHub](https://github.com/KingKaitoKid/Nezuki)!* 🚀

---

📌 **Autore:** *Sergio Catacci*  
📌 **Versione:** *2.0.2*  
📌 **Licenza:** *MIT*  

---

📌 **Se ti è utile, lascia una ⭐ su [GitHub](https://github.com/KingKaitoKid/Nezuki)!** 😊