from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    client_sessions_count = fields.Integer(
        string='Número de Sesiones',
        compute='_compute_client_sessions_count'
    )

    @api.depends()
    def _compute_client_sessions_count(self):
        for partner in self:
            partner.client_sessions_count = self.env['client.sessions'].search_count([
                ('partner_id', '=', partner.id)
            ])

    def action_view_client_sessions(self):
        """Acción para abrir las sesiones del cliente"""
        self.ensure_one()

        sessions = self.env['client.sessions'].search([
            ('partner_id', '=', self.id)
        ])

        action = {
            'name': f'Sesiones de Cliente - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'client.sessions',
            'view_mode': 'list,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {
                'default_partner_id': self.id,
            }
        }

        return action
