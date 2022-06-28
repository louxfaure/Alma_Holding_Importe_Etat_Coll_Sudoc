import os
# external imports
import requests
import xml.etree.ElementTree as ET
import logging
from datetime import datetime
# internal import
from logs import logs




ns = {'oai': 'http://www.openarchives.org/OAI/2.0/',
        'marc': 'http://www.loc.gov/MARC21/slim' }


class AlmaOai(object):

    def __init__(self, institution ='network',service='AlmaOai',instance='Test',metadataPrefix='unimarc',oai_set='abes_docelec',date_from=None, date_to=None):
        self.logger = logging.getLogger(service)
        self.institution = institution
        self.service = service
        self.instance = instance
        self.metadataPrefix = metadataPrefix
        self.set = oai_set
        self.date_from = date_from
        self.date_to = date_to
        self.records_infos = []

    @property

    def baseurl(self):
        if self.instance == 'Test' :
            return "https://eu02-psb.alma.exlibrisgroup.com/view/oai/{}/request?verb=ListRecords".format("33PUDB_"+self.institution.upper())
        else :
            return "https://eu02.alma.exlibrisgroup.com/view/oai/{}/request?verb=ListRecords".format("33PUDB_"+self.institution.upper())

    def fullurl(self):
        vardict = {
            'from' : self.date_from,
            'to': self.date_to

        }

        fullurl = self.baseurl + '&metadataPrefix=' + self.metadataPrefix + '&set=' + self.set
        for key, var in vardict.items() :
            if var is not None :
                fullurl = "{}&{}={}".format(fullurl,key,var)
                self.logger.debug(fullurl)
        return fullurl

    def urlwithtoken(self,token):
        return self.baseurl + '&resumptionToken=' + token

    def oai_request(self,token):
        if token is None :
            url=self.fullurl()
        else :
            url=self.urlwithtoken(token)
        print(url)
        r = requests.get(url)
        try:
            r.raise_for_status()  
        except requests.exceptions.HTTPError:
            raise HTTPError(r,self.service)
        reponse = r.content.decode('utf-8')
        reponsexml = ET.fromstring(reponse)
        return reponsexml

    def get_pf_info(self,token=None):
        records_list = self.oai_request(token)
        for record in records_list.findall("oai:ListRecords/oai:record",ns):
            record_info = {
                'date_maj':  datetime.strptime(record.find("oai:header/oai:datestamp",ns).text,'%Y-%m-%dT%H:%M:%SZ'), #2021-05-27T07:31:21Z
                'id': record.find("oai:header/oai:identifier",ns).text,
                'statut':'updated',
                'ppn':None,
            }
            if record.find("oai:header[@status='deleted']",ns) :
                record_info['statut'] = 'delated'
                continue
            record_info['ppn'] = record.find("oai:metadata/marc:record/marc:datafield[@tag='PPN']/marc:subfield[@code='a']",ns).text
            record_info['origine'] = record.find("oai:metadata/marc:record/marc:datafield[@tag='MAJ']/marc:subfield[@code='b']",ns).text
            maj_notice = record.find("oai:metadata/marc:record/marc:datafield[@tag='MAJ']/marc:subfield[@code='a']",ns).text
            record_info['maj_notice'] = datetime.strptime(record.find("oai:metadata/marc:record/marc:datafield[@tag='MAJ']/marc:subfield[@code='a']",ns).text, '%Y-%m-%d %H:%M:%S Europe/Paris'), #2021-05-25 11:38:53 Europe/Paris
            self.logger.debug(type(record_info['maj_notice']))
            # datetime.strptime(maj_notice[0], '%Y-%m-%d %H:%M:%S Europe/Paris'), #2021-05-25 11:38:53 Europe/Paris
            record_info['maj_pf'] = datetime.strptime(record.find("oai:metadata/marc:record/marc:datafield[@tag='997']/marc:subfield[@code='a']",ns).text, '%Y-%m-%d %H:%M:%S Europe/Paris'), #2021-05-25 11:38:53 Europe/Paris
            self.records_infos.append(record_info)
        if records_list.findall("oai:ListRecords/oai:resumptionToken",ns):
            return True,records_list.find("oai:ListRecords/oai:resumptionToken",ns).text
        else:
            return False, None

    def get_records_info(self):
        has_token, token = self.get_pf_info()
        # while has_token is True:
        #     has_token, token = self.get_pf_info(token)
        return self.records_infos

  
#Gestion des erreurs
class HTTPError(Exception):

    def __init__(self, response, service):
        super(HTTPError,self).__init__(self.msg(response, service))

    def msg(self, response, service):
        logger = logging.getLogger(service)
        msg = "\n  HTTP Status: {}\n  Method: {}\n  URL: {}\n  Response: {}"
        sujet = service + 'Erreur'
        message = mail.Mail()
        message.envoie(os.getenv('ADMIN_MAIL'),os.getenv('ADMIN_MAIL'),sujet, msg.format(response.status_code, response.request.method, response.url, response.text) )
        logger.error("HTTP Status: {} || Method: {} || URL: {} || Response: {}".format(response.status_code, response.request.method,
                          response.url, response.text))