from odoo import models, fields, api,exceptions, _
from datetime import datetime
from dateutil import relativedelta
_DATETIME_FORMAT = "%Y-%m-%d"


class Contract(models.Model):
    _name = 'hr.contract'
    _inherit = ["hr.contract"]
    factor_banda = fields.Float('Factor de Banda Salarial')

class salary_increase(models.Model):
    _name = "salary.increase"
    _description = "Salary Increase"


    state = fields.Selection([('draft', 'Borrador'),
        ('calculate', 'Calcular'),
        ('done', 'Calculado')], 'Estado', default ='draft')
    name = fields.Char("Motivo", size=64, required=True, states={'draft': [('readonly', False)]})
    wage = fields.Float('Porcentaje de Aumento',size=3, states={'draft': [('readonly', False)]})
    fecha_decrete = fields.Date('Fecha del Decreto', help='Fecha del Decreto Presidencial',  states={'draft': [('readonly', False)]})
    fecha_increase = fields.Date('Fecha del Aumento', required=True, help='Fecha del Decreto Presidencial', states={'draft': [('readonly', False)]})
    user_id = fields.Many2one('res.users', 'Responsable',   states={'draft': [('readonly', False)]}, default=lambda s: s._uid)
    employee_ids = fields.One2many('salary.increase.line', 'salary_increase_id','Empleado', readonly=True, states={'draft': [('readonly', False)]})
    type_aumento = fields.Selection([('mov', 'Monto'), ('por', 'Porcentaje')], 'Tipo de Aumento')
    monto = fields.Float('Monto')



    @api.multi
    def upload_wage(self):
        return self._uid


    @api.onchange('type_aumento')
    def onchange_validar(self):

        if self.type_aumento == 'mov':
            self.wage = False

        if self.type_aumento == 'por':
            self.monto = False
        else:

            return {}

    @api.onchange('monto')
    def onchange_porcent(self):
        if self.employee_ids:

            for i in self.employee_ids:
                i.amount = monto = self.monto


    @api.multi
    def upload_wage(self):
        contract_obj = self.env['hr.contract']
        for si in self.browse(self.ids):
            if si.employee_ids:
                for line in si.employee_ids:
                    contract = line.employee_id.contract_id
                    line.write({'past_amount': contract.factor_banda})
                    # contract.employee_id.contract_id.write({'wage': line.amount + contract.wage})
                    contract.write({'factor_banda': line.amount + contract.factor_banda})
        self.write({'state': 'done'})

    @api.multi
    def set_to_draft(self):
        self.write({'state': 'draft'})

    @api.multi
    def upload_calcular(self):
        if self.type_aumento=='mov':
            if self.monto==False:
                raise exceptions.except_orm(_('Error !'), _('El monto debe ser mayor a cero'))
        if self.type_aumento == 'por':
            if self.wage==False:
                raise exceptions.except_orm(_('Error !'), _('El monto debe ser mayor a cero'))



        for i in self:
            employees = self.search([('employee_ids.employee_id', '=', [j.employee_id.id for j in i.employee_ids]),
                         ('fecha_increase', '=', i.fecha_increase)])
            if len(employees) > 1:
                raise exceptions.except_orm(_('Error !'), _('El Empleado que ha ingresado ya tiene aumento de la fecha'+' '+ i.fecha_increase))
            if not i.employee_ids:
                raise exceptions.except_orm(_('Error !'), _('Debe Agregar al Empleado'))
        self.write({'state': 'calculate'})


    @api.onchange('wage')
    def onchange_wage(self):
        if self.employee_ids:

            for line in self.employee_ids:
                line.porcent = self.wage
                contract = line.employee_id.contract_id
                line.amount = contract.factor_banda * self.wage/100

                # validacion de fecha

    @api.onchange('fecha_increase')
    def onchange_date_fecha(self):
        fecha = self.fecha_increase
        if self.fecha_decrete:
            if self.fecha_increase < self.fecha_decrete:
                self.fecha_increase = False
                return {'warning': {'title': "Advertencia!",
                                    'message': "La Fecha del Aumento debe ser Mayor a la Fecha del Decreto"}}

    @api.onchange('fecha_decrete')
    def onchange_fecha_decrete(self):
        if self.fecha_increase:
            if self.fecha_decrete > self.fecha_increase:
                self.fecha_decrete = False
                self.wage = False
                return {'warning': {'title': "Advertencia!",
                                    'message': "La Fecha del Decreto debe ser Menor a la Fecha del Aumento"}}

    @api.onchange('wage')
    def onchange_date(self):
        por = self.wage
        if por <= 999:
            self.wage = por
        else:
            self.wage = False
            return {'warning': {'title': "Advertencia!",
                                'message': "El Porcentaje  Debe se Menor a 3 Digitos "}}

    @api.multi
    def _calculate_date(self, value):
        age = 0
        if value:
            ahora = datetime.now().strftime(_DATETIME_FORMAT)
            age = relativedelta.relativedelta(datetime.strptime(ahora, _DATETIME_FORMAT),
                                                  datetime.strptime(value, _DATETIME_FORMAT))
        return age


