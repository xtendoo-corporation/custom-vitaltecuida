from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    pos_default_partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Cliente por defecto",
        related="pos_config_id.default_partner_id",
        readonly=False,
        help="Cliente que se asignará automáticamente a cada nuevo pedido en esta caja.",
    )
