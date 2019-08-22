# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import time

from datetime import datetime, date, timedelta, time
from odoo import models, fields, api,exceptions, _

class hr_retencion_report(models.TransientModel):

    _name = 'hr.retencion.report'
    _description = 'Historico de retenciones'

    #!!!!!!!!!!!!!!!!!!!!!!!!!!111

    date_from = fields.Date('Date From')
    date_to = fields.Date('date_to')
    empleado = fields.Many2one('hr.employee')

    @api.multi
    def print_report(self, docids):
        res = dict()
        docs = []
        update = {'empleado': self.empleado}
        docids.update(update)
        return self.env.ref('int_hr_retencion_impuestos.action_hr_report_retencion_reporte').report_action([], data=docids)

class ReportAccountPayment_5(models.AbstractModel):
    _name = 'report.int_hr_retencion_impuestos.template_retencion_report'

    @api.model
    def get_report_values(self, docids, data):
        var = data
        #contract = self.env['hr.contract'].search([('id','=',data['contract_id'])])
        res = dict()
        docs = []
        empleado = data['empleado']

        docs.append({
            'date_from': 'xxxxxx',
            'date_to':'xxxxx',
            'agente_razon': 'xxxxx',
            'agente_rif': 'xxxx',
            'agente_direccion': 'xxxxx',
            'beneficiario_nombre':'xxxxx',
            'beneficiario_rif':'xxxx',
            'beneficiario_cedula':'xxxx',
            'beneficiario_direccion':'xxxx',
            'enero':'xxx',
            'febrero': 'xxx',
            'marzo': 'xxx',
            'abril': 'xxx',
            'mayo': 'xxx',
            'junio': 'xxx',
            'julio': 'xxx',
            'agosto': 'xxx',
            'septiembre': 'xxx',
            'octubre': 'xxx',
            'noviembre': 'xxx',
            'diciembre': 'xxx',

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