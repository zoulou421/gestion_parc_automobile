# -*- coding: utf-8 -*-
# from odoo import http


# class GestionParcAutomobile(http.Controller):
#     @http.route('/gestion_parc_automobile/gestion_parc_automobile', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/gestion_parc_automobile/gestion_parc_automobile/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('gestion_parc_automobile.listing', {
#             'root': '/gestion_parc_automobile/gestion_parc_automobile',
#             'objects': http.request.env['gestion_parc_automobile.gestion_parc_automobile'].search([]),
#         })

#     @http.route('/gestion_parc_automobile/gestion_parc_automobile/objects/<model("gestion_parc_automobile.gestion_parc_automobile"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('gestion_parc_automobile.object', {
#             'object': obj
#         })

