from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from odoo.tests.common import Form
from odoo.exceptions import UserError
from werkzeug.urls import url_encode
from odoo.exceptions import UserError
class as_stock_picking(models.Model):
    """Heredado para crear funcion de cron quie enviara notificaciones por correo"""
    _inherit="stock.picking"

#     def as_get_notification(self):
#         ahora = fields.Datetime.now() - relativedelta(hours=4)
#         pickings = self.env['stock.picking'].sudo().search([('state','in',('assigned','confirmed','draft','waiting'))])
#         for pick in pickings:
#                 pick.as_send_email()
#             # if pick.scheduled_date == ahora:

#     def as_send_email(self):
#         ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
#         self.ensure_one()
#         template_id = self._find_mail_template_send()
#         lang = self.env.context.get('lang')
#         template = self.env['mail.template'].browse(template_id)
#         if template.lang:
#             lang = template._render_lang(self.ids)[self.id]
#         partners = self.env['res.users.role'].sudo().search([('name','in',('Asistente de almacen ','Coordinador de almacen ','Jefe de almacen '))])
#         as_partner = []
#         for partner in partners:
#             for line in partner.line_ids:
#                 as_partner.append(line.user_id.partner_id.id)
#         ctx = {
#             'default_model': 'stock.picking',
#             'default_res_id': self.ids[0],
#             'default_partner_ids': as_partner,
#             'default_use_template': bool(template_id),
#             'default_template_id': template_id,
#             'default_composition_mode': 'comment',
#             'custom_layout': "mail.mail_notification_light",
#             'force_email': True,
#         }
#         wiz =  {
#             'type': 'ir.actions.act_window',
#             'view_mode': 'form',
#             'res_model': 'mail.compose.message',
#             'views': [(False, 'form')],
#             'view_id': False,
#             'target': 'new',
#             'context': ctx,
#         }

#         wiz = Form(self.env['mail.compose.message'].with_context(ctx)).save()
#         wiz.action_send_mail()
#         self.message_post(body = "<b style='color:green;'>Enviado correo</b>")


#     def _find_mail_template_send(self, force_confirmation_template=False):
#         template_id = self.env['ir.model.data'].xmlid_to_res_id('as_bo_notifications.as_template_pick_email', raise_if_not_found=False)
#         return template_id


#     def _get_share_url(self, redirect=False, signup_partner=False, share_token=None):
#         """
#         Build the url of the record  that will be sent by mail and adds additional parameters such as
#         access_token to bypass the recipient's rights,
#         signup_partner to allows the user to create easily an account,
#         hash token to allow the user to be authenticated in the chatter of the record portal view, if applicable
#         :param redirect : Send the redirect url instead of the direct portal share url
#         :param signup_partner: allows the user to create an account with pre-filled fields.
#         :param share_token: = partner_id - when given, a hash is generated to allow the user to be authenticated
#             in the portal chatter, if any in the target page,
#             if the user is redirected to the portal instead of the backend.
#         :return: the url of the record with access parameters, if any.
#         """
#         self.ensure_one()
#         params = {
#             'model': self._name,
#             'res_id': self.id,
#         }
#         if hasattr(self, 'access_token'):
#             params['access_token'] = self._portal_ensure_token()
#         if share_token:
#             params['share_token'] = share_token
#             params['hash'] = self._sign_token(share_token)
#         if signup_partner and hasattr(self, 'partner_id') and self.partner_id:
#             params.update(self.partner_id.signup_get_auth_param()[self.partner_id.id])

#         return '%s?%s' % ('/mail/view' if redirect else self.access_url, url_encode(params))
    
#     def as_send_email_custom(self,tipo_email):
#         ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
#         self.ensure_one()
#         template_id = self._find_mail_template_send(tipo_email)
#         lang = self.env.context.get('lang')
#         template = self.env['mail.template'].browse(template_id)
#         if template.lang:
#             lang = template._render_lang(self.ids)[self.id]
#         ctx = {
#             'default_model': 'stock.picking',
#             'default_res_id': self.ids[0],
#             'default_use_template': bool(template_id),
#             'default_template_id': template_id,
#             'default_composition_mode': 'comment',
#             'custom_layout': "mail.mail_notification_light",
#             'force_email': True,
#         }
#         wiz =  {
#             'type': 'ir.actions.act_window',
#             'view_mode': 'form',
#             'res_model': 'mail.compose.message',
#             'views': [(False, 'form')],
#             'view_id': False,
#             'target': 'new',
#             'context': ctx,
#         }
#         wiz = Form(self.env['mail.compose.message'].with_context(ctx)).save()
#         wiz.action_send_mail()
#         self.message_post(body = "<b style='color:green;'>Enviado correo</b>")

