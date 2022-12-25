# -*- coding: utf-8 -*-
# Copyright 2020-TODAY Miguel Pardo <ing.miguel.pardo@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, models, fields, tools, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    def _compute_rule_for_pvs(self, localdict):
        """
        :param localdict: dictionary containing the current computation environment
        :return: returns a tuple (amount, qty, rate)
        :rtype: (float, float, float)
        """
        self.ensure_one()
        if self.amount_select != 'fix' and self.amount_select != 'percentage':
            # python code
            try:
                python_code = self.amount_python_compute

                index = python_code.find('get_pvs')
                if index != -1:
                    _index = python_code.find(')', index)

                    if _index != -1:
                        python_code = 'result = employee.' + python_code[index:_index] + ', def_return=False)'

                        safe_eval(python_code or 0.0, localdict, mode='exec', nocopy=True)
                        return localdict.get('result', False)
                    else:
                        return False
                else:
                    return False

            except Exception as e:
                raise UserError(
                    _('Wrong python code defined for salary rule %s (%s).\nError: %s') % (self.name, self.code, e))
        else:
            return False

