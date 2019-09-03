from odoo import models, api, _
from odoo.exceptions import UserError, Warning
from datetime import datetime, date, timedelta

class ReportAccountPayment(models.AbstractModel):
    _name = 'report.int_hr_report_resumen_nomina.template_resumen_nomina'



    @api.model
    def get_report_values(self, docids, data=None):
        if not docids:
            raise UserError(_("You need select a data to print."))
        data = {'form': self.env['hr.payslip.run'].browse(docids)}
        res = dict()
        docs = []
        payslip = self.env['hr.payslip']
        payslip_run = payslip.search([('payslip_run_id', '=', docids)])
        total_monto = 0
        final_total = 0
        if not payslip_run:
            raise UserError(_("Por favor verifique si tiene Nóminas Individuales"))
        for slip in payslip_run:
            for a in slip.line_ids:
                if a.category_id.code == 'NET':
                    totalD_net = a.total
                    net_conv = '{0:,.2f}'.format(totalD_net).replace(',', 'X').replace('.', ',').replace('X', '.')

                    docs.append({
                        'prueba':' ',
                        'iniciales': slip.employee_id.iniciales,
                        'nro_cuenta': slip.employee_id.account_number_2,
                        'total': net_conv,

                    })
                    if totalD_net != 0:
                        total_monto += totalD_net
                        final_total = '{0:,.2f}'.format(total_monto).replace(',', 'X').replace('.', ',').replace('X', '.')
                    else:
                        final_total = 0


        return {
                    'data': data['form'],
                    'model': self.env['report.int_hr_report_resumen_nomina.template_resumen_nomina'],
                    'lines': res,  # self.get_lines(data.get('form')),
                    # date.partner_id
                    'docs': docs,
                    'final_monto': final_total,

                }
