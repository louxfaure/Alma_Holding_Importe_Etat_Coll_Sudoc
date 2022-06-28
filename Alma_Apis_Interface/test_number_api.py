#!/usr/bin/python3
# -*- coding: utf-8 -*-
import Alma_Apis
import xml.etree.ElementTree as ET
import json

import os
# Retourne l'état de collection d'une notice (ppn) pour une bibliothèque (RCR)
# Si plusieurs ou 0 retyourne faux         

user_id = 'afaure001003@u-bordeaux.fr'
request_id = '2726312110004672'
api_key = os.getenv("TEST_UBM_API")
api = Alma_Apis.Alma(apikey=api_key, region='EU', service='test')
print(api.get_api_remaining())
# response['primary_id'] = 'testyaaddi@u-bordeaux.fr'
# a,b = api.update_user(user_id,
#                     "user_group,job_category,pin_number,preferred_language,campus_code,rs_libraries,user_title,library_notices",
#                     json.dumps(response, indent=4, sort_keys=True),
#                     accept='json',
#                     content_type='json')
# print(b)          