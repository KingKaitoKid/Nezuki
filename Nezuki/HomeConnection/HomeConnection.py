import requests
import json
from Common import *
    
@versione("1.0.3")
@deprecated("1.0.3", "Modulo in dismissione per rinnovo domotica")
class HomeConnection:
    """ Classe che definisce funzionalità di una connessione """
    v: str
    """ Versione del modulo HomeConnection """
    def __init__(self):
        self.v = "1.0.1"

    @deprecated("1.0.10", "Funzionalità fornita da Http")
    def doRequest(self, method: str, url: str, headers: dict=None, payload: dict={}) -> dict:
        """ DEPRECATION!! Funzionalità da migrare con il modulo server Http"""
        payload = json.dumps(payload)
        response = requests.request(method.upper(), url, headers=headers, data=payload)

        return response.json()
    
    def mbps_to_mb(self, mbps) -> float:
        """ Converte i Mbps in MB e ritorna un numero a virgola mobile fino ai decimi """
        mb = mbps / 8
        return round(mb, 2)
    
    def find_key_by_value(self, dictionary, search_value):
        """ DEPRECATION!! Funzione inefficiente e non più in uso. Permette di cercare nel dizionario passato un valore specifico """
        # Usa una espressione di generatore per trovare la prima chiave che corrisponde al valore specificato
        return next((key for key, value in dictionary.items() if value == search_value), None)


