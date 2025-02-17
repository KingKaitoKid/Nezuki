# 📜 Nezuki Logger

Il modulo **Logger** di Nezuki fornisce un sistema di logging avanzato che permette di registrare messaggi con informazioni dettagliate sul contesto di esecuzione, supportando sia la console che file log con rotazione automatica.

---

## 📌 **Caratteristiche principali**
✅ Formattazione avanzata con informazioni sul chiamante  
✅ Supporto per console e file log con rotazione automatica  
✅ Possibilità di configurazione personalizzata o utilizzo di un logger di default  
✅ Filtro automatico per distinguere log utente e log interni  

---

## 🛠 **Installazione**
Se hai già installato il pacchetto **Nezuki**, il modulo `Logger` è incluso.  
Se non lo hai ancora, puoi installarlo con:
```sh
pip3 install nezuki
```

---

## 🚀 **Utilizzo**
Puoi configurare il logger di Nezuki o utilizzare un'istanza di default.  
Ecco alcuni esempi di utilizzo:

### 📌 **1. Configurare il logger personalizzato**
Puoi configurare un logger con le impostazioni desiderate e utilizzarlo nei tuoi moduli.

```python
from nezuki.Logger import configure_nezuki_logger, get_nezuki_logger

# Configurazione personalizzata del logger
custom_config = {
    "file": {
        "filename": "/var/www/test_py/Logs.log",  # Percorso file log
        "maxBytes": 100 * 1024 * 1024,  # 100MB
        "backupCount": 5,  # Numero di backup
        "when": "D",  # Rotazione giornaliera
        "interval": 1  # Ogni giorno
    }
}

# Configura il logger globale
configure_nezuki_logger(custom_config)

# Ottieni il logger configurato
logger = get_nezuki_logger()

logger.info("Questo è un log utente.")
logger.debug("Questo è un log interno di debug.", extra={"internal": True})
```

---

### 📌 **2. Utilizzare il logger senza parametri**
Se nessuna configurazione è fornita, verrà usata una variabile d'ambiente `NEZUKILOGS` in cui ci sono le informazioni minime per il funzionamento dei log, la configurazione minima è presentata nel punto 1

```python
from nezuki.Logger import get_nezuki_logger

logger = get_nezuki_logger()

logger.info("Messaggio informativo di default")
logger.error("Errore critico!")
``` 

---

## 📜 **Formato del Log**
Ogni log scritto segue un formato dettagliato:
```
2025-02-14 11:33:40 - Nezuki - INFO - test_script.py::MyClass::my_function - [USER] - Questo è un messaggio utente.
```

🔹 **Dove:**  
- `2025-02-14 11:33:40` → Data e ora  
- `Nezuki` → Nome del logger  
- `INFO` → Livello del log  
- `test_script.py::MyClass::my_function` → File, classe e funzione che ha generato il log  
- `[USER]` → Indica se il log è dell'utente o interno  
- `"Questo è un messaggio utente."` → Contenuto del log  

---

## 🔄 **Rotazione dei Log**
Il logger supporta la **rotazione automatica** dei log basata su:
1. **Dimensione** (`maxBytes`): Se il file supera la dimensione specificata, viene creato un nuovo file.
2. **Tempo** (`when`, `interval`): I file log vengono ruotati periodicamente (es. ogni giorno).

Esempio di file log generati:
```
Logs.log
Logs.log.1
Logs.log.2
```

---

## ⚙ **Parametri di Configurazione**
Puoi personalizzare la configurazione del logger tramite il dizionario `config`:

| Chiave             | Tipo       | Descrizione                                         | Default |
|--------------------|-----------|-----------------------------------------------------|---------|
| `level`           | `str`      | Livello di logging (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`) | `DEBUG` |
| `console.enabled`  | `bool`     | Abilita o disabilita la stampa su console | `True` |
| `console.level`    | `str`      | Livello minimo di logging per la console | `DEBUG` |
| `file.enabled`     | `bool`     | Abilita o disabilita la scrittura su file | `True` |
| `file.filename`    | `str`      | Percorso del file log (🔴 Obbligatorio se `file.enabled=True`) | `None` |
| `file.level`       | `str`      | Livello minimo di logging per il file | `DEBUG` |
| `file.maxBytes`    | `int`      | Dimensione massima del file prima della rotazione | `100MB` |
| `file.backupCount` | `int`      | Numero massimo di file di backup mantenuti | `5` |
| `file.when`        | `str`      | Periodicità della rotazione (`S`, `M`, `H`, `D`, `W0-W6`) | `"D"` |
| `file.interval`    | `int`      | Ogni quanti giorni/ore/minuti fare la rotazione | `30` |

---

## 🔗 **Esempi di Livelli di Log**
| Metodo                 | Livello | Descrizione |
|------------------------|---------|-------------|
| `logger.debug(msg)`    | `DEBUG` | Messaggi di debug dettagliati |
| `logger.info(msg)`     | `INFO`  | Informazioni generali |
| `logger.warning(msg)`  | `WARNING` | Avvisi potenziali problemi |
| `logger.error(msg)`    | `ERROR` | Errori che richiedono attenzione |
| `logger.critical(msg)` | `CRITICAL` | Errori gravi che potrebbero interrompere il sistema |

---

## 📜 **Conclusione**
Questo modulo fornisce un sistema di logging potente e flessibile, facilmente integrabile nei tuoi progetti. 🚀

Se hai domande o problemi, apri un'**issue** su [GitHub](https://github.com/KingKaitoKid/Nezuki/issues). 🛠

---

📌 **Autore:** *Sergio Catacci*  
📌 **Versione:** *2.0.2*  
📌 **Licenza:** *MIT*  

---

📌 **Se ti è utile, lascia una ⭐ su [GitHub](https://github.com/KingKaitoKid/Nezuki)!** 😊

