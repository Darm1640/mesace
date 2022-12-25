from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    ciudad_requi = fields.Many2one('res.city', 'City')
    unidad_organizativa_requi = fields.Many2one('unidades', 'Organization Unit')
    arl_emp = fields.Many2one('res.partner')
    nivel_riesgo = fields.Selection(
        selection=[('1 RIESGO I', '1 RIESGO I'), ('2 RIESGO II', '2 RIESGO II'), ('3 RIESGO III', '3 RIESGO III'),
                   ('4 RIESGO IV', '4 RIESGO IV'), ('5 RIESGO V', '5 RIESGO V')])


class HrContract(models.Model):
    _inherit = 'hr.contract'

    ciudad_requi = fields.Many2one('res.city', 'City')
    tipo_aprendiz = fields.Selection(
        selection=[('ETAPA LECTIVA', 'ETAPA LECTIVA'), ('ETAPA PRODUCTIVA', 'ETAPA PRODUCTIVA'),
                   ('PRACTICANTE', 'PRACTICANTE UNIVERSITARIO')], string='Apprentice type')
    fecha_fin_etapa_lectiva = fields.Date('Fecha fin etapa lectiva')
    fecha_inicio_etapa_productiva = fields.Date('Fecha inicio etapa productiva')
    fecha_fin_etapa_productiva = fields.Date('Fecha inicio etapa productiva')
