import os
import re
# external imports
import requests
import logging
import xml.etree.ElementTree as ET
# internal import
from mail import mail
from logs import logs


class AbesXml(object):
    """
    AbesXml
    =======
    A set of function wich handle data returned by service 'Sudoc in Xml' 
    http://documentation.abes.fr/sudoc/manuels/administration/aidewebservices/index.html#SudocMarcXML
    On init take a PPN (sudoc identifier) in argument
    ex : https://www.sudoc.fr/178565946.xml   
"""

    def __init__(self,ppn,service='AbesXml'):
        self.logger = logging.getLogger(service)
        self.endpoint = "https://www.sudoc.fr"
        self.service = service
        self.ppn = ppn
        if not(re.search("^\d{8}[\dxX]$", ppn)):
            self.status = "Error"
            self.logger.error("{} :: XmlAbes_Init :: PPN invalide".format(ppn))
            self.error_msg = "PPN invalide"
        else:
            url =  '{}/{}.xml'.format(self.endpoint, self.ppn)
            r = requests.get(url)
            try:
                r.raise_for_status()  
            except requests.exceptions.HTTPError:
                self.status = 'Error'
                self.logger.error("{} :: XmlAbes_Init :: HTTP Status: {} || Method: {} || URL: {} || Response: {}".format(ppn, r.status_code, r.request.method, r.url, r.text))
                self.error_msg = "PPN inconnu ou service indisponible"
            else:
                self.record = r.content.decode('utf-8')
                self.status = 'Succes'
                self.logger.debug("{} :: AbesXml :: Object créé avec succes".format(ppn))

    @property
    
    def get_record(self):
        """
        Return the entire record
        
        Returns:
            string -- the record in unimarc_xml 
        """
        return self.record
    
    def get_init_status(self):
        """Return the init status
        """
        return self.status

    def get_error_msg(self):
        if self.error_msg is not None:
            return self.error_msg
        else:
            return "Pas de message d'erreur"

    
    def get_textual_holdings(self,rcr):
        """
        For a given library return all the text holdings present in the record (955$$r in unimarc SUDOC)
        
        Arguments:
            rcr {string} -- the libray's id in Sudoc
        
        Returns:
            list -- a list of text holdings
        """
        root = ET.fromstring(self.record)
        textual_holdings = []
        for field in root.findall(".//datafield[@tag='955']"):
            item = field.find("subfield[@code='5']").text
            if item[:9] == rcr and field.find("subfield[@code='r']") is not None:
                textual_holdings.append(field.find("subfield[@code='r']").text)
        return textual_holdings
