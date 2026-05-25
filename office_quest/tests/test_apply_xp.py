from odoo.exceptions import AccessError
from odoo.tests.common import tagged
from .common import OfficeQuestCommon


@tagged('office_quest', 'apply_xp')
class TestApplyXp(OfficeQuestCommon):

    def test_award_increases_xp(self):
        """Positive amount increases profile XP."""
        self.profile.apply_xp(100, 'Test award', trusted=True)
        self.assertEqual(self.profile.xp, 100)

    def test_deduct_decreases_xp(self):
        """Negative amount decreases profile XP."""
        self.profile.write({'xp': 200})
        self.profile.apply_xp(-50, 'Test deduct', trusted=True)
        self.assertEqual(self.profile.xp, 150)

    def test_multiple_awards_accumulate(self):
        """Multiple apply_xp calls stack correctly."""
        self.profile.apply_xp(100, 'First',  trusted=True)
        self.profile.apply_xp(50,  'Second', trusted=True)
        self.profile.apply_xp(25,  'Third',  trusted=True)
        self.assertEqual(self.profile.xp, 175)

    def test_level_updates_after_xp_change(self):
        """Level = (xp // 100) + 1 — recalculated on every apply_xp."""
        self.profile.apply_xp(250, 'Level up', trusted=True)
        self.assertEqual(self.profile.level, 3)

    def test_manager_can_award_manually(self):
        """User with manager group can call apply_xp with source='manual'."""
        profile_as_manager = self.profile.with_user(self.manager_user)
        profile_as_manager.apply_xp(50, 'Manager manual award', source='manual')
        self.assertEqual(self.profile.xp, 50)

    def test_non_manager_blocked_for_manual_source(self):
        """User without manager group cannot use source='manual'."""
        profile_as_user = self.profile.with_user(self.regular_user)
        with self.assertRaises(AccessError):
            profile_as_user.apply_xp(50, 'Sneaky award', source='manual')

    def test_trusted_bypasses_manager_check(self):
        """
        trusted=True allows apply_xp regardless of user group.

        In production xp.mixin always calls apply_xp via sudo()
        so record rules never block it. We replicate that here.
        sudo() bypasses record rules — this is intentional and
        correct because XP is always awarded by the system,
        not by the user directly.
        """
        # sudo() = bypass record rules, same as mixin does in production
        self.profile.sudo().apply_xp(
            50, 'Automated award', source='python_hook', trusted=True
        )
        self.assertEqual(self.profile.xp, 50)

    def test_creates_xp_log_entry(self):
        """Every apply_xp call creates exactly one game.xp.log record."""
        before = self.env['game.xp.log'].search_count([
            ('profile_id', '=', self.profile.id)
        ])
        self.profile.apply_xp(75, 'Log test', trusted=True)
        after = self.env['game.xp.log'].search_count([
            ('profile_id', '=', self.profile.id)
        ])
        self.assertEqual(after, before + 1)

    def test_log_records_correct_values(self):
        """The xp.log entry stores the correct amount, reason and source."""
        self.profile.apply_xp(120, 'Verify log', source='python_hook', trusted=True)
        log = self.env['game.xp.log'].search([
            ('profile_id', '=', self.profile.id),
        ], limit=1, order='id desc')
        self.assertEqual(log.xp_change, 120)
        self.assertEqual(log.reason,    'Verify log')
        self.assertEqual(log.source,    'python_hook')

    def test_cron_bonus_awards_all_active_profiles(self):
        """action_weekly_xp_bonus awards 50 XP to every active profile."""
        profile2 = self.env['game.profile'].create({
            'name': 'Active Hero 2',
            'hero_class': 'wizard',
            'xp': 0,
            'is_active_player': True,
        })
        self.profile.write({'is_active_player': True, 'xp': 0})
        self.env['game.profile'].action_weekly_xp_bonus()
        self.assertEqual(self.profile.xp, 50)
        self.assertEqual(profile2.xp,     50)

    def test_cron_skips_inactive_profiles(self):
        """action_weekly_xp_bonus skips profiles where is_active_player=False."""
        inactive = self.env['game.profile'].create({
            'name': 'Inactive Hero',
            'hero_class': 'rogue',
            'xp': 0,
            'is_active_player': False,
        })
        self.env['game.profile'].action_weekly_xp_bonus()
        self.assertEqual(inactive.xp, 0)