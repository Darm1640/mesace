# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval
import logging
_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    """Modelo para almacenar estructuras de asientos contables"""
    _name = 'as.account.structure'
    _description = "Modelo para almacenar estructuras de asientos contables"

    name = fields.Text('Descripción')
    as_code = fields.Text('Código')
    as_journal_id = fields.Many2one('account.journal', 'Diario')
    as_glosa = fields.Text('Glosa')
    as_validado = fields.Boolean('Validado')
    as_structure_lines = fields.One2many('as.account.structure.line', 'as_structure_id',string="Lineas Estructura", ondelete='restrict')

    def as_get_account(self,*objects):
        """Funcion principal que permite invocar a otra que eensamblara las lineas de los asientos"""
        move = self.env['account.move']
        lines = self.as_get_line_accoun(*objects)
        vals = {
            # 'date': fields.Datetime.now(),
            'journal_id': self.as_journal_id.id,
            'move_type' : 'entry',
            'ref': self.as_glosa,
            'line_ids' : lines,

        }
        #crear asientos a partir del JSON ensamblado
        move_id = move.create(vals)
        if self.as_validado:
            move_id.post()
        return move_id
        

    def as_get_line_accoun(self,*objects):
        """funcion de ensambla los asientos a partir de configuracion en las lineas de la estructura"""
        line_ids = []
        for obj in objects:
            modelo = obj
            for line in self.as_structure_lines:
                debit = 0.0
                credit = 0.0
                if line.as_model_id.model == obj._name:
                    debit = 0.0
                    credit = 0.0
                    precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
                    if line.as_debe != '' and line.as_debe != False:
                        try: 
                            int(line.as_debe)
                            debit = round(self.as_get_code(modelo,line,line.as_debe),precision)
                        except Exception:
                            debit = round(self.as_get_code(modelo,line),precision)
                    elif line.as_haber != '' and line.as_haber != False:
                        #toma en cuenta si el debe o haber es numerico y de acuerdo a eso capturar el codigo para retornar calculo mediante la funcion as_get_code
                        try: 
                            int(line.as_haber)
                            credit = round(self.as_get_code(modelo,line,line.as_haber),precision)
                        except Exception:
                            credit = round(self.as_get_code(modelo,line),precision)
                    partner = False
                    if self.as_obtener_cliente(modelo):
                        partner = self.as_obtener_cliente(modelo).id
                    #se asigna el valor que retorna la funcion as_get_code a la linea respectiva si al debe o al haber
                    vals = {
                        'name': line.as_glosa,
                        'account_id': line.as_account.id,
                        'debit': abs(debit),
                        'partner_id': partner,
                        'credit': abs(credit),
                    }
                    line_ids.append((0, 0,vals))
        return line_ids

    def as_get_code(self,obj,line,code=False):
        """funcion de retorna el calculo de acuerdo a la configuracion del debe o el haber"""
        valor = 0.0
        if code:
            line = self.as_structure_lines.filtered(lambda line: line.as_code == code)
        #si es tipo asiento
        if line.as_type == 'Linea_Asiento':
            if obj._fields[line.as_field_id.name].type in ('float','integer'):
                valor = obj._fields[line.as_field_id.name].__get__(obj, type(obj))
            elif obj._fields[line.as_field_id.name].type in ('one2many','many2many'):
                valores = obj._fields[line.as_field_id.name].__get__(obj, type(obj))
                result = 0.0
                if not line.as_detail_id:
                    raise UserError(_("La estructura seleccionada es a muchos debe llenar campo detalle."))
                for val in valores:
                    result +=  val._fields[line.as_detail_id.name].__get__(val, type(val))
                valor = result
        #si es tipo calculado
        if line.as_type == 'calculado':
            localdict = {}
            if not line.as_field_id:
                valores = obj
            else:
                valores = obj._fields[line.as_field_id.name].__get__(obj, type(obj))
            for val in valores:
                if not line.as_detail_id:
                    for k in dict(val._fields):
                        localdict[k]=''
                    localdict['result']= 0.0
                    for key in val._fields.keys():
                        localdict[key]= val._fields[key].__get__(val, type(val))
                    try: 
                        if line.as_debe != '' and line.as_debe != False:
                            safe_eval(line.as_debe, localdict, mode="exec", nocopy=True)
                        elif line.as_haber != '' and line.as_haber != False:
                            safe_eval(line.as_haber, localdict, mode="exec", nocopy=True)
                        valor+= localdict['result']
                    except Exception:
                        raise UserError(_("Formula no es correcta, verifique nombre tecnico de campos."))
                else:
                    valores_detail = valores._fields[line.as_field_id.name].__get__(valores, type(valores))
                    for val in valores_detail:
                        for k in dict(val._fields):
                            localdict[k]=''
                        localdict['result']= 0.0
                        for key in val._fields.keys():
                            localdict[key]= val._fields[key].__get__(val, type(val))
                        try: 
                            if line.as_debe != '' and line.as_debe != False:
                                safe_eval(line.as_debe, localdict, mode="exec", nocopy=True)
                            elif line.as_haber != '' and line.as_haber != False:
                                safe_eval(line.as_haber, localdict, mode="exec", nocopy=True)
                            valor += localdict['result']
                        except Exception:
                            raise UserError(_("Formula no es correcta, verifique nombre tecnico de campos."))
        if type(valor) != type(0.0):
            raise UserError(_("Montos de estructuras no son validos."))
        return valor

    def as_obtener_cliente(self, partner):
        partner_id = False
        datos = ['partner_id','as_partner_id']
        for x in datos:
            if x in partner._fields:
                if x in partner.read()[0]:
                    persona = partner.read()[0][x]
                    if persona:
                        return self.env['res.partner'].browse(persona[0])
        return partner_id

class ProductTemplate(models.Model):
    """Modelo para almacenar estructuras de asientos contables"""
    _name = 'as.account.structure.line'
    _description = "Modelo para almacenar estructuras de asientos contables"

    name = fields.Text('Descripción')
    as_structure_id = fields.Many2one('as.account.structure', 'Estructura')
    as_account= fields.Many2one('account.account', 'Cuenta')
    as_code = fields.Text('Código')
    as_glosa = fields.Text('Glosa')
    as_model_id = fields.Many2one('ir.model', string='Modelo')
    as_field_id = fields.Many2one('ir.model.fields', string='Campo')
    as_model_detail = fields.Char('ir.model', related='as_field_id.relation')
    as_detail_id = fields.Many2one('ir.model.fields', string='Campo Detalle')
    as_debe = fields.Text('Debe')
    as_haber = fields.Text('Haber')
    as_type = fields.Selection([
        ('Linea_Asiento', 'Linea Asiento'),
        ('calculado', 'Calculado'),
    ], string="Tipo",default="Linea_Asiento")