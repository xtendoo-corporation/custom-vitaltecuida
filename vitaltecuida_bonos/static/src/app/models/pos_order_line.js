/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { PosOrderline } from "@point_of_sale/app/models/pos_order_line";

function getBonoBaseName(line) {
    return (
        line._bono_product_display_name ||
        line.product_id?.display_name ||
        line.product_id?.name ||
        line.full_product_name ||
        _t("Bono sin nombre")
    );
}

function getBonoLineName(line) {
    const uses = Math.abs(Number(line.qty || 0)) || 1;
    return `${getBonoBaseName(line)} - ${uses} uso${uses !== 1 ? "s" : ""}`;
}

patch(PosOrderline.prototype, {
    setup(vals) {
        super.setup(...arguments);
        this.is_bono_redemption = Boolean(vals.is_bono_redemption ?? this.is_bono_redemption);
        if (Object.prototype.hasOwnProperty.call(vals, "bono_balance_id")) {
            this.bono_balance_id = vals.bono_balance_id;
        }
        if (this.is_bono_redemption) {
            this.full_product_name = getBonoLineName(this);
        }
    },

    set_quantity(quantity, keep_price) {
        const result = super.set_quantity(...arguments);
        if (this.is_bono_redemption) {
            this.full_product_name = getBonoLineName(this);
        }
        return result;
    },

    can_be_merged_with(orderline) {
        if (this.is_bono_redemption || orderline.is_bono_redemption) {
            return false;
        }
        return super.can_be_merged_with(orderline);
    },

    getDisplayData() {
        const data = super.getDisplayData();
        if (this.is_bono_redemption) {
            data.productName = getBonoLineName(this);
            data.customerNote = this.get_customer_note?.() || _t("Consumo de bono");
        }
        return data;
    },
});
