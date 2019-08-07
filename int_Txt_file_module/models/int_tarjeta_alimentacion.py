# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta
from odoo import models, api, _, fields
from odoo.exceptions import ValidationError
from odoo.tools.misc import formatLang
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
import xlwt
import base64
import urllib

from logging import getLogger


_logger = getLogger(__name__)


class Solicitud_tarjeta(models.TransientModel):
    _name = "account.wizard.solicitud.tarjeta"

    empleados = fields.Many2many('hr.employee')


    # fields for download xls
    state = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')
    report = fields.Binary('Archivo Preparado', filters='.xls', readonly=True)
    name = fields.Char('File Name', size=32)

    @api.multi
    def print_bono(self,cr):


        file = open("archivo.txt", "w")


        for emp in self.empleados:
                letra = emp.nationality
                cedula = emp.identification_id_2
                catcedu = len(cedula)
                if catcedu == 8:
                    catce = '0'
                if catcedu == 7:
                    catce = '00'
                #catce, es los ceros que se agregan antes de la cedula
                #ncedu, es el numero de cedula
                #cval, es la cantidad de ceros que se agregan antes del monto
                #cant, son la cantidad de dias laborados como maximo 20
                name1 = emp.firstname
                name1 = str(name1)
                name1 = name1.upper()
                name2 = emp.firstname2
                name2 = str(name2)
                name2 = name2.upper()
                apellido = emp.lastname
                apellido = str(apellido)
                apellido = apellido.upper()
                apellido2 = emp.lastname2
                apellido2 = str(apellido2)
                apellido2 = apellido2.upper()
                if name1 == 'FALSE':
                    name1 = ' '
                if name2 == 'FALSE':
                    name2 = ' '
                if apellido == 'FALSE':
                    apellido = ' '
                if apellido2 == 'FALSE':
                    apellido2 = ' '
                #Se calcula los espacios que ocupan los nombres para saber los espacios que se deben imprimir en el txt segun el formato
                #nombre y apellido
                var = 21 - (len(name1)+len(apellido)+1)
                num ='                     '
                num = num[0:var]
                #nombre
                var2 = 20 - len(name1)
                num2 = '                     '
                num2 = num2[0:var2]
                #nombre2
                var3 = 20 - len(name2)
                num3 = '                     '
                num3 = num3[0:var3]
                #apellido
                var4 = 20 - len(apellido)
                num4 = '                     '
                num4 = num4[0:var4]
                # apellido2
                var5 = 20 - len(apellido2)
                num5 = '                     '
                num5 = num5[0:var5]
                #me traigo la fecha de cumplea;os
                date_f = emp.birthday
                a = date_f[0:4]
                m = date_f[5:7]
                d = date_f[8:]
                #traigo los datos civiles

                lineas = [letra,
                          catce,
                          cedula,
                          '  ',
                          name1,
                          ' ',
                          apellido,
                          num,
                          name1,
                          num2,
                          name2,
                          num3,
                          apellido,
                          num4,
                          apellido2,
                          num5,
                          d,m,a,
                          'SOMGALPON34']
                for l in lineas:
                    file.write(str(l))
                file.write('\n')

        file.close()

        r = base64.b64encode(open("archivo.txt", 'rb').read())
        self.write({'state': 'get', 'report': r, 'name': 'Solicitud de Tarjeta.txt'})
        return {
            'name': ("Descarga de archivo"),
            'type': 'ir.actions.act_window',
            'res_model': 'account.wizard.solicitud.tarjeta',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }

