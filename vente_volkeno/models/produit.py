# -*- encoding: utf-8 -*-
from odoo import models ,api ,fields
import datetime
try:
    import qrcode
except ImportError:
    qrcode = None
try:
    import base64
except ImportError:
    base64 = None
from io import BytesIO
import uuid
uuid4 = str(uuid.uuid4())
import re


class ProductTemplate(models.Model):
    _inherit = "product.template"
    
    commentaire_produit = fields.Text(string = "Commentaire Produit")

    serial_number = fields.Char(
        string='Numéro de série',
        size=64,
    )
    qr_code = fields.Binary("Code QR", compute='generate_qr_code')
    num_autom = fields.Char('Numéro automatisé')
    code_article = fields.Char('Code article',compute='generate_ref_produit')
      
    def generate_ref_produit(self):
        if self.categ_id and len(self.categ_id.name)>1:
            code_article = list(self.categ_id.name)
            code_article = code_article[0]+code_article[1].capitalize() 
            if not self.code_article and not self.default_code:
                self.code_article = code_article
                self.default_code =  self.code_article #+"-"+self.name 
        elif self.categ_id and len(self.categ_id.name)<=1:
            if not self.code_article and not self.default_code:
                self.code_article = self.categ_id.name.capitalize() 
                self.default_code =  self.code_article #+"-"+self.name 
        else:
            self.code_article = self.code_article
    
    def update_ref_product(self):
        products = self.env['product.template'].search([])
        for product in products:
            product.default_code = None
                
                    
                    
    def generate_qr_code(self):
        for rec in self:
            if qrcode and base64:
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=3,
                    border=4,
                )
                qr.add_data(", responsable : ")
                qr.add_data(rec.responsible_id.name)
                qr.add_data("prix de vente : ")
                qr.add_data(rec.list_price)
                qr.add_data(", nom produit : ")
                qr.add_data(rec.name)
                qr.add_data(", prix d'achat : ")
                qr.add_data(rec.standard_price)
                qr.make(fit=True)
                img = qr.make_image()
                temp = BytesIO()
                img.save(temp, format="PNG")
                qr_image = base64.b64encode(temp.getvalue())
                rec.update({'qr_code': qr_image})
                
    @api.model
    def create(self, vals):
        # seq = self.env['ir.sequence'].next_by_code('product.template')
        # name = vals.get("name")
        # if not name:
        #     name=''
        # vals["num_autom"] = seq+"-"+name
        # if not vals.get('serial_number'):
        #    vals['serial_number'] = uuid4
           
        # categorie = self.env['product.category'].search([('id','=',vals.get("categ_id"))])
        # if vals.get("categ_id") and len(categorie)>1:
        #     product = self.env['product.template'].search([('categ_id','=',vals.get("categ_id"))])
        #     code_article = list(product.categ_id.name)
        #     code_article = code_article[0]+code_article[1]
        #     vals['code_article'] = code_article
            
        # if vals.get("categ_id") and len(categorie)<1:
        #     product = self.env['product.template'].search([('categ_id','=',vals.get("categ_id"))])
        #     code_article = list(product.categ_id.name)
        #     code_article = code_article[0]+code_article[1]
        #     vals['code_article'] = code_article
            
        # if not vals.get("default_code") and vals.get('code_article'):
        #     vals["default_code"] =  vals['code_article']+"-"+vals['name']
        res = super(ProductTemplate, self).create(vals)
        return res
    
    
    # def write(self,vals):

    #     name = vals.get("name")
    #     if name :
    #         if re.search(r"^(([0-9]*)([-]*))*",name) :
    #             name = re.sub(r"^(([0-9]*)([-]*))*","",name)
    #             name = self.name[0:4]+name
    #         vals["name"] = name
    #     res = super(ProductTemplate, self).write(vals)
    #     return res
    
    #######  Fonction pour mettre à jour les noms des produits existants avec des séquences #########
    
    def update_product_names_with_sequences(self):
        products = self.env['product.template'].search([])
        products = products.sorted(key=lambda p: p.id)

        for product in products:
            seq = product.env['ir.sequence'].next_by_code('product.template')
            new_name = "%s-%s" % (seq, product.name)
            product.write({'num_autom': new_name})


    # @api.onchange('name')
    # def generate_unique_serial_number(self):
    #     product_template_id = self.env.context.get('active_id')
    #     serial_number = uuid4
    #     ProductProduct = self.env['product.product']
    #     while ProductProduct.search([('serial_number', '=', serial_number), ('product_tmpl_id', '=', product_template_id)]):
    #         serial_number = uuid4
    #     return serial_number, product_template_id


    def generate_serial_numbers_all(self):
        """
        Fonction pour générer des numéros de série uniques pour tous les produits existants dans tous les modèles de produits.
        """
        product_model = self.env['product.product']
        product_template_model = self.env['product.template']

        # Récupérer tous les modèles de produits
        templates = product_template_model.search([])

        # Générer et attribuer des numéros de série uniques pour tous les produits
        for template in templates:
            products = product_model.search([('product_tmpl_id', '=', template.id)])
            for product in products:
                if not product.serial_number:
                    serial_number = uuid4
                    while product_model.search([('serial_number', '=', serial_number), ('product_tmpl_id', '=', product.product_tmpl_id.id)]):
                        serial_number =uuid4
                    product.serial_number = serial_number



    # def track_serial_numbers_for_product_template(self):
    #     ProductProduct = self.env['product.product']
    #     product_template = self.browse(self.env.context.get('active_id'))
    #     products = ProductProduct.search([('product_tmpl_id', '=', product_template.id)])
    #     serial_numbers = [product.serial_number for product in products]

    #     return serial_numbers