class salary_line(models.Model):

    _name = "salary.increase.line"
    _description = "History Salary Increase"
    _order = "fecha_increase desc"

    salary_increase_id = fields.Many2one(comodel_name="salary.increase", string="Incremento")
    employee_id = fields.Many2one('hr.employee','Empleado', readonly=True)
    vat = fields.Char(string="C.I", related='employee_id.identification_id_2', readonly=True)
    porcent = fields.Integer(string="Porcentaje", readonly=True)
    past_amount = fields.Float(string="Salario anterior")
    amount = fields.Float(string="Monto")
    fecha_increase = fields.Date(string="Fecha del Aumento", related='salary_increase_id.fecha_increase', store=True)
    increase_name = fields.Char(string="Motivo", related='salary_increase_id.name', readonly=True)


    @api.onchange('porcent')
    def onchange_porcent(self):
        if self.employee_id:
            #self.porcent = self.wage
            contract = self.employee_id.contract_id
            self.amount = self.monto
        else:
            return {}

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        ctx = self._context
        if ctx.get('order_display', False):
            order = ctx['order_display']
        res = super(salary_line, self).search(
            args, offset=offset, limit=limit, order=order, count=count
        )
        return res


class salary_increase_ajuste_tasa(models.Model):
    _name = "salary.increase.ajuste.tasa"
    _description = "Salary Adjustment"


    state = fields.Selection([('draft', 'Borrador'),
        ('confirm', 'Confirmado'),
        ('done', 'Ejecutado')], 'Estado', default ='draft')
    fecha_actual = fields.Date(string="Fecha de Ajuste")
    user_id = fields.Many2one('res.users', 'Responsable',   states={'draft': [('readonly', False)]}, default=lambda s: s._uid)
    name = fields.Char("Motivo", size=64, states={'draft': [('readonly', False)]})
    tasa = fields.Many2one('res.currency.rate',string="Factor de Corrección de Inflación",required=True,  help="Por favor indique la Fecha de Ajuste para buscar la ultima tasa registrada" )
    Empleado = fields.Many2many('hr.employee')

    @api.multi
    def funcion_confirmar(self):
        self.write({'state': 'confirm'})
    @api.multi
    def set_to_draft(self):
        self.write({'state': 'draft'})

    @api.multi
    def funcion_aprobar(self):
        if self.Empleado:
            for emp in self.Empleado:
                contract = self.env['hr.contract'].search([('employee_id', '=', emp.id)])

                if not contract or len(contract) == 0:
                    raise exceptions.except_orm(_('Advertencia!'), (u'La persona seleccionada, no posee contrato.\n \
                                    Por favor verifique el contrato del empleado %s y corrija para proceder a generar la operación.') % (
                        emp.name))
                if  contract.factor_banda <= 0:
                    raise exceptions.except_orm(_('Advertencia!'), (u'Por favor verifique el contrato del empleado %s y agregue su factor de banda salarial para proceder.') % (emp.name))
                monto = (contract.factor_banda) * self.tasa.rate_real
                contract.write({'wage': monto})
            return self.write({'state': 'done'})
class modificacion_name_get(models.Model):
    _inherit = 'res.currency.rate'

    @api.multi
    def name_get(self):
        result = []
        for res in self:
            name = str(res.rate_real) + ' - ' + str(res.hora)
            result.append((res.id, name))
        return result