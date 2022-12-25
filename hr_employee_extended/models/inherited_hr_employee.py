from odoo import models, fields, exceptions, api
from odoo import tools, _
import base64
import locale, datetime


class TipoCotizante(models.Model):
    _inherit = 'tipo.cotizante'
    _description = 'Type Cotizante'

    has_eps = fields.Boolean()
    eps_rate = fields.Float()
    has_afp = fields.Boolean()
    pension_rate = fields.Float()
    eps_rate = fields.Float()
    has_ccf = fields.Boolean()
    ccf_rate = fields.Float()


class Todoo_subtipo_tipo_cotizante(models.Model):
    _name = 'subtipo.cotizante'
    _rec_name = 'nombre_sub_tipo_cotizante'

    nombre_sub_tipo_cotizante = fields.Char()
    code = fields.Char()


class Employee(models.Model):
    _inherit = "hr.employee"

    current_contract = fields.Many2one("hr.contract", compute="contract_actual", string="Current contract")
    id_current_contract = fields.Integer(compute="id_contract")
    firm = fields.Binary()
    payroll_manager = fields.Many2one("hr.employee", string="Payroll Manager", compute="set_payroll_manager")
    date_now = fields.Text(compute="set_date_now")
    start_date_current_contract = fields.Text(compute="set_date_start")
    is_multi_company = fields.Boolean(string="Is Multi-Company", tracking=True)
    multi_company_ids = fields.Many2many(comodel_name='res.company', string='Multi-Company', tracking=True)

    """Employer substitution"""
    is_employer_substitution = fields.Boolean('Employer Substitution', default=False, tracking=True)

    """Names Employee"""
    name = fields.Char(tracking=True)
    label_name = fields.Char(compute='_compute_label_name')
    third_name = fields.Char('First Surname', default='', tracking=True)
    fourth_name = fields.Char('Second Surname', default='', tracking=True)
    first_name = fields.Char('First Name', default='', tracking=True)
    second_name = fields.Char('Second Name', default='', tracking=True)

    tipo_cotizante_emp = fields.Many2one("tipo.cotizante", string="Tipo Cotizante", tracking=True)
    subtipo_cotizante_emp = fields.Many2one("subtipo.cotizante", string="SubTipo Cotizante", tracking=True)

    @api.depends('name')
    @api.onchange('name')
    def _compute_label_name(self):
        self.label_name = self.name

    @api.onchange('first_name', 'second_name', 'third_name', 'fourth_name')
    def _compute_full_name(self):
        names = (self.first_name, self.second_name, self.third_name, self.fourth_name)
        full_name = ''

        for x in names:
            if x:
                if full_name != '':
                    full_name = full_name + ' ' + x.strip().capitalize()
                else:
                    full_name = x.strip().capitalize()

        self.name = full_name.strip()

    @api.onchange('is_employer_substitution')
    def check_employer_substitution(self):
        if self.check_employer_substitution:
            employer_substitution = self.env['hr.employee.category'].search([('name', '=', 'Employer Substitution')])
            if employer_substitution:
                self.category_ids = (4, employer_substitution.id)
            else:
                employer_substitution = self.env['hr.employee.category'].create({'name': 'Employer Substitution'})
                self.category_ids = (4, employer_substitution.id)
        for rec in self:
            if rec.is_employer_substitution:
                employer_substitution = self.env['hr.employee.category'].search(
                    [('name', '=', _('Employer Substitution'))])
                if employer_substitution:
                    rec.write({
                        'category_ids': [(4, employer_substitution.id)]
                    })
                else:
                    employer_substitution = self.env['hr.employee.category'].create(
                        {'name': _('Employer Substitution')})
                    rec.write({
                        'category_ids': [(4, employer_substitution.id)]
                    })

    def action_report_mass(self, report_id):
        report = self.env['ir.actions.report'].search([('id', '=', report_id)])
        pdf = report.render_qweb_pdf(self.ids)
        b64_pdf = base64.b64encode(pdf[0])
        attname = "Employee-" + self.name + str(self.id) + '.pdf'

        return {'b64_pdf': b64_pdf, 'attname': attname}

    def contract_actual(self):
        """
        Método llamado por la declaración del atributo current_contract como campo calculado, que indexa el contrato actual al campo.
        """
        for employee in self:
            contract = self.env["hr.contract"].search([("employee_id.id", "=", employee.id), ("state", "=", "open")],
                                                      limit=1)
            if len(contract) > 1 or len(contract) == 0:
                employee.current_contract = None
            else:
                employee.current_contract = contract

    def id_contract(self):
        """
        Método llamado por la declaración del atributo id_current_contract como campo calculado, que indexa el id del contrato actual al campo.
        """
        if self.current_contract is not None:
            self.id_current_contract = self.current_contract.id
        else:
            self.id_current_contract = 5

    def set_payroll_manager(self):
        """
        Método llamado por la declaración del atributo payroll_manager como campo calculado, que indexa el empleado que es gerente de nomina.
        """

        payroll_manager = self.env['res.company'].search([('id', '=', self.company_id.id)]).payroll_manager

        if payroll_manager:
            for employee in self:
                employee.payroll_manager = payroll_manager
        else:
            for employee in self:
                employee.payroll_manager = False

    def set_date_now(self):
        """
        Método llamado por la declaración del atributo date_now como campo calculado, que almacena la fecha actual con formato colombiano en el campo.
        """
        # locale.setlocale(locale.LC_ALL, 'es_CO.UTF-8')
        now = datetime.datetime.now()
        for employee in self:
            employee.date_now = now.strftime('%B %d de %Y').capitalize()

    def set_date_start(self):
        """
        Método llamado por la declaración del atributo start_date_current_contract como campo calculado, que almacena la fecha del inicio del contrato con formato colombiano.
        """
        # locale.setlocale(locale.LC_ALL, 'es_CO.UTF-8')
        for employee in self:
            # print(employee.current_contract.date_start)
            now = datetime.datetime.strftime(employee.current_contract.date_start, '%B %d de %Y').capitalize()
            employee.start_date_current_contract = now
