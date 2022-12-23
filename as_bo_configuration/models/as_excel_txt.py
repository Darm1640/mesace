from odoo import api, fields, models, _
from odoo.exceptions import UserError

class as_excel_extended(models.TransientModel):
    """ Se crea el modelo excel.extended con los campos a continuacion, parametros para generar reporte en excel"""
    _name= "excel.extended"
    _description="Parametros para generar reporte en excel"

    as_excel_file = fields.Binary(string='Descargar Reporte Excel', readonly=True)
    as_file_name = fields.Char('Excel File', readonly=True)
    as_header = fields.Char('Cabecera File', readonly=True)

class as_txt_extended(models.TransientModel):
    """ Se crea el modelo txt.extended con los campos a continuacion, parametros para generar archivo txt"""
    _name= "txt.extended"
    _description="Parametros para generar archivo txt"

    as_txt_file = fields.Binary('Descargar TXT',readonly=True)
    as_file_name = fields.Char('Txt File', size=64,readonly=True)