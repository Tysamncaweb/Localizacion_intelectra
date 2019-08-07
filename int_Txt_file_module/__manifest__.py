# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details..
{
    'name': 'Txt_file_module',
    'version': '1.0',
    'summary': 'Genera un txt para bancos',

    'description': """

    """,
    'author': 'Tysamnca',
    'collaborator': 'Yorman Pineda',
    'category': 'TxtFile',
    'website': 'https://www.odoo.com/page/billing',
    'depends': ['base','hr_payroll','hr_datos_rrhh','hr_personal_info'],
    'data': [

        'views/int_txt_file_view.xml',
        'views/int_tarjeta_alimentacion_view.xml'

    ],
    'installable': True,
    'application': True,
    'auto_install': False,

}
