from odoo import _, fields, models
from odoo.exceptions import UserError


class PosOrder(models.Model):
    _inherit = "pos.order"

    bono_operations_processed = fields.Boolean(copy=False, default=False)

    def _process_saved_order(self, draft):
        self.ensure_one()
        if not draft:
            self._validate_bono_requirements()
        result = super()._process_saved_order(draft)
        if not draft and not self.bono_operations_processed and self.state != "cancel":
            self._apply_bono_operations()
            self.bono_operations_processed = True
        return result

    def _validate_bono_requirements(self):
        self.ensure_one()
        bono_lines = self.lines.filtered(lambda line: line.product_id.is_bono or line.is_bono_redemption)
        if bono_lines and not self.partner_id:
            raise UserError(_("Debes seleccionar un cliente para vender o consumir bonos."))

        for line in self.lines.filtered("is_bono_redemption"):
            line._resolve_missing_bono_balance()
            if not line.bono_balance_id:
                raise UserError(_("La línea de consumo de bono no tiene un saldo asociado."))
            if line.bono_balance_id.partner_id != self.partner_id:
                raise UserError(_("El bono seleccionado no pertenece al cliente del pedido."))
            if line.bono_balance_id.product_id != line.product_id:
                raise UserError(_("El bono consumido no coincide con el producto de la línea."))

    def _apply_bono_operations(self):
        self.ensure_one()
        if not self.lines:
            return

        positive_restore_lines = self.lines.filtered(
            lambda line: line.is_bono_redemption and line.qty < 0
        )
        positive_purchase_lines = self.lines.filtered(
            lambda line: line.product_id.is_bono and not line.is_bono_redemption and line.qty > 0
        )
        consume_lines = self.lines.filtered(
            lambda line: line.is_bono_redemption and line.qty > 0
        )
        refund_purchase_lines = self.lines.filtered(
            lambda line: line.product_id.is_bono and not line.is_bono_redemption and line.qty < 0
        )

        for line in positive_restore_lines:
            line._restore_bono_uses()
        for line in positive_purchase_lines:
            line._grant_bono_uses()
        for line in consume_lines:
            line._consume_bono_uses()
        for line in refund_purchase_lines:
            line._remove_granted_bono_uses()
