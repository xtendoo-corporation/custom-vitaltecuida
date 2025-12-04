from odoo import models, api, _
from odoo.exceptions import UserError


class SignSendRequestSigner(models.TransientModel):
    _inherit = 'sign.send.request.signer'

    @api.constrains('partner_id')
    def _check_partner_email(self):
        """Override to skip email validation when no_sign_mail context is set"""
        if self.env.context.get('no_sign_mail'):
            return
        # Call parent constraint if exists
        if hasattr(super(), '_check_partner_email'):
            return super()._check_partner_email()

    @api.model_create_multi
    def create(self, vals_list):
        """Override to skip email validation when no_sign_mail context is set"""
        if self.env.context.get('no_sign_mail'):
            # Skip email validation but still check for required fields
            for vals in vals_list:
                if not vals.get('partner_id'):
                    role_id = vals.get('role_id')
                    role = self.env['sign.item.role'].browse(role_id)
                    raise UserError(_(
                        'Please select recipients for the following roles: %(roles)s',
                        roles=role.name,
                    ))
            return super(SignSendRequestSigner, self.with_context(mail_create_nosubscribe=True)).create(vals_list)
        return super().create(vals_list)

