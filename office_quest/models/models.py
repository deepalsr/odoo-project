from odoo import models, fields, api

class GameProfile(models.Model):
    _name = 'game.profile'
    _description = 'Office Quest - Player Profile'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Hero Name', required=True, tracking=True)

    hero_class = fields.Selection([
        ('warrior', 'Warrior'),
        ('wizard', 'Wizard'),
        ('healer', 'Healer'),
        ('rogue', 'Rogue'),
    ], string='Class', default='warrior')

    xp = fields.Integer(string='Experience Points', default=0, tracking=True)
    level = fields.Integer(string='Level', default=1)
    bio = fields.Text(string='Hero Bio')
    is_active_player = fields.Boolean(string='Active Player', default=True, tracking=True)

    badge_ids = fields.Many2many(
        comodel_name='game.badge',
        relation='game_profile_badge_rel',
        column1='profile_id',
        column2='badge_id',
        string='Badges',
    )
    rank = fields.Integer(
    string="Rank",
    compute="_compute_rank",
    store=False,
    )

    @api.depends("xp")
    def _compute_rank(self):
        all_profiles = self.search([], order="xp desc")
        rank_map = {profile.id: index + 1 for index, profile in enumerate(all_profiles)}
        for record in self:
            record.rank = rank_map.get(record.id, 0)

    @api.onchange('xp')
    def _onchange_xp(self):
        for record in self:
            record.level = (record.xp // 100) + 1

    def write(self, vals):
        if 'xp' in vals:
            vals['level'] = (vals['xp'] // 100) + 1

        result = super().write(vals)

        if 'xp' in vals:
            for record in self:
                self._check_and_award_badges(record)

        return result

    def action_weekly_xp_bonus(self):
        active_profiles = self.search([('is_active_player', '=', True)])
        for profile in active_profiles:
            profile.xp += 50

    def _check_and_award_badges(self, record):
        first_kill = self.env['game.badge'].search(
            [('name', '=', '💀 First Kill')], limit=1)
        high_achiever = self.env['game.badge'].search(
            [('name', '=', '🏆 High Achiever')], limit=1)
        legend = self.env['game.badge'].search(
            [('name', '=', '🦸 Legend')], limit=1)

        if record.xp >= 100 and first_kill:
            if first_kill not in record.badge_ids:
                record.badge_ids = [(4, first_kill.id)]

        if record.xp >= 500 and high_achiever:
            if high_achiever not in record.badge_ids:
                record.badge_ids = [(4, high_achiever.id)]

        if record.level >= 10 and legend:
            if legend not in record.badge_ids:
                record.badge_ids = [(4, legend.id)]


class ResUsers(models.Model):
    _inherit = 'res.users'

    profile_id = fields.Many2one(
        comodel_name='game.profile',
        string='Hero Profile',
        ondelete='set null',
    )
