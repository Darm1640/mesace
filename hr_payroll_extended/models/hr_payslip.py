# -*- coding: utf-8 -*-
# Copyright 2020-TODAY Miguel Pardo <ing.miguel.pardo@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


import base64
import os
import threading
import zipfile

from odoo import fields, models, api, _, exceptions
from odoo.exceptions import UserError, ValidationError
import logging
from datetime import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
from zipfile import ZipFile

_logger = logging.getLogger(__name__)


class HrPayslip(models.Model):
    _name = "hr.payslip"
    _inherit = ['hr.payslip', 'mail.thread', 'mail.activity.mixin']

    @api.depends('employee_id.address_home_id.vat')
    def _compute_identification_id(self):
        for rec in self:
            rec.identification_id = rec.employee_id.address_home_id.vat

    state = fields.Selection(
        selection_add=[('to_confirm', 'To Confirm'), ('paid', 'Paid')])
    total_amount = fields.Float(compute="_compute_total_amount", store=True)
    identification_id = fields.Char(
        compute='_compute_identification_id', string='Identification No',
        store=True)
    pay_annual = fields.Boolean(
        'Pay Annual',
        readonly=True,
        states={'draft': [('readonly', False)]})
    pay_biannual = fields.Boolean(
        'Pay Biannual',
        readonly=True,
        states={'draft': [('readonly', False)]})
    pay_contributions = fields.Boolean(
        'Pay contributions',
        readonly=True,
        states={'draft': [('readonly', False)]})
    rule_ids = fields.Many2many('hr.salary.rule', string='Rules')
    total = fields.Float(compute="_compute_total", store=True)
    process_status = fields.Text()
    progress_action = fields.Char()
    payslip_type_id = fields.Many2one('hr.payslip.type', 'Payslip Type')
    description = fields.Text('Description Details')

    @api.depends('line_ids')
    def _compute_total(self):
        for payslip in self:
            total = sum([line.total for line in payslip.line_ids.filtered(
                lambda x: x.salary_rule_id.total_cost)])
            payslip.total = total / 160 if total else 0.0

    @api.onchange('contract_id')
    def _calculate_date(self):
        if self.contract_id.structure_type_id:

            if self.contract_id.structure_type_id.default_schedule_pay == 'monthly':
                date_from = date.today().replace(day=1)
                date_to = date_from + relativedelta(months=+ 1, day=1, days=-1)

                self.date_from = date_from
                self.date_to = date_to

            elif self.contract_id.structure_type_id.default_schedule_pay == 'bi-weekly':

                payslip = self.env['hr.payslip'].search(
                    [('employee_id', '=', self.employee_id.id), ('state', '=', 'done')], order="date_to desc, id desc",
                    limit=1)

                if payslip:
                    date_to_payslip = payslip.date_to

                    if date_to_payslip.day in [30, 31]:
                        date_from = date.today().replace(day=1)
                        date_to = date_from.replace(day=15)

                    if date_to_payslip.day in [15, 16]:
                        date_from = date.today().replace(day=16)
                        date_to = date_from + relativedelta(months=+ 1, day=1, days=-1)

                else:

                    date_from = date.today().replace(day=1)
                    date_to = date_from.replace(day=15)

                self.date_from = date_from
                self.date_to = date_to

    def action_to_confirm(self):
        self.state = 'to_confirm'

    def action_pay(self):
        self.state = 'paid'

    def action_payslip_cancel(self):
        return self.write({'state': 'cancel'})

    '''
    def compute_sheet_all_thread(self):
        self._onchange_employee()
        super(HrPayslip, self).compute_sheet()
        self.compute_sheet_rf()
        res = super(HrPayslip, self).compute_sheet()
        # self.message_post("The Calculate All Process Completed!")
        return res

    def compute_sheet_all_thread_extended(self):
        try:
            with api.Environment.manage():
                new_cr = self.pool.cursor()
                self = self.with_env(self.env(cr=new_cr))
                self.compute_sheet_all_thread()
                new_cr.commit()
                new_cr.close()
            return {'type': 'ir.actions.act_window_close'}
        except Exception as error:
            _logger.info(error)

    def compute_sheet_all(self):
        threaded_calculation = threading.Thread(target=self.with_context(
            progress_action=threading.get_ident()).compute_sheet_all_thread_extended, args=())
        threaded_calculation.start()
        self.message_post(
            subject="Calculate All .",
            body=_(
                "The Calculate All is generating in this moment "
                "please wait Process:- %s Date:- %s" % (
                    threading.get_ident(), fields.Date.today())))
    '''

    #### Test

    # @api.model
    def calcular_diferencias(self):
        pickings = self.env['hr.payslip'].search([('payslip_run_id.id', '=', 8), ('state', '=', 'verify')])
        cont = 1
        for picking in pickings:
            print('CONTABILIZANDO LOTE 7 NOMINAS QUINCENALES THOMAS COLOMBIA')
            print(picking)
            print(cont)
            print('')
            cont += 1
            picking.action_payslip_done()
        return True

    def compute_sheet_all(self):
        self._onchange_employee()
        super(HrPayslip, self).compute_sheet()
        self.compute_sheet_rf()
        res = super(HrPayslip, self).compute_sheet()
        # self.message_post("The Calculate All Process Completed!")
        return res

    def action_payslip_done(self):
        res = super(HrPayslip, self).action_payslip_done()
        for slip in self:
            slip.control_payslip()
            sum_days = 0.0
            if not self.env['hr.leave.allocation'].search([
                ('payslip_id', '=', slip.id)]):
                for work_day in self.env['hr.payslip.worked_days'].search([
                    ('payslip_id', '=', slip.id)]):
                    sum_days += work_day.number_of_days
                if sum_days > 30.0:
                    sum_days = 30.0
                # if slip.contract_id.leave_generate_id and sum_days > 0.0:
                #    leave_generate_rec = slip.contract_id.leave_generate_id
                #    self.env['hr.leave.allocation'].create({
                #        'name': slip.number,
                #        'holiday_type': 'employee',
                #        'holiday_status_id': leave_generate_rec.leave_id.id,
                #        'employee_id': slip.employee_id.id,
                #        'number_of_days': 1.25 / 30 * sum_days,
                #        'notes': 'HR Leave Generate via Payslip',
                #        'payslip_id': slip.id})
                holiday_leave_type = self.env['hr.leave.type'].search([
                    ('autogenerate_from_payslip', '=', True)])
                if holiday_leave_type and sum_days > 0.0:
                    holiday_leave = self.env['hr.leave.allocation'].create({
                        'name': slip.number,
                        'holiday_type': 'employee',
                        'holiday_status_id': holiday_leave_type.id,
                        'employee_id': slip.employee_id.id,
                        'number_of_days': 1.25 / 30 * sum_days,
                        'notes': 'Holiday Leave Generate via Payslip',
                        'payslip_id': slip.id})
                    holiday_leave.action_approve()
            # att_id = slip.create_attachment_payslip()
            # if att_id.url:
            #    slip.attachment_url = att_id.url
        return res

    def control_payslip(self):

        date_from = self.date_from - relativedelta(months=1)
        date_to = self.date_to - relativedelta(months=1) if self.date_to.day == 31 else self.date_to - relativedelta(
            months=1) + relativedelta(days=1)
        if self.payslip_type_id.control_payslip:
            if self.contract_id.structure_type_id.default_schedule_pay == 'monthly':
                payslip = self.env['hr.payslip'].search(
                    [('employee_id', '=', self.employee_id.id), ('state', '=', 'done'), ('date_from', '>=', date_from),
                     ('date_to', '<=', date_to)], order="date_to desc, id desc", limit=1)

                if not len(payslip) == 1:
                    raise exceptions.ValidationError(
                        _(
                            'The payroll cannot be confirmed as there is an unconfirmed payroll from the previous month.'))

            if self.contract_id.structure_type_id.default_schedule_pay == 'bi-weekly':
                payslip = self.env['hr.payslip'].search(
                    [('employee_id', '=', self.employee_id.id), ('state', '=', 'done'), ('date_from', '>=', date_from),
                     ('date_to', '<=', date_to)], order="date_to desc, id desc", limit=2)

                if not len(payslip) == 2:
                    raise exceptions.ValidationError(
                        _('The payroll cannot be confirmed since there is an unconfirmed biweekly payroll.'))

    @api.depends('line_ids')
    def _compute_total_amount(self):
        for payslip in self:
            for line in payslip.line_ids.filtered(lambda x: x.code == 'NET'):
                payslip.total_amount = round(line.total)

    def create_attachment_payslips(self):
        for slip in self:
            if slip.state == 'done':
                att_id = slip.create_attachment_payslip()
                if att_id.url:
                    slip.attachment_url = att_id.url

    def create_attachment_payslip(self):
        report_id = self.env.ref('hr_payroll.action_report_payslip')
        pdf = report_id.render_qweb_pdf(self.ids)
        b64_pdf = base64.b64encode(pdf[0])
        att_name = _("Payslip %s from %s to %s" % (
            self.employee_id.name, self.date_from, self.date_to))

        att_id = self.env['ir.attachment'].create({
            'name': att_name,
            'type': 'binary',
            'datas': b64_pdf,
            'datas_fname': att_name + '.pdf',
            'store_fname': att_name,
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/x-pdf'
        })
        return att_id

    def send_payslip_email(self):
        mail_template_id = self.env.ref(
            'hr_payroll_extended.email_template_payslip_email')
        att_id = self.env['ir.attachment'].search([
            ('res_model', '=', 'hr.payslip'),
            ('res_id', '=', self.id)], limit=1)
        if not att_id:
            att_id = self.create_attachment_payslip()
        values = {
            'attachment_ids': [att_id.id],
        }
        if att_id.url:
            self.attachment_url = att_id.url
        mail_template_id.send_mail(self.id, email_values=values)

        return True

    def action_acumulate(self):
        for rec in self:
            hr_rules_acumulate_ids = self.env['hr.conf.acumulated'].search([
                ('active', '!=', False)])
            employee_acumulate_ids = self.env['hr.employee.acumulate'].search(
                [('pay_slip_id', '=', self.id)])
            if employee_acumulate_ids:
                employee_acumulate_ids.unlink()
            for hr_rules_acumulate_id in hr_rules_acumulate_ids:
                for done_payslip in self.env['hr.payslip'].search(
                        [('id', '=', self.id)]):
                    if self.env['hr.employee.acumulate'].search(
                            [('pay_slip_id', '=', done_payslip.id),
                             ('hr_rules_acumulate_id', '=',
                              hr_rules_acumulate_id.id)]):
                        self.env['hr.employee.acumulate'].search(
                            [('pay_slip_id', '=', done_payslip.id),
                             ('hr_rules_acumulate_id', '=',
                              hr_rules_acumulate_id.id)]).unlink()
                    emp_acumulate = \
                        self.env['hr.employee.acumulate'].create({
                            'name':
                                'Acumulate for ' +
                                done_payslip.employee_id.name,
                            'employee_id': done_payslip.employee_id.id,
                            'pay_slip_id': done_payslip.id,
                            'hr_rules_acumulate_id':
                                hr_rules_acumulate_id.id,
                        })
                    self.env['hr.deduction.accumulate.rf'].search(
                        [('year', '=', str(fields.Date.today().year)),
                         ('employee_id', '=', rec.employee_id.id)]).unlink()
                    rec.employee_id.calculate_accumulate()
                    emp_acumulate.onchange_pay_slip_id()

    def unlink(self):
        if not self.env.user.has_group('hr_payroll_extended.group_payslip_delete'):
            raise UserError(_('You can not delete Payslip!'))
        return super(HrPayslip, self).unlink()

    def action_payslip_review_parameters_thread(self):
        for rec in self:
            rec._onchange_employee()
        self.message_post("The Calculate Parameters Process Completed!")
        return True

    def action_payslip_review_parameters_thread_extended(self):
        try:
            with api.Environment.manage():
                new_cr = self.pool.cursor()
                self = self.with_env(self.env(cr=new_cr))
                self.action_payslip_review_parameters_thread()
                new_cr.commit()
                new_cr.close()
            return {'type': 'ir.actions.act_window_close'}
        except Exception as error:
            _logger.info(error)

    def action_payslip_review_parameters(self):
        threaded_calculation = threading.Thread(target=self.with_context(
            progress_action=threading.get_ident()).action_payslip_review_parameters_thread_extended, args=())
        threaded_calculation.start()
        self.message_post(
            subject="Calculate All",
            body=_(
                "The Calculate Parameters is generating in this moment "
                "please wait Process:- %s Date:- %s" % (
                    threading.get_ident(), fields.Date.today())))

    def action_payslip_caluculate_sheet_thread(self):
        for rec in self:
            rec.compute_sheet()
            print("MAPFFF", rec.name)
        # self.process_status = str(self.process_status + "Nómina Calculada")
        self.message_post("The Calculate payroll Process Completed!")
        return True

    def action_payslip_caluculate_sheet_thread_extended(self):
        try:
            with api.Environment.manage():
                new_cr = self.pool.cursor()
                self = self.with_env(self.env(cr=new_cr))
                self.action_payslip_caluculate_sheet_thread()
                new_cr.commit()
                new_cr.close()
            return {'type': 'ir.actions.act_window_close'}
        except Exception as error:
            _logger.info(error)

    def action_payslip_caluculate_sheet(self):
        threaded_calculation = threading.Thread(target=self.with_context(
            progress_action=threading.get_ident()).action_payslip_caluculate_sheet_thread_extended, args=())
        threaded_calculation.start()
        self.message_post(
            subject="Calculate payroll.",
            body=_(
                "The Calculate payroll is generating in this moment "
                "please wait Process:- %s Date:- %s" % (
                    threading.get_ident(), fields.Date.today())))

    '''
    def action_payslip_calculate_retention_thread(self):
        # super(HrPayslip, self).compute_sheet()
        for rec in self:
            print("MAPFFF", rec.name)
            rec.compute_sheet_rf()
        # self.process_status = str(self.process_status + "Retención Calculada")
        # self.message_post("The Calculate RF Process Completed!")
        return True

    def action_payslip_calculate_retention(self):
        threaded_calculation = threading.Thread(target=self.with_context(
            progress_action=threading.get_ident()).action_payslip_calculate_retention_thread_extended, args=())
        threaded_calculation.start()
        self.message_post(
            subject="Calculate RF.",
            body=_(
                "The Calculate RF is generating in this moment "
                "please wait Process:- %s Date:- %s" % (
                    threading.get_ident(), fields.Date.today())))

    '''

    def action_payslip_calculate_retention_thread_extended(self):
        try:
            with api.Environment.manage():
                new_cr = self.pool.cursor()
                self = self.with_env(self.env(cr=new_cr))
                self.action_payslip_calculate_retention_thread()
                new_cr.commit()
                new_cr.close()
            return {'type': 'ir.actions.act_window_close'}
        except Exception as error:
            _logger.info(error)

    def action_payslip_calculate_retention(self):
        # super(HrPayslip, self).compute_sheet()
        for rec in self:
            print("MAPFFF", rec.name)
            rec.compute_sheet_rf()
        # self.process_status = str(self.process_status + "Retención Calculada")
        # self.message_post("The Calculate RF Process Completed!")
        return True

    def compute_sheet_thread(self):
        thread = threading.Thread(
            target=self.compute_sheet_sub_thread, args=())
        thread.start()

    def compute_sheet_sub_thread(self):
        try:
            with api.Environment.manage():
                new_cr = self.pool.cursor()
                self = self.with_env(self.env(cr=new_cr))
                self.action_payslip_calculate_retention()
                self.action_payslip_caluculate_sheet()
                self.action_payslip_review_parameters()
                new_cr.commit()
                new_cr.close()
            return {'type': 'ir.actions.act_window_close'}
        except Exception as error:
            _logger.info(error)
            self.message_post(
                subject="Compute Sheet process.",
                body=_("The process Compute Sheet is not Completed"))

    def compute_sheet(self):
        print("MAPFFF", self.name)
        res = super(HrPayslip, self).compute_sheet()
        self.message_post(
            subject="Compute Sheet process.",
            body=_("The process Compute Sheet is Completed!"))

        if self.payslip_type_id.sequence_id.use_date_range:
            self.number = self.payslip_type_id.sequence_id.next_by_code(sequence_date=date.today())
        else:
            self.number = self.payslip_type_id.sequence_id.next_by_code(self.payslip_type_id.sequence_id.code)

        return res

    def action_send_email_mass(self, template_id, report_id, ):
        mail_template = self.env['mail.template'].search([('id', '=', template_id)])
        report = self.env['ir.actions.report'].search([('id', '=', report_id)])
        pdf = report.render_qweb_pdf(self.ids)
        b64_pdf = base64.b64encode(pdf[0])
        attname = "Payslip-" + self.employee_id.name + '.pdf'

        att_id = self.env['ir.attachment'].create({
            'name': attname,
            'type': 'binary',
            'datas': b64_pdf,
            'store_fname': attname,
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/x-pdf'
        })
        mail_template.attachment_ids = [att_id.id]
        mail_template.send_mail(self.id, force_send=True)

    def action_report_mass(self, report_id):
        report = self.env['ir.actions.report'].search([('id', '=', report_id)])
        pdf = report.render_qweb_pdf(self.ids)
        b64_pdf = base64.b64encode(pdf[0])
        attname = "Payslip-" + self.employee_id.name + str(self.id) + '.pdf'

        return {'b64_pdf': b64_pdf, 'attname': attname}


