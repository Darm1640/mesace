# -*- coding: utf-8 -*-
# Copyright 2020-TODAY Miguel Pardo <ing.miguel.pardo@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import base64
import os
import zipfile

from odoo import fields, models, api
from odoo.exceptions import ValidationError


class HrEmployeeWizard(models.TransientModel):
    _name = 'hr.employee.generate.send.wizard'
    _description = 'Generate & Send reports hr.contract'

    send_by_mail = fields.Boolean(string="Send by e-mail")
    template_id = fields.Many2one('mail.template', 'Use template', index=True,
                                  domain="[('model', '=', 'hr.employee')]")
    report_id = fields.Many2one('ir.actions.report', 'Report', index=True,
                                domain="[('model', '=', 'hr.employee')]")
    file = fields.Binary("Attachment")
    file_name = fields.Char("File Name")
    download = fields.Boolean("Download", default=False)

    def confirm(self):
        # getting working module where your current python file (model.py) exists
        path = os.path.dirname(os.path.realpath(__file__))
        print(path)
        # creating dynamic path to create zip file
        file_name = "Employee"
        file_name_zip = file_name + ".rar"
        print(file_name_zip)

        if os.path.isfile(str(path + "/" + file_name_zip)):
            os.remove(str(path + "/" + file_name_zip))

        zipfilepath = os.path.join(path, file_name_zip)
        # creating zip file in above mentioned path
        zip_archive = zipfile.ZipFile(zipfilepath, "x")

        for employee in self._context.get('active_ids'):
            obj_employee = self.env['hr.employee'].search([('id', '=', employee)])
            doc_employee = obj_employee.action_report_mass(self.report_id.id)
            object_name = str(doc_employee['attname'])
            if os.path.isfile(object_name):
                os.remove(object_name)
            object_handle = open(object_name, "wb")
            # writing binary data into file handle
            object_handle.write(base64.b64decode(doc_employee['b64_pdf']))
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
            'name': 'Employee.rar',
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
            'res_model': 'hr.employee.generate.send.wizard',
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def action_send_email_mass(self):
        for payslip in self._context.get('active_ids'):
            obj_payslip = self.env['hr.payslip'].search([('id', '=', payslip)])
            obj_payslip.action_send_email_mass(self.template_id.id, self.report_id.id)
