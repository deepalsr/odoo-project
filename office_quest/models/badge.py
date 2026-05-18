from odoo import models, fields, api


class Badge(models.Model):
    _name = 'game.badge'
    _description = 'Office Quest - Badge'

    name = fields.Char(string='Badge Name', required=True)
    description = fields.Text(string='Description')
    icon = fields.Image(string='Icon', max_width=64, max_height=64)
    color = fields.Integer(string='Color Index', default=0)
    emoji = fields.Char(string='Emoji', default='🏆')

    display_name = fields.Char(
        string='Display Name',
        compute='_compute_display_name',
        store=True,
    )

    @api.depends('name', 'emoji')
    def _compute_display_name(self):
        for record in self:
            if record.emoji:
                record.display_name = f"{record.emoji} {record.name}"
            else:
                record.display_name = record.name