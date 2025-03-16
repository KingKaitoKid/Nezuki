import os
import psutil
import time
import socket
import subprocess, re
import json
import netifaces

from nezuki.Logger import configure_nezuki_logger, get_nezuki_logger
custom_config = {
    "file": {
        "filename": "/server/new_managment/services/logs/MonitoringSystemCore_service.log",
        "maxBytes": 100 * 1024 * 1024,  # 100MB
        "backupCount": 5,
        "when": "D",
        "interval": 1  # Ogni giorno
    }
}
configure_nezuki_logger(custom_config)
logger = get_nezuki_logger()

from nezuki.Database import Database


# Configura il database Nezuki
db = Database(database="monitoring", db_type="postgresql")

def get_cpu_temperature():
    """Rileva la temperatura della CPU"""
    try:
        temp = subprocess.check_output("cat /sys/class/thermal/thermal_zone0/temp", shell=True)
        logger.info(f"Temperatura CPU {(int(temp) / 1000.0)}°C")
        return int(temp) / 1000.0  # Converti da millesimi di grado
    except Exception:
        logger.error("Errore nel recupero informazione temperatura")
        return None  # Se fallisce, restituisce None

def get_ip_address():
    """Ottiene l'IP locale sulla rete"""
    interfaces = netifaces.interfaces()
    for iface in interfaces:
        addrs = netifaces.ifaddresses(iface)
        if netifaces.AF_INET in addrs:
            for addr in addrs[netifaces.AF_INET]:
                ip = addr['addr']
                if ip != "127.0.0.1" and not ip.startswith("169.254"):  # Evita loopback e indirizzi APIPA
                    logger.info(f"IP Address: {ip}")
                    return ip
    return "Unknown"

def get_cpu_info():
    """Raccoglie informazioni dettagliate sulla CPU"""
    cpu_freq = psutil.cpu_freq()
    logger.info(f"Core fisici: {psutil.cpu_count(logical=False)}, logici: {psutil.cpu_count(logical=True)}. Frequenza: {round(cpu_freq.current, 2) if cpu_freq else None}, CPU usata: {psutil.cpu_percent(interval=1)}. Temperatura: {get_cpu_temperature()}°C")
    return {
        "physical_cores": psutil.cpu_count(logical=False),
        "logical_cores": psutil.cpu_count(logical=True),
        "frequency": {
            "current_mhz": round(cpu_freq.current, 2) if cpu_freq else None,
            "min_mhz": round(cpu_freq.min, 2) if cpu_freq else None,
            "max_mhz": round(cpu_freq.max, 2) if cpu_freq else None,
        },
        "usage": {
            "total_percent": psutil.cpu_percent(interval=1),
            "per_core_percent": psutil.cpu_percent(percpu=True, interval=1)
        },
        "temperature_celsius": get_cpu_temperature()
    }

def get_fan_info():
    """Raccoglie le informazioni sulle ventole (se disponibili)"""
    try:
        fans = psutil.sensors_fans()
        return {k: [{"label": fan.label, "speed_rpm": fan.current} for fan in v] for k, v in fans.items()} if fans else None
    except Exception:
        return None

def get_temperature_info():
    """Raccoglie le temperature dei sensori"""
    try:
        temperatures = psutil.sensors_temperatures()
        return {k: [{"label": t.label, "temp_c": t.current} for t in v] for k, v in temperatures.items()} if temperatures else None
    except Exception:
        return None

def get_storage_usage(mount_point="/"):
    """Restituisce l'utilizzo di un disco in GB e percentuale"""
    try:
        usage = psutil.disk_usage(mount_point)
        logger.info(f"Memoria interna usata: {round(usage.used / (1024**3), 2)}GB ({round(usage.percent, 2)}%), disponibile: {round(usage.free / (1024**3), 2)}, Totale: {round(usage.total / (1024**3), 2)}")
        return {
            "total_gb": round(usage.total / (1024**3), 2),
            "used_gb": round(usage.used / (1024**3), 2),
            "free_gb": round(usage.free / (1024**3), 2),
            "percent_used": round(usage.percent, 2)
        }
    except Exception:
        return None

