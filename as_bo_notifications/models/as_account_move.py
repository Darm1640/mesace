from odoo import models, fields, api

class accountmove(models.Model):
    """Heredado para crear funcion de cron quie enviara notificaciones dde facturas a whtsapp"""
    _inherit="account.move"

    def as_cron_invoice_whatsapp(self):
        invoice= self.env['account.move'].sudo().search([('state','=','posted'),('move_type','=','out_invoice'),('payment_state','!=','paid')])
        for inv in invoice:
            date =  fields.Date.context_today(self)
            date_invoice = inv.invoice_date
            dias = date - date_invoice
            self.get_send_whatsapp(inv,dias.days)
        return True

    def get_send_whatsapp(self,inv,dias):
        type_days = self.env['as.envio.notifications'].sudo().search([])
        for days_type in type_days:
            if days_type.as_dias == dias:
                numbers = inv.partner_id.mobile
                if numbers:
                    message = "*😊"+str(inv.company_id.name)+" 😊* le informa.\n Estimado Cliente, Espectrocom tiene el placer de saludarle e informarle que su factura: Nro. "+str(inv.name)+" se encuentra vencida,nuestra empresa pone a su disposición los siguientes datos bancarios: \n"
                    for bank in inv.company_id.partner_id.bank_ids:
                        message += str(bank.acc_number)+' - '+str(bank.bank_id.name)+'\n'
                    message += "\nSi tiene dudas o consultas puede contactar a "+ str(inv.user_id.partner_id.name)+'  -Encargado de facturacion - celular '+ str(inv.user_id.partner_id.mobile)+' y correo electrónico '+str(inv.company_id.email)+'\n'
                    result = self.env['as.whatsapp'].sudo().as_send_whatsapp(numbers,message)
                    inv.message_post(body=str(days_type.name)+': '+message)
                    inv.message_post(body=result)



class AsEnvioNotifications(models.Model):
    """Modelo encargado de guardar las condiciones de envio de notificaciones"""
    _name="as.envio.notifications"
    _description="Modelo encargado de guardar las condiciones de envio de notificaciones"

    name = fields.Char(string='Titulo')
    as_dias = fields.Integer(string='Dias')
