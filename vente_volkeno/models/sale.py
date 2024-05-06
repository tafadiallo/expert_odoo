# -*- coding: utf-8 -*-
from odoo import models, fields, api , _
from odoo.exceptions import ValidationError
from datetime import date

class Order(models.Model):
    _inherit = "sale.order"
    
    date_order = fields.Datetime(
    string='Order Date',
    required=True,
    readonly=True,
    index=True,
    states={'draft': [('readonly', False)], 'sent': [('readonly', False)], 'sale': [('readonly', False)]},  # Added 'sale' state
    copy=False,
    default=fields.Datetime.now,
    help="Creation date of draft/sent orders,\nConfirmation date of confirmed orders."
    )

           
    @api.depends('order_line.purchase_line_ids.order_id')
    def _compute_purchase_order_count(self):
        for order in self:
            if order.name:
                achat = self.env['purchase.order'].search([('origin', '=',order.name)])
                if achat:
                    achat.project_client_tags = order.partner_id
            order.purchase_order_count = len(order._get_purchase_orders())



    
            


class Task(models.Model):
    _inherit = "project.task"
    
    employe_id = fields.Many2one('hr.employee', string="Employes")
    
