# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError
import re
import xlrd
from xlrd import open_workbook
import base64
import logging
_logger = logging.getLogger(__name__)

class as_importador_productos(models.Model):
    _name="as.importador.productos.inv"
    _description="importar productos a partir de un archivo xls"

    # def default_product_template(self):
    #     if self._context.get('active_ids', False) and self.as_comprobante_id:

    def _get_default_productos(self):
        ctx = self._context
        if 'active_id' in ctx:
            product_templ_obj = self.env['product.template']
            product_obj = self.env['product.product']
            product = product_obj.search([('product_tmpl_id','in',ctx['active_id'])])
            # template = product_templ_obj.browse(ctx['active_id'])
            return [6,0,product.ids]
        else:
            return None

    def _get_default_campos(self):
        search_obj = ['state','default_code','barcode','active','name','type','list_price','lst_price','uom_id','uom_po_id','sale_ok','purchase_ok','categ_id','taxes_id','supplier_taxes_id','ew_marca_id']
        campos = self.env['ir.model.fields'].search([('model','=','product.template'),('name','in',search_obj)])
        return campos

    xls_file = fields.Binary('Archivo excel', help=u'Seleccione un archivo en excel de compras para importar')
    xls_name = fields.Char('Nombre archivo',help=u'Seleccione un archivo en excel de compras para importar')
    product_template_ids = fields.Many2many('product.template', 
        string="Productos", default=_get_default_productos)
    as_fields_ids = fields.Many2many('ir.model.fields',
        string='Campos', help=u'Nombre de campos de producto.',
        domain="[('ttype','!=','one2many'),('model','=','product.template')]", default=_get_default_campos)

    log_completo = fields.Text(string="Logs")
    log_warnings = fields.Text(string="Advertencias")


    def exportar_archivo(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'product.template'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        if context.get('xls_export'):
            return self.env.ref('as_bo_stock.as_rentabilidad_compras_productsv').report_action(self, data=datas)

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

    def validacion_tipo_dato(self,valor, tipo):
        try:
            resultado = tipo(valor)
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
        self.log_completo = ''
        self.log_warnings = ''
        if self.xls_file:
            errores_importacion = ''
            # Decodificar el registro binario para que lea xlrd
            filecontent = base64.b64decode(self.xls_file)
            book = open_workbook(file_contents=filecontent)
            sheet = book.sheet_by_index(0)
            # Obtener las columnas
            keys = [sheet.cell(0, col_index).value for col_index in range(sheet.ncols)]
            aux = list(set(keys))
            aux.remove('id')
            campos_fields = self.env['ir.model.fields'].search([('model','=','product.template'),('name','in',keys)])
            if not len(keys):
                raise UserError('No hay titulos de columnas en la primera fila.')
            dict_list = []
            array_list = []
            product_obj = self.env['product.product']
            campos_product = [key for key in product_obj._fields.keys()]
            for row_index in range(1, sheet.nrows):
                fila = {keys[col_index]: sheet.cell(row_index, col_index).value
                    for col_index in range(sheet.ncols)}

                try:
                    product_id = self.validacion_tipo_dato(fila['id'], int)
                    productos = False
                    if product_id:
                        productos = self.env['product.template'].search([('id','=', product_id)])

                    # campos_product_template = {}

                    value_templates = {k:None for k in aux}

                    for key in fila:
                        if fila[key] and key != 'name':
                            for f in campos_fields:
                                if f.name == key:
                                    if f.ttype == 'many2one':
                                        id_obj = self.validacion_tipo_dato(fila[key], int)
                                        objeto = self.env[str(f.relation)].sudo().search([('id', '=', id_obj)])
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
                                    elif f.ttype == 'boolean':
                                        if str(fila[key]).lower() in ['t','true','verdadero',1,'1',True]:
                                            value_templates[key] = True
                                        else:
                                            value_templates[key] = False
                                    else:
                                        value_templates[key] = str(fila[key]).strip()

                    bandera = True

                    if 'name' in fila and (fila['name'] not in [None, False, '']):
                        value_templates['name'] = fila['name'].encode('utf-8')
                    else:
                        errores_importacion += ('Este campo name no puede ser vacio, en la fila: '+ str(row_index) + "\n")
                        bandera = False

                    if not bandera:
                        continue
                    if 'id' in value_templates:
                        value_templates.pop('id')
                    if productos:
                        productos.write(value_templates)
                        self.log_completo += "\n Actualizacion exitosa: "+productos.name+" en fila "+str(row_index)
                        if not value_templates.get('name'):
                            self.log_completo += "\n Observacion: Nombre no actualizado por contener caracter especial: "+productos.name
                            self.log_warnings += "\n Observacion en fila "+str(row_index)+": Nombre no actualizado por contener caracter especial: "+productos.name
                        _logger.info('\nACTUALIZACION EXITOSA\n\n %r              fila %r\n\n', productos.name,row_index)
                    else:
                        data_product = product_obj.with_context(default_active=1).default_get(campos_product)
                        data_product['name'] = fila['name'].encode('utf-8')
                        data_product['name'] = data_product['name'].decode('utf-8').replace(str("'")," ")
                        nuevo_product_product = product_obj.create(data_product)
                        if value_templates.get('name'):
                            value_templates['name'] = value_templates['name'].decode('utf-8').replace(str("'")," ")
                        #nuevo_product_product.product_tmpl_id.update(value_templates)
                        self.log_completo += "\n Creacion exitosa: "+str(nuevo_product_product.name)+" en fila "+str(row_index)
                        _logger.info('\nCREACION EXITOSA\n\n %r fila %r\n\n', nuevo_product_product.name,row_index+1)
                except:
                    self.log_completo += "\n La importacion a fallado y se detuvo en la fila: "+str(row_index)
                    _logger.info('\n\nIMPORTACION FALLIDA!!!\n de la fila %r\n\n', row_index+1)
                    break

            # self.as_mensaje = errores_importacion