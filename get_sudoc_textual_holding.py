#!/usr/bin/python3
# -*- coding: utf-8 -*-
#Modules externes
import os
import re
import logging
import csv
import xml.etree.ElementTree as ET

#Modules maison
from Abes_Apis_Interface.AbesXml import AbesXml
from Alma_Apis_Interface import Alma_Sru
from Alma_Apis_Interface import Alma_Apis_Records
from logs import logs

SERVICE = "Etat_Col_Sudoc"

LOGS_LEVEL = 'DEBUG'
LOGS_DIR = os.getenv('LOGS_PATH')

REGION = 'EU'
INSTITUTION = 'ubm'
API_KEY = os.getenv('PROD_UBM_BIB_API')
ALMA_LIBRARY_ID = '3200000000'
RCR = '335222302'

BACKUP_MARC_FIELD = '901'
KEEP_NOTE = True

IN_FILE = "/media/sf_Partage_LouxBox/ppn_regards.txt"
OUT_FILE = 'rapport_traitement2.csv'
 
def get_sudoc_textual_holding(rcr,ppn):
    """Interact with AbesXml.get_textual_holdings 
    
    Check the number of textual holdings.  If its != 1 return false and error message
    
    Arguments:
        rcr {string} -- library id in SUDOC
        ppn {string} -- record id in SUDOC
    
    Returns:
        boolean -- true if list contain one elment false if not
        string -- the content of textual hoding or error message
    """
    abes = AbesXml(ppn=ppn,service=SERVICE)
    if abes.get_init_status() == 'Error':
        msg = abes.get_error_msg()
        return None, msg
    textual_holding = abes.get_textual_holdings(rcr)
    if len(textual_holding) == 1:
        return textual_holding[0], 0
    elif len(textual_holding) == 0:
        log_module.error("{} :: get_sudoc_textual_holding :: Pas d'état de colection".format(ppn))
        return None, "Aucun état de collection dans le SUDOC pour cette revue ppn {}".format(ppn)
    else:
        log_module.error("{} :: get_sudoc_textual_holding :: {} états de collection dans le SUDOC pour cette revue".format(ppn,len(textual_holding)))
        return None, "{} états de collection dans le SUDOC pour cette revue ppn {}".format(len(textual_holding),ppn)

#Pour toutes les occurences de champs passés en paramètre (xml object),
#retourne la liste detoutes les valeurs d'un sous-champs dont le code est passé en paramètre 
def get_subfields_value(fields,subfield_code):
    """For all instances of marc fields return textual content of subfield with given code 
    
    Arguments:
        fields {object} -- xmletree object.  
        subfield_code {string} -- subfield code
    
    Returns:
        list -- list of textual content for each subfields with given code     
        """
    subfields_textual_contents = []
    for field in fields:
        for subfield in field.findall("subfield[@code='{}']".format(subfield_code)):
            subfields_textual_contents.append(subfield.text)
    return subfields_textual_contents

def create_field(tag,first_ind,second_ind):
    """Create a marc xml field 
    
    Arguments:
        tag {string} -- marc field tag
        first_ind {string} -- marc first indicator
        second_ind {string} -- marc second indicator
    
    Returns:
        object -- xmletree object
    """
    new_field =  ET.Element("datafield")
    new_field.set('ind1', first_ind)
    new_field.set('ind2', second_ind)
    new_field.set('tag', tag)
    return new_field

def create_subfield(code,value):
    """Create & return a marc xml subfield
    
    Arguments:
        code {string} -- marc subfield code
        value {string} -- subfield textual value
    
    Returns:
        object -- xmletree object
    """
    new_subfield =  ET.Element("subfield")
    new_subfield.set('code', code)
    new_subfield.text = value
    return new_subfield

def get_index_of_element(elements,tag):
    index = 0
    for element in elements:
        index += 1
        if (element.get('tag') == '852'):
            return index
    return index

