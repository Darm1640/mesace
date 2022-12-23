# -*- coding: utf-8 -*-
from random import randint
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import tostring
from odoo.exceptions import UserError
from odoo import api, fields, models, _
import xmltodict
import requests
import urllib3
from odoo.exceptions import UserError
from odoo.http import request, Response
import json
from datetime import datetime, timedelta, date
import logging
_logger = logging.getLogger(__name__)


def as_process_json(endpoint_extract,as_json,user,token,accion,self=False,hash_inv=False,number=False):
    if self:
        request_val = self
    else:
        request_val = request
    params = {}
    endpoint = request_val.env['as.siat.endpoint'].search([('as_type','=',endpoint_extract)], limit=1)
    if hash_inv:
        params['hash_inv'] = hash_inv
    if number:
        params['number'] = number
    if token:
        headers = {'Authorization' : token}
    else:
        headers = {}
    try:
        as_timeout = int(request_val.env['ir.config_parameter'].sudo().get_param('res_config_settings.as_timeout_inv'))
        as_url_api = str(request_val.env['ir.config_parameter'].sudo().get_param('res_config_settings.as_url_api'))
        if as_url_api == 'False' or not endpoint:
            raise UserError(_("Debe completar URL para API."))
        response = requests.post(as_url_api+endpoint.name, json=as_json, headers=headers, verify=False, params=params,timeout=as_timeout)
        if response.reason == 'OK':
            result = json.loads(response.text)
            if 'result' in result:
                as_registro_log(accion,user,True,result['result']['estado'],result['result']['mensaje'],as_json,False,request_val)
                return True,result['result']
            else:
                return False, {'mensaje': 'Error'}
        else:
            as_registro_log(accion,user,False,'Error, sin respuesta',{},False,request_val)
            return False, {'mensaje': 'Fuera de tiempo, sin respuesta'} 
    except requests.Timeout:
        as_registro_log(accion,user,False,1,'Fuera de tiempo, sin respuesta',{},False,request_val)
        return False, {'mensaje': 'Fuera de tiempo, sin respuesta'} 
    except requests.exceptions.HTTPError as e:
        as_registro_log(accion,user,False,1,e,{},False,request_val)
        return False, {'mensaje': e} 
    except requests.exceptions.ConnectionError as e:
        as_registro_log(accion,user,False,1,e,{},False,request_val)
        return False, {'mensaje': e} 

def as_registro_log(action,user,as_success,as_estado,as_info,as_json,as_xml,self=False):
    log = self.env['as.siat.log'].sudo().create({
        'name':action,
        'as_user_id':user,
        'as_success':as_success,
        'as_estado':as_estado,
        'as_info':as_info,
        'as_json':as_json,
        'as_xml':as_xml,
    })
    return log


def as_format_error(as_str):
    name = '<b style="color:red">'+str(as_str)+'</b>'
    return name

def as_format_success(as_str):
    name = '<b style="color:green">'+str(as_str)+'</b>'
    return name

def decimal_to_hex(inp):
    return hex(int(inp)).lstrip("0x").upper().rstrip("L")

def date2local_timezone(date_sync):
    return date_sync - timedelta(hours = 4)    

def date2timezone(date_sync):
    return date_sync.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]

def date2timestamp(date_sync):
    return date_sync.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3].replace('-','').replace('T','').replace(':','').replace('.','')
