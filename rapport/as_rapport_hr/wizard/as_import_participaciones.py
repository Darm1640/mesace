# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, except_orm, ValidationError
import base64
import datetime
import xlrd
import csv
from xlrd import open_workbook
from datetime import datetime
import pytz
from odoo import models,fields
from datetime import datetime, timedelta
from io import StringIO
import logging
_logger = logging.getLogger(__name__)

class as_importador(models.Model):
    _name = 'as.importador'
    _inherit = ['mail.thread']
    _order = "write_date desc"

    as_xls_file = fields.Binary('Archivo excel', help=u'Seleccione un archivo en excel de compras para importar')
    as_xls_name = fields.Char('Nombre archivo',help=u'Seleccione un archivo en excel de compras para importar')
    as_log_completo = fields.Text(string="Logs")
    as_log_warnings = fields.Text(string="Advertencias")

    def validacion_espacios(self, valor):
        valores = valor.replace(', ',',').split(',')
        array = []
        for d in valores:
            try:
                valor = float(d)
                try:
                    valor = int(valor)
                except:
                    valor = 0
            except:
                valor = 0
            array.append(valor)
        return array

    def validacion_tipo_str(self, name):
        not_caracters = ('`~"[]{}.\'')
        nom = name
        if name:
            for char in name:
                if char in not_caracters:
                    nom = nom.replace(char,'-')
        return str(nom).encode('latin1').decode('latin1')

    def validacion_tipo_dato(self,valor, tipo):
        try:
            resultado = tipo(valor)
        except:
            resultado = 0
        return resultado
    def validacion_tipo_datononey(self,valor, tipo):
        resultado = float(round(valor,2))
        return resultado

    def validacion_tipo_date(self,valor, tipo):
        try:
            if tipo == 'date':
                fecha_inicial = datetime(*xlrd.xldate_as_tuple(valor, 0))
                resultado = str(fecha_inicial.strftime('%Y-%m-%d'))
            else:
                hora_actual = (datetime.now() - timedelta(hours = 4)).strftime('%H:%M:%S')
                fecha_inicial = datetime(*xlrd.xldate_as_tuple(valor, 0))
                resultado = str(fecha_inicial.strftime('%Y-%m-%d'))+' '+str(hora_actual)
        except:
            resultado = 0
        return resultado

    def validacion_flotantes(self, value):
        new_value = ''
        if not value:
            return None
        if value == '0':
            new_value = None
        else:
            new_value = re.sub(r'(([.])\w+)','',value)
        return new_value


    def importar_archivo(self):
        self.as_log_completo = ''
        self.as_log_warnings = ''
        cont = 0
        model = ''
        many2ones=[]
        many2ones_line=[]
        count = 0
        elapsed = 0
        total_elapsed = 0
        counter = 0
        errores = 0
        percentage = 0
        fallidos = ''
        tipo_operacion =''
        if self.as_xls_file:
            errores_importacion = ''
            filecontent = base64.b64decode(self.as_xls_file)
            book = open_workbook(file_contents=filecontent)
            sheet = book.sheet_by_index(0)
            field = []
            fieldss = []
            # Obtener las columnas
            keys = [sheet.cell(0, col_index).value for col_index in range(sheet.ncols)]
            aux = list(set(keys))
            aux2 = []
            if 'id' in aux:
                aux.remove('id')
            model = 'survey.user_input'
            campos_fields = self.env['ir.model.fields'].search([('model','=',model)])
            # campos_secundarios = self.env['ir.model.fields'].search([('model','=',str(model)+'.line'),('name','in',fieldss)])
            if not len(keys):
                raise UserError('No hay titulos de columnas en la primera fila.')
            dict_list = []
            array_list = []
            product_obj = self.env[model]
            campos_product = [key for key in product_obj._fields.keys()]
            campos={k:None for k in fieldss}
            order_create = []
            nro_orders = sheet.nrows
            for row_index in range(1, sheet.nrows):
                fila = {keys[col_index]: sheet.cell(row_index, col_index).value
                    for col_index in range(sheet.ncols)}
                value_templates = {k:None for k in aux2}
                for key in fila:
                    if fila[key] and key != 'name':
                        for f in campos_fields:
                            if f.name == key:
                                if f.ttype == 'many2one':
                                    many2ones.append(key)
                                    id_obj = self.validacion_tipo_dato(fila[key], int)
                                    objeto = self.env[str(f.relation)].sudo().search([('id', '=', id_obj)],limit=1)
                                    value_templates[key] = objeto.id or None
                                elif f.ttype == 'many2many':
                                    objeto = self.env[str(f.relation)].sudo().search([('id', 'in', self.validacion_espacios(str(fila[key])))])
                                    if objeto:
                                        value_templates[key] = [(6,0,[objeto.ids])]
                                    else:
                                        value_templates[key] = []
                                elif f.ttype == 'integer':
                                    value_templates[key] = self.validacion_tipo_dato(fila[key], int)
                                elif f.ttype == 'float':
                                    value_templates[key] = self.validacion_tipo_dato(fila[key], float)
                                elif f.ttype == 'datetime':
                                    value_templates[key] = self.validacion_tipo_date(fila[key], 'datetime')
                                elif f.ttype == 'boolean':
                                    if str(fila[key]).lower() in ['t','true','verdadero',1,'1',True]:
                                        value_templates[key] = True
                                    else:
                                        value_templates[key] = False
                                else:
                                    value_templates[key] = self.validacion_tipo_str(str(fila[key]).strip())
                bandera = True
                for field in many2ones:
                    if value_templates[field] in [None, False, '']:
                        bandera = False
                bandera_line = True
                for field in many2ones_line:
                    if campos[field] in [None, False, '']:
                        bandera_line = False

                if 'partner_id' in fila and (fila['partner_id'] not in [None, False, '']):
                    if bandera != False:
                        data_product = product_obj.with_context(default_active=1).default_get(campos_product)
                        data_product.update(value_templates)
                        errores = 0
                        nuevo_product_product = product_obj.create(data_product)
                        if 'as_total_survery' in data_product:
                            nuevo_product_product.as_get_lines_survey(data_product['as_total_survery'])
                        # nuevo_product_product._compute_amount_total()
    
                        order_create.append(nuevo_product_product.id)
                        self.as_log_completo += "\n CREACION EXITOSA: "+str(nuevo_product_product.display_name)+" TOTAL "+str(nuevo_product_product.as_total_survery)+" Creado a las "+str(nuevo_product_product.create_date)+" en fila "+str(row_index)
                        _logger.info('\nCREACION EXITOSA\n\n %r fila %r\n\n', nuevo_product_product.display_name,row_index+1)
                   
                    else:
                        nuevo_product_product= ()
                        self.as_log_completo += "\n LINEA NO IMPORTADA: en fila "+ str(fila)+str(row_index)
                        fallidos+="|Venta invalida no importada: en fila "+str(row_index)
          
                self.as_log_warnings += "Nro:"+ str(counter)+" Producto:"+ str(row_index)+" Operacion:" +str(tipo_operacion)+" Porcentaje:"+ str(percentage)+" Segundos:"+str(elapsed)+" TOTAL TIEMPO:"+str(round((total_elapsed/60),2))+"\n"
            self.as_log_completo += '\nUn total de lineas creadas de:'+str(cont)
        