def get_external_storage_info():
    """Rileva solo dispositivi di archiviazione esterni montati leggendo da /proc/mounts."""
    devices = {}

    # Otteniamo tutti i dispositivi montati dal file di sistema
    mounted_devices = {}
    try:
        with open("/proc/mounts", "r") as f:
            for line in f.readlines():
                parts = line.split()
                if parts[0].startswith("/dev/sd"):  # Considera solo i dischi esterni
                    mounted_devices[parts[0]] = parts[1]  # /dev/sdc1 -> /media/usb
    except Exception as e:
        print(f"Errore nel leggere /proc/mounts: {e}")

    # Ora raccogliamo informazioni per i dispositivi montati
    for dev_name, mount_point in mounted_devices.items():
        try:
            usage = get_storage_usage(mount_point)
            devices[dev_name] = {
                "label": "Unknown",  # lsblk non fornisce label, si può aggiungere se necessario
                "mount_status": "Mounted",
                "mount_point": mount_point,
                "total_gb": usage["total_gb"] if usage else None,
                "used_gb": usage["used_gb"] if usage else None,
                "free_gb": usage["free_gb"] if usage else None,
                "percent_used": usage["percent_used"] if usage else None
            }
        except Exception as e:
            print(f"Errore nel recuperare informazioni per {dev_name}: {e}")

    return devices if devices else None

def get_gvfs_mounted_devices():
    """Rileva i dispositivi montati tramite GVFS/UDisks2 (GNOME, KDE)."""
    devices = {}

    try:
        gvfs_output = subprocess.check_output("gvfs-mount -li", shell=True, text=True)
        for line in gvfs_output.split("\n"):
            if "Mount(" in line:
                parts = line.split("'")
                if len(parts) > 1:
                    devices[parts[1]] = {
                        "label": "GVFS Mounted",
                        "mount_status": "GVFS Mounted",
                        "mount_point": "/run/user/1000/gvfs/"
                    }
    except Exception:
        pass  # Ignora errori se gvfs-mount non è disponibile

    return devices if devices else None

def get_all_external_storage():
    """Combina i dispositivi montati normalmente e quelli GVFS."""
    external_disks = get_external_storage_info()  # Dischi tradizionalmente montati
    gvfs_disks = get_gvfs_mounted_devices()  # Dischi montati da GNOME/KDE

    # Unisci le due liste
    return {**(external_disks or {}), **(gvfs_disks or {})}

def get_network_info():
    """Raccoglie informazioni sulle interfacce di rete"""
    net_io = psutil.net_io_counters(pernic=True)
    net_stats = psutil.net_if_stats()
    net_addrs = psutil.net_if_addrs()
    
    interfaces = {}
    for iface, counters in net_io.items():
        interfaces[iface] = {
            "upload_mb": round(counters.bytes_sent / (1024 * 1024), 2),
            "download_mb": round(counters.bytes_recv / (1024 * 1024), 2),
            "packets_sent": counters.packets_sent,
            "packets_recv": counters.packets_recv,
            "errors_in": counters.errin,
            "errors_out": counters.errout,
            "drop_in": counters.dropin,
            "drop_out": counters.dropout,
            "addresses": [addr.address for addr in net_addrs.get(iface, [])],
            "speed_mbps": net_stats[iface].speed if iface in net_stats else None,
            "is_up": net_stats[iface].isup if iface in net_stats else None
        }
    
    return interfaces

def get_battery_cycle_count():
    """Recupera il numero di cicli di ricarica della batteria"""
    try:
        return int(subprocess.check_output("cat /sys/class/power_supply/BAT0/cycle_count", shell=True).strip())
    except Exception:
        return None  # Se il file non esiste o errore

def get_battery_capacity():
    """Recupera la capacità attuale della batteria in percentuale"""
    try:
        return float(subprocess.check_output("cat /sys/class/power_supply/BAT0/capacity", shell=True).strip())
    except Exception:
        return None

