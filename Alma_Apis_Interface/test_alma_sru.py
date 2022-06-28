#!/usr/bin/python3
# -*- coding: utf-8 -*-

from Alma_Apis_Interface import Alma_Sru
import xml.etree.ElementTree as ET
from logs import logs
import logging
import os

#Init logger
SERVICE = "TEST_SRU"
LOGS_LEVEL = 'DEBUG'
LOGS_DIR = os.getenv('LOGS_PATH')

logs.init_logs(LOGS_DIR,SERVICE,LOGS_LEVEL)
logger = logging.getLogger(SERVICE)


sru = Alma_Sru.AlmaSru(institution='ub',service='test')
nextRecordPosition = 1

# On va faire une boucle de requête. On ne sortira qu'une fois la dernière requête passé. On va se baser sur la valeur de nextRecordPosition
while nextRecordPosition > 0 :
    results = sru.requete(query='trail',index='alma.title',startrecord=nextRecordPosition)
    nb_results = sru.get_nombre_resultats(results)
    if nextRecordPosition == 1 : 
        logger.debug("La requête retourne {} résultats".format(nb_results))
    # on fait des trucs
    # on récupère la valeur de nextRecordPosition
    nextRecordPosition = sru.get_nextrecord_position(results)
    logger.debug(nextRecordPosition)
