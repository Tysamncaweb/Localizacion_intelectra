# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#    Change: jeduardo **  05/07/2016 **  hr_contract **  Modified
#    Comments: Creacion de campos adicionales para la ficha del trabajador
#
# ##############################################################################################################################################################################

from odoo import fields, models, _ ,exceptions, api
# importando el modulo de regex de python
import re
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime, date
from dateutil import relativedelta

_DATETIME_FORMAT = "%Y-%m-%d"


class HrEmployee(models.Model):
    _name = 'hr.employee'
    _inherit = "hr.employee"

    lugar_acuerdo = fields.Char('Lugar del Acuerdo:', size=24)
    fecha_acuerdo = fields.Date('Fecha del Acuerdo:')
    hora_acuerdo = fields.Char('Hora del Acuerdo:', size=16)
