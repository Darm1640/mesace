
import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from werkzeug.urls import url_encode

import base64

class as_Hr_Leave(models.Model):
    _inherit = "hr.leave"

    partner_id = fields.Char('Cliente')
        
    def action_approve(self):
        res = super(as_Hr_Leave, self).action_approve()
                
        #CASO 52: AL PRESIONAR BOTON APROBAR (PERMISOS) 
        #el numero de la plantilla es el ID de la plantilla que corresponde
        valores_email_cincuatro = self.env['mail.template'].search([('id','=',146)])
        if valores_email_cincuatro:
            nombre_modelo_cincuatro = valores_email_cincuatro.model_id.model
            #envio de email sin adjuntos
            self.env['mail.template'].as_send_email_con_adjuntos(self, valores_email_cincuatro.id, nombre_modelo_cincuatro)
            if valores_email_cincuatro.as_mobile:
                number_cincuatro = valores_email_cincuatro.as_mobile
                if valores_email_cincuatro.as_desde and valores_email_cincuatro.as_asunto:
                    if valores_email_cincuatro.as_desde == '${object.env.user.partner_id.email}':
                        remitente_seis = str(self.env.user.partner_id.email)
                    if valores_email_cincuatro.as_desde == '${object.user_id.login}':
                        remitente_seis = str(self.user_id.login)
                    if valores_email_cincuatro.as_desde != '${object.env.user.partner_id.email}' and valores_email_cincuatro.as_desde != '${object.user_id.login}':
                        remitente_seis = str(valores_email_cincuatro.as_desde)
                        
                    mensajito = str('DE: ')+ remitente_seis +' '+ valores_email_cincuatro.as_asunto+': '+valores_email_cincuatro.as_mensaje_whatsapp_email +' '+str(self.user_id.partner_id.name)
                    
                    self.env['as.whatsapp'].sudo().as_send_whatsapp(number_cincuatro,mensajito)
                    self.message_post(body = "<b style='color:blue;'>Mensaje enviado por WhatsApp 'Caso 54'</b>")
        return res
    
    #funcion necesaria para poder enviar emails
    def _get_share_url(self, redirect=False, signup_partner=False, share_token=None):
        """
        Build the url of the record  that will be sent by mail and adds additional parameters such as
        access_token to bypass the recipient's rights,
        signup_partner to allows the user to create easily an account,
        hash token to allow the user to be authenticated in the chatter of the record portal view, if applicable
        :param redirect : Send the redirect url instead of the direct portal share url
        :param signup_partner: allows the user to create an account with pre-filled fields.
        :param share_token: = partner_id - when given, a hash is generated to allow the user to be authenticated
            in the portal chatter, if any in the target page,
            if the user is redirected to the portal instead of the backend.
        :return: the url of the record with access parameters, if any.
        """
        self.ensure_one()
        params = {
            'model': self._name,
            'res_id': self.id,
        }
        if hasattr(self, 'access_token'):
            params['access_token'] = self._portal_ensure_token()
        if share_token:
            params['share_token'] = share_token
            params['hash'] = self._sign_token(share_token)
        if signup_partner and hasattr(self, 'partner_id') and self.partner_id:
            params.update(self.partner_id.signup_get_auth_param()[self.partner_id.id])

        return '%s?%s' % ('/mail/view' if redirect else self.access_url, url_encode(params))
