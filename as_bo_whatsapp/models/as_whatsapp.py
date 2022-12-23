# -*- coding: utf-8 -*-
import logging
from tabulate import tabulate
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import requests
import json
import base64
from datetime import datetime
_logger = logging.getLogger(__name__)

# Modelo transicional para verificion de funcionamiento de las pasarelas de whatsapp
class AsWhatsapp(models.TransientModel):
    _name = 'as.whatsapp'
    _inherit = ['mail.thread']

    qrImage = fields.Binary('Qr de autorizacion')
    status = fields.Char('Estado de Conexión')
    number_test = fields.Char('Celular de Prueba')
    message_test = fields.Char('Mensaje de Prueba')
    fecha_limite_inicial = fields.Date('Fecha Inicial')
    fecha_limite_final = fields.Date('Fecha Final')
    url_image = fields.Char('URL Imagen')

    # Funcion global para envio de mensajes a whatsapp por la pasarela activada en res_config_settings.as_whatsapp_default_gateway
    # Esta funcion debe usarse en cualquier modelo para enviar mensajes
    def as_send_whatsapp(self, number, message):
        as_whatsapp_default_gateway = self.env['ir.config_parameter'].sudo().get_param('res_config_settings.as_whatsapp_default_gateway')
        result = False
        for num in number.split(','):
            if as_whatsapp_default_gateway == 'chatapi':
                result =  True
            elif as_whatsapp_default_gateway == 'wablas':
                if num and message:
                    status = self.as_wablas_send_message(num,message)
                result = True
        return result

    # Enviar imagen
    def as_send_whatsapp_imagen(self, number, message, as_imagen):
        as_whatsapp_default_gateway = self.env['ir.config_parameter'].sudo().get_param('res_config_settings.as_whatsapp_default_gateway')
        result = False
        for num in number.split(','):
            if as_whatsapp_default_gateway == 'chatapi':
                result =  True
            elif as_whatsapp_default_gateway == 'wablas':
                if num and message:
                    status = self.as_wablas_send_message_imagen(num, message, as_imagen)
                result = True
        return result

    ########## wablas
    ########## wablas
    ########## wablas
    
    # obtener la url de la configuracion
    
    def _get_wablas_url(self):
        url = self.env['ir.config_parameter'].sudo().get_param('res_config_settings.as_whatsapp_wablas_url')
        return url   

    # obtener el token de la configuracion
    
    def _get_wablas_token(self):
        token = self.env['ir.config_parameter'].sudo().get_param('res_config_settings.as_whatsapp_wablas_token')
        return token    

    # enviar mensaje por wablas
    
    def as_wablas_send_message(self, mobile, message, image="", document=""):
        url = self._get_wablas_url()
        token = self._get_wablas_token()
        if url and token:
            try:    
                headers = {'Authorization': token}
                payload = {'phone': mobile, 'message': message}            
                r = requests.post("https://us.wablas.com/api/send-message", data=payload, headers=headers)

                _logger.debug("\n\n\nas_wablas_send_message: %s\n\n\n",r.text)
                self.message_post(body="as_wablas_send_message:\n" + str(r.text) )
                
                return r.text
            except:
                return False

    # enviar imagen por wablas
    
    def as_wablas_send_message_imagen(self, mobile, message, image=""):
        url = self._get_wablas_url()
        token = self._get_wablas_token()
        if url and token:
            try:    
                headers = {'Authorization': token}
                payload = {
                    'phone': mobile, 
                    'caption': message,
                    'image': image,
                    }
                r = requests.post("https://us.wablas.com/api/send-image", data=payload, headers=headers)

                _logger.debug("\n\n\nas_wablas_send_message_imagen: %s\n\n\n",r.text)
                self.message_post(body="as_wablas_send_message_imagen:\n" + str(r.text) )
                
                return r.text
            except:
                return False

    # verificacion de conexion del celular a wablas
    
    def as_wablas_verify(self):
        url = self._get_wablas_url()
        token = self._get_wablas_token()
        if url and token:
            wablas_url = f"{url}/api/device/info?token={token}"
            r = requests.get(wablas_url)

            self.status = "WABLAS " + json.loads(r.text)['data']['whatsapp']['status'].upper()

            _logger.debug("\n\n\nas_wablas_verify: %s\n\n\n",r.text)
            self.message_post(body="as_wablas_verify:\n" + str(r.text),content_subtype='html')
            
            return r.text

    # reinicio de la instancia de wablas
    
    def as_wablas_restart(self):
        url = self._get_wablas_url()
        token = self._get_wablas_token()
        if url and token:
            wablas_url = f"{url}/api/device/reconnect?token={token}"
            r = requests.get(wablas_url)

            _logger.debug("\n\n\nas_wablas_restart: %s\n\n\n",r.text)
            self.message_post(body="as_wablas_restart:\n" + str(r.text) )
            
            return r.text

    # vincular celular con plataforma wablas con qr
    
    def as_wablas_QR(self):
        url = self._get_wablas_url()
        token = self._get_wablas_token()
        if url and token:
            wablas_url = f"{url}/generate/qr.php?token={token}&url=aHR0cHM6Ly91cy53YWJsYXMuY29t"
            # r = requests.get(wablas_url)
            wablas_url = "<a href='" + wablas_url + "' target='_blank'>Conectar Odoo con el Smartphone</a>"
            _logger.debug("\n\n\nas_wablas_restart: %s\n\n\n",wablas_url)
            self.message_post(body=wablas_url,content_subtype='html')
            return wablas_url

    # Boton Enviar prueba mensaje
    
    def as_wablas_send_test_msg(self):
        number = self.number_test
        message_test = self.message_test
        
        if number:
            status = self.as_wablas_send_message(number,message_test)

    # Boton Enviar prueba imagen
    
    def as_wablas_send_test_imagen(self):
        number = self.number_test
        message_test = self.message_test
        url_image = self.url_image
        
        if number:
            status = self.as_wablas_send_message_imagen(number,message_test,url_image)

    ########## chat api
    ########## chat api
    ########## chat api
    
    def _get_chatapi_url(self):
        url = self.env['ir.config_parameter'].sudo().get_param('res_config_settings.as_whatsapp_chatapi_url')
        return url   

    
    def _get_chatapi_token(self):
        token = self.env['ir.config_parameter'].sudo().get_param('res_config_settings.as_whatsapp_chatapi_token')
        return token    

    # Chatapi Desconectar
    
    def as_chatapi_logout(self):    
        url = self._get_chatapi_url()
        token = self._get_chatapi_token()
        if url and token:
            url_new = f"{url}logout?token={token}"
            answer_status = requests.get(url_new)
            status = json.loads(answer_status.text)
            status = _( answer_status.text).upper()
            self.message_post(body="as_chatapi_logout: " + str(status) )

    # Chatapi Resetear
    
    def as_chatapi_reset(self):    
        url = self._get_chatapi_url()
        token = self._get_chatapi_token()
        if url and token:
            url_new = f"{url}reboot?token={token}"
            answer_status = requests.get(url_new)
            status = json.loads(answer_status.text)
            self.message_post(body="as_chatapi_reset: " + str(status) )

    # Chatapi mensajes
    
    def as_chatapi_mensajes(self):    
        url = self._get_chatapi_url()
        token = self._get_chatapi_token()
        if url and token:
            url_new = f"{url}messages?token={token}&last=1"
            answer_status = requests.get(url_new)
            status = json.loads(answer_status.text)
            mensajes = ''
            if 'messages' in status:
                ultimos_mensajes = []
                for msg in status['messages']:
                    date_msg = datetime.fromtimestamp(msg['time']).strftime("%d/%m/%Y")
                    ultimos_mensajes.append((date_msg, msg['senderName'], msg['body'], msg['author']))

                headers = ["Fecha", "Nombre","Mensaje", "Autor"]
                table = tabulate(ultimos_mensajes, headers, tablefmt='html')
                table = table.replace("<table>","<table class='blueTable'")

                self.message_post(body=table)
            else:
                messages = _( answer_status.text).upper()
                self.message_post(body="Mensajes:\n" + str(status) )

    # Chatapi status
    
    def as_chatapi_status(self):
        url = self._get_chatapi_url()
        token = self._get_chatapi_token()
        if url and token:
            url_new = f"{url}status?token={token}&full=1"
            answer_status = requests.get(url_new)
            status = json.loads(answer_status.text)
            if 'accountStatus' in status:
                self.status = "CHATAPI " + _(status['accountStatus']).upper()
                self.message_post(body="as_chatapi_status:\n" + str(status) )
            else:
                self.status = _( answer_status.text).upper()
                self.message_post(body="as_chatapi_status:\n" + str(status) )

    # Chatapi obtener QR
    
    def as_chatapi_qr(self):
        url = self._get_chatapi_url()
        token = self._get_chatapi_token()
        if url and token:
            url_new = f"{url}qr_code?token={token}"
            headers = {'Content-type': 'application/plain'}
            answer = requests.get(url_new)
            # status = json.loads(answer.text)
            if answer.content:
                answer_html = "<image src='data:image/png;base64,"+base64.b64encode(answer._content).decode('utf-8')+"' />"
                self.message_post(body="as_chatapi_send_message: " + answer_html, content_subtype='html' )

    # Chatapi Enviar Prueba
    
    def as_chatapi_send_message(self, mobile, message, image="", document=""):
        url = self._get_chatapi_url()
        token = self._get_chatapi_token()
        if url and token:
            method = "sendMessage"
            url = f"{url}{method}?token={token}"
            headers = {'Content-type': 'application/json'}
            data = {"phone":mobile,"body":message}
            answer = requests.post(url, data=json.dumps(data), headers=headers)

            _logger.debug("\n\n\nas_chatapi_send_message: %s\n\n\n",answer.json() )
            self.message_post(body="as_chatapi_send_message:\n" + str(answer.json() ) )

            return answer.json()             

    # Boton Enviar prueba
    
    def as_chatapi_send_test_msg(self):
        number = self.number_test
        message_test = self.message_test
        
        if number:
            status = self.as_chatapi_send_message(number,message_test)            