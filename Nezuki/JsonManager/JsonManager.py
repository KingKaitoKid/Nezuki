import json, re
from jsonpath_ng import parse
from Common import *
from commonLogId import *

@versione("1.0.3")
class JsonManager:
    '''
        Questa classe serve per gestire un json.
    '''

    
    def __init__(self, json_data:dict|str|list={}) -> None:
        '''
            istanzia l'oggetto.
        '''
        self.logger = get_logger()
        self.load_data(json_data)

    
    def load_data(self, data:dict) -> None:
        if str(type(data)) == "<class 'str'>" and re.match(r'^(.+)\/([^\/]+)$', data):
            data = self.read_json(data)

        match str(type(data)):
            case "<class 'dict'>":
                self.data = data

            case "<class 'str'>":
                self.data = json.loads(data)

            case "<class 'list'>":
                self.data = json.loads(json.dumps(data, indent=2))

            case _:
                self.data = json.load(data)

    
    def read_json(self, path: str) -> dict:
        """
            Legge il file da path assoluto e torna il contenuto del file in un JSON decodificato.

            Input:

                path: Path asosluto del file JSON da leggere
        """
        try:
            with open(path, "r") as file_json:
                content_json = json.loads(file_json.read())
        except Exception as e:
            content_json = None
        return content_json

    
    def retrieveKey(self, key:str) -> str|list:
        '''
            dato un pattern di chiavi, torna il valore corrispondente
            esempio: "$.tastiera.inline_keyboard[*][*].text"
        '''
        jsonpath_expression = parse(key)

        aggregatore = []

        for match in jsonpath_expression.find(self.data):
            aggregatore.append(match.value)

        if len(aggregatore) == 1:
            aggregatore = aggregatore[0]

        return aggregatore

    
    def updateKey(self, pattern:str, valore) -> None:
        '''
            dato un pattern di chiavi ed un valore, la funzione va ad aggiornare la chiave con il valore passato
            esempio: "$.tastiera.inline_keyboard[*][*].text"
        '''
        jsonpath_expr = parse(pattern)
        jsonpath_expr.find(self.data)
        jsonpath_expr.update(self.data, valore)

# json_data = {
#     "message_id": 22050,
#     "chat_id": 115420076,
#     "bot_id": 5270541563,
#     "lingua": 8,
#     "tastiera": {
#       "inline_keyboard": [
#         [
#           {
#             "text": "Erbaiuto",
#             "callback_data": "Pokdx Ability 1 65"
#           },
#           {
#             "text": "Clorofilla",
#             "callback_data": "Pokdx Ability 1 34"
#           }
#         ],
#         [
#           {
#             "text": "🔙 Bulbasaur",
#             "callback_data": "Pokdx Info Cerca 1"
#           }
#         ]
#       ]
#     }
#   }

# x = JsonManager({'ok': True, 'results': [], 'rows_affected': 0, 'error': None})
# print(x.retrieveKey("results[0][0]"))
# x.updateKey('$.tastiera.inline_keyboard[*][*].text',"miaomiao")
# print(x.data)

