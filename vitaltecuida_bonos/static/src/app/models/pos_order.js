/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { PosOrder } from "@point_of_sale/app/models/pos_order";

function partnerHasChanged(currentPartner, newPartner) {
    const currentId = currentPartner?.id || false;
    const newId = newPartner?.id || false;
    return currentId !== newId;
}

patch(PosOrder.prototype, {
    hasBonoRedemptionLines() {
        return this.lines.some((line) => line.is_bono_redemption);
    },

    set_partner(partner) {
        if (
            this.hasBonoRedemptionLines() &&
            partnerHasChanged(this.get_partner(), partner)
        ) {
            return false;
        }
        return super.set_partner(partner);
    },
});

