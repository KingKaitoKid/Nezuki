# 📜 Nezuki EncoderDecoder

Il pacchetto **EncoderDecoder** di Nezuki fornisce un insieme di strumenti per la **codifica** e **decodifica** di dati, supportando diverse tecniche come QR Code, hashing e crittografia AES.

---

## 📌 **Caratteristiche principali**
✅ Classe base `EncoderDecoder` per un'implementazione uniforme
✅ Supporto per **QR Code**, **hashing** (SHA, MD5, ecc.) e **crittografia AES**
✅ API semplice e intuitiva
✅ Logger integrato per una tracciabilità completa

---

## 🛠 **Installazione**
Se hai già installato il pacchetto **Nezuki**, il modulo `EncoderDecoder` è incluso.  
Se non lo hai ancora, puoi installarlo con:
```sh
pip install nezuki
```

---

## 🚀 **Utilizzo**
### 📌 **1. Creazione di un QR Code**
```python
from nezuki.EncoderDecoder import QRCode

qr = QRCode()
qr_code = qr.encode("https://kaito.link")
print("QR Code Base64:", qr_code)
```

---

### 📌 **2. Generazione di un hash**
```python
from nezuki.EncoderDecoder import Hash

hash_gen = Hash()
hash_value = hash_gen.encode("password123", algorithm="sha256")
print("SHA256 Hash:", hash_value)
```

---

### 📌 **3. Cifratura e Decifratura AES**
```python
from nezuki.EncoderDecoder import AES

aes_handler = AES()
cipher_text = aes_handler.encode("Messaggio segreto")
plain_text = aes_handler.decode(cipher_text)

print("Testo cifrato:", cipher_text)
print("Testo decifrato:", plain_text)
```

---

## 📜 **Componenti del Pacchetto**

| Modulo            | Funzione principale |
|-------------------|---------------------|
| `QRCode`         | Genera e legge QR Code |
| `Hash`           | Genera hash (SHA, MD5, ecc.) |
| `AES`            | Crittografia e decrittografia AES |
| `EncoderDecoder` | Classe base astratta per codifica/decodifica |

---

## 🔄 **Struttura del Pacchetto**
```sh
nezuki/EncoderDecoder/
├── __init__.py
├── EncoderDecoder.py
├── qrCode.py
├── hashGenerator.py
├── aesManager.py
```

---

## 📜 **Formato dei Log**
Ogni operazione viene registrata nel logger:
```
2025-02-17 12:34:56 - Nezuki - INFO - qrCode.py::QRCodeHandler::encode - [INTERNAL] - QR Code generato con successo.
```

---

## 📜 **Conclusione**
Questo modulo fornisce strumenti potenti e semplici per la gestione della codifica e crittografia dei dati. 🚀

Se hai domande o problemi, apri un'**issue** su [GitHub](https://github.com/KingKaitoKid/Nezuki/issues). 🛠

---

📌 **Autore:** *Sergio Catacci*  
📌 **Versione:** *1.0.0*  
📌 **Licenza:** *MIT*  

---

📌 **Se ti è utile, lascia una ⭐ su [GitHub](https://github.com/KingKaitoKid/Nezuki)!** 😊

