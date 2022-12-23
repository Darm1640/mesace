# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import base64

class SaleOrder(models.Model):
    _inherit = "sale.order"

    as_custodio_id = fields.Many2one('hr.employee', string="Técnico responsable")
    as_permiso_cancelar = fields.Boolean(string='Cancelar venta', default=False)
    
    def _action_confirm(self):
        res = super(SaleOrder, self)._action_confirm()
        for tarea in self.tasks_ids:
            tarea.as_analytic_account_id = self.analytic_account_id
            if self.analytic_account_id:
                tarea.name = str(tarea.name)+': '+str(self.analytic_account_id.name)+': '+str(self.as_alias_lugar)+': '+str(self.as_referencia)+': '+str(tarea.as_ot)
            for instructiva_trabajo in self.as_instructive_lines:
                if instructiva_trabajo.as_fecha_planificada == False:
                    raise UserError('No puede confirmarse la venta, verifique que la instructiva de trabajo contenga una fecha planificada')
                else:
                    tarea.date_deadline = instructiva_trabajo.as_fecha_planificada
                    tarea.as_presupuesto = instructiva_trabajo.as_presupuesto_planificado
                    if instructiva_trabajo.as_note!=False:
                        tarea.description = instructiva_trabajo.as_note.replace('\n', '<br/>')
                    else:
                        tarea.description = instructiva_trabajo.as_note
                    if instructiva_trabajo.as_tipo_adjunto != False:
                        modelo = 'project.task'
                        self.env['ir.attachment'].create({
                            'name': 'Documento adjunto' and _("%s.pdf") % 'Documento adjunto',
                            'type': 'binary',
                            'datas': (instructiva_trabajo.as_tipo_adjunto),
                            'res_model': modelo,
                            'res_id': tarea.id,
                            'mimetype': 'application/pdf',
                        })
        #CASO 47: AL PRESIONAR BOTON CONFIRMAR (VENTAS)        
        #el numero de la plantilla es el ID de la plantilla que corresponde
        valores_email_cuarentasiete = self.env['mail.template'].search([('id','=',165)])    
        if valores_email_cuarentasiete:
            nombre_modelo_cuarentasiete = valores_email_cuarentasiete.model_id.model
            #envio de email sin adjuntos
            self.env['mail.template'].as_send_email_sin_adjuntos(self, valores_email_cuarentasiete.id, nombre_modelo_cuarentasiete)
            if valores_email_cuarentasiete.as_mobile:
                number_cuarsiete = valores_email_cuarentasiete.as_mobile
                if valores_email_cuarentasiete.as_desde and valores_email_cuarentasiete.as_asunto:
                    if valores_email_cuarentasiete.as_desde == '${object.env.user.partner_id.email}':
                        remitente_cuarsiete = str(self.env.user.partner_id.email)
                    if valores_email_cuarentasiete.as_desde == '${object.as_project_task_id.user_id.login}':
                        remitente_cuarsiete = str(self.as_project_task_id.user_id.login)
                    if valores_email_cuarentasiete.as_desde != '${object.env.user.partner_id.email}' and valores_email_cuarentasiete.as_desde != '${object.as_project_task_id.user_id.login}':
                        remitente_cuarsiete = str(valores_email_cuarentasiete.as_desde)
                        
                    mensajito = str('DE: ')+ remitente_cuarsiete +': '+ valores_email_cuarentasiete.as_asunto +': '+ valores_email_cuarentasiete.as_mensaje_whatsapp_email + str(self.name) 
                    
                    self.env['as.whatsapp'].sudo().as_send_whatsapp(number_cuarsiete,mensajito)
                    self.message_post(body = "<b style='color:blue;'>Mensaje enviado por WhatsApp 'Caso 47'</b>")
                
                
        #CASO 48: AL PRESIONAR BOTON CONFIRMAR (VENTAS)    
        #en caso de que alguno de sus productos sea activo fijo    
        #el numero de la plantilla es el ID de la plantilla que corresponde
        lineas_venta = self.env['sale.order.line'].search([('order_id','=',self.id)])
        if lineas_venta:
            for o in lineas_venta:
                lineas_producto = self.env['product.product'].search([('id','=',o.product_id.id)])
                if lineas_producto:
                    prod_category = self.env['account.asset.category'].search([('id','=',lineas_producto.asset_category_id.id)])
                    if prod_category:
                        cuarto = self.env['mail.template'].search([('id','=',142)])
                        if cuarto:
                            nombre_modelo_cuarentaocho = cuarto.model_id.model
                            #envio de email con adjuntos
                            self.env['mail.template'].as_send_email_sin_adjuntos(self, cuarto.id, nombre_modelo_cuarentaocho)
                            if cuarto.as_mobile:
                                number_cuarsiete = cuarto.as_mobile
                                if cuarto.as_desde and cuarto.as_asunto:
                                    if cuarto.as_desde == '${object.env.user.partner_id.email}':
                                        remitente_cuarsiete = str(self.env.user.partner_id.email)
                                    if cuarto.as_desde == '${object.as_project_task_id.user_id.login}':
                                        remitente_cuarsiete = str(self.as_project_task_id.user_id.login)
                                    if cuarto.as_desde != '${object.env.user.partner_id.email}' and cuarto.as_desde != '${object.as_project_task_id.user_id.login}':
                                        remitente_cuarsiete = str(cuarto.as_desde)
                                        
                                    mensajito = str('DE: ')+ remitente_cuarsiete +': '+ cuarto.as_asunto +': '+ cuarto.as_mensaje_whatsapp_email + str(self.name) 
                                    
                                    self.env['as.whatsapp'].sudo().as_send_whatsapp(number_cuarsiete,mensajito)
                                    self.message_post(body = "<b style='color:blue;'>Mensaje enviado por WhatsApp 'Caso 48'</b>")
                                
                                
        
        #CASO 49: AL PRESIONAR BOTON CONFIRMAR (VENTAS)    
        #en caso de que alguno de sus productos sea venta normal    
        #el numero de la plantilla es el ID de la plantilla que corresponde
        valores_email_cuatronueve = self.env['mail.template'].search([('id','=',143)])    
        if valores_email_cuatronueve:
            nombre_modelo_cuarentanueve = valores_email_cuatronueve.model_id.model
            #envio de email con adjuntos
            self.env['mail.template'].as_send_email_sin_adjuntos(self, valores_email_cuatronueve.id, nombre_modelo_cuarentanueve)
            if valores_email_cuatronueve.as_mobile:
                number_cuarnueve = valores_email_cuatronueve.as_mobile
                if valores_email_cuatronueve.as_desde and valores_email_cuatronueve.as_asunto:
                    if valores_email_cuatronueve.as_desde == '${object.env.user.partner_id.email}':
                        remitente_cuarsiete = str(self.env.user.partner_id.email)
                    if valores_email_cuatronueve.as_desde == '${object.as_project_task_id.user_id.login}':
                        remitente_cuarsiete = str(self.as_project_task_id.user_id.login)
                    if valores_email_cuatronueve.as_desde != '${object.env.user.partner_id.email}' and valores_email_cuatronueve.as_desde != '${object.as_project_task_id.user_id.login}':
                        remitente_cuarsiete = str(valores_email_cuatronueve.as_desde)
                        
                    mensajito = str('DE: ')+ remitente_cuarsiete +': '+ valores_email_cuatronueve.as_asunto +': '+ valores_email_cuatronueve.as_mensaje_whatsapp_email +' '+str(self.name) +' usted tiene tarea asignada.'
                    
                    self.env['as.whatsapp'].sudo().as_send_whatsapp(number_cuarnueve,mensajito)
                    self.message_post(body = "<b style='color:blue;'>Mensaje enviado por WhatsApp 'Caso 49'</b>")
                
        #CASO 50: AL PRESIONAR BOTON CONFIRMAR (VENTAS)    
        #en caso de que alguno de sus productos sea activo fijo    
        #el numero de la plantilla es el ID de la plantilla que corresponde
        lineas_venta_service = self.env['sale.order.line'].search([('order_id','=',self.id)])
        if lineas_venta_service:
            for j in lineas_venta_service:
                lineas_producto = self.env['product.product'].search([('id','=',j.product_id.id)])
                if lineas_producto.type == 'service':
                    quinto = self.env['mail.template'].search([('id','=',145)])
                    if quinto:
                        nombre_modelo_cincuentas = quinto.model_id.model
                        #envio de email con adjuntos
                        self.env['mail.template'].as_send_email_sin_adjuntos(self, quinto.id, nombre_modelo_cincuentas)
                        if quinto.as_mobile:
                            number_cuarnueve = quinto.as_mobile
                            if quinto.as_desde and quinto.as_asunto:
                                if quinto.as_desde == '${object.env.user.partner_id.email}':
                                    remitente_cuarsiete = str(self.env.user.partner_id.email)
                                if quinto.as_desde == '${object.as_project_task_id.user_id.login}':
                                    remitente_cuarsiete = str(self.as_project_task_id.user_id.login)
                                if quinto.as_desde != '${object.env.user.partner_id.email}' and quinto.as_desde != '${object.as_project_task_id.user_id.login}':
                                    remitente_cuarsiete = str(quinto.as_desde)
                                mensajito = str('DE: ')+ remitente_cuarsiete +': '+ quinto.as_asunto +': '+ quinto.as_mensaje_whatsapp_email + str(self.name) 
                                self.env['as.whatsapp'].sudo().as_send_whatsapp(number_cuarnueve,mensajito)
                                self.message_post(body = "<b style='color:blue;'>Mensaje enviado por WhatsApp 'Caso 50'</b>")

        return res

    def _prepare_analytic_account_data(self, prefix=None):
        """
        Prepare method for analytic account data

        :param prefix: The prefix of the to-be-created analytic account name
        :type prefix: string
        :return: dictionary of value for new analytic account creation
        """
        name = self.name
        # if prefix:
        #     name = prefix + ": " + self.name
        return {
            'name': name,
            'code': self.client_order_ref,
            'company_id': self.company_id.id,
            'partner_id': self.partner_id.id
        }

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _timesheet_create_project(self):
        """ Generate project for the given so line, and link it.
            :param project: record of project.project in which the task should be created
            :return task: record of the created task
        """
        self.ensure_one()
        values = self._timesheet_create_project_prepare_values()
        if self.product_id.project_template_id:
            values['name'] = "%s - %s" % (values['name'], self.product_id.project_template_id.name)
            project = self.product_id.project_template_id.copy(values)
            project.tasks.write({
                'sale_line_id': self.id,
                'partner_id': self.order_id.partner_id.id,
                'email_from': self.order_id.partner_id.email,
            })
            # duplicating a project doesn't set the SO on sub-tasks
            project.tasks.filtered(lambda task: task.parent_id != False).write({
                'sale_line_id': self.id,
                'sale_order_id': self.order_id,
            })
        else:
            project = self.env['project.project'].create(values)

        # Avoid new tasks to go to 'Undefined Stage'
        # if not project.type_ids:
        #     project.type_ids = self.env['project.task.type'].create({'name': _('New')})
        states_new = self.env['project.task.type'].search([('as_repartir_nuevo','=',True)],limit=1)
        if states_new:
            project.type_ids = states_new
        else:
            raise UserError("No existe etapa marcada como Nueva")
        states = self.env['project.task.type'].search([('as_repartir','=',True)])
        for etapa in states:
            etapas_def = []
            for item in etapa.project_ids:
                etapas_def.append(item.id)
            etapas_def.append(project.id)
            etapa.project_ids = etapas_def


        # link project as generated by current so line
        self.write({'project_id': project.id})
        return project