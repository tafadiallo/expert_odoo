# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.http import request
from datetime import timedelta, datetime
import pytz

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    partner_ids = fields.One2many('res.partner', string="Clients", compute='_compute_sale_order_count')
    partner_id_custom = fields.Char(string='Clients', compute='_get_partner_ids', store=True)
    workorder_done = fields.Float(string="Progression", compute="_workorder_done")

    #
    tache_name = fields.Char(string='Nom de la tâche')

    def adjust_order_dates(self):
        print("Adjusting order dates...")
        
        # Définir les heures de début et de fin de la journée de travail
        work_start = 8  # Heure de début (09h00)
        work_end = 17  # Heure de fin (17h00)
        work_days = [0, 1, 2, 3, 4]  # Jours ouvrés : Lundi (0) à Vendredi (4)
        tz = pytz.timezone(self.env.user.tz or 'UTC')  # Fuseau horaire de l'utilisateur
       
        # Fonction pour trouver le prochain jour ouvré
        def next_working_day(date):
            while date.weekday() not in work_days:
                date += timedelta(days=1)
                print("date",date)
            return date

        # Fonction pour ajuster l'heure de début à l'heure de travail
        def next_working_hour(date):
            if date.hour < work_start:
                return date.replace(hour=work_start, minute=0)
            elif date.hour >= work_end:
                date = next_working_day(date + timedelta(days=1))
                return date.replace(hour=work_start, minute=0)
            return date

        # Récupérer les ordres de fabrication qui ne sont ni terminés ni annulés
        orders = self.search([('state', 'not in', ['done', 'cancel'])])
        
        for order in orders:
            # Vérifier que les dates de début et de fin prévues sont définies
            if not order.date_planned_start or not order.date_planned_finished:
                continue

            # Convertir les dates de début et de fin prévues en fuseau horaire de l'utilisateur
            

            # date_planned_start = pytz.utc.localize(order.date_planned_start).astimezone(tz)
            # date_planned_finished = pytz.utc.localize(order.date_planned_finished).astimezone(tz)
             
          
            # nouveau code order.date_planned_start #
            date_planned_start = order.date_planned_start
            print(type(date_planned_start))
            date_planned_finished = "2024-05-30 17:00:00"
            date_obj = datetime.strptime(date_planned_finished, "%Y-%m-%d %H:%M:%S")
            print(type(date_obj))
            order.with_context(skip_adjust_order_dates=True).write({
                # 'date_planned_start': date_planned_start.astimezone(pytz.utc).replace(tzinfo=None),
                # 'date_planned_finished': end_date.astimezone(pytz.utc).replace(tzinfo=None)
                'date_planned_start': date_planned_start,
                'date_planned_finished': date_planned_finished
            }) 
        # duratio_attendue 
        # for om in self.workorder_ids:
        #     duratio_attendue = om.duration_expected
            
            
            # Ajuster la date de début
            # date_planned_start = next_working_hour(date_planned_start)

            # Calculer la durée et ajuster la date de fin
            
        # hours__finish = date_obj.hour + date_obj.minute / 60 + date_obj.second / 3600
        # hours_date_planned_start = date_planned_start.hour + date_planned_start.minute / 60 + date_planned_start.second / 3600
        dure_restant = 2000.0 - 8.0
        if dure_restant > 0:
            self.create({
            # 'date_planned_start': date_planned_start.astimezone(pytz.utc).replace(tzinfo=None),
            # 'date_planned_finished': end_date.astimezone(pytz.utc).replace(tzinfo=None)
            'date_planned_start': "2024-05-31 08:00:00",
            'date_planned_finished': "2024-05-31 17:00:00",
            'company_id': 1,
            'consumption':'flexible',
            'location_dest_id':1,
            'location_src_id':1,
            'product_id': 46,  
            'product_uom_id': 1
            })
            
            # working_hours = work_end - work_start
            # total_days = duration.total_seconds() // (working_hours * 3600)
            # remaining_hours = (duration.total_seconds() % (working_hours * 3600)) / 3600

            # end_date = date_planned_start + timedelta(days=total_days)
            # end_date = next_working_day(end_date)
            # end_date = end_date.replace(hour=work_start + int(remaining_hours), minute=0)
            # end_date = next_working_hour(end_date)

            # Convertir les dates ajustées en UTC avant de les enregistrer
            

    @api.model
    def create(self, vals):
        print("Creating MRP Production...")
        res = super(MrpProduction, self).create(vals)
        if not self.env.context.get('skip_adjust_order_dates'):
            res.with_context(skip_adjust_order_dates=True).adjust_order_dates()
        return res


    def write(self, vals):
        print("Writing MRP Production...")
        if self.env.context.get('skip_adjust_order_dates'):
            return super(MrpProduction, self).write(vals)
        res = super(MrpProduction, self).write(vals)
        self.adjust_order_dates()
        return res

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






    


        