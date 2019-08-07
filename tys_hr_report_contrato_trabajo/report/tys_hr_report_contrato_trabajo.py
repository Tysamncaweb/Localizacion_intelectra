from odoo import models, api, _
from odoo.exceptions import UserError, Warning
from datetime import datetime, date, timedelta

class ReportAccountPayment(models.AbstractModel):
    _name = 'report.tys_hr_report_contrato_trabajo.template_contrato_trabajo'



    @api.model
    def get_report_values(self, docids, data=None):
        if not docids:
            raise UserError(_("You need select a data to print."))
        data = {'form': self.env['hr.contract'].browse(docids)}
        res = dict()
        docs = []
        return {
            'data': data['form'],
            'model': self.env['report.tys_hr_report_contrato_trabajo.template_contrato_trabajo'],
            'lines': res,  # self.get_lines(data.get('form')),
            # date.partner_id
            'docs': docs,

        }
