# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details..

from datetime import datetime, timedelta
from odoo import models, api, fields
import base64
from logging import getLogger

class men_descarga(models.Model):
    _name = 'men.descarga'
    name = fields.Text("Título", required="True")

class bono(models.TransientModel):
    _name = "account.wizard.generacion.txtfile"

    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')
    correlativo = fields.Integer('Correlativo')
    fecha_pago = fields.Date('Fecha de Abono')
    # fields for downlo   ad xls
    state = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')
    report = fields.Binary('Archivo Preparado', filters='.xls', readonly=True)
    name = fields.Char('File Name')


    @api.multi
    def print_bono(self):
        file = open("archivo.txt", "w")
        # Searching for customer invoices
        payslip = self.env['hr.payslip'].search(
            [('date_to', '<=', self.date_to), ('date_from', '>=', self.date_from),('struct_id.code','=','7000'),('state','=','done')])
        date_f = str(self.fecha_pago)
        a = date_f[0:4]
        m = date_f[5:7]
        d = date_f[8:]
        for slip in payslip:
            #V+0+cedula
            letra = slip.employee_id.nationality
            cedula = slip.employee_id.identification_id_2
            catcedu = len(cedula)
            if catcedu == 8:
                catce = '0'
            if catcedu == 7:
                catce = '00'
            for var in slip.line_ids:
                if var.code == '7001':
                    monto = var.total
            monto = str(monto)
            for i in range(0, len(monto)):
                if (monto[i] == '.'):
                    cds = monto[i + 1:]
            if len(cds) == 2:
                ceroextra = '0'
                imprimir0 = ''
            else:
                ceroextra = ''
                imprimir0 = '0'
            monto = monto.replace(".", "")
            #formato monto+decimales(00)+fechapago
            formato = monto+imprimir0 + d+m+a
            formato = str(formato).zfill(29)  # agrega ceros delente del pago segun lo establecido por Cestaticket
            # imprimo en el txt
            lineas = [letra,
                      catce,
                      cedula,
                      '  ',
                      formato
                      ]
            for l in lineas:
                file.write(str(l))
            file.write('\n')
        file.close()
        #Nombre del txt
        if self.correlativo < 10:
            imp_correlativo = '0'+str(self.correlativo)
        else:
            imp_correlativo = str(self.correlativo)
        nombre_txt = 'ABONOS'+'4946'+ imp_correlativo + d+m+a+'.txt'
        modelo = 'account.wizard.generacion.txtfile'
        return self.imprimir_txt(nombre_txt,modelo)
    @api.multi
    def imprimir_txt(self,nombretxt,nameclass):
        # Apertura del archivo TXT generado y enviado a la ventana
        r = base64.b64encode(open("archivo.txt", 'rb').read())
        self.write({'state': 'get', 'report': r, 'name': nombretxt})
        return {
            'name': ("Descarga de archivo"),
            'type': 'ir.actions.act_window',
            'res_model': nameclass,
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }