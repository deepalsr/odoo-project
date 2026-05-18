from odoo import models, fields


class Badge(models.Model):
    _name = 'game.badge'
    _description = 'Office Quest - Badge'

    name = fields.Char(string='Badge Name', required=True)
    description = fields.Text(string='Description')
    icon = fields.Image(string='Icon', max_width=64, max_height=64)
    color = fields.Integer(string='Color Index', default=0)
    emoji = fields.Char(string='Emoji', default='🏆')

    def name_get(self):
        result = []
        for record in self:
            name = f"{record.emoji} {record.name}" if record.emoji else record.name
            result.append((record.id, name))
        return result