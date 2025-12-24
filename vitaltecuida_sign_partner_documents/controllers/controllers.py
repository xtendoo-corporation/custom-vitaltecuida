# pylint: disable=import-error,unused-import
from odoo import http
from odoo.http import request
from odoo.addons.sign_oca.controllers.main import PortalSign

class PortalSignCustom(PortalSign):
    @http.route(
        ["/sign_oca/document/<int:signer_id>/<string:access_token>"],
        type="http",
        auth="public",
        website=True,
    )
    def get_sign_oca_access(self, signer_id, access_token, **kwargs):
        no_email_thanks = request.httprequest.args.get('no_email_thanks') == '1'
        try:
            signer_sudo = self._document_check_access(
                "sign.oca.request.signer", signer_id, access_token
            )
        except Exception:
            return request.redirect("/my")
        if signer_sudo.signed_on:
            return request.render(
                "sign_oca.portal_sign_document_signed",
                {
                    "signer": signer_sudo,
                    "company": signer_sudo.request_id.company_id,
                    "no_email_thanks": no_email_thanks,
                },
            )
        return super().get_sign_oca_access(signer_id, access_token, **kwargs)
