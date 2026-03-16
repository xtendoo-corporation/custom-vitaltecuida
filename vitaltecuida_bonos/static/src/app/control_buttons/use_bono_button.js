/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { makeAwaitable } from "@point_of_sale/app/store/make_awaitable_dialog";
import { SelectionPopup } from "@point_of_sale/app/utils/input_popups/selection_popup";
import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";

function getRelationId(value) {
    if (Array.isArray(value)) {
        return value[0];
    }
    if (value && typeof value === "object") {
        return value.id;
    }
    return value || false;
}

function getRelationName(value) {
    if (Array.isArray(value)) {
        return value[1];
    }
    if (value && typeof value === "object") {
        return value.display_name || value.name || false;
    }
    return false;
}

function getBalanceProduct(pos, balance) {
    const productId = getRelationId(balance.product_id);
    return productId ? pos.models["product.product"].get(productId) : null;
}

function getBalanceProductName(pos, balance) {
    return (
        balance.product_display_name ||
        getRelationName(balance.product_id) ||
        getBalanceProduct(pos, balance)?.display_name ||
        getBalanceProduct(pos, balance)?.name ||
        _t("Bono sin nombre")
    );
}

patch(ControlButtons.prototype, {
    async clickUseBono() {
        const order = this.pos.get_order();
        const partner = order?.get_partner?.();
        if (!partner) {
            this.notification.add(_t("Selecciona primero un cliente para usar un bono."), {
                type: "warning",
            });
            return;
        }

        const balances = await this.pos.data.searchRead(
            "vitaltecuida.bono.balance",
            [
                ["partner_id", "=", partner.id],
                ["remaining_uses", ">", 0],
            ],
            ["id", "product_id", "product_display_name", "remaining_uses"]
        );

        const availableBalances = balances
            .map((balance) => {
                const pendingUses = order.lines
                    .filter((line) => line.is_bono_redemption)
                    .filter((line) => {
                        const balanceId = line.bono_balance_id?.id || line.bono_balance_id;
                        return balanceId === balance.id;
                    })
                    .reduce((acc, line) => acc + Math.abs(Number(line.qty || 0)), 0);
                return {
                    ...balance,
                    remaining_after_pending: balance.remaining_uses - pendingUses,
                };
            })
            .filter((balance) => balance.remaining_after_pending > 0);

        if (!availableBalances.length) {
            this.notification.add(_t("El cliente no tiene bonos disponibles para consumir."), {
                type: "warning",
            });
            return;
        }

        const selectedBalance = await makeAwaitable(this.dialog, SelectionPopup, {
            title: _t("Selecciona el bono a consumir"),
            list: availableBalances.map((balance) => ({
                id: balance.id,
                label: `${getBalanceProductName(this.pos, balance)} · ${balance.remaining_after_pending} uso(s) disponible(s)`,
                item: balance,
            })),
        });

        if (!selectedBalance) {
            return;
        }

        const product = getBalanceProduct(this.pos, selectedBalance);
        if (!product) {
            this.notification.add(_t("El producto del bono no está cargado en este TPV."), {
                type: "danger",
            });
            return;
        }

        const productName = getBalanceProductName(this.pos, selectedBalance);
        await this.pos.addLineToCurrentOrder(
            {
                product_id: product,
                qty: 1,
                price_unit: 0,
                is_bono_redemption: true,
                bono_balance_id: selectedBalance.id,
                full_product_name: productName,
                _bono_product_display_name: productName,
                customer_note: _t("Consumo de bono"),
            },
            {},
            false
        );
    },
});
