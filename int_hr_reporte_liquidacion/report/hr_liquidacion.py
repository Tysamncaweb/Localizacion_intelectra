# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import time

from datetime import datetime, date, timedelta, time
from odoo import models, fields, api,exceptions, _


class hr_liquidacion(models.TransientModel):
    _name = 'hr.liquidacion'
    _description = 'liquidacion del trabajador'
    gerente = fields.Many2one('hr.employee',string="Gerente del área", required=True)

    @api.multi
    def print_report(self, docids):
        res = dict()
        docs = []
        idddd = docids['active_id']
        update = {'slip_id': idddd,'gerente':self.gerente.name}
        docids.update(update)
        return self.env.ref('int_hr_reporte_liquidacion.action_hr_report_liquidacion_reporte').report_action([], data=docids)

class ReportAccountPayment_5(models.AbstractModel):
    _name = 'report.int_hr_reporte_liquidacion.template_liquidacion_trabajo'

    @api.model
    def get_report_values(self, docids, data):
        var = data
        slip_id = self.env['hr.payslip'].search([('id','=',data['slip_id'])])
        if slip_id.structure.code != 'ESP-05':
            raise exceptions.except_orm(_('Advertencia!'),
                                        (u'Por favor verifique que la nómina sea de Liquidación'))
        if slip_id.state != 'done':
            raise exceptions.except_orm(_('Advertencia!'),
                                        (u'Por favor verifique que la nómina de Liquidación este en estado "Realizado"'))

        rif_empleador = 'V'+'-'+str(slip_id.employee_id.coach_id.rif[2:10])+'-'+ str(slip_id.employee_id.coach_id.rif[-1])
        ci_empleado =  str(slip_id.employee_id.nationality) + '-'+ str(slip_id.employee_id.identification_id_2)
        fecha_ingreso = datetime.strptime(slip_id.date_from, '%Y-%m-%d')
        fecha_ingreso = fecha_ingreso.strftime('%d/%m/%Y')
        fecha_actual = date.today()
        fecha_actual = fecha_actual.strftime('%d/%m/%Y')
        if not slip_id.employee_id.fecha_fin or not slip_id.employee_id.m_egreso:
            raise exceptions.except_orm(_('Advertencia!'),
                                        (u'Por favor recuerde registrar la Fecha de Egreso y el Motivo de Egreso'))
        fecha_egreso = datetime.strptime(slip_id.employee_id.fecha_fin, '%Y-%m-%d')
        fecha_egreso = fecha_egreso.strftime('%d/%m/%Y')
        res = dict()
        docs = []
        asignaciones=[]
        deducciones=[]
        for a in slip_id.line_ids:
            dias_porcentaje = ''
            dias_porcentaje_ded = ''
            salario = ''
            monto = 0
            if a.category_id.code == 'ALW':
                #if a.amount_python_compute.find("dias_prestaciones_acum") != -1:
                #    dias_porcentaje = slip_id.dias_prestaciones_acum
                if a.amount_python_compute.find("dias_prestaciones_adi") != -1:
                    dias_porcentaje = slip_id.dias_prestaciones_adi
                if a.code == '5002':
                    dias_porcentaje = slip_id.dias_prestaciones_acum
                if a.code == '5003':
                    dias_porcentaje = slip_id.aporte_dias_adicionales
                if a.code == '5008':
                    dias_porcentaje = '16,66%'
                    salario = a.amount/0.1666
                    salario = self.separador_cifra(salario)
                #if a.amount_python_compute.find("aporte_dias_adicionales") != -1:
                #    dias_porcentaje = slip_id.aporte_dias_adicionales
                monto = a.amount
                monto = self.separador_cifra(monto)
                asignaciones.append({
                    'nombre': a.name,
                    'dias_porcentaje': dias_porcentaje,
                    'salario':salario,
                    'monto': monto,
                })

            if a.category_id.code == 'DED':
                if a.code == '5022':
                    dias_porcentaje_ded = '1%'
                if a.code == '5024':
                    dias_porcentaje_ded = '0,50%'
                monto = a.amount
                monto = self.separador_cifra(monto)
                deducciones.append({
                    'nombre': a.name,
                    'dias_porcentaje': dias_porcentaje_ded,
                    'salario':'',
                    'monto': monto,
                })


            if a.category_id.code == 'BASIC':
                total_asignaciones = a.amount
                total_asignaciones = self.separador_cifra(total_asignaciones)
            if a.category_id.code == 'GROSS':
                total_deducciones = a.amount
                total_deducciones = self.separador_cifra(total_deducciones)
            if a.category_id.code == 'NET':
                neto_pagar = a.amount
                neto_pagar = self.separador_cifra(neto_pagar)

        docs.append({
            'nombre_empleador':slip_id.employee_id.coach_id.name.title(),
            'rif_empleador':rif_empleador,
            'nombre_empleado':slip_id.employee_id.name.title(),
            'ci_empleado': ci_empleado,
            'fecha_ingreso': fecha_ingreso,
            'cargo': slip_id.employee_id.job_id.name,
            'fecha_egreso': fecha_egreso,
            'salario_mensual': self.separador_cifra(slip_id.salario_basico),
            'motivo': slip_id.employee_id.m_egreso.name,
            'salario_diario': self.separador_cifra(slip_id.salario_basico_diario),
            'años_servicio': slip_id.tiempo_servicio_year,
            'meses_servicio': slip_id.tiempo_servicio_meses,
            'dias_servicio': slip_id.tiempo_servicio_dias,
            'salario_integral': self.separador_cifra(slip_id.salario_integral),
            'fecha_actual':fecha_actual,
            'nombre_gerente':data['gerente'].title(),
            'total_asignaciones': total_asignaciones,
            'total_deducciones':total_deducciones,
            'neto_pagar':neto_pagar,
        })
        return {
            'model': self.env['report.int_hr_reporte_liquidacion.template_liquidacion_trabajo'],
            'lines': res,  # self.get_lines(data.get('form')),
            # date.partner_id
            'docs': docs,
            'asignaciones':asignaciones,
            'deducciones':deducciones,


        }

    def separador_cifra(self,valor):
        monto = '{0:,.2f}'.format(valor).replace('.', '-')
        monto = monto.replace(',', '.')
        monto = monto.replace('-', ',')
        return  monto