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
        """Open wizard to select a sign template and sign with this partner"""
        self.ensure_one()

        return {
            'name': 'Seleccionar Plantilla de Firma',
            'type': 'ir.actions.act_window',
            'res_model': 'sign.template.wizard',
            'view_mode': 'form',
            'context': {
                'default_partner_id': self.id,
            },
            'target': 'new',
        }

    def action_view_sign_templates_no_email(self):
        """Open wizard to select a sign template and sign with this partner (without email requirement)"""
        self.ensure_one()

        return {
            'name': 'Seleccionar Plantilla de Firma (Sin Email)',
            'type': 'ir.actions.act_window',
            'res_model': 'sign.template.wizard.no.email',
            'view_mode': 'form',
            'context': {
                'default_partner_id': self.id,
            },
            'target': 'new',
        }

