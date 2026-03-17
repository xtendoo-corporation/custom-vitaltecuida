# Vitaltecuida Bonos

Módulo para gestionar bonos por usos en Odoo 18.

## Qué hace

- Configura productos bono directamente desde la ficha del producto marcando `Bono` junto a `Punto de venta`.
- Marca esos productos con `is_bono` y configura `n_uses`.
- Acumula usos por combinación `cliente + producto bono`.
- Añade un smart button en contactos para ver bonos y movimientos.
- Permite consumir bonos desde POS con un botón `Usar bono`.
- Refleja el consumo como línea visible del pedido y del ticket.

## Diseño funcional

- El propio producto define si es un bono.
- El saldo real vive en `vitaltecuida.bono.balance`.
- Cada compra incrementa usos.
- Cada consumo en POS descuenta usos al validar el pedido.
- Si un mismo cliente vuelve a comprar el mismo bono, los usos se acumulan.

## Notas de esta primera versión

- El consumo en POS añade una línea a precio 0 para dejar trazabilidad en el ticket.
- El botón de POS exige cliente seleccionado.
- La validación fuerte del saldo se hace en backend al confirmar el pedido.
