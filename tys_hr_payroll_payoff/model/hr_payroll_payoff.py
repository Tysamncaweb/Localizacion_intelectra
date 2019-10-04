# coding: utf-8
from odoo import fields, models, api, exceptions, _
from odoo import osv
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from dateutil.relativedelta import relativedelta
from odoo.tools import float_compare, float_is_zero
from odoo.exceptions import UserError


class hr_payslip(models.Model):
    _inherit ='hr.payslip'

    ESTADOS = [
        ('draft', 'Borrador'),
        ('verify', 'Calculado'),
        ('confirm', 'Confirmado'),
        ('done', 'Realizado'),
        ('cancel', 'Cancelado'),
    ]
    department_id = fields.Many2one('hr.department', 'Departamento')
    job_id = fields.Many2one('hr.job', 'Cargo')
    contract_id = fields.Many2one('hr.contract', 'Contratos liquidacion')
    tiempo_servicio_dias = fields.Integer('Tiempo de servicio en Dias')
    tiempo_servicio_meses = fields.Integer('Tiempo de servicio en Meses')
    tiempo_servicio_year = fields.Integer('Tiempo de servicio en  Years')
    antiguedad_19061997_dias = fields.Integer('Antiuedad dede 1906199 Dias')
    antiguedad_19061997_meses = fields.Integer('Antiuedad dede 1906199 Meses')
    antiguedad_19061997_year = fields.Integer('Antiuedad dede 1906199 Years')
    month_worked_year_str = fields.Char('Meses trabajados en el año', size=20, help="Tiempo trabajado durante el año.")
    month_worked_year = fields.Integer('Meses trabajados en el año', help="Meses trabajados durante el año.")
    conceptos_salariales = fields.Many2many('hr.salary.rule', 'payslip_liquidacion_rel', 'payslip_id', 'rule_id','Conceptos salariales')
    notes = fields.Text('Observaciones', readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection(ESTADOS, string='state',
        help='* Cuando la liquidacion es creada el estado es \'Borrador\'.\
        \n* Si la liquidacion esta bajo verificacion, El estado es \'En Espera\'. \
        \n* Si la liquidacion es confirmada entonces el estado cambia a \'Hecho\'.\
        \n* Cuando el usuario cancela la liquidacion el estado es \'Cancelado\'.')
    vacation_amount = fields.Float('Bono de Vacaciones', digits=(10, 2))
    dias_habiles = fields.Integer('Nro dias habiles', help=u'este campo trae los días hábiles')
    days_to_pay = fields.Integer('Días a pagar')
    vacation_reserva = fields.Float('Dias/Porcion Reserva')
    salario_integral = fields.Float('Salario integral', digits=(10, 2))
    dias_adicionales = fields.Integer('Dias adicionales')
    tiempo_servicio = fields.Integer("Tiempo de servicio")
    ut = fields.Integer('Unidad Tributaria', help='este campo trae la Unidad Tributaria')
    general_state = fields.Char('Estado General', size=100)
    is_payoff = fields.Boolean('Es liquidacion')
    salario_basico = fields.Float('Salario Basico Mensual', digits=(10, 2))
    salario_basico_diario = fields.Float('Salario Basico diario', digits=(10, 2))
    salario_prom_mensual = fields.Float('Salario promedio mensual', digits=(10, 2))
    salario_prom_diairo = fields.Float('Salario promedio diario', digits=(10, 2))
    alic_bono_vac_liq = fields.Float('Alicuota bono vacacional liquidacion', digits=(10, 2))
    alic_util_liq = fields.Float('Alicuota utilidades liquidacion', digits=(10, 2))
    journal_id = fields.Many2one('account.journal', 'Salary Journal', readonly=True, required=True,
                                 states={'draft': [('readonly', False)]},
                                 default=lambda self: self.env['account.journal'].search([('type', '=', 'general')],
                                                                                         limit=1))
    vacaciones_fracc = fields.Float('Vacaciones Fraccionadas')
    dias_prestaciones_acum = fields.Integer('Dias Acumulados Prestaciones')
    dias_prestaciones_adi = fields.Integer('Dias Adicionales Prestaciones')
    monto_gps = fields.Float('Monto GPS Acumulado', digits=(10,2))
    aporte_dias_adicionales = fields.Float('Aporte acumulado días adicionales', digits=(10,2))
    interes_anual = fields.Float('Interes anual', digits=(10,2))
    anticipo_prestaciones = fields.Float('Anticipo prestaciones', digits=(10,2))
    fecha_anticipo = fields.Date('Fecha del Anticipo')
    literal_c = fields.Float('Literal C')
    structure = fields.Many2one('hr.payroll.structure', 'Estructura', states={'draft': [('readonly', False)]})
    move_id = fields.Many2one('account.move', 'Accounting Entry', readonly=True, copy=False)

    @api.onchange('employee_id')
    def onchange_employee_dos(self):
        if self._context.get('is_payoff'):
            res = {}
            job = False
            employee_obj = self.env['hr.employee']
            contract_obj = self.env['hr.contract']
            if self.employee_id:
                employee_data = employee_obj.browse([self.employee_id.id])
                department_id = employee_data.department_id.id
                job_id = employee_data.job_id.id
                contract_id = contract_obj.search([('employee_id', '=', self.employee_id.id)])
                # contract_id = employee_obj._get_latest_contract([self.employee_id.id])
                if contract_id:
                    contract_data = contract_obj.browse([contract_id.id])
                    date_start = contract_data.date_start
                    date_end = contract_data.date_end
                    wage = contract_data.wage
                    state = contract_data.state

                else:

                    raise exceptions.except_orm(('Advertencia!'),
                                                ('El empleado ', self.employee_id.name, ' no posee contrato!'))
            else:
                return {'value': res}
            self.department_id = department_id
            self.job_id = job_id
            self.date_from = date_start
            self.date_to = date_end
            self.structure = self.env['hr.payroll.structure'].search([('code', '=', 'ESP-05')])

    @api.onchange('date_to')
    def onchange_dateee_end(self):
        if self._context.get('is_payoff'):
            config_obj = self.env['hr.config.parameter']
            tiempo_servicio = {
                'dias': 0,
                'meses': 0,
                'anios': 0,
            }
            months_worked_year = 0
            months_worked_year_int = 0
            ts = 0

            if self.date_from and self.date_to:
                # se le suma un dia a la fecha de finalizacion de la relacion laboral porque se considera que ese dia el empleado trabaja
                fecha_temp = datetime.strptime(self.date_to, DEFAULT_SERVER_DATE_FORMAT)
                fecha_temp = fecha_temp
                date_end = datetime.strftime(fecha_temp, DEFAULT_SERVER_DATE_FORMAT)
                #TODO si se requiere se puede hacer persistir en el contrato la fecha de culminacion. Solo cuando se confirme la liquidacion
                tiempo_servicio = self.get_years_service(self.date_from, date_end)
                ts = tiempo_servicio['anios'] + 1 if tiempo_servicio['meses'] >= 6 else tiempo_servicio['anios']

                if self.employee_id:
                    #employee = self.env['hr.employee'].search(['id', '=', self.employee_id.id])

                    months_worked_year, months_worked_year_int = self.get_year_worked_time(self.date_from, date_end)


                    return {'value': {
                        'tiempo_servicio_dias': tiempo_servicio['dias'],
                        'tiempo_servicio_meses': tiempo_servicio['meses'],
                        'tiempo_servicio_year': tiempo_servicio['anios'],
                        'month_worked_year_str': months_worked_year,
                        'month_worked_year': months_worked_year_int,
                        'tiempo_servicio': ts,
                    }
                    }


    def get_years_service(self, fecha_inicio, fecha_fin=None):
        dias = 0
        meses = 0
        anios = 0
        res = {}
        if fecha_inicio and fecha_fin:
            antiguedad = relativedelta(datetime.strptime(fecha_fin, DEFAULT_SERVER_DATE_FORMAT),
                                                     datetime.strptime(fecha_inicio, DEFAULT_SERVER_DATE_FORMAT))
            res = {
                'dias': antiguedad.days,
                'meses': antiguedad.months,
                'anios': antiguedad.years,
            }
        return res


    def get_year_worked_time(self, date_start, date_end=None):
        year_worked_time = ''
        if not date_end:
            ahora = datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT)
        else:
            ahora = date_end
        date_start_year = "-01-01"
        date_start_year = ahora.split("-")[0] + date_start_year
        if date_start > date_start_year:
            months_worked_year = self.get_years_service(date_start, ahora)
        else:
            months_worked_year = self.get_years_service(date_start_year, ahora)
        months_worked_year_int = months_worked_year['meses']
        months_worked_sumado = int(months_worked_year['dias'])+1

        year_worked_time = str(months_worked_year['meses']) + (' meses' if months_worked_year['meses'] > 1 else ' mes ') \
                           + (' y ' + str(months_worked_sumado) + (
        ' días' if months_worked_sumado > 1 else ' dia') if months_worked_sumado > 0 else '')

        return year_worked_time, months_worked_year_int

    @api.multi
    def hr_verify_sheet(self):
        #self.compute_sheet()
        ctx = self._context.copy() or {}
        is_payoff = self.env.context.get('come_from', False)
        payoff_values = {}
        prestaciones_values = {}
        if is_payoff:
            ctx.update({'slip_id': self.ids[0]})
            self.env.context = ctx
            payoff_values = self.get_payoff_values()
            payoff_values.update({'is_payoff': True})
            prestaciones_values = self.get_history_fideicomiso()
            self.write(payoff_values)
            self.write(prestaciones_values)
            self.compute_sheet_2()

        return self.write({'state': 'verify'})

    @api.multi
    def compute_sheet_2(self):

        slip_line_pool = self.env['hr.payslip.line']
        sequence_obj = self.env['ir.sequence']
        for payslip in self.browse(self._ids):
            struct= self.structure = self.env['hr.payroll.structure'].search([('code', '=', 'ESP-05')])
            number = payslip.number or sequence_obj.next_by_code('salary.slip')
            # delete old payslip lines
            old_slipline_ids = slip_line_pool.search([('slip_id', '=', payslip.id)])
            #            old_slipline_ids
            if old_slipline_ids:
                payslip.line_ids.unlink()
                #old_slipline_ids.unlink()
            if payslip.contract_id:
                # set the list of contract for which the rules have to be applied
                contract_ids = [payslip.contract_id.id]
            else:
                # if we don't give the contract, then the rules to apply should be for all current contracts of the employee
                contract_ids = self.get_contract(payslip.employee_id, payslip.date_from, payslip.date_to
                                                 )

            lines = [(0, 0, line) for line in
                     self._get_payslip_lines(contract_ids, payslip.id)]


            self.write({'line_ids': lines, 'number': number})
        return


    @api.multi
    def hr_action_cancel(self):
        return self.write({'state': 'cancel','is_payoff': True})

    # colocar el estado en "borrador"
    @api.multi
    def hr_action_draft(self):
        return self.write({'state': 'draft'})

    # colocar el estado en "confirmado"
    @api.multi
    def hr_action_confirm(self):
        return self.write({'state': 'confirm'})

    # colocar el estado en "hecho"
    @api.multi
    def hr_action_done(self, context=None):
        sequence_obj = self.env['ir.sequence']
        #number = sequence_obj.next_by_code('salary.slip')
        #struct_new = self.env['hr.contract'].search([('employee_id', '=', self.employee_id)])
        for slip in self:
            # slip.write({'number': number}) #ya venia comentado!!!
            self = self.with_context({'struct_id': slip.struct_id.id, 'payoff': 'payoff',
                                      'payoff_date': datetime.now().strftime('%Y-%m-%d')})
            self.action_payslip_done_new()
            #self.compute_sheet_2()
            if slip.move_id:
                slip.move_id.write(
                    {'name': '%s de %s' % (slip.struct_id.name, slip.employee_id.name)})
            self.employee_id.write({'active': False})
        return self.write({'state': 'done'})

    @api.multi
    def action_payslip_done_new(self):
        precision = self.env['decimal.precision'].precision_get('Payroll')

        for slip in self:
            line_ids = []
            debit_sum = 0.0
            credit_sum = 0.0
            date = slip.date or slip.date_to

            name = _('Payslip of %s') % (slip.employee_id.name)
            move_dict = {
                'narration': name,
                'ref': slip.number,
                'journal_id': slip.journal_id.id,
                'date': date,
            }
            for line in slip.details_by_salary_rule_category:
                amount = slip.credit_note and -line.total or line.total
                if float_is_zero(amount, precision_digits=precision):
                    continue
                debit_account_id = line.salary_rule_id.account_debit.id
                credit_account_id = line.salary_rule_id.account_credit.id

                if debit_account_id:
                    debit_line = (0, 0, {
                        'name': line.name,
                        'partner_id': line._get_partner_id(credit_account=False),
                        'account_id': debit_account_id,
                        'journal_id': slip.journal_id.id,
                        'date': date,
                        'debit': amount > 0.0 and amount or 0.0,
                        'credit': amount < 0.0 and -amount or 0.0,
                        'analytic_account_id': line.salary_rule_id.analytic_account_id.id,
                        'tax_line_id': line.salary_rule_id.account_tax_id.id,
                    })
                    line_ids.append(debit_line)
                    debit_sum += debit_line[2]['debit'] - debit_line[2]['credit']

                if credit_account_id:
                    credit_line = (0, 0, {
                        'name': line.name,
                        'partner_id': line._get_partner_id(credit_account=True),
                        'account_id': credit_account_id,
                        'journal_id': slip.journal_id.id,
                        'date': date,
                        'debit': amount < 0.0 and -amount or 0.0,
                        'credit': amount > 0.0 and amount or 0.0,
                        'analytic_account_id': line.salary_rule_id.analytic_account_id.id,
                        'tax_line_id': line.salary_rule_id.account_tax_id.id,
                    })
                    line_ids.append(credit_line)
                    credit_sum += credit_line[2]['credit'] - credit_line[2]['debit']

            if float_compare(credit_sum, debit_sum, precision_digits=precision) == -1:
                acc_id = self.journal_id.default_credit_account_id.id
                if not acc_id:
                    raise UserError(_('The Expense Journal "%s" has not properly configured the Credit Account!') % (
                        self.journal_id.name))
                adjust_credit = (0, 0, {
                    'name': _('Adjustment Entry'),
                    'partner_id': False,
                    'account_id': acc_id,
                    'journal_id': slip.journal_id.id,
                    'date': date,
                    'debit': 0.0,
                    'credit': debit_sum - credit_sum,
                })
                line_ids.append(adjust_credit)

            elif float_compare(debit_sum, credit_sum, precision_digits=precision) == -1:
                acc_id = slip.journal_id.default_debit_account_id.id
                if not acc_id:
                    raise UserError(_('The Expense Journal "%s" has not properly configured the Debit Account!') % (
                        slip.journal_id.name))
                adjust_debit = (0, 0, {
                    'name': _('Adjustment Entry'),
                    'partner_id': False,
                    'account_id': acc_id,
                    'journal_id': slip.journal_id.id,
                    'date': date,
                    'debit': credit_sum - debit_sum,
                    'credit': 0.0,
                })
                line_ids.append(adjust_debit)
            move_dict['line_ids'] = line_ids
            move = slip.env['account.move'].create(move_dict)
            slip.write({'move_id': move.id, 'date': date})
            move.post()
        return


    @api.model
    def fields_view_get(self, view_id=None, view_type=False, toolbar=False, submenu=False):
        ir_ui_obj = self.env['ir.ui.view']
        context = self._context
        is_payoff = context.get('is_payoff',False)
        if view_type == 'form':
            if is_payoff:
                view_id = ir_ui_obj.search([('name', '=', 'hr.payroll.payoff.form.view')], limit=1).id
            else:
                view_id = ir_ui_obj.search([('name', '=', 'hr.payslip.form')], limit=1).id

        return super(hr_payslip, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)

    @api.model
    def create(self,values, context=None):
        if context is None: context = {}
        res = {}

        if context.get('is_payoff', False):
            values.update({'is_payoff': True})
        res = super(hr_payslip, self).create(values)
        return res

    @api.multi
    def write(self, values):
        # if context is None: context = {}
        # if not hasattr(ids, '__iter__'): ids = [ids]
        # values = {}
        if self.env.context.get('is_payoff', False):
            values.update({'is_payoff': True})
        res = super(hr_payslip, self).write(values)
        return res

    def get_payoff_values(self):
        values = {}
        limite = 2
        dias_b_v = 0
        config_obj = self.env['hr.config.parameter']
        vacaciones_obj = self.env["hr.payroll.dias.vacaciones"]
        dias_str = config_obj._hr_get_parameter( 'hr.dias.x.mes')

        # SALARIO BASE
        sal_mensual = self.employee_id.contract_id.wage

        #SALARIO PROMEDIO
        tipo_pago = self.employee_id.contract_id.schedule_pay
        if tipo_pago == 'monthly':
            limite=1
        elif tipo_pago == 'weekly':
            #TODO obtener el numero de lunes
            limite = self.get_mondays(self.date_to)
        promedio = self.calculo_sueldo_promedio(self.employee_id, self.date_to, 0, 'liquidacion', limite)
        #CALCULO DE ALICUOTAS
        vac_frac = 0
        if self.tiempo_servicio:
            literal_c = self.tiempo_servicio*int(dias_str)
            min_days = int(config_obj._hr_get_parameter('hr.payroll.vacation.min'))
            max_days = int(config_obj._hr_get_parameter('hr.payroll.vacation.max'))
            pay_days = min_days + ((self.tiempo_servicio - 1) if self.tiempo_servicio > 0 else 0)  # * step_days
            pay_days = pay_days if pay_days < max_days else max_days
            if self.tiempo_servicio == 0 and int(self.month_worked_year_str[0:1]) >= 3:  # antiguedad menor a un anio y mayor a 3 meses
                vac_frac = (float(self.month_worked_year_str[0:1]) / float(12)) * float(pay_days)
                asignacion = pay_days
            else:
                asignacion = pay_days
               # vac_frac = asignacion
        else:
            raise exceptions.except_orm((u'No se han calculado los días de bono vacacional, debido a que\n'
                           u' no se ha cargado la lista de días a pagar por años de servicio.\n'
                           u' Por favor consulte con el administrador!'))
        if asignacion:
            dias_bv = asignacion
        if vac_frac and vac_frac > 0:
            self.vacaciones_fracc = vac_frac
        else:
            if self.tiempo_servicio > 0 and int(self.month_worked_year_str[0:1]) > 0:
                vac_frac2 = (float(self.month_worked_year_str[0:1]) / float(12)) * float(pay_days)
                self.vacaciones_fracc = vac_frac2

        alic_b_v = self.calculo_alic_bono_vac((sal_mensual), dias_bv)
        alic_u =  self.calculo_alic_util((sal_mensual),alic_b_v)

        sal_diar = ((sal_mensual)/float(dias_str) + alic_b_v + alic_u)
        values.update({'salario_basico':sal_mensual,
                       'salario_basico_diario':sal_mensual/float(dias_str),
                  #     'salario_prom_mensual': (sal_mensual + (promedio*4))/2,
                   #    'salario_prom_diairo': ((sal_mensual + (promedio*4))/2) / float(dias_str),
                       'alic_bono_vac_liq': alic_b_v,
                       'alic_util_liq': alic_u,
                       'salario_integral':sal_diar,
                       'literal_c': (float(literal_c)*float(sal_diar))
                       })
        return values

    def get_history_fideicomiso(self):
        fi_hist_obj = self.env['hr.historico.fideicomiso']
        values = {}
        history = fi_hist_obj.get_last_history_fi(self.employee_id.id, None)
        if history:
            values.update({'dias_prestaciones_acum': history.dias_acumuluados - history.dias_adicionales,
                           'dias_prestaciones_adi': history.dias_adicionales,
                           'monto_gps': history.monto_acumulado + history.total_anticipos,
                           'aporte_dias_adicionales':history.GPS_dias_adicionales,
                           'interes_anual': history.monto_total_intereses,
                           'anticipo_prestaciones': history.total_anticipos,
                           'fecha_anticipo': history.fecha_anticipo,
                          })

        else:
            raise exceptions.except_orm(('Advertencia!'),
                                        (u'El Empleado %s no posee Historico de Prestaciones Sociales, por favor verifique y genere el mismo para poder proceder con la liquidación.')%(self.employee_id.name))
        return values



    def get_mondays(self,fecha):
        mondays = 0
        rango = self.rango_mes_anterior(fecha,0,'is_liq')
        recursive_days = date_from = datetime.strptime(str(rango[0]), DEFAULT_SERVER_DATE_FORMAT)
        date_to = datetime.strptime(str(rango[1]), DEFAULT_SERVER_DATE_FORMAT)
        date_end = date_to + relativedelta(days=+1)
        while recursive_days != date_end:
            if recursive_days.weekday() == 0:
                mondays += 1
            recursive_days += relativedelta(days=+1)
        return mondays