def create_new_holding(holding, new_textual_holding):
    """Create a marc xml element for textual holding (866 field)

    Backup in 901 fields old textual holding value (all 866 fields & subfields)
    Create a new 866 field with new textual holding value
    Inject in the new 886 field the notes of old textual holdings fields (886$$x and 886$$z)
     
    Arguments:
        holding {xml object} -- holding record 
        textual_holding {string}     

    Returns:
        xml object -- holding record
    """
    root = ET.fromstring(holding)
    #Get public notes (866 $$z)
    public_notes = get_subfields_value(root.findall(".//datafield[@tag='866']"),"z")
    #Get internal notes (866 $$x)
    internal_notes = get_subfields_value(root.findall(".//datafield[@tag='866']"),"x")
    #Backup old textual holding in 901 field
    record = root.find('.//record')
    record.append(ET.Element("backup"))
    for champ in record.findall(".//datafield[@tag='866']"):
        champ.set('tag', BACKUP_MARC_FIELD)
    # print(ET.tostring(old_fields_textual_holding))
    new_field_textual_hodling = create_field('866',' ','0')
    new_subfield_text = create_subfield('a',new_textual_holding)
    new_field_textual_hodling.append(new_subfield_text)
    #On réinjecte les notes
    if KEEP_NOTE:
        for note in internal_notes :
            new_subfield_note = create_subfield('x',note)
            new_field_textual_hodling.append(new_subfield_note)
        for note in public_notes :
            new_subfield_note = create_subfield('z',note)
            new_field_textual_hodling.append(new_subfield_note)
    record.insert(get_index_of_element(record ,'852'),new_field_textual_hodling)
    print(ET.tostring(root))
    return ET.tostring(root)
 
def ppn_to_holding(alma_sru, alma_api, ppn):
    reponse_status, error_msg, mms_id, alma_holdings = alma_sru.ppn_to_holding_id(ppn='(PPN)'+ppn,library_id=ALMA_LIBRARY_ID)
    if reponse_status == "Ko":
        return "Echec", error_msg
    sudoc_textual_holding, error_msg = get_sudoc_textual_holding(RCR,ppn)
    if sudoc_textual_holding is not None:
        for holding_id in alma_holdings :
            status, holding = alma_api.get_holding(mms_id, holding_id, accept='xml')
            if status == 'Error':
                return "Echec", "Impossible de retrouver la Holding Id {}".format(holding_id)
            newHolding = create_new_holding(holding,sudoc_textual_holding)     
            status, reponse = alma_api.set_holding(mms_id, holding_id, newHolding)
            if status == 'Error':
                return "Echec", "Echec de la mise à jour de la Holding Id {}".format(holding_id)
        return "Succes", "{} holding(s) mise(s) à jour".format(len(alma_holdings))
    else :
        return "Echec", error_msg

def format_ppn(text):
    p = re.compile('="(.*?)"')
    try:
        return p.match(text).group(1)
    except:
        return text

#On initialise le logger
logs.init_logs(LOGS_DIR,SERVICE,LOGS_LEVEL)
log_module = logging.getLogger(SERVICE)
log_module.info("Début du traitement")
report = open(OUT_FILE, "w")
alma_sru = Alma_Sru.AlmaSru(institution=INSTITUTION,service=SERVICE)
alma_api = Alma_Apis_Records.AlmaRecords(apikey=API_KEY, region=REGION, service=SERVICE)

with open(IN_FILE, newline='') as f:
    log_module.info("Début")
    reader = csv.reader(f, delimiter=';')
    headers = next(reader)
    for row in reader:
        log_module.info(row[0])
        ppn = format_ppn(row[0])
        log_module.info("{} :: Main :: Début du traitement".format(ppn))
        status, response = ppn_to_holding(alma_sru, alma_api, ppn)
        report.write("{}\t{}\t{}\n".format(ppn,status,response))
        log_module.info("{} :: Main :: Fin du traitement".format(ppn))
log_module.info("Fin du traitement")
report.close