#     def _find_mail_template_send(self, tipo_email, force_confirmation_template=False):
#         if tipo_email == 'venta_productos_almacenable':
#             template_id = self.env['ir.model.data'].xmlid_to_res_id('as_bo_notifications.as_template_pick_email_venta_productos', raise_if_not_found=False)
#         if tipo_email == 'venta_productos_mixtos':
#             template_id = self.env['ir.model.data'].xmlid_to_res_id('as_bo_notifications.as_template_pick_email_alquiler_productos', raise_if_not_found=False)
#         if tipo_email == 'venta_servicios':
#             template_id = self.env['ir.model.data'].xmlid_to_res_id('as_bo_notifications.as_template_pick_email_alquiler_servicios', raise_if_not_found=False)
#         return template_id
    
#     # email para salida de invenatrio
    
#     def button_validate(self):
#         res = super().button_validate()
#         self.as_send_email_salida_inventario()
#         return res
    
#     def as_send_email_salida_inventario(self):
#         self.ensure_one()
#         template_id = self._find_mail_template_send_salida_inventario()
#         lang = self.env.context.get('lang')
#         template = self.env['mail.template'].browse(template_id)
#         attachment = self.env['ir.attachment'].search([('res_id','=',self.sale_id.id),('res_model','=','sale.order')])
#         if template.lang:
#             lang = template._render_lang(self.ids)[self.id]
#         ctx = {
#             'default_model': 'stock.picking',
#             'default_res_id': self.ids[0],
#             'default_use_template': bool(template_id),
#             'default_template_id': template_id,
#             'default_composition_mode': 'comment',
#             'custom_layout': "mail.mail_notification_light",
#             'force_email': True,
#             'default_attachment_ids': attachment.ids,
#         }
#         wiz =  {
#             'type': 'ir.actions.act_window',
#             'view_mode': 'form',
#             'res_model': 'mail.compose.message',
#             'views': [(False, 'form')],
#             'view_id': False,
#             'target': 'new',
#             'context': ctx,
#         }
#         wiz = Form(self.env['mail.compose.message'].with_context(ctx)).save()
#         wiz.action_send_mail()
#         self.message_post(body = "<b style='color:green;'>Enviado correo</b>")

#     def _find_mail_template_send_salida_inventario(self, force_confirmation_template=False):
#         template_id = self.env['ir.model.data'].xmlid_to_res_id('as_bo_notifications.as_template_pick_email_salida_almacen', raise_if_not_found=False)
#         return template_id

# class as_sale_order_email(models.Model):
#     _inherit='sale.order'
    
#     def action_confirm(self):
#         vals = super(as_sale_order_email, self).action_confirm()
#         bandera_product = False
#         bandera_servicio = False
#         cont_product= 0
#         cont_service= 0
#         hola=self.picking_ids
#         lineas = self.env['sale.order.line'].sudo().search([('order_id','=',self.id),('display_type','=', False)])
#         tamaño_lineas_cotizacion = len(lineas)
#         if lineas:
#             for line in lineas:
#                 if line.product_id.type == 'product':
#                     print("es alamcenable")
#                     cont_product+=1
#                     bandera_product=True
                   
#                 if line.product_id.type == 'service':
#                     print("es servicio")
#                     cont_service+=1
#                     bandera_servicio=True
            
#             if cont_product == tamaño_lineas_cotizacion:
#                 for picking in self.picking_ids:
#                     picking.as_send_email_custom('venta_productos_almacenable')
                    
#             if cont_service == tamaño_lineas_cotizacion:
#                 for order in self:
#                     order.tasks_ids = self.env['project.task'].search(['|', ('sale_line_id', 'in', order.order_line.ids), ('sale_order_id', '=', order.id)])
               
#                 for val in order.tasks_ids:
#                     val.as_send_email_customer('venta_servicios')
            
#             if bandera_product ==True and bandera_servicio == True:
#                 print ('la venta tiene productos de tipo almacenable y tipo servicio')
#                 for picking in self.picking_ids:
#                     picking.as_send_email_custom('venta_productos_mixtos')
#                 for order in self:
#                     order.tasks_ids = self.env['project.task'].search(['|', ('sale_line_id', 'in', order.order_line.ids), ('sale_order_id', '=', order.id)])
               
#                 for val in order.tasks_ids:
#                     val.as_send_email_customer('venta_servicios')
#         return vals


    
    
    
    