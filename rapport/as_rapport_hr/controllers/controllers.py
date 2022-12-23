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
class Evaluacion(http.Controller):
    
    @http.route(['/evaluacion_empleado/evaluacion'], auth="public", type="http")
    def evaluacion(self, **post):
        total_1 = post.get('total_1') or None
        # _logger.debug(total_1)
        # _logger.debug("\n\n HOLASSSS %s\n\n",total_1)

        total_cuad=request.env['as.survey.cuadrante'].sudo().search([('as_range_start','<=',total_1),('as_range_end','>=',total_1)] )#consulto a la base de datos
        _logger.debug("\n\n HOLASSSS 2 %s\n\n",total_cuad.name)
        # result_total= request.env['hr.employee.as.talent'].sudo().create({'resultado':total_1})
        # _logger.debug("\n\n eh aqui %s\n\n",result_total)
        bandera = False
        if total_1:
            if total_1 != 'NaN':
                result_total= request.env['hr.employee.as.talent'].sudo().create({'resultado':total_1})
            
            bandera = True
            vals = {
                'name':total_cuad.name,
                'bandera':bandera,

            }
            return json.dumps(vals)
        else:
                    
            return None

    # @http.route('/evaluacion_resultado', auth="public", website=True , type="http")
    # def resultado(self, **kwargs):
    #     result={}
    #     data=cgi.FieldStorage()
    #     output=data.getvalue("resultado")
    #     result["a"]=output
    #     return json.dumps(result)
        