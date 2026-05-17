from odoo import models, fields


class Badge(models.Model):
    _name = 'game.badge'
    _description = 'Office Quest - Badge'

    name = fields.Char(string='Badge Name', required=True)
    description = fields.Text(string='Description')
    icon = fields.Image(string='Icon', max_width=64, max_height=64)