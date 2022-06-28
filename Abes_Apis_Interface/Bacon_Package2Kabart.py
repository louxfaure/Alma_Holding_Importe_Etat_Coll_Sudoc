import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import json

class Bacon_Package(object):
    """
    Bacon
    =======
    A set of function wich handle data returned by service 'Bacon in json' 
    http://documentation.abes.fr/aidebacon/index.html#WebservicePackage
    On init take a package identifierin argument
    ex : https://bacon.abes.fr/package2kbart/CAIRN_COUPERIN_PSYCHOLOGIE.json
"""

    def __init__(self,pk_id,service='bacon'):
        self.logger = logging.getLogger(service)
        self.endpoint = "https://bacon.abes.fr/package2kbart/"
        self.service = service
        self.pk_id = pk_id
        url =  '{}/{}.json'.format(self.endpoint, self.pk_id)
        r = requests.get(url)
        try:
            r.raise_for_status()  
        except requests.exceptions.HTTPError:
            self.status = 'Error'
            self.logger.error("{} :: XmlAbes_Init :: HTTP Status: {} || Method: {} || URL: {} || Response: {}".format(ppn, r.status_code, r.request.method, r.url, r.text))
            self.error_msg = "Package inconnu ou service indisponible"
        else:
            self.record = r.content.json()
            self.status = 'Succes'
            self.logger.debug("{} :: Bacon :: Package créé avec succes".format(pk_id))