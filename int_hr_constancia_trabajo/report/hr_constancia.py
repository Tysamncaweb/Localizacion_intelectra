# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import time

from datetime import datetime, date, timedelta, time
from odoo import models, fields, api,exceptions, _


class hr_constancia(models.TransientModel):

    _name = 'hr.constancia'
    _description = 'Constancia de trabajo'
    dirigido = fields.Char(string="A quién va dirigido",required=1)

    @api.multi
    def print_report(self, docids):
        res = dict()
        docs = []
        idddd = docids['active_id']
        update = {'dirigido':self.dirigido,'id_employee': idddd}
        docids.update(update)
        return self.env.ref('int_hr_constancia_trabajo.action_hr_report_constancia_reporte').report_action([], data=docids)

class ReportAccountPayment_2(models.AbstractModel):
    _name = 'report.int_hr_constancia_trabajo.template_constancia_trabajo'

    @api.model
    def get_report_values(self, docids, data):
        var = data
        employee = self.env['hr.employee'].search([('id','=',data['id_employee'])])
        res = dict()
        docs = []

        contract = self.env['hr.contract'].search([('employee_id','=',data['id_employee'])])

        if not contract or len(contract) == 0:
            raise exceptions.except_orm(_('Advertencia!'), (u'La persona seleccionada, no posee contrato'))


        #Fechas operaciones con ellas///////////////////////////////////////
        fecha_actual0 = date.today()
        fecha_entrega = datetime.strptime(employee.fecha_inicio, '%Y-%m-%d')

        fecha_entrega = self.month_converter(fecha_entrega)
        fecha = self.month_converter(fecha_actual0)
        #Fin fechas formato///////////////////////////////////////////////
        salario = contract.wage
        salario_cifra = self.numero_to_letras(salario)
        entero = int(salario)
        decimal = int(round((salario - entero) * 100))
        decimal_cifra = self.numero_to_letras(decimal)
        if decimal_cifra != '':
            monto_cifra = salario_cifra + ' CON ' + decimal_cifra
        else:
            monto_cifra = salario_cifra

        salario_conv = '{0:,.2f}'.format(salario).replace(',', 'X').replace('.', ',').replace('X', '.')

        docs.append({'fecha_actual':fecha,
                     'dirigido': data['dirigido'],
                     'nombre_empleador': employee.coach_id.name,
                     'letra_empleador': employee.coach_id.nationality,
                     'cedula_empleador': employee.coach_id.identification_id_2,
                     'cargo_empleador': employee.coach_id.job_id.name,
                     'nombre_trabajador': employee.name,
                     'letra_trabajador': employee.nationality,
                     'cedula_trabajador':employee.identification_id_2,
                     'cargo_trabajador': employee.job_id.name,
                     'fecha_ingreso_empleado': fecha_entrega,
                     'salario' : salario_conv,
                     'salario_cifra': monto_cifra,
                     })

        return {
            'model': self.env['report.int_hr_constancia_trabajo.template_constancia_trabajo'],
            'lines': res,  # self.get_lines(data.get('form')),
            # date.partner_id
            'docs': docs,


        }

    def numero_to_letras(self,numero):
        indicador = [("", ""), ("MIL", "MIL"), ("MILLON", "MILLONES"), ("MIL", "MIL"), ("BILLON", "BILLONES")]
        entero = int(numero)
        decimal = int(round((numero - entero) * 100))
        # print 'decimal : ',decimal
        contador = 0
        numero_letras = ""
        while entero > 0:
            a = entero % 1000
            if contador == 0:
                en_letras = self.convierte_cifra(a, 1).strip()
            else:
                en_letras = self.convierte_cifra(a, 0).strip()
            if a == 0:
                numero_letras = en_letras + " " + numero_letras
            elif a == 1:
                if contador in (1, 3):
                    numero_letras = indicador[contador][0] + " " + numero_letras
                else:
                    numero_letras = en_letras + " " + indicador[contador][0] + " " + numero_letras
            else:
                numero_letras = en_letras + " " + indicador[contador][1] + " " + numero_letras
            numero_letras = numero_letras.strip()
            contador = contador + 1
            entero = int(entero / 1000)
        numero_letras = numero_letras
        return numero_letras
    def convierte_cifra(self,numero, sw):
        lista_centana = ["", ("CIEN", "CIENTO"), "DOSCIENTOS", "TRESCIENTOS", "CUATROCIENTOS", "QUINIENTOS",
                         "SEISCIENTOS", "SETECIENTOS", "OCHOCIENTOS", "NOVECIENTOS"]
        lista_decena = ["", (
        "DIEZ", "ONCE", "DOCE", "TRECE", "CATORCE", "QUINCE", "DIECISEIS", "DIECISIETE", "DIECIOCHO", "DIECINUEVE"),
                        ("VEINTE", "VEINTI"), ("TREINTA", "TREINTA Y "), ("CUARENTA", "CUARENTA Y "),
                        ("CINCUENTA", "CINCUENTA Y "), ("SESENTA", "SESENTA Y "),
                        ("SETENTA", "SETENTA Y "), ("OCHENTA", "OCHENTA Y "),
                        ("NOVENTA", "NOVENTA Y ")
                        ]
        lista_unidad = ["", ("UN", "UNO"), "DOS", "TRES", "CUATRO", "CINCO", "SEIS", "SIETE", "OCHO", "NUEVE"]
        centena = int(numero / 100)
        decena = int((numero - (centena * 100)) / 10)
        unidad = int(numero - (centena * 100 + decena * 10))
        # print "centena: ",centena, "decena: ",decena,'unidad: ',unidad

        texto_centena = ""
        texto_decena = ""
        texto_unidad = ""

        # Validad las centenas
        texto_centena = lista_centana[centena]
        if centena == 1:
            if (decena + unidad) != 0:
                texto_centena = texto_centena[1]
            else:
                texto_centena = texto_centena[0]

        # Valida las decenas
        texto_decena = lista_decena[decena]
        if decena == 1:
            texto_decena = texto_decena[unidad]
        elif decena > 1:
            if unidad != 0:
                texto_decena = texto_decena[1]
            else:
                texto_decena = texto_decena[0]
        # Validar las unidades
        # print "texto_unidad: ",texto_unidad
        if decena != 1:
            texto_unidad = lista_unidad[unidad]
            if unidad == 1:
                texto_unidad = texto_unidad[sw]

        return "%s %s %s" % (texto_centena, texto_decena, texto_unidad)

    def month_converter(self,fecha):
        mes = fecha.strftime('%m')
        meses = {'01': 'Enero',
               '02': 'Febrero',
               '03': 'Marzo',
               '04': 'Abril',
               '05': 'Mayo',
               '06': 'Junio',
               '07': 'Julio',
               '08': 'Agosto',
               '09': 'Septiembre',
               '10': 'Octubre',
               '11': 'Noviembre',
               '12': 'Diciembre'
        }
        mes_letra = meses.get(mes)
        fecha_lista = fecha.strftime('%d de {} de %Y').format(mes_letra)
        return fecha_lista
