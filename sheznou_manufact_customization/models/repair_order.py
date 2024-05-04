# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class RepairOrder(models.Model):
    _inherit = 'repair.order'

    employee_ids = fields.Many2many('hr.employee', string="Assigné à")