# -*- coding: utf-8 -*-
# Copyright 2020-TODAY Miguel Pardo <ing.miguel.pardo@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import datetime
import base64
import os
import zipfile
from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT


class NoticeLetterWizard(models.TransientModel):
    _name = 'hr.contract.notice.letter.wizard'
    _description = 'Notice Letter Wizard -> Report'

    generate_individual_report = fields.Boolean(string="Generate Individual Report")
    send_by_mail = fields.Boolean(string="Send by e-mail")
    template_id = fields.Many2one('mail.template', 'Use template', index=True,
                                  domain="[('model', '=', 'hr.contract')]")
    report_id = fields.Many2one('ir.actions.report', 'Include report', index=True,
                                domain="[('model', '=', 'hr.contract')]")

    file = fields.Binary("Attachment")
    file_name = fields.Char("File Name")
    download = fields.Boolean("Download", default=False)

    def confirm(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_start': self.generate_individual_report,
                'date_end': self.send_by_mail,
            },
        }

        # use `module_name.report_id` as reference.
        # `report_action()` will call `_get_report_values()` and pass `data` automatically.

        # getting working module where your current python file (model.py) exists
        path = os.path.dirname(os.path.realpath(__file__))
        print(path)
        # creating dynamic path to create zip file
        file_name = "Contract"
        file_name_zip = file_name + ".rar"
        print(file_name_zip)

        if os.path.isfile(str(path + "/" + file_name_zip)):
            os.remove(str(path + "/" + file_name_zip))

        zipfilepath = os.path.join(path, file_name_zip)
        # creating zip file in above mentioned path
        zip_archive = zipfile.ZipFile(zipfilepath, "x")

        for contract in self._context.get('active_ids'):
            obj_contract = self.env['hr.contract'].search([('id', '=', contract)])
            doc_contract = obj_contract.action_report_mass(self.report_id.id)
            object_name = str(str(path + "/" + doc_contract['attname']))
            if os.path.isfile(object_name):
                os.remove(object_name)
            object_handle = open(object_name, "wb")
            # writing binary data into file handle
            object_handle.write(base64.b64decode(doc_contract['b64_pdf']))
            object_handle.close()
            zip_archive.write(object_name)
            if os.path.isfile(object_name):
                os.remove(object_name)

        zip_archive.close()
        encode_string = None
        with open(str(zipfilepath), "rb") as f:
            bytes = f.read()
            encode_string = base64.b64encode(bytes)

        att_id = self.env['ir.attachment'].create({
            'name': 'Contract.rar',
            'type': 'binary',
            'datas': encode_string,
            'store_fname': 'payslip.rar',
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/x-rar-compressed'
        })
        self.file = att_id.datas
        self.file_name = att_id.name
        self.download = True
        return {
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.contract.notice.letter.wizard',
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def action_send_email_mass(self):
        for contract in self._context.get('active_ids'):
            obj_contract = self.env['hr.contract'].search([('id', '=', contract)])
            obj_contract.action_send_email_mass(self.template_id.id, self.report_id.id)


class NoticeLetterReport(models.AbstractModel):
    """Abstract Model for report template.

    for `_name` model, please use `report.` as prefix then add `module_name.report_name`.
    """

    _name = 'report.hr_contract_completion.report_hr_contract_notice_letter'

    @api.model
    def _get_report_values(self, docids, data=None):
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        date_start_obj = datetime.strptime(date_start, DATE_FORMAT)
        date_end_obj = datetime.strptime(date_end, DATE_FORMAT)
        date_diff = (date_end_obj - date_start_obj).days + 1
        docs = []
        employees = self.env['hr.employee'].search([], order='name asc')
        for employee in employees:
            presence_count = self.env['hr.attendance'].search_count([
                ('employee_id', '=', employee.id),
                ('check_in', '>=', date_start_obj.strftime(DATETIME_FORMAT)),
                ('check_out', '<=', date_end_obj.strftime(DATETIME_FORMAT)),
            ])

            absence_count = date_diff - presence_count

            docs.append({
                'employee': employee.name,
                'presence': presence_count,
                'absence': absence_count,
            })

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_start': date_start,
            'date_end': date_end,
            'docs': docs,
        }
