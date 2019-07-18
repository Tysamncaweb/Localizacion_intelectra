# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution
# Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#
##############################################################################
{   'active': False,
    'author': 'Michel Castillo',
    'category': 'Generic Modules/purchase',
    'data': ['view/intelectra_purchase.xml',
             'report/report_purchasequotation.xml'],
    'demo': [],
    'depends': ['purchase',
               ],
    'description': '\n\n    \n\n This module provides to manage checks (issued and third) \n\n    Add models of Issued Checks and Third Checks. (Accounting/Banck ans Cash/Checks/)\n\n    Add options in Jorunals for using  checks in vouchers.\n\n    Add range of numbers for issued check (CheckBook).Accounting/configuration/Miscellaneous/CheckBooks.\n\n    Add ticket deposit for third checks. Change states from Holding to deposited.(Accounting/Banck ans Cash/Checks/)\n\n    \n\n\t\t',
    'installable': True,
    'auto_install': False,
    'name': 'Intelectra_purchase',
    'test': [],
    'version': '8.0.0.0.1'}

#'view/intelectra_purchase.xml'