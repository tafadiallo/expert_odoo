# -*- coding: utf-8 -*-
# from odoo import http


# class SheznouManufactCustomization(http.Controller):
#     @http.route('/sheznou_manufact_customization/sheznou_manufact_customization', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sheznou_manufact_customization/sheznou_manufact_customization/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('sheznou_manufact_customization.listing', {
#             'root': '/sheznou_manufact_customization/sheznou_manufact_customization',
#             'objects': http.request.env['sheznou_manufact_customization.sheznou_manufact_customization'].search([]),
#         })

#     @http.route('/sheznou_manufact_customization/sheznou_manufact_customization/objects/<model("sheznou_manufact_customization.sheznou_manufact_customization"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sheznou_manufact_customization.object', {
#             'object': obj
#         })
