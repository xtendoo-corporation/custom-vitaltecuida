/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { PosStore } from "@point_of_sale/app/store/pos_store";

patch(PosStore.prototype, {
    async selectPartner() {
        const currentOrder = this.get_order();
        if (currentOrder?.hasBonoRedemptionLines?.()) {
            this.dialog.add(AlertDialog, {
                title: _t("No se puede cambiar el cliente"),
                body: _t(
                    "Este pedido ya tiene líneas de consumo de bono. Crea un nuevo pedido si necesitas trabajar con otro cliente."
                ),
            });
            return currentOrder.get_partner();
        }
        return await super.selectPartner(...arguments);
    },

    async postSyncAllOrders(orders) {
        await super.postSyncAllOrders(...arguments);

        const partnerIds = [...new Set(
            (orders || [])
                .map((order) => order.partner_id?.id)
                .filter(Boolean)
        )];

        if (!partnerIds.length) {
            return;
        }

        const payload = await this.data.call(
            "vitaltecuida.bono.balance",
            "get_pos_ui_data",
            [partnerIds]
        );

        const balanceModel = this.models["vitaltecuida.bono.balance"];
        const recordsToRemove = balanceModel.readMany(payload.remove_ids || []).filter(Boolean);
        if (recordsToRemove.length) {
            balanceModel.deleteMany(recordsToRemove, { silent: true });
        }

        if (payload.upsert?.length) {
            this.models.loadData(
                { "vitaltecuida.bono.balance": payload.upsert },
                ["vitaltecuida.bono.balance"],
                false
            );
        }
    },
});

