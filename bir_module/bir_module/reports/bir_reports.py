# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class BirReports(models.Model):
    _inherit = 'account.move'

    def get_bir_quarter(value):
    	return value
