# -*- coding: utf-8 -*-
import logging
import odoo
from odoo import SUPERUSER_ID
from odoo import api, fields, models, _

class ComprasConfig(models.TransientModel):
    _inherit = 'res.config.settings'

    as_facturas_confirmadas = fields.Selection([
        ('0', 'No Confirmar factura, al momento de crear una factura desde compras'),
        ('1', 'Confirmar factura, al momento de crear una factura desde compras'),],
        'Facturas de compras', help='Al crear al compra realizara el evento asigando')

    tipo_factura_defecto = fields.Many2one('as.tipo.factura', 
        string='Tipo de factura por defecto en tesoreria y compras', help="Tipo de factura al momento de crear un compra o una compra y facturas de comrpas.")
        # , 
        # default=lambda self: self.env.ref('as_bo_purchase_invoice.as_tipo_factura_prov1'))

    group_escanner_codigo_qr = fields.Boolean(string="Habilitar escanner codigo QR", 
        help=" Habilita un campo para que pueda scannear el QR en el formulario de compras y facturas de compras",
        implied_group='as_bo_purchase_invoice.group_escanner_codigo_qr')

    group_habilitar_plan_pagos_po = fields.Boolean(string="Habilitar plan de pagos en factura proveedores", 
        help=" Habilita plan de pagos visual en el formulario de Facturas de proveedores",
        implied_group='as_bo_purchase_invoice.group_habilitar_plan_pagos_po')

    as_ingreso_confirmado = fields.Boolean(string="Crear factura si el ingreso a almacen esta confirmado",
        help="Dejara crear factura si los productos fueron ingresados al almacen", default=False)
        
    @api.model
    def get_values(self):
        res = super(ComprasConfig, self).get_values()
        res['as_ingreso_confirmado'] = self.env['ir.config_parameter'].sudo().get_param('res_config_settings.as_ingreso_confirmado')
        res['as_facturas_confirmadas'] = self.env['ir.config_parameter'].sudo().get_param('res_config_settings.as_facturas_confirmadas')

        return res
    #de aqui en adelante es la obtencion d elos valores dado que el modelo es transitorio
    @api.model
    def set_values(self):
        self.env['ir.config_parameter'].sudo().set_param('res_config_settings.as_ingreso_confirmado', self.as_ingreso_confirmado)
        self.env['ir.config_parameter'].sudo().set_param('res_config_settings.as_facturas_confirmadas', self.as_facturas_confirmadas)
        super(ComprasConfig, self).set_values()

    # @api.multi
    def set_param_fac_po(self):
        ir_config_parameter_obj = self.env['ir.config_parameter']
        ir_config_parameter_obj.sudo().set_param('res.config.settings', 'as_facturas_confirmadas', self.as_facturas_confirmadas or '0')

    @api.model
    def get_param_fac_po(self, fields):
        ir_config_parameter_obj = self.env['ir.config_parameter']
        as_facturas_confirmadas = ir_config_parameter_obj.sudo().get_param('as_facturas_confirmadas')

        return {
            'as_facturas_confirmadas': as_facturas_confirmadas,
        }

    # @api.multi
    def set_tipo_factura_defecto(self):
        res = self.env['ir.config_parameter'].set_param('res.config.settings', 'tipo_factura_defecto', self.tipo_factura_defecto.id)
        return res

    # @api.multi
    def set_tipo_factura_defecto1(self):
        self.env['ir.config_parameter'].write({'tipo_factura_defecto': self.tipo_factura_defecto.id})


    # @api.multi
    def set_as_ingreso_confirmado(self):
        res = self.env['ir.config_parameter'].set_param('res.config.settings', 'as_ingreso_confirmado', self.as_ingreso_confirmado)
        return res

    # @api.multi
    def set_as_ingreso_confirmado1(self):
        self.env['ir.config_parameter'].write({'as_ingreso_confirmado': self.as_ingreso_confirmado})