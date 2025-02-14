# 📦 JsonManager - Gestione Avanzata di JSON

Il modulo **JsonManager** di Nezuki permette di leggere, modificare e interrogare strutture JSON in modo semplice e potente, utilizzando JSONPath per navigare tra i dati.

---

## 🚀 **Installazione**
Se hai già installato il pacchetto **Nezuki**, il modulo `JsonManager` è incluso.

Se non lo hai ancora, installalo con:
```sh
pip install nezuki
```

---

## 📌 **Funzionalità Principali**
- Lettura e parsing automatico di file JSON
- Interrogazione con **JSONPath** per accedere facilmente ai dati
- Modifica dinamica di valori all'interno di JSON complessi
- Supporto per stringhe JSON, file e liste
- Log avanzati per il debug e il tracciamento delle operazioni

---

## 📜 **Utilizzo**

### 🔹 **Creazione di un'istanza JsonManager**

Puoi creare un'istanza a partire da una stringa JSON, un file o un dizionario.

```python
from nezuki.JsonManager import JsonManager

# Creazione a partire da un dizionario JSON
json_data = {
    "utente": "Sergio",
    "eta": 28,
    "linguaggi": ["Python", "Go", "JavaScript"]
}

manager = JsonManager(json_data)
```

| Parametro  | Tipo   | Descrizione |
|------------|--------|-------------|
| `json_data` | dict / str / list | JSON di partenza (stringa, file, dizionario, lista) |

---

### 🔹 **Lettura da file JSON**

Se hai un file JSON e vuoi caricarlo:

```python
manager = JsonManager("/percorso/al/file.json")
```

---

### 🔹 **Recuperare valori da JSON con JSONPath**

```python
valore = manager.retrieveKey("$.linguaggi[0]")
print(valore)  # "Python"
```

| Parametro | Tipo | Descrizione |
|-----------|------|-------------|
| `key` | str | Espressione JSONPath per recuperare dati |

💡 **Esempi JSONPath**:
- `$.utente` → Recupera il valore della chiave `utente`
- `$.linguaggi[*]` → Recupera tutti i valori nell'array `linguaggi`

---

### 🔹 **Modificare un valore all'interno del JSON**

```python
manager.updateKey("$.linguaggi[0]", "Rust")
print(manager.data)  # Aggiorna il valore "Python" con "Rust"
```

| Parametro | Tipo | Descrizione |
|-----------|------|-------------|
| `pattern` | str | Espressione JSONPath della chiave da aggiornare |
| `valore`  | any | Nuovo valore da assegnare |

---

## 🚨 **Gestione degli Errori**

Se un'operazione non riesce, JsonManager cattura e registra l'errore con il sistema di logging interno di Nezuki.

Esempio di gestione manuale degli errori:
```python
try:
    valore = manager.retrieveKey("$.chiave_inesistente")
    if not valore:
        print("Chiave non trovata")
except Exception as e:
    print(f"Errore: {e}")
```

---

## 🎯 **Conclusione**
Il modulo **JsonManager** di Nezuki semplifica la gestione dei dati JSON, offrendo strumenti avanzati per la manipolazione e interrogazione.

Se hai domande o problemi, apri un'**issue** su [GitHub](https://github.com/KingKaitoKid/Nezuki/issues). 🛠

---

📌 **Autore:** *Sergio Catacci*  
📌 **Versione:** *2.0.2*  
📌 **Licenza:** *MIT*  

📌 **Se ti è utile, lascia una ⭐ su [GitHub](https://github.com/KingKaitoKid/Nezuki)!** 😊

