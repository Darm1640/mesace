import pytz
from odoo import http, api, fields, models, _
from datetime import datetime, timedelta  
from odoo.http import request
import json
import logging
_logger = logging.getLogger(__name__)
from odoo import models, fields, api
import datetime
import urllib
from odoo import http
import json
import yaml

mensaje_error = {			
                "success": False,
                "estado": 1,
                "mensaje":""
            }
mensaje_correcto = {		
                "success": True,
                "estado": 0,
                "mensaje":""		
}

class EvaluacionTest(http.Controller):
    """Endpoint para crear registros demo en modelo de odoo"""   

    @http.route(['/evaluacion_empleado/demo',], auth="public", type="http", method=['GET'], csrf=False, cors='*')
    def demo(self, **post):
        try:
            json_date = post
            if json_date:
                as_demo = request.env['hr.employee.test'].sudo().create(json_date)
                as_demo.as_get_compromiso()
                as_demo.as_send_email()
                mensaje_correcto['mensaje']="Creado Registro Satisfactoriamente"
                return json.dumps(mensaje_correcto)
            else:
                mensaje_error['mensaje']="No posee Usuario"
                return json.dumps(mensaje_error)
            
        except Exception as e:
            mensaje_error['mensaje']=str(e)
            return json.dumps(mensaje_error)

    # def as_get_json_validate(self,as_json):
    #     partner = as_json['as_cliente']
    #     cliente = request.env['res.users'].sudo().search([('name','=',partner)])
    #     if cliente:
    #         as_json['as_cliente'] = cliente.id
    #         return as_json
    #     else:
    #         cliente = request.env['res.users'].sudo().create(
    #             {
    #                 'name':partner,
    #                 'login':as_json['as_email'],
    #                 'email':as_json['as_email'],
    #                 'groups_id': [(6, 0, [request.env.ref('base.group_user').id])],
    #             }
    #             )
    #         as_json['as_cliente'] = cliente.id
    #         return as_json

    @http.route(['/evaluacion_empleado/config',], auth="public", type="http", method=['GET'], csrf=False, cors='*')
    def config(self, **post):
        try:
            json_date = request.env['as.test.config'].sudo().search([],limit=1)
            if json_date:
                mensaje_correcto['mensaje']= {
                    'as_ini_massage': json_date.as_ini_massage,
                    'as_save_massage': json_date.as_save_massage,
                }
                return json.dumps(mensaje_correcto)
            else:
                mensaje_error['mensaje']="No posee Usuario"
                return json.dumps(mensaje_error)
            
        except Exception as e:
            mensaje_error['mensaje']=str(e)
            return json.dumps(mensaje_error)