from datetime import timedelta
import json
import re
from flask import Flask, jsonify, request, session
from fido2.webauthn import PublicKeyCredentialCreationOptions, PublicKeyCredentialRequestOptions, AttestationObject, CollectedClientData
from fido2.server import Fido2Server
from fido2 import cbor
from flask.sessions import NullSession
from flask_cors import CORS
import os
import base64
from Database import Database
from commonLogId import *
# from fido2.attestation import AttestationObject

class WebAuthnServer:
    def __init__(self, rp_id, rp_name, secret_key=None):
        self.rp = {"id": rp_id, "name": rp_name}
        self.fido2_server = Fido2Server(rp=self.rp, verify_origin=False)
        self.users = {}  # Memorizzazione degli utenti
        self.logger = get_logger(True, os.path.dirname(__file__))
        print("Fido2Server inizializzato con RP ID:", self.rp['id'], "e RP Name:", self.rp['name'])

        self.db = Database("", "DEV", "passkeys")

        # Configurazione di Flask
        self.app = Flask(__name__)
        CORS(self.app, supports_credentials=True, origins=["http://localhost:3000"])
        self.app.config['SESSION_COOKIE_SAMESITE'] = 'None'
        self.app.config['SESSION_COOKIE_SECURE'] = False  # Solo per sviluppo locale
        self.app.permanent_session_lifetime = timedelta(minutes=30)  # Configura la durata della sessione
        print(secret_key, " è il secret \n")
        self.app.secret_key = secret_key or os.getenv('SECRET_KEY', 'default_secret')

        # Definizione delle route
        self.setup_routes()

    # Funzione che converte i dati binari in una stringa base64
    @staticmethod
    def bytes_to_base64(data):
        if isinstance(data, bytes):
            return base64.b64encode(data).decode('utf-8')
        return data

    def setup_routes(self):
        app = self.app

        @app.route("/register", methods=["POST"])
        def register():
            username = request.json.get("username")
            if not username:
                return jsonify({"error": "Il nome utente è richiesto"}), 401
            
            # Crea le opzioni di registrazione WebAuthn
            registration_data, state = self.fido2_server.register_begin(
                {
                    "id": username.encode("utf-8"),
                    "name": username,
                    "displayName": username,
                },
                user_verification="discouraged",
            )
            
            # Stampa i dati per vedere il contenuto
            print("Dati di registrazione originali:", registration_data)

            # Salva lo stato della registrazione nella sessione
            session["state"] = state
            session.permanent = True
            print("State: ", session['state'])
            
            # Conversione del campo 'challenge' e 'user.id' in base64 solo per il JSON di risposta
            response_data = {
                "publicKey": {
                    "rp": registration_data.public_key.rp,
                    "user": {
                        "id": self.bytes_to_base64(registration_data.public_key.user.id),  # Converte user.id
                        "name": registration_data.public_key.user.name,
                        "displayName": registration_data.public_key.user.display_name
                    },
                    "challenge": self.bytes_to_base64(registration_data.public_key.challenge),  # Converte challenge
                    "pub_key_cred_params": registration_data.public_key.pub_key_cred_params,
                    "timeout": registration_data.public_key.timeout,
                    "exclude_credentials": registration_data.public_key.exclude_credentials,
                    "authenticator_selection": registration_data.public_key.authenticator_selection,
                    "attestation": registration_data.public_key.attestation,
                    "extensions": registration_data.public_key.extensions,
                }
            }
            
            # Restituisci i dati di registrazione come JSON
            return jsonify(response_data)
        
        def fix_base64_padding(data):
            # Rimuovi caratteri non validi se presenti
            data = re.sub(r'[^A-Za-z0-9+/=]', '', data)

            print(f"Stringa Base64 originale: {data}")  # Log della stringa originale

            # Controllo sulla lunghezza della stringa
            if len(data) % 4 == 1:
                raise ValueError("La stringa Base64 non può avere una lunghezza che risulti 1 in più di un multiplo di 4.")

            # Aggiungi padding solo se la lunghezza non è divisibile per 4
            if len(data) % 4 != 0:
                data += '=' * (4 - len(data) % 4)

            print(f"Stringa Base64 con padding: {data}")  # Log della stringa con padding
            return data
        
        def base64_urlsafe_to_standard(data):
            # Converte '-' in '+' e '_' in '/'
            data = data.replace('-', '+').replace('_', '/')
            
            # Aggiungi il padding se necessario
            padding_needed = 4 - (len(data) % 4)
            if padding_needed:
                data += '=' * padding_needed

            return data

        @app.route("/register/complete", methods=["POST"])
        def register_complete():
            try:
                print("Richiesta ricevuta dal client")
                print("Sessione attuale prima del completamento:", dict(session))

                # Decodifica i dati JSON dalla richiesta
                data = json.loads(request.data.decode('utf-8'))
                print(f"Dati decodificati dal client: {data}")

                # Recupera lo stato della sessione
                state = session.get("state", None)
                if not state:
                    return jsonify({"error": "Stato non trovato"}), 418

                # Verifica che i campi attesi siano presenti
                if "attestationObject" not in data:
                    print("Errore: mancano attestationObject")
                    return jsonify({"error": "Dati mancanti"}), 400

                if "clientDataJSON" not in data:
                    print("Errore: mancano clientDataJSON")
                    return jsonify({"error": "Dati mancanti"}), 401

                # Converte Base64 URL-safe in Base64 standard
                attestation_object_str = base64_urlsafe_to_standard(data["attestationObject"])
                client_data_json_str = base64_urlsafe_to_standard(data["clientDataJSON"])

                # Decodifica Base64
                attestation_object_bytes = base64.b64decode(attestation_object_str)
                client_data_json_str = base64.b64decode(client_data_json_str)

                print(f"Lunghezza attestationObject: {len(attestation_object_bytes)}")
                attestation_object = AttestationObject(attestation_object_bytes)

                # CollectedClientData viene creato direttamente con la stringa JSON decodificata
                client_data_json = CollectedClientData(client_data_json_str)
                raw_id = data["rawId"]

                print(f"ClientDataJSON dopo la deserializzazione: {client_data_json}")
                print(f"Origin da clientDataJSON: {client_data_json.origin}")
                # Completa la registrazione sul server
                auth_data = self.fido2_server.register_complete(
                    state=state,
                    attestation_object=attestation_object,
                    client_data=client_data_json
                )

                # Inserisci l'utente nel database
                username = request.json.get("username")
                self.db.doQuery("INSERT INTO users (username, display_name) VALUES (%s, %s)", (username, username))
                user_id = self.db.doQuery("SELECT id FROM users WHERE username = %s", (username,))['results'][0][0]

                self.db.doQuery("INSERT INTO credentials (user_id, credential_id, credential_public_key, sign_count, credential_data) VALUES(%s, %s, %s, %s, %s)", 
                    (user_id, raw_id, auth_data.credential_data.public_key, auth_data.credential_data.sign_count, auth_data.credential_data))

                return jsonify({"success": True})

            except Exception as e:
                print(f"Errore durante la registrazione: {e}")
                raise e
                return jsonify({"error": str(e)}), 500

        @app.route("/login", methods=["POST"])
        def login():
            username = request.json.get("username")
            if username not in self.users:
                return jsonify({"error": "Utente non trovato"}), 404

            auth_data, state = self.fido2_server.authenticate_begin([self.users[username]])
            
            # Stampa i dati per vedere il contenuto
            print("Dati di autenticazione originali:", auth_data)

            session["state"] = state

            # Converti tutti i campi che potrebbero essere di tipo bytes in base64
            auth_data = {k: self.bytes_to_base64(v) if isinstance(v, bytes) else v for k, v in auth_data.items()}
            
            return jsonify(auth_data)

        @app.route("/login/complete", methods=["POST"])
        def login_complete():
            data = cbor.decode(request.data)
            state = session.pop("state", None)

            if not state:
                return jsonify({"error": "Stato non trovato"}), 400

            auth_data = self.fido2_server.authenticate_complete(
                state,
                self.users[data["username"]],
                data["credentialId"],
                data["clientDataJSON"],
                data["authenticatorData"],
                data["signature"],
            )

            return jsonify({"success": True})

    def get_app(self):
        return self.app

# Funzione per creare l'app che Gunicorn può richiamare
def create_app():
    server = WebAuthnServer(
        rp_id=os.getenv("RP_IDs", "localhost"),
        rp_name='Pass Key Authorization Server',
        secret_key=os.getenv("SECRET_KEY", "default_secret")
    )
    return server.get_app()

app = create_app()