# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta
from odoo import models, api, fields,_, exceptions
from logging import getLogger

class hr_payslip_run_total(models.Model):
    _inherit ='hr.payslip.run'

    total_asig = fields.Float (string= 'Total de Asignaciones', compute='calculosprocesamiento')
    total_deduc = fields.Float(string='Total de Deducciones', compute='calculosprocesamiento')
    total = fields.Float(string='Total', compute='calculosprocesamiento')


    @api.multi
    def calculosprocesamiento(self):
        sumaasig = sumaded = sumatotal = 0
        busqueda = self.env['hr.salary.rule.category'].search([('id', '!=', 0)])
        if busqueda:
            for a in busqueda:
                if a.code == 'BASIC':
                    tasig = a.id
                if a.code == 'GROSS':
                    tdeduc = a.id
                if a.code == 'NET':
                    ttotal = a.id
        else:
            tasig = tdeduc = ttotal = 0

        busqueda2 = self.env['hr.payslip.line'].search([('id', '!=', 0)])
        for var in self.slip_ids:
            for b in var.line_ids:
                if b.category_id.id == tasig:
                    sumaasig += b.total
                if b.category_id.id == tdeduc:
                    sumaded += b.total
                if b.category_id.id == ttotal:
                    sumatotal += b.total
        self.total_asig = sumaasig
        self.total_deduc = sumaded
        self.total = sumatotal
        return

class hr__days_period(models.Model):
    _inherit = 'hr.payslip'

    @api.multi
    def compute_sheet(self):
        super(hr__days_period, self).compute_sheet()
        worked_days = self.env['hr.payslip.worked_days']

        for a in self:
            payslip_run = worked_days.search([('payslip_id', '=', a.id)])
            check_struct = self[0].payslip_run_id.check_special_struct
            if check_struct == False:
                for var in payslip_run:
                    if var.code == 'WORK100':
                        if var.number_of_days > 8:
                            raise exceptions.except_orm(_('Advertencia!'), (u'El Período seleccionado para la nómina que esta intentando generar es mayor al Período de una Semana.\n \
                                                Por favor recuerde que las Reglas Salariales estan basadas Semanalmente.'))
                        if var.number_of_days > 7:
                            var.write({'number_of_days': '7'})
                        if var.number_of_days == 5:
                          #  if a.date_from[5:7] == '02':
                           #     if (a.date_from[8:10] == '16') and ((a.date_to[8:10]== '28')or (a.date_to[8:10]== '29')):
                            #        var.write({'number_of_days': '15'})
                          var.write({'number_of_days': '7'})
                        if var.number_of_days == 6:
                           var.write({'number_of_days': '7'})
                        if var.number_of_days == 5:
                            var.write({'number_of_days': '7'})
        return

            