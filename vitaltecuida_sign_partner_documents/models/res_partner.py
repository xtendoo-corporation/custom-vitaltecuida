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


    def action_view_sign_templates(self):
        """Open the list of all sign templates"""
        self.ensure_one()

        return {
            'name': 'Plantillas de Firma',
            'type': 'ir.actions.act_window',
            'res_model': 'sign.template',
            'view_mode': 'kanban,list,form',
            'context': {
                'create': True,
            },
            'target': 'current',
        }
