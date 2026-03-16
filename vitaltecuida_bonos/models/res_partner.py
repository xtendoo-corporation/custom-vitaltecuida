from odoo import _, api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    bono_balance_count = fields.Integer(
        string="Bonos",
        compute="_compute_bono_balance_count",
    )
    bono_balance_ids = fields.One2many(
        "vitaltecuida.bono.balance",
        "partner_id",
        string="Bonos",
    )

    @api.depends("bono_balance_ids.remaining_uses")
    def _compute_bono_balance_count(self):
        for partner in self:
            partner.bono_balance_count = self.env["vitaltecuida.bono.balance"].search_count([
                ("partner_id", "=", partner.id),
                ("remaining_uses", ">", 0),
            ])

    def action_view_bono_balances(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "vitaltecuida_bonos.action_vitaltecuida_bono_balance"
        )
        action["name"] = _("Bonos - %s") % self.display_name
        action["domain"] = [("partner_id", "=", self.id)]
        action["context"] = {
            "default_partner_id": self.id,
            "search_default_available": 1,
        }
        return action