class HrPayslipRun(models.Model):
    _name = "hr.payslip.run"
    _inherit = ['hr.payslip.run', 'mail.thread', 'mail.activity.mixin']

    # journal_id = fields.Many2one(
    #    'account.journal', 'Salary Journal',
    #    states={'draft': [('readonly', False)]}, readonly=True,
    #    required=True,
    #    default=lambda self: self.env['account.journal'].search([
    #        ('name', 'like', '%NOMINA%')], limit=1))
    pay_annual = fields.Boolean(
        'Pay Annual',
        states={'draft': [('readonly', False)]}, readonly=True)
    pay_biannual = fields.Boolean(
        'Pay Biannual',
        states={'draft': [('readonly', False)]}, readonly=True)
    rule_ids = fields.Many2many('hr.salary.rule', string='Rules')
    result_process = fields.Text("Result")
    state = fields.Selection(selection_add=[
        ('pending_confirm', 'Pending Confirm'),
        ('confirmed', 'Confirmed'),
        ('acumulate', 'Acumulate'),
        ('cancelled', 'Cancelled')])
    description = fields.Text('Description Details')

    def send_payslip_run_email(self):
        for slip in self.slip_ids:
            slip.send_payslip_email()

    def compute_sheet_thread(self):
        for rec in self:
            for line in rec.slip_ids:
                if line.state == 'draft':
                    line.compute_sheet_thread()

    def compute_sheet(self):
        for rec in self:
            for line in rec.slip_ids:
                if line.state in ('draft', 'verify'):
                    line.compute_sheet()

    def compute_sheet_all(self):
        for rec in self:
            for line in rec.slip_ids:
                if line.state in ('draft', 'verify'):
                    line.compute_sheet_all()

    def action_to_confirm(self):
        for rec in self:
            for line in rec.slip_ids:
                if line.state == 'draft':
                    line.action_to_confirm()
            rec.write({'state': 'pending_confirm'})

    def action_payslip_done_thread(self):
        thread = threading.Thread(target=self.with_context(
            progress_action=threading.get_ident()).compute_action_payslip_done_thread, args=())
        thread.start()
        self.message_post(
            subject="Payslip Done Process...",
            body=_(
                "The Payslip Done process is generating in this moment "
                "please wait Process:- %s Date:- %s" % (
                    threading.get_ident(), fields.Date.today())))
        return {'type': 'ir.actions.act_window_close'}

    def compute_action_payslip_done_thread(self):
        try:
            with api.Environment.manage():
                new_cr = self.pool.cursor()
                self = self.with_env(self.env(cr=new_cr))
                self.action_payslip_done()
                new_cr.commit()
                new_cr.close()
            return {'type': 'ir.actions.act_window_close'}
        except Exception as error:
            _logger.info(error)

    def action_payslip_done(self):
        for rec in self:
            for line in rec.slip_ids:
                if line.state == 'to_confirm':
                    _logger.info("action_payslip_done Line ====%s>>", line)
                    line.action_payslip_done()
                    line.action_acumulate()
            rec.write({'state': 'acumulate'})
            self.message_post("The Payslip process completed!")

    def action_payslip_cancel(self):
        for rec in self:
            for line in rec.slip_ids:
                if line.state != 'done' or line.state != 'paid':
                    line.action_payslip_cancel()
            rec.write({'state': 'cancelled'})

    def action_accumulate_thread(self):
        thread = threading.Thread(target=self.with_context(
            progress_action=threading.get_ident()).compute_action_accumulate_thread, args=())
        thread.start()
        self.message_post(
            subject="Accumulate Process...",
            body=_(
                "The Accumulate process is generating in this moment "
                "please wait Process:- %s Date:- %s" % (
                    threading.get_ident(), fields.Date.today())))
        return {'type': 'ir.actions.act_window_close'}

    def compute_action_accumulate_thread(self):
        try:
            with api.Environment.manage():
                new_cr = self.pool.cursor()
                self = self.with_env(self.env(cr=new_cr))
                self.action_acumulate()
                new_cr.commit()
                new_cr.close()
            return {'type': 'ir.actions.act_window_close'}
        except Exception as error:
            _logger.info(error)

    def action_acumulate(self):
        for rec in self:
            for line in rec.slip_ids:
                if line.state == 'done':
                    _logger.info("action_accumulate Line ====%s>>", line)
                    line.action_acumulate()
            rec.write({'state': 'acumulate'})
            self.message_post("Accumulate Process Completed!")

    def action_payslip_draft(self):
        for rec in self:
            aux = 0
            for line in rec.slip_ids:
                if line.state == 'cancel':
                    line.action_payslip_draft()
            rec.write({'state': 'draft'})

    def action_payslip_review_parameters(self):
        for rec in self:
            aux = 0
            for line in rec.slip_ids:
                if line.state == 'draft':
                    aux += 1
                    print("MAPFFFFFF---->>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",
                          aux, line.employee_id.name)
                    line.action_payslip_review_parameters()

    def action_payslip_calculate_retention(self):
        for rec in self:
            aux = 0
            for line in rec.slip_ids:
                if line.state in ('draft', 'verify'):
                    aux += 1
                    print("MAPFFFFFF---->>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",
                          aux, line.employee_id.name)
                    line.action_payslip_calculate_retention()

    def action_payslip_caluculate_sheet_thread(self):
        for rec in self:
            aux = 0
            for line in rec.slip_ids:
                if line.state == 'draft':
                    aux += 1
                    print("MAPFFFFFF---->>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",
                          aux, line.employee_id.name)
                    line.action_payslip_caluculate_sheet()
            rec.message_post("The Calculate payroll Process Completed!")

    def action_payslip_caluculate_sheet_thread_extended(self):
        try:
            with api.Environment.manage():
                new_cr = self.pool.cursor()
                self = self.with_env(self.env(cr=new_cr))
                self.action_payslip_caluculate_sheet_thread()
                new_cr.commit()
                new_cr.close()
            return {'type': 'ir.actions.act_window_close'}
        except Exception as error:
            _logger.info(error)

    def action_payslip_caluculate_sheet(self):
        threaded_calculation = threading.Thread(target=self.with_context(
            progress_action=threading.get_ident()).action_payslip_caluculate_sheet_thread_extended, args=())
        threaded_calculation.start()
        self.message_post(
            subject="Calculate payroll.",
            body=_(
                "The Calculate payroll is generating in this moment "
                "please wait Process:- %s Date:- %s" % (
                    threading.get_ident(), fields.Date.today())))

    def create_attachment_payslips(self):
        for rec in self:
            for line in rec.slip_ids:
                line.create_attachment_payslips()


