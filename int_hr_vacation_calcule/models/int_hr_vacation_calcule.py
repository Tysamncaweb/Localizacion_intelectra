# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta, date
from odoo import models, api, _, fields
from odoo.exceptions import ValidationError
from odoo.tools.misc import formatLang
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from dateutil.relativedelta import relativedelta


from logging import getLogger


_logger = getLogger(__name__)


class Holidays(models.Model):
    _inherit = "hr.holidays"
    vacation = fields.Boolean('Vacaciones')
    bono_vacacional = fields.Boolean('Anticipo Bono Vacacional')

    @api.onchange('date_to')
    def dias_no_feriados(self):
        number_of_days_temp = self.number_of_days_temp
        number_of_days = self.number_of_days
        if self.vacation == True:
            holydays = 0
            hollydays_str = ''
            hr_payroll_hollydays = self.env['hr.payroll.hollydays']
            fecha_desde = None
            fecha_hasta = None
            if self.date_from and self.date_to:
                fecha_desde = self.date_from[:10]
                fecha_hasta = self.date_to[:10]
            else:
                return

            recursive_days = date_from = datetime.strptime(fecha_desde, DEFAULT_SERVER_DATE_FORMAT)
            date_to = datetime.strptime(fecha_hasta, DEFAULT_SERVER_DATE_FORMAT)
            date_end = date_to + relativedelta(days=+1)
            while recursive_days != date_end:
                if 0 <= recursive_days.weekday() <= 4:
                    hollyday_id = hr_payroll_hollydays.search(
                        [('date_from', '<=', str(recursive_days)[:10]), ('date_to', '>=', str(recursive_days)[:10])])
                    if hollyday_id:
                        for holy in hollyday_id:
                            holydays += 1
                recursive_days += relativedelta(days=+1)

            self.number_of_days_temp = number_of_days_temp - holydays
            self.number_of_days = number_of_days + holydays
class hr_contract(models.Model):
    _inherit = 'hr.contract'
    acumulado =  fields.Integer('Dias acumulados')
    solicitado =  fields.Integer('Dias solicitados')
    dias_totales =  fields.Integer('Dias totales')
    active = fields.Boolean(default=True)

    @api.multi
    def calculo_dias_vacaciones(self):
        acumulado_solicitado = 0
        fecha_actual = str(date.today())
        fecha_ingreso = self.date_start
        años = int(fecha_actual[0:4]) - int(fecha_ingreso[0:4])
        if int(fecha_ingreso[5:7]) > int(fecha_actual[5:7]):
            años = años -1
        elif (int(fecha_ingreso[5:7]) == int(fecha_actual[5:7])) and (int(fecha_ingreso[8:10]) < int(fecha_actual[8:10])):
            años = años -1
        if años > 16 :
            años = 16
        config_param = self.env['hr.config.parameter']
        if años:
            min_days = int(config_param._hr_get_parameter('hr.payroll.vacation.min'))
            max_days = int(config_param._hr_get_parameter('hr.payroll.vacation.max'))

         #Si hay algun cambio en la ley de los dias que corresponden segun el tiempo de servicio para los dias de bono vacacional, se debe colocar Step_days y agregarlo como parametro
            #step_days = config_param._hr_get_parameter('hr.payroll.vacation.step')

            pay_days = min_days + ((años - 1) if años > 0 else 0) #* step_days
            pay_days = pay_days if pay_days < max_days else max_days
            #actualizo el registro de dias de vacaciones por tiempo de servicio
            total_acumulado = 0
            for i in range(años):
                total_acumulado += min_days+i
            self.write({'acumulado': total_acumulado })

            #calculo los dias que a solicitado en su tiempo de servicio
            solicitudes_vacaciones = self.env['hr.holidays'].search([('employee_id', '=', self.employee_id.id),('vacation','=',True)])
            if solicitudes_vacaciones:
                for sol in solicitudes_vacaciones:
                    acumulado_solicitado +=  int(sol.number_of_days_temp)
            self.write({'solicitado': acumulado_solicitado,'dias_totales':total_acumulado-acumulado_solicitado })
        return
