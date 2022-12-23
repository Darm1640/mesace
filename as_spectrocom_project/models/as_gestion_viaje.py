# -*- coding: utf-8 -*-
from odoo import tools
from odoo.tests.common import Form
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import time
from werkzeug.urls import url_encode
#tools
from collections import defaultdict

from odoo import api, fields, models, tools, _
from odoo.addons.stock_landed_costs.models import product
from odoo.exceptions import UserError, RedirectWarning, ValidationError
import odoo.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)

class Gestion_Viaje(models.Model):
    _name = 'as.gestion.viaje'
    _description = "Plantilla de costos de importacion"
    _inherit = ['mail.thread']
    
    as_state_viaje = fields.Selection([
        ('draft', 'Borrador'),
        ('to_approval', 'Para Aprobar'),
        ('approval', 'Aprobado')
    ], string='Estado Viatico', default='draft')
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
        default=lambda self: self.env.company)
    as_approval = fields.Boolean(string="Permitido aprobar",compute="_get_approvals")
    partner_id = fields.Char(string='Cliente')
    
    # def _as_obtener_cliente_viaje(self):
    #     result = self.env['project.task'].search([('id','=',self.as_project_task_id.id)])
    #     if self.as_project_task_id.id and not result:
    #         raise UserError(_('Usted no tiene permiso para ingresar a esta gestion de viaje. La tarea no esta asignada a usted, ponerse en contacto con su administrador'))
    #     if result:
    #         self.partner_id = result.partner_id
    #         return self.partner_id
        
    #     if self.as_project_task_id
    
    @api.model
    def _default_user(self):
        return self.env.context.get('user_id', self.env.user.id)
    user_id = fields.Many2one('res.users', 'Usuario')
    
    
    @api.depends('total')
    def _get_approvals(self):
        for order in self:
            aprobar = False
            monto = order.total
            usuario = order.env.user.id
            rango_approval = self.env['as.level.approval'].sudo().search([('as_type','=','viajes'),('as_amount_min','<=',monto),('as_amount_max','>=',monto)],order=" id desc",limit=1)
            if rango_approval:
                if usuario in rango_approval.as_users_ids.ids:
                    aprobar = True 
            order.as_approval = aprobar

    def button_confirm_viaje(self):
        for project in self:
            project.as_state_viaje = 'approval'
            # project.as_send_email([project.user_id.partner_id.id],'approval')
            
            #CASO 43: AL PRESIONAR BOTON aprobar (gestion viajes)       
            #el numero de la plantilla es el ID de la plantilla que corresponde
            valores_email_cuarentatres = self.env['mail.template'].search([('id','=',137)])
            if valores_email_cuarentatres:
                nombre_modelo_tresiete = valores_email_cuarentatres.model_id.model
                #envio de email sin adjuntos
                self.env['mail.template'].as_send_email_sin_adjuntos(self, valores_email_cuarentatres.id, nombre_modelo_tresiete)
                if valores_email_cuarentatres.as_mobile:
                    number_treitres = valores_email_cuarentatres.as_mobile
                    if valores_email_cuarentatres.as_desde and valores_email_cuarentatres.as_asunto:
                        if valores_email_cuarentatres.as_desde == '${object.env.user.partner_id.email}':
                            remitente_seis = str(self.env.user.partner_id.email)
                        if valores_email_cuarentatres.as_desde == '${object.as_project_task_id.user_id.login}':
                            remitente_seis = str(self.as_project_task_id.user_id.login)
                        if valores_email_cuarentatres.as_desde != '${object.env.user.partner_id.email}' and valores_email_cuarentatres.as_desde != '${object.as_project_task_id.user_id.login}':
                            remitente_seis = str(valores_email_cuarentatres.as_desde)
                            
                        mensajito = str('DE: ')+ remitente_seis +': '+ valores_email_cuarentatres.as_asunto+': '+valores_email_cuarentatres.as_mensaje_whatsapp_email + str(self.as_project_task_id.name)
                        
                        self.env['as.whatsapp'].sudo().as_send_whatsapp(number_treitres,mensajito)
                        self.message_post(body = "<b style='color:blue;'>Mensaje enviado por WhatsApp 'Caso 43'</b>")
                    
            #CASO 44: AL PRESIONAR BOTON aprobar (gestion viajes)        
            #el numero de la plantilla es el ID de la plantilla que corresponde
            # if self.as_presupuesto_viaticos > 1:
            valores_email_cuarentacuatro = self.env['mail.template'].search([('id','=',138)])
            if valores_email_cuarentacuatro:
                nombre_modelo_tresiete = valores_email_cuarentacuatro.model_id.model
                #envio de email sin adjuntos
                self.env['mail.template'].as_send_email_sin_adjuntos(self, valores_email_cuarentacuatro.id, nombre_modelo_tresiete)
                if valores_email_cuarentacuatro.as_mobile:
                    number_treicuatro = valores_email_cuarentacuatro.as_mobile
                    if valores_email_cuarentacuatro.as_desde and valores_email_cuarentacuatro.as_asunto:
                        if valores_email_cuarentacuatro.as_desde == '${object.env.user.partner_id.email}':
                            remitente_seis = str(self.env.user.partner_id.email)
                        if valores_email_cuarentacuatro.as_desde == '${object.as_project_task_id.user_id.login}':
                            remitente_seis = str(self.as_project_task_id.user_id.login)
                        if valores_email_cuarentacuatro.as_desde != '${object.env.user.partner_id.email}' and valores_email_cuarentacuatro.as_desde != '${object.as_project_task_id.user_id.login}':
                            remitente_seis = str(valores_email_cuarentacuatro.as_desde)
                            
                        mensajito = str('DE: ')+ remitente_seis +': '+ valores_email_cuarentacuatro.as_asunto+': '+valores_email_cuarentacuatro.as_mensaje_whatsapp_email + str(self.as_project_task_id.name) + str(' fue aprobado.')
                        
                        self.env['as.whatsapp'].sudo().as_send_whatsapp(number_treicuatro,mensajito)
                        self.message_post(body = "<b style='color:blue;'>Mensaje enviado por WhatsApp 'Caso 44'</b>")
            
            #CASO 45: AL PRESIONAR BOTON aprobar (gestion viajes)        
            #el numero de la plantilla es el ID de la plantilla que corresponde
            # if self.as_presupuesto_viaticos > 1:
            valores_email_cuarentacinco = self.env['mail.template'].search([('id','=',139)])
            if valores_email_cuarentacinco:
                nombre_modelo_tresiete = valores_email_cuarentacinco.model_id.model
                #envio de email sin adjuntos
                self.env['mail.template'].as_send_email_sin_adjuntos(self, valores_email_cuarentacinco.id, nombre_modelo_tresiete)
                if valores_email_cuarentacinco.as_mobile:
                    number_treicinco = valores_email_cuarentacinco.as_mobile
                    if valores_email_cuarentacinco.as_desde and valores_email_cuarentacinco.as_asunto:
                        if valores_email_cuarentacinco.as_desde == '${object.env.user.partner_id.email}':
                            remitente_seis = str(self.env.user.partner_id.email)
                        if valores_email_cuarentacinco.as_desde == '${object.as_project_task_id.user_id.login}':
                            remitente_seis = str(self.as_project_task_id.user_id.login)
                        if valores_email_cuarentacinco.as_desde != '${object.env.user.partner_id.email}' and valores_email_cuarentacinco.as_desde != '${object.as_project_task_id.user_id.login}':
                            remitente_seis = str(valores_email_cuarentacinco.as_desde)
                            
                        mensajito = str('DE: ')+ remitente_seis +': '+ valores_email_cuarentacinco.as_asunto+': '+valores_email_cuarentacinco.as_mensaje_whatsapp_email + str(self.as_project_task_id.name)
                        
                        self.env['as.whatsapp'].sudo().as_send_whatsapp(number_treicinco,mensajito)
                        self.message_post(body = "<b style='color:blue;'>Mensaje enviado por WhatsApp 'Caso 45'</b>")
            
            #CASO 46: AL PRESIONAR BOTON aprobar (gestion viajes)        
            #el numero de la plantilla es el ID de la plantilla que corresponde
            # if self.as_presupuesto_viaticos > 1:
            valores_email_cuarentaseis = self.env['mail.template'].search([('id','=',140)])
            if valores_email_cuarentaseis:
                nombre_modelo_cuarentaseis = valores_email_cuarentaseis.model_id.model
                #envio de email sin adjuntos
                self.env['mail.template'].as_send_email_sin_adjuntos(self, valores_email_cuarentaseis.id, nombre_modelo_cuarentaseis)
                if valores_email_cuarentaseis.as_mobile:
                    number_treicinco = valores_email_cuarentaseis.as_mobile
                    if valores_email_cuarentaseis.as_desde and valores_email_cuarentaseis.as_asunto:
                        if valores_email_cuarentaseis.as_desde == '${object.env.user.partner_id.email}':
                            remitente_seis = str(self.env.user.partner_id.email)
                        if valores_email_cuarentaseis.as_desde == '${object.as_project_task_id.user_id.login}':
                            remitente_seis = str(self.as_project_task_id.user_id.login)
                        if valores_email_cuarentaseis.as_desde != '${object.env.user.partner_id.email}' and valores_email_cuarentaseis.as_desde != '${object.as_project_task_id.user_id.login}':
                            remitente_seis = str(valores_email_cuarentaseis.as_desde)
                            
                        mensajito = str('DE: ')+ remitente_seis +' '+ valores_email_cuarentaseis.as_asunto+': '+valores_email_cuarentaseis.as_mensaje_whatsapp_email + str(self.as_project_task_id.name) +'  fue aprobado: '
                        
                        self.env['as.whatsapp'].sudo().as_send_whatsapp(number_treicinco,mensajito)
                        self.message_post(body = "<b style='color:blue;'>Mensaje enviado por WhatsApp 'Caso 46'</b>")

    as_worker_signature = fields.Binary(string='Firma del conductor')
    as_customer_signature_i = fields.Binary(string='Firma del inspector')
    as_comentarios = fields.Text(string='Comentarios de la revisión del vehiculo')
    as_inspector = fields.Many2one('hr.employee', string="Inspector")
    as_cargo = fields.Char('Cargo del inspector')

    as_project_task_id = fields.Many2one('project.task', string="Proyecto")

    name = fields.Char('Nombre')
    marca = fields.Char('Marca y modelo')
    conductor = fields.Many2one('res.partner', string="Conductor")
    conductor_h = fields.Many2one('hr.employee', string="Conductor")
    as_vehiculos = fields.Many2one('fleet.vehicle', string="Marca y modelo")
    tipo_vehiculo = fields.Char('Tipo de vehiculo')
    nro_licencia = fields.Char('Nº licencia')
    venc_lc = fields.Date('Venc LC.')
    venc_md = fields.Date('Venc MD.')
    categoria = fields.Char('Categoria')
    km_inicial = fields.Char('Km inicial')
    km_final = fields.Char('Km final')
    nro_interno = fields.Char('Nº interno')
    nro_placa = fields.Char('Nº placa')
    km_cambio_aceite = fields.Char('Km cambio de aceite')
    color = fields.Char('Color')
    firma = fields.Binary('Firma')

    # Datos del viaje
    motivo_viaje = fields.Char('Motivo del viaje')
    fecha_salida = fields.Datetime('Fecha/Hora de salida')
    fecha_estimada = fields.Datetime('Fecha/Hora de llegada estimada')
    lugar_partida = fields.Char('Lugar de partida')
    lugar_destino = fields.Char('Lugar de destino')
    ruta_plan = fields.Char('Ruta planificada (Ennumere localidades o puntos importantes de la ruta)')
    acompanante = fields.Selection(selection=[('Si','Si'),('No','No')],default='No', string="Acompañante")
    nro_pasajeros = fields.Integer('Numero de pasajeros)')
    nombre_acompanante = fields.Char('Nombre acompañante')
    # tipo_carga = fields.Selection(selection=[('Si','Si'),('No','No')],default='No', string="Acompañante")
    tipo_cargas = fields.Char('Tipo de carga que transporta')

    # vehiculo antes del viaje estado general
    llantas = fields.Selection(selection=[('B','B'),('R','R'),('N/A','N/A')], string="Llantas y llanta de auxilio")
    luces = fields.Selection(selection=[('B','B'),('R','R'),('N/A','N/A')], string="Luces de parqueo")
    luces_direccionales = fields.Selection(selection=[('B','B'),('R','R'),('N/A','N/A')], string="Luces direccionales")
    luces_alta = fields.Selection(selection=[('B','B'),('R','R'),('N/A','N/A')], string="Luces alta y baja")
    luces_freno = fields.Selection(selection=[('B','B'),('R','R'),('N/A','N/A')], string="Luces de freno")
    luces_retroceso = fields.Selection(selection=[('B','B'),('R','R'),('N/A','N/A')], string="Luces de retroceso")
    baliza = fields.Selection(selection=[('B','B'),('R','R'),('N/A','N/A')], string="Baliza")
    rompe_nieblas = fields.Selection(selection=[('B','B'),('R','R'),('N/A','N/A')], string="Rompe Nieblas")
    limpia_parabrisas = fields.Selection(selection=[('B','B'),('R','R'),('N/A','N/A')], string="Limpia Parabrisas")
    bocina = fields.Selection(selection=[('B','B'),('R','R'),('N/A','N/A')], string="Bocina")
    espejos = fields.Selection(selection=[('B','B'),('R','R'),('N/A','N/A')], string="Espejos")
    asientos = fields.Selection(selection=[('B','B'),('R','R'),('N/A','N/A')], string="Asientos")
    chapero_pintura = fields.Selection(selection=[('B','B'),('R','R'),('N/A','N/A')], string="Chaperio y Pintura")

    # dispositovs seguridad
    cinternos_seguridad = fields.Selection(selection=[('B','B'),('R','R'),('N/A','N/A')], string="Cinturones de seguridad")
    conos = fields.Selection(selection=[('B','B'),('R','R'),('N/A','N/A')], string="Conos/Triangulos")
    extintor = fields.Selection(selection=[('B','B'),('R','R'),('N/A','N/A')], string="Extintor")
    kit = fields.Selection(selection=[('B','B'),('R','R'),('N/A','N/A')], string="Kit Antiderrame")
    documentacion = fields.Selection(selection=[('B','B'),('R','R'),('N/A','N/A')], string="Documentación de vehiculo")
    bocino_retroceso = fields.Selection(selection=[('B','B'),('R','R'),('N/A','N/A')], string="Bocina de retroceso")
    radio_comunicacion = fields.Selection(selection=[('B','B'),('R','R'),('N/A','N/A')], string="Radio de comunicación")
    tacografo = fields.Selection(selection=[('B','B'),('R','R'),('N/A','N/A')], string="Tacógrafo")
    linterna = fields.Selection(selection=[('B','B'),('R','R'),('N/A','N/A')], string="Linterna")
    pala = fields.Selection(selection=[('B','B'),('R','R'),('N/A','N/A')], string="Pala")
    cable_winche = fields.Selection(selection=[('B','B'),('R','R'),('N/A','N/A')], string="Cable winche")
    cable_corriente = fields.Selection(selection=[('B','B'),('R','R'),('N/A','N/A')], string="Cable pasa corriente")
    barra_antivuelco = fields.Selection(selection=[('B','B'),('R','R'),('N/A','N/A')], string="Barra antivuelco (Interno e Externo)")

    # sistema y elementos basicos
    sistema_encendido = fields.Selection(selection=[('B','B'),('R','R'),('N/A','N/A')], string="Sistema de encendido")
    direccion = fields.Selection(selection=[('B','B'),('R','R'),('N/A','N/A')], string="Direccion")
    nivel_liquidacion = fields.Selection(selection=[('B','B'),('R','R'),('N/A','N/A')], string="Nivel de líquido de freno")
    nivel_aceite = fields.Selection(selection=[('B','B'),('R','R'),('N/A','N/A')], string="Niveles de aceite")
    sistema_enfriamiento = fields.Selection(selection=[('B','B'),('R','R'),('N/A','N/A')], string="Sistema de enfriamiento")
    caja_cambio = fields.Selection(selection=[('B','B'),('R','R'),('N/A','N/A')], string="Caja de cambio y doble tracción")
    mangueras = fields.Selection(selection=[('B','B'),('R','R'),('N/A','N/A')], string="Magueras")
    correas = fields.Selection(selection=[('B','B'),('R','R'),('N/A','N/A')], string="Correas")
    estado_bateria = fields.Selection(selection=[('B','B'),('R','R'),('N/A','N/A')], string="Estado de la batería")
    aire_acondicionado = fields.Selection(selection=[('B','B'),('R','R'),('N/A','N/A')], string="Aire Acondicionado")
    chapas = fields.Selection(selection=[('B','B'),('R','R'),('N/A','N/A')], string="Chapas y Traba puertas")
    estado_freno = fields.Selection(selection=[('B','B'),('R','R'),('N/A','N/A')], string="Estado del freno de mano")
    gato_llave = fields.Selection(selection=[('B','B'),('R','R'),('N/A','N/A')], string="Gato y llave de rueda")

    # distancia a recorrer
    distancia_recorrer = fields.Selection(selection=[('1','(1) <50 Km'),('2','(2) 50 a 100 Km'),('3','(3) 100 a 300 Km'),('4','(4) > 300 Km')],default='0', string="Distancia a recorrer")
    clima = fields.Selection(selection=[('1','(1) Soleado'),('2','(2) Nublado'),('3','(3) Lloviznas'),('4','(4) Lluvia fuerte y/o nieblas')],default='0', string="Clima")
    ruta = fields.Selection(selection=[('1','(1) Pavimento'),('2','(2) Mixta'),('3','(3) Montaña / Cerros')],default='0', string="Ruta")
    conocimiento_ruta = fields.Selection(selection=[('1','(1) Conoce la ruta'),('2','(2) Recorrida al menos 1 vez'),('3','(3) No la conoce')],default='0', string="Conocimiento de ruta")
    comunicacio_disponible = fields.Selection(selection=[('1','(1) Celular / Radio'),('2','(2) Tramos sin comunicacion'),('3','(3) Sin comunicación')],default='0', string="Conocimiento disponible")
    personas_por_vehiculo = fields.Selection(selection=[('1','(1) vehiculo con 2 o + pasajeros'),('2','(2) 1 vehiculo con 1 persona')],default='0', string="Personas por vehiculo")
    horas_viaje = fields.Selection(selection=[('1','(1) < 8Hrs - 1'),('2','(2) 8-12 Hrs - 2'),('3','(3) 12 - 16 Hrs - 3'),('4','(4) > 16 Hrs - 4')],default='0', string="Horas de Viaje + Horas de Trabajo")
    total = fields.Integer(string="TOTAL")
    as_resultado = fields.Char('Autoriza:')

    
    state = fields.Selection(selection=[('Borrador','Borrador'),('Autorizado','Autorizado'),('Cierre','Cierre')],default='Borrador', string="Estado")
    gestion_viaje_lines = fields.One2many('as.gestion.viaje.lines', 'as_gestion_viaje', string='Cost Lines')

    @api.onchange('distancia_recorrer','clima','ruta','conocimiento_ruta','comunicacio_disponible','personas_por_vehiculo','horas_viaje')
    def onchange_total_viaje(self):
        aux = 0
        p = 0
        self.total = int(self.distancia_recorrer) + int(self.clima)+ int(self.ruta) + int(self.conocimiento_ruta) + int(self.comunicacio_disponible) + int(self.personas_por_vehiculo) + int(self.horas_viaje)
        if self.total > 0:
            self.as_resultado = ' Autoriza Supervisión SSMA'
        if self.total >= 16 and self.total <= 21:
            self.as_resultado = 'Autoriza Jefatura SSMA'
        if self.total > 21:
            self.as_resultado = ' Autoriza Gerencia'
    
    @api.onchange('conductor_h')
    def onchange_data(self):
        conductor = self.conductor_h.as_vehiculo
        empleado = self.conductor_h
        # if conductor.id == False:
        #     raise UserError(_("El conductor ingresado no posee un vehiculo asignado."))
        if conductor:
            self.color = conductor.color
        if conductor:
            self.nro_placa = conductor.license_plate
            if conductor.model_id.name:
                self.marca = conductor.model_id.name
            if conductor.model_id.vehicle_type == 'car':
                self.tipo_vehiculo = 'Automovil'
            if conductor.model_id.vehicle_type == 'bike':
                self.tipo_vehiculo = 'Bicicleta'
        if empleado:
            self.nro_licencia = empleado.as_numero_licencia
            self.categoria = empleado.as_categoria
            self.venc_lc = empleado.as_vencimiento
            self.venc_md = empleado.as_vencimiento_md
    
    @api.onchange('as_inspector')
    def onchange_inspector(self):

        if self.as_inspector.contract_id:
            self.as_cargo = self.as_inspector.contract_id.job_id.name

    @api.onchange('as_vehiculos')
    def onchange_as_vehiculosr(self):

        if self.as_vehiculos.color:
            self.color = self.as_vehiculos.color

        if self.as_vehiculos.license_plate:
            self.nro_placa = self.as_vehiculos.license_plate

    def button_change_state_viajes(self):
        for viaje in self:
            viaje.as_state_viaje = 'to_approval'
            monto = viaje.total
            usuario = viaje.env.user.id
            rango_approval = self.env['as.level.approval'].sudo().search([('as_type','=','viajes'),('as_amount_min','<=',monto),('as_amount_max','>=',monto)],order=" id desc",limit=1)
            if rango_approval:
                partners = []
                for users in rango_approval.as_users_ids:
                    partners.append(users.partner_id.id)
        self.as_send_email_gestion_viaje()
            
    def action_ruta(self):
        return self.env.ref('as_spectrocom_project.as_reporte_hoja_ruta').report_action(self)
    
    def extraer_proyecto(self):
        proyecto = self.env['project.task'].sudo().search([('id','=',self.as_project_task_id.id)])
        if proyecto:
            proy=proyecto.as_codigo
            return proy
        
    def _lineas_viajeros(self):
        listaventas=[]
        lin=''
        for linea in self.as_project_task_id.as_viajeros:
            lin=linea.name
            json={
                'empleados':lin
            }
            listaventas.append(json)
        return listaventas
    
    def extraer_cliente(self):
        cliente = self.env['project.task'].sudo().search([('id','=',self.as_project_task_id.id)])
        if cliente:
            client=cliente.partner_id.name
            return client
        
    def as_send_email_gestion_viaje(self):
        self.ensure_one()
        template_id = self._find_mail_template_send_gestion_viaje()
        lang = self.env.context.get('lang')
        template = self.env['mail.template'].browse(template_id)
        attachment = self.env['ir.attachment'].search([('res_id','=',self.id),('res_model','=','as.gestion.viaje')])
        if template.lang:
            lang = template._render_lang(self.ids)[self.id]
        ctx = {
            'default_model': 'as.gestion.viaje',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'custom_layout': "mail.mail_notification_paynow",
            'force_email': True,
            'default_attachment_ids': attachment.ids,
        }
        wiz =  {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }
        wiz = Form(self.env['mail.compose.message'].with_context(ctx)).save()
        wiz.action_send_mail()
        self.message_post(body = "<b style='color:green;'>Enviado correo</b>")


    def _find_mail_template_send_gestion_viaje(self, force_confirmation_template=False):
        template_id = self.env['ir.model.data'].xmlid_to_res_id('as_spectrocom_project.as_template_pick_email_gestion_viajes', raise_if_not_found=False)
        return template_id
    
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

class Gestion_Viajelines(models.Model):
    _name = 'as.gestion.viaje.lines'
    _description = "Plantilla de costos de importacion productos tipo gastos de envio"

    name = fields.Char('Estado general')
    b_estado_general = fields.Boolean(string='B', default=False)
    r_estado_general = fields.Boolean(string='R', default=False)
    na_estado_general = fields.Boolean(string='N/A', default=False)

    dispositivos_seguridad = fields.Char('Dispositivos seguridad')
    b_dispositivos_seguridad = fields.Boolean(string='B', default=False)
    r_dispositivos_seguridad = fields.Boolean(string='R', default=False)
    na_dispositivos_seguridad = fields.Boolean(string='N/A', default=False)

    sistemas_elementes_basicos = fields.Boolean(string='Sistemas y elementos basicos', default=False)
    b_sistemas_elementes_basicos = fields.Boolean(string='B', default=False)
    r_sistemas_elementes_basicos = fields.Boolean(string='R', default=False)
    na_sistemas_elementes_basicos = fields.Boolean(string='N/A', default=False)

    as_gestion_viaje = fields.Many2one('as.gestion.viaje', 'Relacion gestion viaje',required=True, ondelete='cascade')