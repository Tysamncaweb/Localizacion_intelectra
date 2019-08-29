# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta, date
from odoo import models, api, _, fields
from odoo.exceptions import ValidationError
from odoo.tools.misc import formatLang
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
import xlwt
import base64
import urllib

from logging import getLogger


_logger = getLogger(__name__)


class Holidays(models.Model):
    _inherit = "hr.holidays"
    vacation = fields.Boolean('Vacaciones')

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