def get_battery_temperature():
    """Recupera la temperatura della batteria in °C (divisa per 10 se necessario)"""
    try:
        temp = float(subprocess.check_output("cat /sys/class/power_supply/BAT0/temp", shell=True).strip())
        return temp / 10 if temp > 100 else temp  # Alcuni sistemi riportano milligradi
    except Exception:
        return None

def get_battery_original_capacity():
    """Recupera la capacità originale della batteria"""
    try:
        return float(subprocess.check_output("cat /sys/class/power_supply/BAT0/energy_full_design", shell=True).strip()) / 1000
    except Exception:
        return None

def get_battery_real_capacity():
    """Recupera la capacità attuale reale della batteria"""
    try:
        return float(subprocess.check_output("cat /sys/class/power_supply/BAT0/energy_full", shell=True).strip()) / 1000
    except Exception:
        return None

def get_battery_live_status():
    """Recupera l'energia attuale immagazzinata nella batteria"""
    try:
        return float(subprocess.check_output("cat /sys/class/power_supply/BAT0/energy_now", shell=True).strip()) / 1000
    except Exception:
        return None

# Funzione generica per leggere file sysfs
def read_sysfs_value(path, scale=1.0):
    try:
        with open(path, "r") as f:
            return round(int(f.read().strip()) / scale, 3)
    except Exception:
        return None

# Recupera informazioni dalla batteria se disponibile
def get_battery_info():
    """Recupera le informazioni della batteria utilizzando UPower (MacBook/Linux con batteria)"""
    try:
        battery_info = subprocess.check_output("upower -i /org/freedesktop/UPower/devices/battery_BAT0", shell=True, text=True)

        # Debug: Stampiamo l'output per verificare il formato
        print(" Output UPower:\n", battery_info)

        battery = {
            "percentage": extract_value(r"percentage:\s+(\d+(?:\.\d+)?)%", battery_info),
            "cycle_count": int(get_battery_cycle_count()),
            "state": extract_value(r"state:\s+(\w+)", battery_info, str),
            "capacity": extract_value(r"capacity:\s+(\d+(?:\.\d+)?)%", battery_info),
            "temperature": get_battery_temperature(),  # Fixato
            "energy": {
                "original": extract_value(r"energy-full-design:\s+(\d+(?:\.\d+)?)\s+Wh", battery_info),
                "real": extract_value(r"energy-full:\s+(\d+(?:\.\d+)?)\s+Wh", battery_info),
                "live_status": extract_value(r"energy:\s+(\d+(?:\.\d+)?)\s+Wh", battery_info),
                "unit": "Wh"
            }
        }

        if battery['percentage'] is not None:
            return battery
        else:
            return None

    except subprocess.CalledProcessError:
        return None
    except Exception:
        return None

# Recupera informazioni sull'alimentazione per dispositivi senza batteria (Raspberry Pi)
def get_power_supply_info():
    """Recupera le informazioni sull'alimentazione per Raspberry Pi (Volt, Ampere, Watt)"""
    power_info = {
        "voltage_v": None,
        "current_a": None,
        "power_w": None,
        "cpu_freq_mhz": None
    }

    # Recupera il voltaggio con vcgencmd
    try:
        output = subprocess.check_output("vcgencmd measure_volts", shell=True, text=True).strip()
        power_info["voltage_v"] = float(output.replace("volt=", "").replace("V", ""))
    except Exception:
        pass

    # Recupera la frequenza della CPU
    try:
        output = subprocess.check_output("vcgencmd measure_clock arm", shell=True, text=True).strip()
        power_info["cpu_freq_mhz"] = int(output.split("=")[1]) // 1000000  # Converti Hz in MHz
    except Exception:
        pass

    # Recupera la corrente assorbita dalla linea VDD_CORE_A (linea principale della CPU)
    try:
        adc_output = subprocess.check_output("vcgencmd pmic_read_adc", shell=True, text=True).split("\n")
        for line in adc_output:
            if "VDD_CORE_A" in line:  # Trova la riga con la corrente della CPU
                power_info["current_a"] = float(line.split("=")[1].replace("A", "").strip())
                break
    except Exception:
        pass

    # Calcola la potenza (W = V * A)
    if power_info["voltage_v"] is not None and power_info["current_a"] is not None:
        power_info["power_w"] = round(power_info["voltage_v"] * power_info["current_a"], 3)

    return power_info

