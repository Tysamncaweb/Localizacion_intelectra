from odoo import models, api, _
from odoo.exceptions import UserError, Warning
from datetime import datetime, date, timedelta

class ReportAccountPayment(models.AbstractModel):
    _name = 'report.int_hr_recibo_nomina.template_recibo_nomina'



    @api.model
    def get_report_values(self, docids, data=None):
        if not docids:
            raise UserError(_("You need select a data to print."))
        data = {'form': self.env['hr.payslip'].browse(docids)}
        res = dict()
        docs = []
        docs2 = []
        docs3 =[]
        var2 = 0
        payslip = self.env['hr.payslip'].search([('id', '=', docids)])
        for slip in payslip:
            name = slip.employee_id.display_name
            fecha_ing = slip.employee_id.fecha_inicio
            fecha_ingreso = fecha_ing[8:10] + "/" + fecha_ing[5:7] + "/" + fecha_ing[0:4]
            empleador = slip.employee_id.coach_id.display_name
            cedula_res= slip.employee_id.coach_id.identification_id_2
            cedula = slip.employee_id.identification_id_2
            rif = slip.employee_id.rif
            cargo = slip.employee_id.job_id.display_name
            date_desde = slip.date_from
            date_from = date_desde[8:10] + "/" + date_desde[5:7] + "/" + date_desde[0:4]
            date_hasta = slip.date_to
            date_to = date_hasta[8:10] + "/" + date_hasta[5:7] + "/" + date_hasta[0:4]
            fecha_actual0 = str(date.today())
            fecha_genera = fecha_actual0[8:10] + "/" + fecha_actual0[5:7] + "/" + fecha_actual0[0:4]
            cont = 0
            total_monto = 0
            cont2 = 0
            for a in slip.line_ids:
                if a.category_id.code == 'ALW':
                    cont += 1
                    cont2 += 1
                    if a.amount_python_compute:
                        if (a.amount_python_compute.find("worked_days.WORK100.number_of_days") != -1):
                            cant_sueldo = int(slip.worked_days_line_ids[0].number_of_days)
                            n_dias = slip.worked_days_line_ids[0].number_of_days
                            if n_dias > 30:
                                n_dias = 30
                            varsal = a.total
                            unidad = a.total/n_dias

                            total_asg_conv = '{0:,.2f}'.format(a.total).replace(',', 'X').replace('.', ',').replace('X',
                                                                                           '.')
                            if unidad != 0:
                                unidad_conv = '{0:,.2f}'.format(unidad).replace(',', 'X').replace('.', ',').replace('X', '.')
                            else:
                                unidad_conv = ' '
                            docs2.append({
                                'descripcion': a.name,
                                'total_alw': total_asg_conv,
                                'total_ded': ' ',
                                'cant_sueldo': cant_sueldo,
                                'unidad': unidad_conv,
                            })
                elif a.category_id.code == 'DED':
                    cont += 1
                    total_ded_conv = '{0:,.2f}'.format(a.total).replace(',', 'X').replace('.', ',').replace('X', '.')
                    docs3.append({
                        'descripcion': a.name,
                        'total_alw': ' ',
                        'total_ded': total_ded_conv,
                        'cant_sueldo': cant_sueldo,
                        'unidad': unidad_conv,
                    })

                if a.category_id.code == 'NET':
                    totalD_net = a.total
                if a.category_id.code == 'GROSS':
                    totalD_ded = a.total
                if a.category_id.code == 'BASIC':
                    totalD_asig = a.total
            if not slip.struct_id:
                totalD_net = 0


            asig_conv = '{0:,.2f}'.format(totalD_asig).replace(',', 'X').replace('.', ',').replace('X', '.')
            ded_conv = '{0:,.2f}'.format(totalD_ded).replace(',', 'X').replace('.', ',').replace('X', '.')
            net_conv = '{0:,.2f}'.format(totalD_net).replace(',', 'X').replace('.', ',').replace('X', '.')
            docs.append({
                'name': name,
                'fecha_ingreso': fecha_ingreso,
                'date_from': date_from,
                'date_to': date_to,
                'rif': rif,
                'cedula': cedula,
                'cargo': cargo,
                'monto': 'xxxx',
                'n_dias': 'xxx',
                'var1': cont -1,
                'var2': var2,
                'salario_diario':'xxxx',
                'fecha_genera': fecha_genera,
                'empleador': empleador,
                'cedula_res': cedula_res,

            })
            var2 = var2 + cont2
            sal_sem = (unidad * 7)
            sal_semanal = '{0:,.2f}'.format(sal_sem).replace(',', 'X').replace('.', ',').replace('X', '.')
        return {
            'data': data['form'],
            'model': self.env['report.int_hr_recibo_nomina.template_recibo_nomina'],
            'lines': res,  # self.get_lines(data.get('form')),
            # date.partner_id
            'docs': docs,
            'asig_total': asig_conv,
            'ded_total': ded_conv,
            'net_total': net_conv,
            'docs2': docs2,
            'docs3': docs3,
            'sal_diario': unidad_conv,
            'sal_semanal': sal_semanal,
        }
