from odoo import api, fields, models, _
from odoo.exceptions import UserError

class res_partner(models.Model):
    _inherit = 'res.partner'


    as_complemento_nit = fields.Char('Complemento', help="Complemento de Carnet de Identidad")
    as_identification = fields.Many2one('as.siat.catalogos', string="Documento Identidad", domain="[('as_group', '=', 'DOCUMENTO_IDENTIDAD')]", default=lambda self: self.env['as.siat.catalogos'].search([('as_group', '=', 'DOCUMENTO_IDENTIDAD')],limit=1))
    as_type_contribuyente = fields.Selection(selection=[
            ('1', 'Normal'),
            ('2', 'Gubernamental'),
            ('3', 'Tributario Impuestos'),
        ], string='Tipo Contribuyente', required=True, default="1", change_default=True)

    @api.onchange('as_type_contribuyente')
    def as_onchange_contribuyente(self):
        for partner in self:
            if partner.as_type_contribuyente == '1':
                partner.vat = ''
                partner.as_razon_social = '' 
            elif partner.as_type_contribuyente == '2':
                partner.vat = '99001'
                partner.as_razon_social = ''
            else:
                partner.vat = '99002'
                partner.as_razon_social = 'CONTROL TRIBUTARIO'
                