#!/usr/bin/python3
# -*- coding: utf-8 -*-
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import json
import logging

class Bacon_Id2Kbart(object):
    """
    Bacon_Id2Kbart
    =======
    A set of function wich handle data returned by service 'Bacon in json' 
   http://documentation.abes.fr/aidebacon/index.html#WebserviceId2
    On init take a bib identifier in argument
    ex : https://bacon.abes.fr/id2kbart/9782807308534.json
"""

    def __init__(self,bib_id,service='bacon'):
        self.logger = logging.getLogger(service)
        self.endpoint = "https://bacon.abes.fr/id2kbart"
        self.service = service
        self.bib_id = bib_id
        self.multi_providers = False
        url =  '{}/{}.json'.format(self.endpoint, self.bib_id)
        r = requests.get(url)
        try:
            r.raise_for_status()  
        except requests.exceptions.HTTPError:
            self.status = 'Error'
            self.logger.error("{} :: XmlAbes_Init :: HTTP Status: {} || Method: {} || URL: {} || Response: {}".format(self.bib_id, r.status_code, r.request.method, r.url, r.text))
            self.error_msg = "Package inconnu ou service indisponible"
        else:
            self.record = r.json()
            if "provider" in self.record["query"] :
                # Test le nombre de providers
                if type(self.record["query"]["provider"]) is dict :
                    #Test du nombre de Kbart (on peut avoir plusieurs Kbart pour un même ISBN et provider)
                    if type(self.record["query"]["provider"]["kbart"]) is list :
                        self.status = 'Matching multiples'
                    else:    
                        self.status = 'Succes'
                else : # Plusieurs providers
                    self.multi_providers = True
                    if type(self.record["query"]["provider"][0]["kbart"]) is list :
                        self.status = 'Matching multiples'
                    else:    
                        self.status = 'Succes'
            else :
                self.status = 'None'
            self.logger.debug("{} :: Bacon :: Package créé avec succes".format(bib_id))

    def get_publication_title(self):
        if self.multi_providers :
            return self.record["query"]["provider"][0]["kbart"]["publication_title"]
        else :
            return self.record["query"]["provider"]["kbart"]["publication_title"]
        

    def get_publisher_name(self):
        if self.multi_providers :
            return self.record["query"]["provider"][0]["kbart"]["publisher_name"]
        else:
            return self.record["query"]["provider"]["kbart"]["publisher_name"]

    def get_online_pubdate(self):
        if self.multi_providers :
            return self.record["query"]["provider"][0]["kbart"]["date_monograph_published_online"]
        else:
            return self.record["query"]["provider"]["kbart"]["date_monograph_published_online"]

    def get_print_pubdate(self):
        if self.multi_providers :
            return self.record["query"]["provider"][0]["kbart"]["date_monograph_published_print"]
        else:
            return self.record["query"]["provider"]["kbart"]["date_monograph_published_print"]

    def get_ppn(self):
        if self.multi_providers :
            if self.record["query"]["provider"][0]["kbart"]["bestppn"]:
                return self.record["query"]["provider"][0]["kbart"]["bestppn"]
            else:
                return 'None'
        else :
            if self.record["query"]["provider"]["kbart"]["bestppn"]:
                return self.record["query"]["provider"]["kbart"]["bestppn"]
            else:
                return 'None'