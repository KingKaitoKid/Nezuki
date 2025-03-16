import asyncio, datetime
from typing import List, Optional
from fastapi import FastAPI, WebSocket, Query, WebSocketDisconnect
import json
import asyncpg
from nezuki.Logger import configure_nezuki_logger, get_nezuki_logger
# Configura il logger
custom_config = {
    "file": {
        "filename": "/server/new_managment/services/logs/api_service.log",
        "maxBytes": 100 * 1024 * 1024,  
        "backupCount": 5,
        "when": "D",
        "interval": 1
    }
}
configure_nezuki_logger(custom_config)
logger = get_nezuki_logger()

from nezuki.Database import Database

# Mantiene i nodi che hanno ricevuto un update
pending_nodes = set()
debounce_time = 0.2  # Tempo di attesa per cumulare notifiche (200ms)

# Configura il Database
db = Database(database="monitoring", db_type="postgresql")

app = FastAPI(title="Monitoring API", description="API per il recupero delle metriche di sistema in tempo reale.")

async def fetch_latest_metrics(node_id: Optional[int] = None, limit: int = 10):
    """Recupera le ultime `limit` metriche per ogni categoria di un nodo specifico o di tutti i nodi, includendo hostname e IP"""
    
    # Recuperiamo tutti i nodi
    nodes_query = "SELECT id, hostname, ip_address FROM nodes"
    if node_id:
        nodes_query += f" WHERE id = {node_id}"
    
    result = db.doQueryNamed(nodes_query)
    nodes_info = {}

    if result["ok"] and result["results"]:
        nodes_info = {
            row["id"]: {"hostname": row["hostname"], "ip_address": row["ip_address"]}
            for row in result["results"]
        }
    
    # Se non ci sono nodi, restituiamo un JSON vuoto
    if not nodes_info:
        return {}

    queries = {
        "cpu": "SELECT * FROM cpu_metrics {} ORDER BY timestamp DESC LIMIT %s",
        "ram": "SELECT * FROM ram_metrics {} ORDER BY timestamp DESC LIMIT %s",
        "temperature": "SELECT * FROM temperature_metrics {} ORDER BY timestamp DESC LIMIT %s",
        "fans": "SELECT * FROM fan_metrics {} ORDER BY timestamp DESC LIMIT %s",
        "network": "SELECT * FROM network_metrics {} ORDER BY timestamp DESC LIMIT %s",
        "power": "SELECT * FROM power_metrics {} ORDER BY timestamp DESC LIMIT %s",
        "storage": "SELECT * FROM storage_metrics {} ORDER BY timestamp DESC LIMIT %s",
        "node": "SELECT * FROM node_metrics {} ORDER BY timestamp DESC LIMIT %s"
    }

    metrics_data = []

    for node_id in nodes_info:
        node_metrics = {}
        condition = f"WHERE node_id = {node_id}"

        for key, query in queries.items():
            formatted_query = query.format(condition)
            params = (limit,)

            result = db.doQueryNamed(formatted_query, params)
            if result["ok"] and result["results"]:
                node_metrics[key] = result["results"]
            else:
                node_metrics[key] = []

        # Associa le metriche ai dettagli del nodo
        metrics_data.append({
            "node_id": node_id,
            "hostname": nodes_info[node_id]["hostname"],
            "ip_address": nodes_info[node_id]["ip_address"],
            "metrics": node_metrics
        })

    return metrics_data

def serialize_data(data):
    """Converte i tipi non serializzabili in JSON (es. datetime)."""
    if isinstance(data, datetime.datetime):
        return data.isoformat()  # Converte datetime in stringa ISO 8601
    elif isinstance(data, list):
        return [serialize_data(item) for item in data]
    elif isinstance(data, dict):
        return {key: serialize_data(value) for key, value in data.items()}
    return data  # Per gli altri tipi lascia invariato

@app.websocket("/ws/metrics")
async def websocket_metrics(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket connesso, in attesa di notifiche da PostgreSQL.")

    # Recupera la lista di tutti i nodi con hostname e IP all'avvio
    nodes_query = "SELECT id, hostname, ip_address FROM nodes"
    result = db.doQueryNamed(nodes_query)

    if result["ok"] and result["results"]:
        nodes_info = {row["id"]: {"hostname": row["hostname"], "ip_address": row["ip_address"]} for row in result["results"]}
    else:
        nodes_info = {}

    # Set per accumulare i nodi aggiornati
    pending_nodes = set()
    debounce_time = 0.5  # 500ms di attesa per raggruppare gli aggiornamenti
    processing_updates = False  # Flag per evitare esecuzioni concorrenti

    async def process_updates():
        """Invia i dati aggiornati in batch dopo il debounce"""
        nonlocal processing_updates
        if processing_updates:
            return  # Evita di avviare più cicli concorrenti
        processing_updates = True

        while True:
            await asyncio.sleep(debounce_time)  # Attendi un breve periodo per accumulare gli update

            if pending_nodes:
                nodes_to_update = list(pending_nodes)
                pending_nodes.clear()  # Pulisce il set dopo la copia

                # Recupera le metriche aggiornate per i nodi modificati
                updates = await fetch_latest_metrics(limit=1)
                await websocket.send_json({"nodes": updates})

            processing_updates = False  # Permette il prossimo ciclo

    async def handle_update(conn, pid, channel, payload):
        """Accoda gli aggiornamenti e li raggruppa per inviarli in batch"""
        nonlocal pending_nodes
        logger.info(f"Notifica ricevuta: {payload}")
        data = json.loads(payload)

        node_id = data.get("node_id")
        if node_id:
            pending_nodes.add(node_id)  # Aggiunge il nodo alla lista di aggiornamento
            asyncio.create_task(process_updates())  # Avvia il debounce

    try:
        connection = await db.as_start_connection()
        conn = await connection
        await conn.add_listener("metrics_update", handle_update)
        await asyncio.Future()  # Mantieni aperto il WebSocket
    except Exception as e:
        logger.error(f"Errore WebSocket: {e}")
    finally:
        await conn.close()

@app.get("/metrics")
async def get_metrics(
    limit: int = Query(10, ge=1), 
    node_id: Optional[int] = None
):
    """Endpoint HTTP per recuperare le metriche più recenti con filtri opzionali"""
    latest_metrics = await fetch_latest_metrics(node_id, limit)
    return {"nodes": latest_metrics}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=18000)