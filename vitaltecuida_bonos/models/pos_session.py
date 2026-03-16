from odoo import models


class PosSession(models.Model):
    _inherit = "pos.session"

    def _load_pos_data_models(self, config_id):
        models_to_load = super()._load_pos_data_models(config_id)
        if "vitaltecuida.bono.balance" not in models_to_load:
            models_to_load.append("vitaltecuida.bono.balance")
        return models_to_load