# Unifica le informazioni di batteria e alimentazione
def get_power_info():
    """Determina se il dispositivo ha una batteria o è alimentato da corrente e unifica l'output"""
    battery = get_battery_info()
    
    if battery:
        return {"type": "battery", "data": battery}
    else:
        return {"type": "power_supply", "data": get_power_supply_info()}

# Funzione per estrarre dati con regex
def extract_value(pattern, text, cast_type=float):
    match = re.search(pattern, text)
    return cast_type(match.group(1)) if match else None

def get_metrics():
    """Raccoglie tutte le informazioni di sistema"""
    return {
        "hostname": socket.gethostname(),
        "ip_address": get_ip_address(),
        "battery": get_power_info(),
        "cpu": get_cpu_info(),
        "fans": get_fan_info(),
        "temperatures": get_temperature_info(),
        "ram": {
            "total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "used_gb": round(psutil.virtual_memory().used / (1024**3), 2),
            "free_gb": round(psutil.virtual_memory().available / (1024**3), 2),
            "usage_percent": round(psutil.virtual_memory().percent, 2)
        },
        "storage": {
            "system_disk": get_storage_usage("/"),
            "external_disks": None
        },
        "network": get_network_info()
    }

def insert_metrics():
    """Inserisce le metriche nel database PostgreSQL utilizzando il modulo Nezuki"""
    metrics = get_metrics()

    logger.info(f"Raccolta metriche per {metrics['hostname']} ({metrics['ip_address']})")
    logger.debug(f"JSON Metriche: {metrics}")

    # Avvio della transazione
    db.doQuery("BEGIN;")
    
    try:
        # Controlla se il nodo esiste già
        node_result = db.doQuery("SELECT id FROM nodes WHERE hostname = %s", (metrics["hostname"],))
        
        if node_result["ok"] and node_result["results"]:
            node_id = node_result["results"][0]["id"]
        else:
            node_result = db.doQuery(
                "INSERT INTO nodes (hostname, ip_address) VALUES (%s, %s) RETURNING id",
                (metrics["hostname"], metrics["ip_address"])
            )
            if not node_result["ok"]:
                raise Exception(f"Errore creando il nodo {metrics['hostname']}: {node_result['error']}")
            
            node_id = node_result["lastrowid"]

        # **Inserisci metriche CPU**
        result = db.doQuery(
            """
            INSERT INTO cpu_metrics 
            (node_id, physical_cores, logical_cores, frequency_current_mhz, frequency_min_mhz, frequency_max_mhz, cpu_temperature, usage_total_percent, usage_per_core_percent)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                node_id,
                metrics["cpu"]["physical_cores"],
                metrics["cpu"]["logical_cores"],
                metrics["cpu"]["frequency"]["current_mhz"],
                metrics["cpu"]["frequency"]["min_mhz"],
                metrics["cpu"]["frequency"]["max_mhz"],
                metrics["cpu"]["temperature_celsius"],
                metrics["cpu"]["usage"]["total_percent"],
                json.dumps(metrics["cpu"]["usage"]["per_core_percent"]),
            )
        )
        if not result["ok"]:
            raise Exception(f"Errore SQL CPU: {result['error']}")

        # **Inserisci metriche RAM**
        result = db.doQuery(
            """
            INSERT INTO ram_metrics 
            (node_id, total_gb, used_gb, free_gb, usage_percent) 
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                node_id,
                metrics["ram"]["total_gb"],
                metrics["ram"]["used_gb"],
                metrics["ram"]["free_gb"],
                metrics["ram"]["usage_percent"]
            )
        )
        if not result["ok"]:
            raise Exception(f"Errore SQL RAM: {result['error']}")

        # **Inserisci metriche temperatura**
        result = db.doQuery(
            """
            INSERT INTO temperature_metrics 
            (node_id, sensor_data) 
            VALUES (%s, %s)
            """,
            (
                node_id,
                json.dumps(metrics["temperatures"])
            )
        )
        if not result["ok"]:
            raise Exception(f"Errore SQL Temperature: {result['error']}")

        # **Inserisci metriche ventole**
        result = db.doQuery(
            """
            INSERT INTO fan_metrics 
            (node_id, fan_data) 
            VALUES (%s, %s)
            """,
            (
                node_id,
                json.dumps(metrics["fans"])
            )
        )
        if not result["ok"]:
            raise Exception(f"Errore SQL Ventole: {result['error']}")

        # **Inserisci metriche rete**
        for iface, data in metrics["network"].items():
            result = db.doQuery(
                """
                INSERT INTO network_metrics 
                (node_id, interface, upload_mb, download_mb, packets_sent, packets_recv, addresses) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (node_id, iface, data["upload_mb"], data["download_mb"], data["packets_sent"], data["packets_recv"], json.dumps(data["addresses"]))
            )
            if not result["ok"]:
                raise Exception(f"Errore SQL Rete: {result['error']}")

        # **Inserisci metriche alimentazione**
        logger.debug(metrics["battery"])
        if metrics["battery"]["type"] == "battery":
            query = "INSERT INTO power_metrics (node_id, power_type, percentage, cycle_count, state, capacity, temperature, energy) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            query_params = (node_id, "battery", metrics["battery"]["data"]["percentage"], metrics["battery"]["data"]["cycle_count"], metrics["battery"]["data"]["state"], metrics["battery"]["data"]["capacity"], metrics["battery"]["data"]["temperature"], json.dumps(metrics["battery"]["data"]["energy"]))
        else:  # Caso di dispositivo senza batteria (alimentazione diretta)
            query = "INSERT INTO power_metrics (node_id, power_type, voltage_v, current_a, power_w) VALUES (%s, %s, %s, %s, %s)"
            query_params = (node_id, "power_supply", metrics["battery"]["data"]["voltage_v"], metrics["battery"]["data"]["current_a"], metrics["battery"]["data"]["power_w"])

        result = db.doQuery(query, query_params)
        if not result["ok"]:
            raise Exception(f"Errore SQL Alimentazione: {result['error']}")

        result = db.doQuery(
            """
            INSERT INTO node_metrics 
            (node_id, cpu_temperature, cpu_usage_percent, ram_usage_percent, ram_used_gb, fans, battery_temp)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                node_id,
                metrics["cpu"]["temperature_celsius"],
                metrics["cpu"]["usage"]["total_percent"],
                metrics["ram"]["usage_percent"],
                metrics["ram"]["used_gb"],
                json.dumps(metrics["fans"]),
                None if metrics["battery"]["type"] == "power_supply" else metrics["battery"]["data"]["temperature"]
            )
        )
        if not result["ok"]:
            raise Exception(f"Errore SQL Node Metrics: {result['error']}")
        
        result = db.doQuery(
            """
            INSERT INTO storage_metrics 
            (node_id, total_gb, used_gb, free_gb, percent_used, external_storage)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                node_id,
                metrics["storage"]["system_disk"]["total_gb"],
                metrics["storage"]["system_disk"]["used_gb"],
                metrics["storage"]["system_disk"]["free_gb"],
                metrics["storage"]["system_disk"]["percent_used"],
                json.dumps(metrics["storage"]["external_disks"]) if metrics["storage"]["external_disks"] else '{}'
            )
        )
        if not result["ok"]:
            raise Exception(f"Errore SQL Storage Metrics: {result['error']}")

        # **Se tutto è andato bene, fai il commit**
        db.doQuery("COMMIT;")
        logger.info(f"Metriche aggiornate per {metrics['hostname']}")

    except Exception as e:
        db.doQuery("ROLLBACK;")  # Se c'è un errore, annulla la transazione
        logger.error(f"Errore transazione SQL: {str(e)}")

if __name__ == "__main__":
    insert_metrics()
