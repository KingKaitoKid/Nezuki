# 🚀 Guida allo Sviluppo di Nezuki

Benvenuto nello sviluppo di **Nezuki**! Questo documento fornisce le linee guida necessarie per garantire che le modifiche siano conformi agli standard del progetto, evitando problemi con le pipeline CI/CD e conflitti con il codice esistente.

---

## 📌 **Regole Generali**

- **Branching:** Tutti gli sviluppi devono partire da `develop`. Non fare commit diretti su `main`.
- **Feature Branch:** Ogni nuova funzionalità o bugfix deve essere sviluppata in un branch separato con nome descrittivo.🔹 Esempi:
  ```
  feature/tmdb-integration
  bugfix/fix-authentication
  refactor/logging-improvements
  ```
- **Pull Request (PR):** Tutte le modifiche devono passare attraverso una PR verso `develop` e devono essere approvate da almeno un revisore.
- **Formato dei Commit:** Usa un formato chiaro e descrittivo per i commit.
  ✅ Esempio:
  ```
  feat(api): aggiunto supporto a TMDB
  fix(auth): corretto bug nel login con passkey
  refactor(db): migliorata gestione connessione MySQL
  ```

---

## 🛠 **Setup dell'Ambiente di Sviluppo**

1. **Clona il repository:**

   ```sh
   git clone https://github.com/KingKaitoKid/Nezuki.git
   cd Nezuki
   ```
2. **Crea e attiva un ambiente virtuale:**

   ```sh
   python3 -m venv .venv
   source .venv/bin/activate  # Su Windows usa .venv\Scripts\activate
   ```
3. **Installa le dipendenze di sviluppo:**

   ```sh
   pip install -r requirements.txt
   ```
4. **Installa il pacchetto in modalità sviluppo:**

   ```sh
   pip install -e .
   ```

---

## ✅ **Check Pre-Commit**

Prima di effettuare un commit, esegui i seguenti controlli per evitare errori nelle pipeline:

### 🔹 **Linting & Code Style**

Assicurati che il codice sia formattato correttamente:

```sh
black nezuki/
flake8 nezuki/
```

Se Black modifica i file, ricordati di fare un nuovo commit.

---

## 🛠 **Testing**

Esegui i test prima di inviare una PR:

```sh
pytest --cov=nezuki --cov-report=term-missing
```

Se il coverage è troppo basso o un test fallisce, correggi il problema prima di pushare.

---

## 🚀 **Linee Guida per le PR**

1. **Mantieni il codice pulito e ben documentato.**
2. **Aggiorna la documentazione** (se necessario) prima di creare la PR.
3. **Assicurati che la pipeline passi senza errori.**
4. **Aggiorna il CHANGELOG.md** se hai aggiunto nuove feature o fix.

---

## 🔄 **Gestione delle Versioni**

- Il numero di versione si trova in `version.txt` e segue **Semantic Versioning** (`MAJOR.MINOR.PATCH`).
- Se fai una modifica significativa, assicurati di aggiornare la versione **prima** di creare la PR.

---

## 🗑 **Rimozione dei Branch**

Dopo che una PR è stata mergeata su `develop`, il branch di partenza verrà eliminato automaticamente.

---

## 🚨 **Evita questi errori comuni**

❌ **Commit direttamente su `develop` o `main`** → Usa un feature branch.
❌ **Push senza testare il codice** → Esegui sempre i test prima di pushare.
❌ **Dimenticare di aggiornare il CHANGELOG.md** → Se aggiungi nuove feature, documentale.
❌ **Ignorare il linting** → Il codice mal formattato blocca la pipeline.

---

## 💚 **Supporto**

Se hai dubbi o incontri problemi:

- Controlla le [Issue](https://github.com/KingKaitoKid/Nezuki/issues)
- Contatta il team su Discord o Telegram.

Grazie per contribuire a **Nezuki**! 🎉🔥
