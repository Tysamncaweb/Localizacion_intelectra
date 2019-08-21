# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Reporte Contrato Trabajador',
    'version' : '1.0',
    'summary': 'Genera el PDF del contrato del empleado',
    'description': """
Genera el contrato del empleado en formato PDF solicitado.
Colaboradores: Ing. Yorman Pineda 
    """,

    'category': 'Human Resources',
    'website': 'http://www.tysamnca.com',
    'depends' : ['hr_payroll','hr_contract','field_timepicker'],
    'data': [
        'report/int_contrato_report.xml',
        'report/hr_contrato_report_wizard.xml',
        'report/hr_contract_add_acuerd.xml',
    ],
    'qweb': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}