# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Constancia de trabajo',
    'version' : '1.0',
    'summary': 'Genera la constancia de trabajo',
    'description': """
Genera la constancia de trabajo en el modulo de empleados
Colaboradores: Ing. Yorman Pineda 
    """,

    'category': 'Human Resources',
    'website': 'http://www.tysamnca.com',
    'depends' : ['hr_payroll','hr_contract'],
    'data': [
        'report/int_constancia_report.xml',
        'report/hr_constancia_wizard.xml',

    ],
    'qweb': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
