from odoo import http
from odoo.http import request


class QuestWebsite(http.Controller):

    @http.route('/quest', auth='public', website=True)
    def leaderboard(self, **kwargs):
        profiles = request.env['game.profile'].sudo().search(
            [], order='xp desc'
        )
        return request.render('office_quest.quest_leaderboard', {
            'profiles': profiles,
        })

    @http.route('/quest/my', auth='user', website=True)
    def my_profile(self, **kwargs):
        user = request.env.user
        profile = user.profile_id
        if not profile:
            return request.redirect('/quest')

        logs = request.env['game.xp.log'].sudo().search(
            [('profile_id', '=', profile.id)],
            order='create_date desc',
            limit=20,
        )

        all_badges = request.env['game.badge'].sudo().search([])
        earned_badge_ids = profile.badge_ids.ids

        badge_progress = []
        for badge in all_badges:
            if badge.id in earned_badge_ids:
                continue
            name_lower = badge.name.lower()
            if 'first kill' in name_lower:
                needed = 100
                remaining = max(0, needed - profile.xp)
                badge_progress.append({
                    'badge': badge,
                    'type': 'xp',
                    'needed': needed,
                    'current': profile.xp,
                    'remaining': remaining,
                    'percent': min(100, int((profile.xp / needed) * 100)),
                })
            elif 'high achiever' in name_lower:
                needed = 500
                remaining = max(0, needed - profile.xp)
                badge_progress.append({
                    'badge': badge,
                    'type': 'xp',
                    'needed': needed,
                    'current': profile.xp,
                    'remaining': remaining,
                    'percent': min(100, int((profile.xp / needed) * 100)),
                })
            elif 'legend' in name_lower:
                needed = 10
                remaining = max(0, needed - profile.level)
                badge_progress.append({
                    'badge': badge,
                    'type': 'level',
                    'needed': needed,
                    'current': profile.level,
                    'remaining': remaining,
                    'percent': min(100, int((profile.level / needed) * 100)),
                })

        return request.render('office_quest.quest_my_profile', {
            'profile': profile,
            'logs': logs,
            'badge_progress': badge_progress,
        })

    @http.route('/quest/manage', auth='user', website=True)
    def manage(self, **kwargs):
        if not request.env.user.has_group(
            'office_quest.group_office_quest_manager'
        ):
            return request.redirect('/quest')
        profiles = request.env['game.profile'].sudo().search(
            [], order='xp desc'
        )
        logs = request.env['game.xp.log'].sudo().search(
            [], order='create_date desc', limit=50
        )
        return request.render('office_quest.quest_manage', {
            'profiles': profiles,
            'logs': logs,
        })