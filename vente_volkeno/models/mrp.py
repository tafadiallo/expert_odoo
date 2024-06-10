# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json
import datetime
import math
import re
import warnings

from collections import defaultdict
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _

class MrpProduction(models.Model):
    _inherit = 'mrp.production'


###################################################################################################
#                       1er cas: l'ordre de fabrication ne depasse pas 17h
###################################################################################################
 
            
    @api.model
    def create(self, vals):
        res = super(MrpProduction, self).create(vals)
        dure_hour = sum(res.workorder_ids.mapped('duration_expected')) / 60
        liste_date = []
        date_planned_start = res.date_planned_start
        date = date_planned_start.date()
        date_planned_finished = f"{date} 17:00:00"
        # si la OM va etre cree uniquement le jour j
        if dure_hour <= 8.0:
            self.env['mrp.workorder'].create({
                'date_planned_start': date_planned_start,
                'date_planned_finished': date_planned_finished,
                'name': 'TEST3',
                'workcenter_id': 1,  
                'product_uom_id': res.product_uom_id.id,  
                'production_id': res.id  
            })
        # si la OM va etre cree au moins le jour j et le j+1
        if dure_hour > 8.0:
            dure_restant = dure_hour - 8.0
            i = 0
            
            liste_date.append(str(date_planned_start))
            liste_date.append(str(date_planned_finished))
            print("liste_date",liste_date)
            # tant que il reste du temps dans l OM necessaire pour creer le jour j et le jour j+1
            while(dure_restant > 0):
                nom = res.name+'_'+str(i)
                date_planned_start = res.date_planned_start
                date = date_planned_start.date()
                date_planned_finished = f"{date} 17:00:00"
                self.env['mrp.workorder'].create({
                    'date_planned_start': liste_date[0],
                    'date_planned_finished': liste_date[1],
                    'name': nom,
                    'workcenter_id': 1,  
                    'product_uom_id': res.product_uom_id.id,  
                    'production_id': res.id
                })
                i+=1
                # del liste_date[0] 
                # liste_date[0] = liste_date[1]
                # liste_date[1] = "2024-06-11 15:00:00"
                dure_restant = dure_restant - 8.0

            # dure_restant < 0 : si le temps restant ne permet pas de cree le jours j+1, on cree l om le jour j uniquement
            date_planned_start = res.date_planned_start
            date = date_planned_start.date()
            date_planned_finished = f"{date} 17:00:00"
            
            self.env['mrp.workorder'].create({
                    'name': 'TEST_adi1',
                    'workcenter_id': 1,  
                    'product_uom_id': res.product_uom_id.id,  
                    'production_id': res.id,
                    'date_planned_start': "2024-06-11 10:00:00",
                    'date_planned_finished': "2024-06-11 17:00:00",
            })
        return res
    