class HrPayslipLine(models.Model):
    _inherit = "hr.payslip.line"

    @api.depends('salary_rule_id', 'salary_rule_id.work_days_value', 'slip_id')
    def _compute_days(self):
        days = 0.0
        for rec in self:
            if rec.salary_rule_id and rec.salary_rule_id.work_days_value:
                days = 0.0
                worked_days = {}
                for worked_days in self.env[
                    'hr.payslip.worked_days'].search([
                    ('payslip_id', '=', rec.slip_id.id),
                    ('code', 'in',
                     [code.strip() for code in
                      rec.salary_rule_id.work_days_value.split(
                          ',')])]):
                    days += worked_days.number_of_days
                rec.days = days
            elif rec.salary_rule_id and rec.salary_rule_id.use_percentage_rent:
                rec.days = rec.slip_id.percentage_renting_calculate
            else:
                rec.days = 0

    @api.depends('salary_rule_id', 'salary_rule_id.work_hours_value', 'slip_id')
    def _compute_hours(self):
        hours = 0.0
        for rec in self:
            if rec.salary_rule_id and rec.salary_rule_id.work_hours_value:
                hours = 0.0
                for worked_hours in self.env[
                    'hr.payslip.worked_days'].search([
                    ('payslip_id', '=', rec.slip_id.id),
                    ('code', 'in',
                     [code.strip() for code in
                      rec.salary_rule_id.work_hours_value.split(
                          ',')])]):
                    hours += worked_hours.number_of_hours
                rec.hours = hours
            else:
                rec.hours = 0

    @api.depends('salary_rule_id', 'salary_rule_id.model',
                 'salary_rule_id.asigned_base',
                 'salary_rule_id.field',
                 'salary_rule_id.value',
                 'salary_rule_id.categ',
                 'slip_id', 'category_id', 'category_id.code', 'total')
    def _compute_base(self):
        for rec in self:
            base = 0.0
            if rec.salary_rule_id.asigned_base == 'value' and \
                    rec.salary_rule_id.value:
                base = rec.salary_rule_id.value
                rec.base = base
            elif rec.salary_rule_id.asigned_base == 'model' and \
                    rec.salary_rule_id.model and rec.salary_rule_id.field:
                if rec.salary_rule_id.model.model == 'hr.contract':
                    data = rec.slip_id.contract_id.read(
                        [rec.salary_rule_id.field.name])
                    if data:
                        base = data[0].get(rec.salary_rule_id.field.name)
                        rec.base = base
                    else:
                        rec.base = 0
                else:
                    rec.base = 0
            elif rec.salary_rule_id.asigned_base == 'categ' and \
                    rec.salary_rule_id.categ:
                for line in self.search([
                    ('slip_id', '=', rec.slip_id.id)]):
                    if line.category_id and line.category_id.code:
                        if line.category_id.code in [
                            x.strip() for x in
                            rec.salary_rule_id.categ.split(',')] and \
                                line.total:
                            base += line.total
                rec.base = base
            else:
                rec.base = 0

    days = fields.Float(compute='_compute_days', store=True)
    hours = fields.Float(compute='_compute_hours', store=True)
    base = fields.Float(compute='_compute_base', store=True)
    description = fields.Text('Description Details')


class HrPayslipType(models.Model):
    _name = 'hr.payslip.type'
    _description = 'Payslip Type'

    name = fields.Char('Name')
    control_payslip = fields.Boolean('Control Payslip?')
    sequence_id = fields.Many2one('ir.sequence', 'Sequence')
