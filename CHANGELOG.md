# Changelog

Tutte le modifiche a questo progetto saranno documentate in questo file.

Il formato seguente è ispirato a [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) e al Semantic Versioning.

---

## [Unreleased]
### Overview
- **Added:**
  - Nuovo modulo TMDB per futura integrazione (previsto rilascio in versione 2.5.0).
- **Changed:**
  - **BREAKING CHANGE** La connessione al DB deve essere passata esplicitamente mediante funzione `connection_params` per rimozione file property
- **Deprecated:**
  - Il modulo Common è stato rimosso; le funzioni correlate sono state spostate in `Nezuki/versioning.py`.
- **Fixed:**
  - Il comportamento di `import *` ora include tutti i moduli di Nezuki.
- **Security:**
  - Niente di specifico da riportare

<details>
  <summary>Dettagli specifici per Moduli</summary>

### Database
- **Removed:**
  - Dipendenza dal file property; La connessione al DB deve essere passata esplicitamente mediante funzione `connection_params`
  - Dipendenza dall'`env`
  - Dipendenza del logger

</details>

---

## [1.0.0] - 2025-02-06
### Added
- Rilascio iniziale di Nezuki, migrazione as-is dei componenti esistenti.
  - Componenti migrati:
    1. APIModules
    2. Bot
    3. commonLoggerSingleTon
    4. commonLogId
    5. Common
    6. Database
    7. Documentor
    8. File
    9. GeneratoreCodici
    10. HomeConnection
    11. Http
    12. JsonManager
    13. LogContext
    14. Logger
    15. Mail
    16. PassKey
    17. PyModules
    18. QrCode
    19. ServerUtils
    20. TelegramApi
    21. TelegramParser
    22. Telegram
    23. WebLogsViewer
    24. YamlManager

### Changed
- Nessuna modifica rispetto alla versione iniziale (release as-is).

### Deprecated
- Alcune classi verranno riviste e potenzialmente dismesse nelle prossime release (da definire durante la fase di refactoring).

### Removed
- Nessun componente rimosso in questa versione.

### Fixed
- Bug minori riscontrati durante il processo di migrazione.

### Security
- Nessuna modifica di sicurezza.

---
