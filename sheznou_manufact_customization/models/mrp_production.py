# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.http import request

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    partner_ids = fields.One2many('res.partner', string="Clients", compute='_compute_sale_order_count')
    partner_id_custom = fields.Char(string='Clients', compute='_get_partner_ids', store=True)
    workorder_done = fields.Float(string="Progression", compute="_workorder_done")

    #
    tache_name = fields.Char(string='Nom de la tâche')
    #,compute="_concat_tache_client_article"

    
    # def _concat_tache_client_article(self):
    #     for res in self:
    #        
    #         if res.partner_ids and res.product_id:
    #             res.tache_name = res.partner_ids.name+'/'+res.product_id.name+'/'+res.name
    #             res.name = res.tache_name
    #         else:
    #             res.tache_name = res.tache_name




    #
    #partner_id =  fields.Many2one('res.partner', string="Client",compute='_compute_sale_order')
    

    ########## affichage des informations dans vue calendar ###############
    
    def name_get(self):
        result = []
        for production in self:
            name = '%s-%s-%s' % (production.partner_ids.name or '',production.product_id.name or '',production.name or '')
            result.append((production.id, name))
        return result
    
    ########## new ###############

    @api.depends('partner_ids')
    def _get_partner_ids(self):
       for rec in self:
           if rec.partner_ids:
               partner_custom = ','.join([p.name for p in rec.partner_ids])
           else:
               partner_custom = ''
           rec.partner_id_custom = partner_custom



    @api.depends('procurement_group_id.mrp_production_ids.move_dest_ids.group_id.sale_id')
    def _compute_sale_order_count(self):
        for production in self:
            production.sale_order_count = len(production.procurement_group_id.mrp_production_ids.move_dest_ids.group_id.sale_id)
            sale_orders = production.procurement_group_id.mrp_production_ids.move_dest_ids.group_id.sale_id
            partner_ids = [order.partner_id.id for order in sale_orders]
            if partner_ids:
                production.partner_ids = [(6, 0, partner_ids)]
            else:
                production.partner_ids = [(5, 0, 0)]  # Clear existing partner_ids if no orders
   
    # @api.depends('procurement_group_id.mrp_production_ids.move_dest_ids.group_id.sale_id')
    # def _compute_sale_order(self):
    #     for production in self:
    #         production.sale_order_count = len(production.procurement_group_id.mrp_production_ids.move_dest_ids.group_id.sale_id)
    #         sale_order = production.procurement_group_id.mrp_production_ids.move_dest_ids.group_id.sale_id
    #         if sale_order:
    #             production.partner_id =sale_order.partner_id.id
    #         else:
    #             production.partner_id =None 
                
    @api.depends('workorder_ids')
    def _workorder_done(self):
        for record in self:
            if not record.workorder_ids:
                record.workorder_done = 0
            else:
                done_workorders = record.workorder_ids.filtered(lambda wo: wo.state == 'done')
                record.workorder_done = 100 * len(done_workorders) / len(record.workorder_ids) if record.workorder_ids else 0


class MrpWorkOrder(models.Model):
    _inherit = 'mrp.workorder'

    partner_ids = fields.One2many('res.partner', string="Clients", related="production_id.partner_ids")
    partner_id_custom = fields.Char(string='Clients', compute='_get_partner_ids', store=True)
    employee_ids = fields.Many2many('hr.employee', string="Employé")

    
    @api.depends('partner_ids')
    def _get_partner_ids(self):
       for rec in self:
           if rec.partner_ids:
               partner_custom = ','.join([p.name for p in rec.partner_ids])
           else:
               partner_custom = ''
           rec.partner_id_custom = partner_custom


    


        