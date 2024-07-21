# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class RepairOrder(models.Model):
    _inherit = 'repair.order'

    employee_id = fields.Many2one('hr.employee', string="Employés")