import os
import json
import pytest
from unittest import mock
import smtplib
from nezuki.Mail import Mail


@pytest.fixture
def mock_env_and_file():
    """🔹 Mock della variabile d'ambiente e del file JSON di configurazione SMTP"""
    mock_smtp_config = {
        "host": "smtp.mail.me.com",
        "port": 587,
        "user": "api_infr@icloud.com",
        "pass": "***",
        "root_email": "api_infr@icloud.com"
    }

    with mock.patch.dict(os.environ, {"NEZUKIMAIL": "/server/smtp.json"}):
        with mock.patch("builtins.open", mock.mock_open(read_data=json.dumps(mock_smtp_config))):
            with mock.patch("json.load", return_value=mock_smtp_config):
                yield mock_smtp_config


@pytest.fixture
def mail_client(mock_env_and_file):
    """Inizializza un'istanza della classe Mail usando il mock della variabile d'ambiente"""
    return Mail()


def test_mail_init_env(mail_client, mock_env_and_file):
    """Testa che la configurazione SMTP venga letta correttamente dalla variabile d'ambiente mockata."""
    assert mail_client.smtp_host == mock_env_and_file["host"]
    assert mail_client.smtp_port == mock_env_and_file["port"]
    assert mail_client.user == mock_env_and_file["user"]
    assert mail_client.password == mock_env_and_file["pass"]
    assert mail_client.root_mail == mock_env_and_file["root_email"]


def test_mail_init_direct():
    """Testa l'inizializzazione passando direttamente la configurazione SMTP."""
    smtp_config = {
        "host": "smtp.test.com",
        "port": 587,
        "user": "test_user",
        "pass": "test_password",
        "root_email": "noreply@test.com"
    }
    mail = Mail(smtp_config=smtp_config)

    assert mail.smtp_host == smtp_config["host"]
    assert mail.smtp_port == smtp_config["port"]
    assert mail.user == smtp_config["user"]
    assert mail.password == smtp_config["pass"]
    assert mail.root_mail == smtp_config["root_email"]


def test_mail_init_missing_env():
    """Testa che venga sollevato un errore se né i parametri SMTP né NEZUKIMAIL sono forniti."""
    with mock.patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError, match="Errore: Né i parametri SMTP né la variabile d'ambiente NEZUKIMAIL sono forniti!"):
            Mail()


def test_mail_send_mock(mocker, mail_client):
    """Testa l'invio dell'email usando un mock del server SMTP."""
    mock_smtp = mocker.patch("smtplib.SMTP", autospec=True)
    mock_smtp_instance = mock_smtp.return_value.__enter__.return_value  # ✅ Correzione!

    # Assicura che i metodi siano intercettati e chiamati correttamente
    mock_smtp_instance.starttls.return_value = None
    mock_smtp_instance.login.return_value = None
    mock_smtp_instance.send_message.return_value = None

    
    mail_client.send_mail(
        sender_name="Test Sender",
        dest="receiver@test.com",
        subject="Test Email",
        body="Questa è una mail di test"
    )

    # 🔹 Verifica che SMTP sia stato chiamato con i giusti parametri
    mock_smtp.assert_called_once_with(mail_client.smtp_host, mail_client.smtp_port)
        
    mock_smtp_instance.starttls.assert_called_once()
    
    mock_smtp_instance.login.assert_called_once_with(mail_client.user, mail_client.password)
    
    mock_smtp_instance.send_message.assert_called_once()
    
def test_mail_send_auth_error(mocker, mail_client):
    """Testa il comportamento quando si verifica un errore di autenticazione SMTP."""
    mock_smtp = mocker.patch("smtplib.SMTP", autospec=True)
    mock_smtp_instance = mock_smtp.return_value.__enter__.return_value  # ✅ Correzione!

    # Simula l'errore di autenticazione
    mock_smtp_instance.starttls.return_value = None
    mock_smtp_instance.login.side_effect = smtplib.SMTPAuthenticationError(535, "Autenticazione fallita")

    # ✅ Mock del logger per verificare il messaggio di errore
    mock_logger = mocker.patch.object(mail_client.logger, "error")

    
    # ✅ Esegui la funzione senza aspettarti che l'errore venga propagato
    mail_client.send_mail(
        sender_name="Test Sender",
        dest="receiver@test.com",
        subject="Test Email",
        body="Questa è una mail di test"
    )

    # ✅ Verifica che il login abbia sollevato l'errore
    mock_smtp_instance.starttls.assert_called_once()
    mock_smtp_instance.login.assert_called_once_with(mail_client.user, mail_client.password)

    # ✅ Assicura che il logger abbia registrato l'errore
    mock_logger.assert_called_once()
    assert "Errore SMTP durante l'invio" in mock_logger.call_args[0][0]

    
