from odoo import models, fields, api

class ClientFields(models.Model):
    _inherit = "res.partner"

    
    forma_pago_id = fields.Many2one('as.forma.pago','Forma de Pago')
    tipo_cliente_id = fields.Many2one('as.tipo.cliente','Tipo de Cliente')
    as_code = fields.Char(string='Código Cliente')

    _sql_constraints = [
        (
            'check_as_code',
            'unique (as_code)',
            "El codigo de Cliente debe ser unico.",
        ),
    ]

    @api.onchange('name')
    @api.depends('name')
    def as_split_name(self):
        for client in self:
            if client.name:
                name = client.name
                cont = 5
                limit = len(name)
                prefix = name[:cont]
                for literal in range(5,limit):
                    prefix = name[:literal]
                    partner = self.env['res.partner'].search([('as_code','=',prefix.upper()),('id','!=',self.id.origin)])
                    if not partner:
                        break  
                client.as_code = prefix.upper()


    def as_generar_codigo(self):
        for client in self:
            if client.name:
                name = client.name
                cont = 5
                limit = len(name)
                prefix = name[:cont]
                for literal in range(5,limit):
                    prefix = name[:literal]
                    partner = self.env['res.partner'].search([('as_code','=',prefix.upper())])
                    if not partner:
                        break  
                client.as_code = prefix.upper()