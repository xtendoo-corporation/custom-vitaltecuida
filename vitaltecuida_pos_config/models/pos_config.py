from odoo import api, fields, models


class PosConfig(models.Model):
    _inherit = "pos.config"

    default_partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Cliente por defecto",
        help="Cliente que se asignará automáticamente a cada nuevo pedido en esta caja.",
    )


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def _load_pos_data_domain(self, data):
        """
        Extend the default partner loading domain to always include
        the default_partner_id configured in the POS config.
        """
        domain = super()._load_pos_data_domain(data)

        config_data = data.get("pos.config", {}).get("data", [{}])[0]
        default_partner_id = config_data.get("default_partner_id")

        if default_partner_id:
            # domain is [('id', 'in', [...])] — extend the list
            if domain and domain[0][0] == "id" and domain[0][1] == "in":
                ids = list(domain[0][2])
                if default_partner_id not in ids:
                    ids.append(default_partner_id)
                domain = [("id", "in", ids)]

        return domain
