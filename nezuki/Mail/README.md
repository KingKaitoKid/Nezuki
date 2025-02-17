# 📧 Nezuki Mail - Modulo per l'invio di email

Il modulo **Mail** di Nezuki permette di inviare email tramite SMTP in modo semplice e flessibile, sia da codice Python che direttamente da terminale.

---

## 📌 **Caratteristiche principali**
✅ Invio email con supporto per destinatari multipli e CC
✅ Possibilità di passare i parametri SMTP o utilizzare un file di configurazione JSON
✅ Integrazione con il logging avanzato di Nezuki
✅ Compatibile con l'utilizzo da terminale come comando CLI (`email`)

---

## 🛠 **Installazione**
Se hai già installato il pacchetto **Nezuki**, il modulo `Mail` è già incluso.
Se non lo hai ancora, puoi installarlo con:

```sh
pip3 install nezuki
```

---

## 🚀 **Utilizzo in Python**

### 📌 **1. Creazione di un'istanza Mail**

Puoi passare direttamente la configurazione SMTP oppure utilizzare un file JSON specificato nella variabile d'ambiente `NEZUKIMAIL`.

```python
from nezuki.Mail import Mail

# Configurazione manuale SMTP
smtp_config = {
    "host": "smtp.example.com",
    "port": 587,
    "user": "your_email@example.com",
    "pass": "your_password",
    "root_email": "noreply@example.com"
}

mail_client = Mail(smtp_config)
```

Se non passi `smtp_config`, il modulo cercherà la variabile d'ambiente `NEZUKIMAIL`, che deve contenere il percorso di un file JSON con la configurazione SMTP.

Esempio di file JSON:
```json
{
    "host": "smtp.example.com",
    "port": 587,
    "user": "your_email@example.com",
    "pass": "your_password",
    "root_email": "noreply@example.com"
}
```

Esempio di definizione della variabile d'ambiente:
```sh
export NEZUKIMAIL="/path/to/smtp_config.json"
```

---

### 📌 **2. Invio di un'email**

```python
mail_client.send_mail(
    name_sender="Nezuki Bot",
    dest=["recipient@example.com"],
    obj="Test Email",
    body="Ciao, questa è una email di test inviata con Nezuki!",
    Cc=["cc@example.com"]
)
```

| Parametro    | Tipo          | Descrizione |
|-------------|--------------|-------------|
| `name_sender` | str | Nome del mittente (es. "Nezuki Bot") |
| `dest` | list\|str | Destinatari principali (lista o singola email) |
| `obj` | str | Oggetto dell'email |
| `body` | str | Corpo del messaggio |
| `Cc` | list\|str | (Opzionale) Indirizzi in CC |

---

## 🖥 **Utilizzo da Terminale**

Una volta installato il pacchetto, puoi inviare email direttamente da terminale con il comando `email`.

### 📌 **Esempio di utilizzo**
```sh
email --to recipient@example.com \
      --subject "Test Email" \
      --body "Ciao, questa è una email di test!" \
      --smtp_host smtp.example.com --smtp_port 587 \
      --smtp_user your_email@example.com --smtp_pass your_password \
      --root_email noreply@example.com
```

### 📌 **Utilizzo con `NEZUKIMAIL`**
Se la variabile d'ambiente `NEZUKIMAIL` è impostata con un file JSON valido, non è necessario specificare i parametri SMTP:
```sh
email --to recipient@example.com --subject "Test Email" --body "Ciao!"
```

| Opzione         | Descrizione |
|----------------|-------------|
| `--to`         | Indirizzo/i del destinatario (separati da virgola) |
| `--cc`         | (Opzionale) Indirizzo/i in CC |
| `--subject`    | Oggetto della mail |
| `--body`       | Contenuto della mail |
| `--smtp_host`  | Server SMTP (opzionale se `NEZUKIMAIL` è impostato) |
| `--smtp_port`  | Porta SMTP (opzionale se `NEZUKIMAIL` è impostato) |
| `--smtp_user`  | Username SMTP (opzionale se `NEZUKIMAIL` è impostato) |
| `--smtp_pass`  | Password SMTP (opzionale se `NEZUKIMAIL` è impostato) |
| `--root_email` | Email mittente (opzionale se `NEZUKIMAIL` è impostato) |

---

## 🚨 **Gestione degli Errori**

Il modulo intercetta gli errori più comuni e li registra tramite il logger di Nezuki.

- ❌ **SMTPAuthenticationError** → Errore di autenticazione SMTP.
- ❌ **SMTPRecipientsRefused** → I destinatari sono stati rifiutati dal server.
- ❌ **SMTPException** → Errore generico SMTP.
- ❌ **FileNotFoundError** → Il file JSON della configurazione SMTP non esiste.
- ❌ **ValueError** → I parametri SMTP non sono stati forniti né tramite argomenti né tramite `NEZUKIMAIL`.

Esempio di gestione degli errori:
```python
try:
    mail_client.send_mail(
        name_sender="Nezuki",
        dest="recipient@example.com",
        obj="Errore Test",
        body="Questa email serve a testare gli errori"
    )
except Exception as e:
    print(f"Errore nell'invio dell'email: {e}")
```

---

## 📜 **Conclusione**

Il modulo **Mail** di Nezuki semplifica l'invio di email sia da codice Python che da terminale, garantendo flessibilità nella configurazione e una gestione avanzata degli errori.

Se hai domande o problemi, apri un'**issue** su [GitHub](https://github.com/KingKaitoKid/Nezuki/issues). 🛠

---

📌 **Autore:** *Sergio Catacci*  
📌 **Versione:** *2.0.2*  
📌 **Licenza:** *MIT*  

---

📌 **Se ti è utile, lascia una ⭐ su [GitHub](https://github.com/KingKaitoKid/Nezuki)!** 😊

