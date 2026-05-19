from odoo import models, fields, api
from odoo.exceptions import AccessError


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
    ], string='Class', default='warrior', tracking=True)

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

    log_ids = fields.One2many(
        comodel_name='game.xp.log',
        inverse_name='profile_id',
        string='XP History',
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

    def _get_thread_with_access(self, thread_id, mode='read', **kwargs):
        thread = self.browse(thread_id)
        if not thread.exists():
            return self.env['game.profile']
        # Allow read for any office quest user
        if mode == 'read':
            return thread if self.env.user.has_group(
                'office_quest.group_office_quest_user'
            ) else self.env['game.profile']
        # Allow write/create for managers OR the user owning this profile
        if mode in ('write', 'create'):
            is_manager = self.env.user.has_group(
                'office_quest.group_office_quest_manager'
            )
            is_own_profile = (
                self.env.user.profile_id.id == thread.id
            )
            if is_manager or is_own_profile:
                return thread
            return self.env['game.profile']
        return self.env['game.profile']

    def apply_xp(self, amount, reason, source='manual', task_id=None):
        """Central method — all XP changes must go through here."""
        self.ensure_one()

        # Authorization — manual XP changes only allowed for managers
        # Automated sources (sale, task, cron) bypass this check
        automated_sources = {
            'sale_confirm', 'sale_cancel',
            'task_done', 'task_cancel', 'task_deadline',
            'cron',
        }
        if source == 'manual' and not self.env.user.has_group(
            'office_quest.group_office_quest_manager'
        ):
            raise AccessError(
                "Only managers can manually award or deduct XP."
            )

        self.xp += amount
        sign = '+' if amount >= 0 else ''

        # Post to chatter — use sudo() so automated sources
        # (salesperson, cron) can post without write permission issues
        self.sudo().message_post(
            body=f"⚡ XP {sign}{amount} — {reason} <i>[{source}]</i>",
            message_type='notification',
        )

        # Write to XP log
        log_vals = {
            'profile_id': self.id,
            'xp_change': amount,
            'reason': reason,
            'source': source,
        }
        if task_id:
            log_vals['task_id'] = task_id
        self.env['game.xp.log'].sudo().create(log_vals)

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
            profile.apply_xp(50, 'Weekly activity bonus', source='cron')

    def _check_and_award_badges(self, record):
        first_kill = self.env['game.badge'].search(
            [('name', '=', '💀 First Kill')], limit=1)
        high_achiever = self.env['game.badge'].search(
            [('name', '=', '🏆 High Achiever')], limit=1)
        legend = self.env['game.badge'].search(
            [('name', '=', '🦸 Legend')], limit=1)

        if record.xp >= 100 and first_kill and first_kill not in record.badge_ids:
            record.badge_ids = [(4, first_kill.id)]
        if record.xp >= 500 and high_achiever and high_achiever not in record.badge_ids:
            record.badge_ids = [(4, high_achiever.id)]
        if record.level >= 10 and legend and legend not in record.badge_ids:
            record.badge_ids = [(4, legend.id)]


class ResUsers(models.Model):
    _inherit = 'res.users'

    profile_id = fields.Many2one(
        comodel_name='game.profile',
        string='Hero Profile',
        ondelete='set null',
    )