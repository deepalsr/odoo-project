# from odoo import http


# class OfficeQuest(http.Controller):
#     @http.route('/office_quest/office_quest', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/office_quest/office_quest/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('office_quest.listing', {
#             'root': '/office_quest/office_quest',
#             'objects': http.request.env['office_quest.office_quest'].search([]),
#         })

#     @http.route('/office_quest/office_quest/objects/<model("office_quest.office_quest"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('office_quest.object', {
#             'object': obj
#         })

