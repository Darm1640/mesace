# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from datetime import datetime, timedelta
from time import mktime
import time
from datetime import datetime, timedelta
from odoo.exceptions import UserError, RedirectWarning, ValidationError, MissingError
from dateutil.relativedelta import relativedelta

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    as_fecha_ingreso = fields.Datetime(string="Fecha Ingreso", default=datetime.now(), required=True)
    as_antiguedad = fields.Integer(string='Años de Antiguedad',compute="_compute_website_url")
    # as_name_afp = fields.Many2one('as.hr.employee.afp',string='AFP a la que aporta', required=True)
    as_name_afp = fields.Many2one('as.hr.employee.afp', string='Nombre AFP')
    as_code_iva = fields.Char(string='Codigo Referencial RC-IVA')
    as_aportador_afp = fields.Selection([('0','0'),('1','1')],string='¿Aporte a la AFP?',default="0", required=True)
    as_persona_discapacidad = fields.Selection([('0','0'),('1','1')],string='¿Persona con discapacidad?', default="0",required=True)
    as_tutor_persona_discapacidad = fields.Selection([('0','0'),('1','1')],string='Tutor de persona con discapacidad', default="0",required=True)
    as_caja_salud = fields.Selection([('0',''),('1','Caja Nacional de Salud (C.N.S).'),('2','Caja Nacional de Salud (C.P.S).'),('3','Caja de Salud de Caminos.'),('4','Caja Bancaria Estatal de Salud (C.B.E.S.).'),('5','Caja de Salud de la Banca Privada (C.S.B.P.).'),('6','Caja de Salud Cordes.'),('7','Seguro Social Universitario (S.I.S.S.U.B.).'),('8','Corporacion del Seguro Social Militar (COOSMIL).'),('9','Seguro Integral de Salud (S.I.N.E.C.).'),('10','Seguro delegado.')],string='Caja de salud',default="0", required=True)
    as_clasificacion_laboral = fields.Selection([('0',''),('1','Ocupaciones de direccion en la administracion publica y empresas.'),('2','Ocupaciones de profesionales cietificos e intelectuales.'),('3','Ocupaciones de tecnicos y profesionales de apoyo.'),('4','Empleados de oficina.'),('5','Trabajadores de los servicios y vendedores del comercio.'),('6','Productores y trabajadoresen la agricultura, pecuaria, agropecuaria y pesca.'),('7','Trabajadores en la industria extractiva, construccion, industria, manufactura y otros oficios.'),('8','Operaciones de instalaciones y maquinarias.'),('9','Trabajadores no calificados'),('10','Fuerzas armadas')],string='Clasificacion Laboral',default="0", required=True)
    nombre = fields.Char(string='Nombre')
    as_documento = fields.Char(string='Tipo Documento',default='CI')
    as_jubilado = fields.Selection([('0','0'),('1','1')],string='Jubilado',default="0", required=True)
    as_complemento_ci = fields.Char(string='Complemento')
    apellido_1 = fields.Char(string='Apellido')
    apellido_2 = fields.Char(string='Segundo Apellido')
    apellido_3 = fields.Char(string='Apellido de Casada')
    as_novedades = fields.Selection([('I','Incorporación'),('V','Vigente'),('D','Desvinculado')], default='V',string='Novedades')
    as_expedito = fields.Selection([('CB','CB'),('LP','LP'),('SZ','SZ'),('OR','OR'),('PT','PT'),('TAR','TAR'),('BN','BN'),('CH','CH'),('PD','PD')], default='CB',string='Expedito')
    as_nua = fields.Char(string='NUA/CUA')
    as_tipo_asegurado = fields.Selection([('M','Minero'),('E','Estacional'),('C','Cooperativista'),('Vacío','Ninguno de los anteriores')], string='Tipo Asegurado')
    as_seguro = fields.Char(string='Nro. Seguro')
    nombre_2 = fields.Char(string='Segundo Nombre')
    fecha_novedad = fields.Date('Fecha Novedad')
    as_tipo_cotizante = fields.Selection([('1','Dependiente o Asegurado con Pensión del SIP < 65 años que aporta'),('8','Dependiente o Asegurado con Pensión del SIP > 65 años que aporta'),('C','Asegurado con Pensión del SIP < 65 años que NO aporta'),('D','Asegurado con Pensión del SIP > 65 años que NO aporta')], default='1',string='Tipo Cotizante')
    as_lugar_de_trabajo = fields.Many2one('as.hr.lugar.trabajo', string='Lugar de trabajo')
    as_sucursal_empleado = fields.Many2one('as.sucursal', string='Sucursal')

    def as_converter_users(self):
        for emp in self:
            group_portal = self.env.ref('base.group_portal')
            if not emp.user_id:
                raise UserError(_('Debe Tener un Usuario ERP creado'))
            emp.user_id.write({'active': True, 'groups_id': [(6, 0, [group_portal.id])]})
            emp.user_id.share = True
            emp.user_id.partner_id.signup_prepare()
    
    @api.onchange('nombre','nombre_2','apellido_1','apellido_2')
    def concatenar_nombres(self):
        for empleado in self:
            nombre = ''
            nombre_2 = ''
            apellido_1 = ''
            apellido_2 = ''
            if empleado.nombre:
                nombre = empleado.nombre
            if empleado.nombre_2:
                nombre_2 = empleado.nombre_2
            if empleado.apellido_1:
                apellido_1 = empleado.apellido_1
            if empleado.apellido_2:
                apellido_2 = empleado.apellido_2
            empleado.name = str(nombre) +' '+ str(nombre_2) +' '+ str(apellido_1) +' '+ str(apellido_2)

    @api.onchange('as_fecha_ingreso')
    def _compute_website_url(self):
        for employee in self:
            now = datetime.now()
            fecha_ingreso = employee.as_fecha_ingreso
            antiguedad = fecha_ingreso - now
            employee.as_antiguedad = int(antiguedad.days/30/12)*-1

