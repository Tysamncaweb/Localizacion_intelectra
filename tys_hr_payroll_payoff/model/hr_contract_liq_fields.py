# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#    Change: jeduardo **  12/05/2016 **  hr_contract **  Modified
#    Comments: Creacion de campos adicionales para el modulo de contratos
#
# ##############################################################################################################################################################################

from odoo import fields, models, api
from odoo import osv
from datetime import datetime
from dateutil import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class hr_contract(models.Model):
    _name = 'hr.contract'
    _inherit = 'hr.contract'

    dias_acum_fideicomiso = fields.Integer('Dias acumulados fideicomiso')
    dias_adic_fideicomiso = fields.Integer('Dias adicionales fideicomiso')
    total_acum_anticipo_ps = fields.Float('Total Anticipos pretacioens sociales')
    total_acum_ps = fields.Float('Total cumulado prestaciones sociales')
    vacaciones_vencidas_check = fields.Boolean('Vacaciones vencidas')
    vacaciones_vencidas_value = fields.Float('Vacaciones vencidas')
    vacaciones_fraccionadas_check = fields.Boolean('Vacaciones fraccionadas')
    literal_a =  fields.Boolean('Literal A')
    literal_b =  fields.Boolean('Literal B')
    literal_c =  fields.Boolean('Literal C')

hr_contract()

class hr_payslip_run(models.Model):
    _name = 'hr.payslip.run'
    _inherit = 'hr.payslip.run'

    @api.multi
    def close_payslip_run(self):
        config_obj = self.env['hr.config.parameter']
        if self._context is None: context = {}
        if not hasattr(self._ids, '__iter__'): ids = [self._ids]
        for pro in self.browse(self._ids):
            if pro.check_special_struct and config_obj._hr_get_parameter('hr.payroll.codigos.nomina.prestaciones',True) in pro.struct_id.code:
                self.actualiza_dias_acum_fi(pro.slip_ids)
        res = super(hr_payslip_run, self).close_payslip_run(self._ids)
        return res

    @api.multi
    def actualiza_dias_acum_fi(self,ids):
        payslip_obj = self.env['hr.payslip']
        contract_obj = self.env['hr.contract']
        payslip_ids = payslip_obj.search([('id', '=', [s.id for s in ids])])
        payslips = payslip_obj.browse(payslip_ids)
        for p in payslips:
            acumulado = p.contract_id.dias_acum_fideicomiso + p.dias_acumulados
            adicionales = p.contract_id.dias_adic_fideicomiso + p.dias_adicionales
            contract_obj.write({
                    'dias_acum_fideicomiso': acumulado,
                    'dias_adic_fideicomiso': adicionales})

    @api.multi
    def close_payslip_run(self):
        res = super(hr_payslip_run, self).close_payslip_run(self)
        payslip_obj = self.env['hr.payslip']
        contract_obj = self.env['hr.contract']
        fi_hist_obj = self.env['hr.historico.fideicomiso']
        config_obj = self.env['hr.config.parameter']
        line_obj = self.env['hr.payslip.line']
        history = None
        contract_values = {}
        tipo_nomina = config_obj._hr_get_parameter('hr.payroll.codigos.nomina.prestaciones', True)
        psr = self.browse(self._ids[0])
        payslip_ids = payslip_obj.search([('payslip_run_id', '=', self._ids[0])])
        payslips = payslip_obj.browse(payslip_ids)
        if psr.check_special_struct and tipo_nomina in psr.struct_id.code:
            for p in payslips:
                contract_id = p.contract_id
                # REGISTRO DEL HISTORICO DE PRESTACIONES SOCIALES
                history = fi_hist_obj.get_last_history_fi(p.employee_id.id, None)
                contract_values.update({'total_acum_ps': history.monto_acumulado,
                                        'total_acum_anticipo_ps': history.total_anticipos,
                                        'dias_acum_fideicomiso': history.dias_acumuluados,
                                        'dias_adic_fideicomiso': history.dias_adicionales})
                contract_obj.write(contract_values)
        else:
            # ANTICIPOS
            for p in payslips:
                # ANTICIPO DE PRESTACIONES SOCIALES
                code_anticipo = config_obj._hr_get_parameter('hr.payroll.anticipo.prestaciones', False)
                line_id = line_obj.search([('slip_id', '=', p.id), ('code', '=', code_anticipo)])
                if line_id:
                    history = fi_hist_obj.get_last_history_fi(p.employee_id.id, None)
                    contract_values.update({'total_acum_ps': history.monto_acumulado,
                                            'total_acum_anticipo_ps': history.total_anticipos,
                                            'dias_acum_fideicomiso': history.dias_acumuluados,
                                            'dias_adic_fideicomiso': history.dias_adicionales})
                    contract_obj.write( contract_values)
        return res

hr_payslip_run()



