# website_sale_checkout_no_payment

**Versión:** 18.0.1.0.0 · Odoo 18 · LGPL-3

## Qué hace

Salta el paso de pago del checkout de `website_sale`. Al confirmar, el pedido queda como
cotización (borrador) y el cliente ve una pantalla de gracias en vez de `/shop/payment`.

- Sobrescribe `shop_confirm_order`: tras validar carrito y direcciones, guarda el pedido en la
  sesión (`sale_last_order_id`) y redirige a `/shop/thank-you`. Si el paso opcional
  `website_sale.extra_info` está activo, redirige primero ahí.
- Agrega la ruta `/shop/thank-you` y su template `thank_you` ("¡Gracias por tu reserva!", con el
  número de reserva).
- Cambia el texto del botón de la pantalla de dirección del visitante con carrito anónimo a
  **"Continuar"** (antes decía "Finalizar pedido").
- El comportamiento **no distingue** visitante de logueado: aplica a todos.

## Dependencias

`website_sale`. Es la base de `website_sale_whatsapp_button`, que depende de este módulo.

## Configuración

Ninguna.

## Datos de la base que necesita

Ninguno. No hay una pasarela de pago configurada ni se necesita una.

## Notas

- Al arrancar Odoo aparece un `WARNING` conocido: `shop_confirm_order` es una sobrescritura sin
  `@route()`, así que Odoo hereda la ruta del padre y avisa. Funciona.
- Se instala antes que `website_sale_whatsapp_button`, que depende de este módulo.

## Documentación

Diseño completo y checklist de deploy: `docs/11-modulo-checkout-reducido.md` (§11.1 y §12) del
repo del sistema,
<https://github.com/jerobarrionuevo/del-litoral-mates-prod/blob/main/docs/11-modulo-checkout-reducido.md>.
