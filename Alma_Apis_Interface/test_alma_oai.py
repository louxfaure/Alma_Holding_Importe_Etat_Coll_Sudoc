#!/usr/bin/python3
# -*- coding: utf-8 -*-
import logging
from Alma_Apis_Interface import Alma_Oai
from Abes_Apis_Interface import AbesXml
import xml.etree.ElementTree as ET
import os
from logs import logs
from datetime import datetime
import time

SERVICE = 'AlmaOai'
LOGS_LEVEL = 'INFO'
LOGS_DIR = os.getenv('LOGS_PATH')
RCR = '330009999'

#Init logger
logs.init_logs(LOGS_DIR,SERVICE,LOGS_LEVEL)
log_module = logging.getLogger(SERVICE)

log_module.info('###DEBUT DU TRAITEMENT###')
oai = Alma_Oai.AlmaOai(institution='bxsa',service=SERVICE,instance='Test',date_from='2021-05-27')
# On récupère la liste des pf publiés
records = oai.get_records_info()
for record in records :
    sudoc_record = AbesXml.AbesXml(record['ppn'],service=SERVICE)
    if sudoc_record.status == 'Error':
            log_module.info("{} - {} - {} - {} - {} - {}".format(record['ppn'],record['date_maj'],record['origine'],record['maj_notice'], record['maj_pf'],sudoc_record.error_msg))
            continue        
    update_date = sudoc_record.test_einventory(RCR, record['id'])
    if update_date is None :
        log_module.info("{} - {} - {} - {} - {} - {}".format(record['ppn'],record['date_maj'],record['origine'],record['maj_notice'], record['maj_pf'],update_date))
    else :
        if(record['origine'] == 'ABES' and record['maj_notice'] > record['maj_pf']):
            log_module.info("{}-{}-{}-{}".format(record['ppn'],record['id'],record['maj_notice'], record['maj_pf']))
            continue
        else :
            if(update_date < record['date_maj']) :
              log_module.info("{} - {} - {} - {} - {} - {}".format(record['ppn'],record['date_maj'],record['origine'],record['maj_notice'], record['maj_pf'],update_date))
log_module.info('###FIN DU TRAITEMENT###')