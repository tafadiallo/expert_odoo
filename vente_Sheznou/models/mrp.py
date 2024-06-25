# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import datetime
from datetime import date
from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)

class MrpProduction(models.Model):
    _inherit = 'mrp.production'


###################################################################################################
#                       1er cas: l'ordre de fabrication ne depasse pas 17h
###################################################################################################
 
            
    @api.model
    def create(self, vals):
        res = super(MrpProduction, self).create(vals)
        duration_expected_heure = sum(res.workorder_ids.mapped('duration_expected')) / 60
       
        if duration_expected_heure <= 8.0:
            heure_date_depart = res.date_planned_start.hour
            _logger.info('##############################')               
            _logger.info(heure_date_depart)        
            _logger.info('##############################') 
            if duration_expected_heure<=5.0 and heure_date_depart in [8,9,10,11,12]: 
                _logger.info('##############################')               
                _logger.info(res.date_planned_start)        
                _logger.info('##############################')               
           
                heure_fin=heure_date_depart+duration_expected_heure
                date_str_01 = res.date_planned_start.strftime("%Y-%m-%d %H:%M:%S").split(' ')[0]
                date_fin_planification = date_str_01+f" {int(heure_fin)}:00:00"
                print("date_fin_planification",date_fin_planification)
                self.env['mrp.workorder'].create({
                'date_planned_start': res.date_planned_start,
                'date_planned_finished': date_fin_planification,
                'name': res.name,
                'workcenter_id': res.workorder_ids[0].workcenter_id.id,  
                'product_uom_id': res.product_uom_id.id,  
                'production_id': res.id
                })
            if duration_expected_heure>5.0:  
                _logger.info('##############################')               
                # heure_fin=heure_date_depart+duration_expected_heure
                date_str_02 = res.date_planned_start.strftime("%Y-%m-%d %H:%M:%S").split(' ')[0] 
                date_fin_planification_01 = date_str_02+f" 13:00:00"
                nom_01=res.name+"Avant_HPause"
                self.env['mrp.workorder'].create({
                'date_planned_start': res.date_planned_start,
                'date_planned_finished': date_fin_planification_01,
                'name': nom_01,
                'workcenter_id': res.workorder_ids[0].workcenter_id.id,  
                'product_uom_id': res.product_uom_id.id,  
                'production_id': res.id
                })
                _logger.info('MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM') 
                nom_02=res.name+"Apres_HPause"
                date_debut_planification_03 = date_str_02+f" 14:00:00"
                heure_planification_fin_04 =14+(duration_expected_heure-5)
                date_fin_planification_04= date_str_02+f" {int(heure_planification_fin_04)}:00:00"
                self.env['mrp.workorder'].create({
                'date_planned_start': date_debut_planification_03,
                'date_planned_finished': date_fin_planification_04,
                'name': nom_02,
                'workcenter_id': res.workorder_ids[0].workcenter_id.id,  
                'product_uom_id': res.product_uom_id.id,  
                'production_id': res.id
                })
            if duration_expected_heure>3 and heure_date_depart in [14,15,16]:
                # date_str = datetime.datetime.strptime(res.date_planned_start, "%Y-%m-%d %H:%M:%S")
                date_debut1_anne = res.date_planned_start.year
                date_debut1_mois = res.date_planned_start.month
                date_debut1_jour = res.date_planned_start.day

                if date_debut1_jour!='31':
                    date_debut1_jour += 1
                    date_debut1_mois=date_debut1_mois
                    date_debut1_anne=date_debut1_anne
                if date_debut1_jour =='31' and date_debut1_mois!='12':
                    date_debut1_jour = 1
                    date_debut1_mois += 1
                    date_debut1_anne=date_debut1_anne
                if date_debut1_jour =='31' and date_debut1_mois=='12':
                    date_debut1_jour = 1
                    date_debut1_mois = 1
                    date_debut1_anne +=1
                date_str_dyn = f"{date_debut1_anne}-{date_debut1_mois:02}-{date_debut1_jour:02}"

                date_str = res.date_planned_start.strftime("%Y-%m-%d %H:%M:%S").split(' ')[0] 
                date_str_03 = res.date_planned_start.strftime("%Y-%m-%d %H:%M:%S").split(' ')[0] 
                date_debut_planification_04 = date_str_03+f" 17:00:00"
                nom_03=res.name+'Avant_17H'

                s = self.env['mrp.workorder'].create({
                'date_planned_start': res.date_planned_start,
                'date_planned_finished': date_debut_planification_04,
                'name': nom_03,
                'workcenter_id': res.workorder_ids[0].workcenter_id.id,  
                'product_uom_id': res.product_uom_id.id,  
                'production_id': res.id
                })
                
                
            #     if s:
            #         nom_04=res.name+'Apres_17H'
            #         date_debut_apres_17=date_str_dyn+f" 08:00:00"
            #         heure_fin_ap_17h=8+(duration_expected_heure-5)
            #         date_fin_apres_17=date_str_dyn+f" 0{int(heure_fin_ap_17h)}:00:00"
            #         print("date_debut_apres_17",date_debut_apres_17)
            #         print("date_fin_apres_17",date_fin_apres_17)
            #         nom_01=res.name+'Avant_HPause'

            #         self.env['mrp.workorder'].create({
            #         'date_planned_start': date_debut_apres_17,
            #         'date_planned_finished': date_fin_apres_17,
            #         'name': nom_04,
            #         'workcenter_id': 1,  
            #         'product_uom_id': res.product_uom_id.id,  
            #         'production_id': res.id
            #         })
        # #
        # if duration_expected_heure > 8.0:
        #     dure_restant = duration_expected_heure
        #     i = 0
        #     while(dure_restant > 0):
        #         nom = res.name+'_'+str(i)

        #         self.env['mrp.workorder'].create({
        #             'date_planned_start': date_debut,
        #             'date_planned_finished': date_fin,
        #             'name': nom,
        #             'workcenter_id': 1,  
        #             'product_uom_id': res.product_uom_id.id,  
        #             'production_id': res.id
        #         })
        #         i+=1
              
        #         date_debut="2024-06-12 08:00:00"
        #         date_fin = "2024-06-12 15:00:00"
               
        #         # 
        #         date_planned_finished_str = "2024-06-12 08:00:00"
        #         date_planned_finished = datetime.datetime.strptime(date_planned_finished_str, "%Y-%m-%d %H:%M:%S")
        #         date_debut1_anne = date_planned_finished.year
        #         date_debut1_mois = date_planned_finished.month
        #         date_debut1_jour = date_planned_finished.day
        #         heure = date_planned_finished.hour
        #         heure_debut1=heure
        #         heure_fin=0
                
               
                
        #         # rendre dynamique la date
        #         if date_debut1_jour:
        #             if date_debut1_jour!='31':
        #                 date_debut1_jour += 1
        #                 date_debut1_mois=date_debut1_mois
        #                 date_debut1_anne=date_debut1_anne
        #             if date_debut1_jour =='31' and date_debut1_mois!='12':
        #                 date_debut1_jour = 1
        #                 date_debut1_mois += 1
        #                 date_debut1_anne=date_debut1_anne
        #             if date_debut1_jour =='31' and date_debut1_mois=='12':
        #                 date_debut1_jour = 1
        #                 date_debut1_mois = 1
        #                 date_debut1_anne +=1
        #             date_str = f"{date_debut1_anne}-{date_debut1_mois:02}-{date_debut1_jour:02}"
                
        #         #rendre dynamique l heure
        #         if heure==17:
        #             if dure_restant<=5:          # ce 5 c est pour la duree du travaille journalier avant la pause
        #                 heure_debut1=8           # ce 8 est equivalent a 08:00
        #                 heure_fin=8+dure_restant # heure_fin est l heure de fin de OM
        #                 date_debut_01 = date_str+f" 0{heure_debut1}:00:00"
        #                 date_fin_01 = date_str+f" {heure_fin}:00:00"
        #                 nom_01=res.name+str(i)
        #                 self.env['mrp.workorder'].create({
        #                 'date_planned_start': date_debut_01,
        #                 'date_planned_finished': date_fin_01,
        #                 'name': nom_01,
        #                 'workcenter_id': 1,  
        #                 'product_uom_id': res.product_uom_id.id,  
        #                 'production_id': res.id
        #                 })
        #             if dure_restant>5:
        #                 heure_debut_01=8
        #                 heure_fin_01=13
        #                 date_avant_hp_debut_01=date_str+f" 0{heure_debut_01}:00:00"
        #                 date_avant_hp_fin_01=date_str+f" {heure_fin_01}:00:00"
        #                 nom_01=res.name+'Avant_HP_'+str(i)
        #                 self.env['mrp.workorder'].create({
        #                 'date_planned_start': date_avant_hp_debut_01,
        #                 'date_planned_finished': date_avant_hp_fin_01,
        #                 'name': nom_01,
        #                 'workcenter_id': 1,  
        #                 'product_uom_id': res.product_uom_id.id,  
        #                 'production_id': res.id
        #                 })
        #                 heure_debut_02=14
        #                 heure_fin_02=14+(dure_restant-5)
        #                 date_apres_hp_debut_02=date_str+f" {heure_debut_02}:00:00"
        #                 date_apres_hp_fin_02=date_str+f" {heure_fin_02}:00:00"
        #                 nom_02=res.name+'Apres_HP_'+str(i)
        #                 self.env['mrp.workorder'].create({
        #                 'date_planned_start': date_apres_hp_debut_02,
        #                 'date_planned_finished': date_apres_hp_fin_02,
        #                 'name': nom_02,
        #                 'workcenter_id': 1,  
        #                 'product_uom_id': res.product_uom_id.id,  
        #                 'production_id': res.id
        #                 })
                    
        #         else:
        #             print("###################")

        #         dure_restant = dure_restant - 8.0

        #     # dure_restant < 0 : si le temps restant ne permet pas de cree le jours j+1, on cree l om le jour j uniquement
        #     if dure_restant < 0:
        #         date_planned_start = res.date_planned_start
        #         date = date_planned_start.date()
        #         date_planned_finished = f"{date} 17:00:00"
                
        #         self.env['mrp.workorder'].create({
        #                 'name': 'TEST_adi1',
        #                 'workcenter_id': 1,  
        #                 'product_uom_id': res.product_uom_id.id,  
        #                 'production_id': res.id,
        #                 'date_planned_start': "2024-06-11 10:00:00",
        #                 'date_planned_finished': "2024-06-11 17:00:00",
        #         })
        return res
    










