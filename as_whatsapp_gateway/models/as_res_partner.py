from odoo import models, fields, api

class ClientFields(models.Model):
    _inherit = "res.partner"

    as_mensaje_whatsapp = fields.Text(string='Whatsapp')

    def boton_send_whatsapp(self):
        if self.mobile:
            number = self.mobile
            self.env['as.whatsapp'].sudo().as_send_whatsapp(number,self.as_mensaje_whatsapp)
        self.as_mensaje_whatsapp = ''
