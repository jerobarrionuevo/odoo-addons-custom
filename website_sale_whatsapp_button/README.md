# website_sale_whatsapp_button

**Versión:** 18.0.2.1.0 · Odoo 18 · LGPL-3

## Qué hace

Agrega un botón verde **"Coordinar por WhatsApp"** a la pantalla de gracias del checkout
(`/shop/thank-you`). El botón abre WhatsApp con un mensaje prellenado para coordinar pago y
entrega de una reserva que quedó como cotización.

- El mensaje incluye el nombre del cliente, el número de pedido, la lista de productos
  (sin las líneas de entrega) y el total.
- **No confirma ni modifica el pedido:** solo arma el enlace `https://wa.me/<número>?text=…`.
- Versiones 1.x (la que hoy está instalada en producción) reemplazaban el botón "Finalizar
  compra" del carrito; esta versión cambió de rol y vive en la pantalla de gracias.

## Dependencias

`website_sale_checkout_no_payment` (aporta la ruta y el template `thank_you` que este módulo
extiende).

## Configuración

El número de destino está fijo en el código: constante `WHATSAPP_PHONE`
(`controllers/main.py`, hoy `5493476515524`). Cambiarlo implica editar el archivo y reiniciar
Odoo.

## Datos de la base que necesita

Ninguno.

## Notas

- Al pasar de 1.x a 2.x hay que instalar antes `website_sale_checkout_no_payment` y recién
  después actualizar este módulo (`-u`). Reiniciar Odoo con los archivos nuevos sin haber hecho
  eso rompe la pantalla de gracias.
- Aviso conocido en el log: `shop_thank_you` se sobrescribe sin `@route()` (Odoo hereda la ruta
  del padre y avisa). Funciona.

## Documentación

Diseño completo y checklist de deploy: `docs/11-modulo-checkout-reducido.md` (§11.1 y §12) del
repo del sistema,
<https://github.com/jerobarrionuevo/del-litoral-mates-prod/blob/main/docs/11-modulo-checkout-reducido.md>.
Historia del módulo: `docs/10-modulo-whatsapp-button.md`.