@versione("1.0.3")
@deprecated("1.0.3", "Modulo in dismissione per rinnovo domotica")
class HomeWiFi(HomeConnection):
    """ Classe che definisce le operazioni della connettività casa WiFi facendo integrazioni """
    wifi_url: str
    """ URL Locale del modem """
    def __init__(self):
        """ Inizializza l'oggetto """
        self.wifi_url = "http://10.143.1.1/JNAP/"
        self.jnap_headers = {
            'X-JNAP-Authorization': 'Basic YWRtaW46S2FpdG9LaWQ5NiZBbmRyeUNvbGEyOQ==',
            'Content-Type': 'application/json'
        }
        self.method = "POST"
        HomeConnection.__init__(self)

    def getRouterInfo(self) -> dict:
        """ Esegue l'action JNAP core/GetDeviceInfo per ricavare le informazioni su Router """
        action = 'http://linksys.com/jnap/core/GetDeviceInfo'
        self.jnap_headers['X-JNAP-Action'] = action

        response = self.doRequest(self.method, self.wifi_url, self.jnap_headers, {})['output']

        result = {"marca": response['manufacturer'], "modello": response['modelNumber'], "descrizione": response['description'], "numeroSerie": response['serialNumber']}
        return result

    def getConnected_Devices(self) -> list:
        """ Esegue l'action JNAP networkconnections/GetNetworkConnections per ricavare le informazioni tecniche sui dispositivi connessi come velocità massima in un preciso momento quanto ammonta """
        action = 'http://linksys.com/jnap/networkconnections/GetNetworkConnections'
        self.jnap_headers['X-JNAP-Action'] = action

        response = self.doRequest(self.method, self.wifi_url, self.jnap_headers, {})
        result = list()
        for connection in response['output']['connections']:
            try:
                result.append({"macAddress": connection.get('macAddress', None), "maxSpeed": {"mb": self.mbps_to_mb(connection.get('negotiatedMbps', 0)), "mbps": connection.get('negotiatedMbps', 0)}, "guest": connection['wireless']['isGuest'], "band": connection['wireless']['band']})
            except Exception as e:
                result.append({"macAddress": connection.get('macAddress', None), "maxSpeed": {"mb": self.mbps_to_mb(connection.get('negotiatedMbps', 0)), "mbps": connection.get('negotiatedMbps', 0)}, "guest": False, "band": None})
        
        return result

    def device_list_info(self) -> list:
        """ Esegue l'action JNAP devicelist/GetDevices3 per ricavare le informazioni specifiche sui dispositivi connessi come nome, ip, macaddress ed altre informazioni calcolate """
        action = 'http://linksys.com/jnap/devicelist/GetDevices3'
        self.jnap_headers['X-JNAP-Action'] = action

        response = self.doRequest(self.method, self.wifi_url, self.jnap_headers, {})

        result = list()
        for device in response['output']['devices']:
            humanName = device.get('friendlyName', None)
            parts: str = None
            marca: str = None
            modello: str = None
            posizionamento: str = None
            analisi = {"marca": None, "modello": None, "posizione": None, "note": None}
            for properties in device['properties']:
                if properties['name'] == "userDeviceName":
                    humanName: str = properties['value']
                    try:
                        parts = humanName.split("-")
                        marca = parts[0]
                        modello = parts[1]
                        posizionamento = parts[2]
                        try:
                            note = parts[3]
                        except Exception as e:
                            note = None
                        analisi = {"marca": marca, "modello": modello, "posizione": posizionamento, "note": note}
                    except Exception as e:
                        analisi = {"marca": None, "modello": None, "posizione": None, "note": None}
            

            if "nodeType" in device:
                is_node = True
                if device['nodeType'].lower() == "master":
                    is_master = True
                else:
                    is_master = False
            else:
                is_node = False
                is_master = False
            for mcaddr in device['knownInterfaces']:
                if mcaddr['interfaceType'].lower() == 'wireless':
                    wifi = True
                else:
                    wifi = False

                for ipconn in device['connections']:
                    if mcaddr['macAddress'] == ipconn['macAddress']:
                        result.append({"deviceID": device.get('deviceID', None), "domotica": analisi, "network_node": {"is_node": is_node, "is_master": is_master}, "online": True, "ipAddress": ipconn.get('ipAddress', None), "macAddress": mcaddr['macAddress'], "humanName": humanName, "parentNode": ipconn.get('parentDeviceID', None), "wireless": wifi, "serial": device.get('unit', None).get('serialNumber')})
                    else:
                        result.append({"deviceID": device.get('deviceID', None), "domotica": analisi, "network_node": {"is_node": is_node, "is_master": is_master}, "online": False, "ipAddress": None, "macAddress": mcaddr['macAddress'], "humanName": humanName, "parentNode": ipconn.get('parentDeviceID', None), "wireless": wifi,  "serial": device.get('unit', None).get('serialNumber')})

        return result
    
    def unify_device_info(self, connected_tech: list, connected_general: list) -> dict:
        """ Unifica le informazioni tecniche e specifiche sui dipositivi connessi sulla rete WiFi """
        result = dict()

        for human_info in connected_general:
            mac_address = human_info['macAddress']
            matched_tech_info = next((tech for tech in connected_tech if tech['macAddress'] == mac_address), None)
            if matched_tech_info:
                result[human_info['deviceID']] = {
                    "network_node": human_info['network_node'],
                    "domotica": human_info['domotica'],
                    "connected": human_info['online'],
                    "ipAddress": human_info['ipAddress'],
                    "macAddress": mac_address,
                    "serial": human_info['serial'],
                    "name": human_info['humanName'],
                    "maxSpeed_mb": matched_tech_info['maxSpeed']['mb'],
                    "maxSpeed_mbps": matched_tech_info['maxSpeed']['mbps'],
                    "guest": matched_tech_info['guest'],
                    "band": matched_tech_info['band'],
                    "is_wifi": human_info['wireless'],
                    "parent": {
                        "deviceID": human_info['parentNode']
                    }
                }
                connected_tech.remove(matched_tech_info)
            else:
                result[human_info['deviceID']] = {
                    "network_node": human_info['network_node'],
                    "domotica": human_info['domotica'],
                    "connected": human_info['online'],
                    "ipAddress": human_info['ipAddress'],
                    "macAddress": mac_address,
                    "serial": human_info['serial'],
                    "name": human_info['humanName'],
                    "maxSpeed_mb": None,
                    "maxSpeed_mbps": None,
                    "guest": None,
                    "band": None,
                    "is_wifi": human_info['wireless'],
                    "parent": {
                        "deviceID": human_info['parentNode']
                    }
                }
        result['router_info'] = self.getRouterInfo()
        return result
    
    def getNetworkDeviceConnected(self) -> dict:
        """ Funzione per ottenere tutte le informazioni sui dipositivi che sono connessi al WiFi """
        return self.unify_device_info(self.getConnected_Devices(), self.device_list_info())