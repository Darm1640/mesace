# -*- coding: utf-8 -*-
from odoo import http

# class AsWhatsappGateway(http.Controller):
#     @http.route('/as_whatsapp_gateway/as_whatsapp_gateway/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/as_whatsapp_gateway/as_whatsapp_gateway/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('as_whatsapp_gateway.listing', {
#             'root': '/as_whatsapp_gateway/as_whatsapp_gateway',
#             'objects': http.request.env['as_whatsapp_gateway.as_whatsapp_gateway'].search([]),
#         })

#     @http.route('/as_whatsapp_gateway/as_whatsapp_gateway/objects/<model("as_whatsapp_gateway.as_whatsapp_gateway"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('as_whatsapp_gateway.object', {
#             'object': obj
#         })