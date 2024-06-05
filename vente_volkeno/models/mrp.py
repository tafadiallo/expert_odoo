# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from datetime import date,datetime
from odoo.exceptions import ValidationError

class MrpProduction(models.Model):
    _inherit = 'mrp.production'


###################################################################################################
#                       1er cas: l'ordre de fabrication ne depasse pas 17h
###################################################################################################

    def adjust_order_dates(self):
        ordre_fabrication = self.env['mrp.production'].search([('id','=',self.id)])
        if ordre_fabrication:
            dure_hour = sum(ordre_fabrication.workorder_ids.mapped('duration_expected')) / 60
            print(dure_hour)
            # une creation pour le jour ( j )ou on a confimer le devis
            if dure_hour <= 8.0:
                date_planned_start = ordre_fabrication.date_planned_start
                date = date_planned_start.date()
                date_planned_finished = f"{date} 17:00:00"
                ordre_fabrication.with_context(skip_adjust_order_dates=True).write({
                    'date_planned_start': date_planned_start,
                    'date_planned_finished': date_planned_finished
                }) 
            #
            
            if dure_hour > 8.0:
                print("11111111")
                dure_restant = dure_hour - 8.0
                while(dure_restant > 0):
                    date_planned_start = ordre_fabrication.date_planned_start
                    date = date_planned_start.date()
                    date_planned_finished = f"{date} 17:00:00"
                    ordre_fabrication.with_context(skip_adjust_order_dates=True).write({
                        'date_planned_start': date_planned_start,
                        'date_planned_finished': date_planned_finished
                    }) 

                    self.env['mrp.production'].with_context(skip_adjust_order_dates=True).create({
                        'date_planned_start': "2024-06-07 08:00:00",
                        'date_planned_finished': "2024-06-07 17:00:00",
                        'company_id': 1,
                        'consumption': 'flexible',
                        'location_dest_id': 1,
                        'location_src_id': 1,
                        'product_id': 1,
                        'product_uom_id': 1
                    })
                    dure_restant = dure_restant - 8.0

                # dure_restant < 0
                date_planned_start = ordre_fabrication.date_planned_start
                date = date_planned_start.date()
                date_planned_finished = f"{date} 17:00:00"
                ordre_fabrication.with_context(skip_adjust_order_dates=True).write({
                    'date_planned_start': date_planned_start,
                    'date_planned_finished': date_planned_finished
                }) 
            
    @api.model
    def create(self, vals):
        res = super(MrpProduction, self).create(vals)
        res.adjust_order_dates()
        return res


####################################################################################################

















###################################################################################################
#                       1er cas_amelioration: l'ordre de fabrication ne depasse pas 17h 
###################################################################################################

    
    # def adjust_order_dates(self):
    #     ordre_fabrication = self.env['mrp.production'].browse(self.id)
    #     if ordre_fabrication:
    #         date_planned_start = "2024-06-02 08:00:00"
    #         date_planned_finished = "2024-06-02 17:00:00"

    #         ordre_fabrication.with_context(skip_adjust_order_dates=True).write({
    #             'date_planned_start': date_planned_start,
    #             'date_planned_finished': date_planned_finished
    #         })

    #         # Assurez-vous que les IDs existent
    #         product = self.env['product.product'].browse(1)
    #         uom = self.env['uom.uom'].browse(1)
    #         location_dest = self.env['stock.location'].browse(1)
    #         location_src = self.env['stock.location'].browse(1)
    #         company = self.env.user.company_id

    #         if not product.exists() or not uom.exists() or not location_dest.exists() or not location_src.exists() or not company:
    #             raise ValidationError("Un des enregistrements référencés n'existe pas.")

    #         # Créez les deux enregistrements
    #         self.env['mrp.production'].with_context(skip_adjust_order_dates=True).create({
    #             'name': 'mounzo____',
    #             'date_planned_start': "2024-06-03 08:00:00",
    #             'date_planned_finished': "2024-06-03 17:00:00",
    #             'company_id': company.id,
    #             'consumption': 'flexible',
    #             'location_dest_id': location_dest.id,
    #             'location_src_id': location_src.id,
    #             'product_id': product.id,
    #             'product_uom_id': uom.id,
    #         })

    #         self.env['mrp.production'].with_context(skip_adjust_order_dates=True).create({
    #             'name': 'mounzo1àààààà',
    #             'date_planned_start': "2024-06-04 08:00:00",
    #             'date_planned_finished': "2024-06-04 17:00:00",
    #             'company_id': company.id,
    #             'consumption': 'flexible',
    #             'location_dest_id': location_dest.id,
    #             'location_src_id': location_src.id,
    #             'product_id': product.id,
    #             'product_uom_id': uom.id
    #         })


    # @api.model
    # def create(self, vals):
    #     res = super(MrpProduction, self).create(vals)
    #     if not self.env.context.get('skip_adjust_order_dates'):
    #         res.with_context(skip_adjust_order_dates=True).adjust_order_dates()
    #     return res
    
    
    # def unlink(self):
    #     for record in self:
    #         # Supprimer les messages liés
    #         mail_messages = self.env['mail.message'].search([])
    #         if mail_messages:
    #             for m in mail_messages:
    #                 m.unlink()
                
    #             print(f"User #{self.env.uid} deleted mail.message records linked to mrp.production ID {record.id}")

    #         # Supprimer les abonnés liés
    #         mail_followers = self.env['mail.followers'].search([])
    #         if mail_followers:
    #             for m in mail_followers:
    #                 m.unlink()
    #             print(f"User #{self.env.uid} deleted mail.followers records linked to mrp.production ID {record.id}")

    #         print(f"User #{self.env.uid} deleted mrp.production record with ID {record.id}")

    #     return super(MrpProduction, self).unlink()



####################################################################################################
