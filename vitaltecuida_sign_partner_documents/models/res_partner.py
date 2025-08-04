from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    sign_request_count = fields.Integer(
        string='Sign Requests Count',
        compute='_compute_sign_request_count'
    )

    @api.depends()
    def _compute_sign_request_count(self):
        """Compute the number of sign requests where this partner is involved"""
        for partner in self:
            # Count sign request items where this partner is the signer
            count = self.env['sign.request.item'].search_count([
                ('partner_id', '=', partner.id)
            ])
            partner.sign_request_count = count

    def action_view_sign_requests(self):
        """Open the list of sign requests for this partner"""
        self.ensure_one()

        # Get all sign request items for this partner
        sign_items = self.env['sign.request.item'].search([
            ('partner_id', '=', self.id)
        ])

        # Get the unique sign requests
        sign_request_ids = sign_items.mapped('sign_request_id').ids

        action = {
            'name': f'Documentos Firmados - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'sign.request',
            'view_mode': 'list,form',
            'domain': [('id', 'in', sign_request_ids)],
            'context': {
                'default_partner_id': self.id,
            }
        }

        if len(sign_request_ids) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': sign_request_ids[0],
            })

        return action
