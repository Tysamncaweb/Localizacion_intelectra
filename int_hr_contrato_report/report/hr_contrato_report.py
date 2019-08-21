# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import time

from datetime import datetime, date, timedelta, time
from odoo import models, fields, api,exceptions, _

class add_fields_contract_employee(models.Model):
    _inherit = 'hr.employee'
    lugar_acuerdo = fields.Text('Lugar de acuerdo',required=True)
    fecha_acuerdo = fields.Date('Fecha de acuerdo',required=True)
    hora_acuerdo = fields.Char('Hora de acuerdo')



class hr_contrato_report(models.TransientModel):

    _name = 'hr.contrato.report'
    _description = 'Contrato de trabajo'
    domicilio = fields.Text(string="Dirección Domicilio",required=1)
    ubicacion_trabajo = fields.Text(string="Ubicacion de trabajo",required=1)


    @api.multi
    def print_report(self, docids):
        res = dict()
        docs = []
        contract_id = docids['active_id']
        update = {'domicilio': self.domicilio,'ubicacion_trabajo': self.ubicacion_trabajo,'contract_id':contract_id,}
        docids.update(update)
        return self.env.ref('int_hr_contrato_report.action_hr_report_constancia_reporte').report_action([], data=docids)

class ReportAccountPayment_3(models.AbstractModel):
    _name = 'report.int_hr_contrato_report.template_contrato_report'

    @api.model
    def get_report_values(self, docids, data):
        var = data
        contract = self.env['hr.contract'].search([('id','=',data['contract_id'])])
        res = dict()
        docs = []
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
        if contract.employee_id.coach_id.nationality == 'V':
            empleador_nac = 'venezolano'
        else:
            empleador_nac = 'extranjero'
        if contract.employee_id.nationality == 'V':
            empleado_nac = 'venezolano'
        else:
            empleado_nac = 'extranjero'
        if contract.employee_id.coach_id.employee_age < 18:
            empleador_edad = 'menor de edad'
        else:
            empleador_edad = 'mayor de edad'
        if (contract.employee_id.marital_2 == 'S') or (contract.employee_id.marital_2 == False):
            estadocivil = 'Soltero'
        if contract.employee_id.marital_2 == 'C':
            estadocivil = 'Casado'
        if contract.employee_id.marital_2 == 'U':
            estadocivil = 'Union Estable de Hecho'
        if contract.employee_id.marital_2 == 'V':
            estadocivil = 'Viudo'
        if contract.employee_id.marital_2 == 'D':
            estadocivil = 'Divorciado'
        if contract.employee_id.hora_acuerdo[:2] > '12':
            tiempo = 'p.m'
        else:
            tiempo = 'a.m'
        fecha = datetime.strptime(contract.employee_id.fecha_acuerdo, '%Y-%m-%d')
        fecha = fecha.strftime('%A (%d) de %B de %Y')

        if not contract.employee_id.coach_id.city_id_res:
            empleador_ciudad = 'Caracas'
        else:
            empleador_ciudad = contract.employee_id.coach_id.city_id_res
        hora_acuerdo = contract.employee_id.hora_acuerdo
        hora_acuerdo = hora_acuerdo.replace(" ","")
        docs.append({
                     'nombre_empleador': contract.employee_id.coach_id.name,
                     'empleador_nac':empleador_nac,
                     'empleador_edad': empleador_edad,
            'empleador_ciudad' : empleador_ciudad,
                     'cedula_empleador': contract.employee_id.coach_id.identification_id_2,
                     'cargo_empleador': contract.employee_id.coach_id.job_id.name,
                     'nombre_trabajador': contract.employee_id.name,
                     'empleado_nac': empleado_nac,
                     'empleado_edad': contract.employee_id.employee_age,
            'estado_civil': estadocivil,
                     'letra_trabajador': contract.employee_id.nationality,
                     'cedula_trabajador':contract.employee_id.identification_id_2,
            'domicilio': data['domicilio'],
                     'cargo_trabajador': contract.employee_id.job_id.name,
            'departamento_trabajador':contract.employee_id.department_id.name,
            'ubicacion_trabajo': data['ubicacion_trabajo'],
                     'salario' : salario_conv,
                     'salario_cifra': monto_cifra,
            'lugar_acuerdo': contract.employee_id.lugar_acuerdo,
            'fecha_acuerdo': fecha,
            'hora_acuerdo': hora_acuerdo,
            'tiempo': tiempo,
                     })

        return {
            'model': self.env['report.int_hr_contrato_report.template_contrato_report'],
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