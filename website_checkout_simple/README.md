# website_checkout_simple

**Versión:** 18.0.3.0.0 · Odoo 18 · LGPL-3

## Qué hace

Checkout reducido **solo para el visitante sin cuenta** (`website.is_public_user()`); el cliente
logueado conserva el flujo estándar de Odoo.

- **Pantalla 1, `/shop/contact`** (ruta propia): nombre, teléfono y correo. Sin dirección.
- **`/shop/checkout`**: "Elija un método de entrega" arriba de "Dirección de entrega".
- **`/shop/address`**: solo dirección. El visitante que todavía no cargó su contacto es desviado
  a `/shop/contact`.
- El contacto nuevo sale con Consumidor Final, DNI y Argentina; empresa, campos AFIP y país
  quedan ocultos.

## Dependencias

`website_sale`, `l10n_ar_website_sale`. No depende de `website_sale_checkout_no_payment` ni de
`website_sale_whatsapp_button`, aunque en el flujo completo se usan los tres (ver el README de
cada uno).

## Configuración

**`PUBLIC_CHECKOUT_EMAIL_MODE`**, al principio de `controllers/main.py`:

| Valor | Efecto |
|---|---|
| `'required'` | El correo se muestra y es obligatorio (lo valida el servidor) |
| `'optional'` | Se muestra con "(opcional)" y puede quedar vacío — **valor actual** |
| `'hidden'` | No se muestra ni se pide |

Se lee **al cargar el módulo**: cambiarlo implica editar el archivo y **reiniciar Odoo**. Un valor
inválido corta el arranque con un error.

## Datos de la base que necesita

Nada de esto viaja con el código:

- **`ir.default` de `res.partner`** para la compañía del sitio: responsabilidad AFIP (Consumidor
  Final), tipo de identificación (DNI) y país (Argentina). Se leen con `user_id=False`. Si falta
  alguno, se registra un `WARNING` y no se inyecta; si faltan AFIP o DNI, `l10n_ar_website_sale`
  puede bloquear el formulario con su aviso rojo. La provincia **no** tiene default.
- **Partner del usuario público, archivado.** Si está activo, los contactos nuevos quedan
  colgados como hijos de ese partner (`parent_id`). En dev es el id 13
  (`public-user@company-2.com`); verificarlo por nombre y login en cada entorno.
- **Orden de los carriers (sequence).** "Retiro en Local" con sequence menor que "Envío a
  coordinar" hace que Retiro venga preseleccionado. Es un dato, no código. Se identifican por
  nombre en `es_AR` (el nombre en `en_US` de "Envío a coordinar" es "Standard delivery").
- **`account_on_checkout`** distinto de `disabled` (hoy `optional`) para que aparezca el recuadro
  "¿Ya tiene una cuenta?".

## Qué toca

- **Controlador:** ruta `/shop/contact`; sobrescribe `shop_address`, `_check_addresses`,
  `_get_mandatory_delivery_address_fields`, `_get_mandatory_billing_address_fields`,
  `_validate_address_values` y `_prepare_address_form_values`.
- **Modelo:** `website._display_partner_b2b_fields` (oculta empresa y AFIP solo al visitante).
- **Vistas** (`views/address_templates.xml`), sin `position="replace"` porque `address.js`
  referencia los campos: heredan `website_sale.address`, `website_sale.checkout`,
  `website_sale.address_kanban` y `website_sale.address_row`.

## Notas

- Las copias de `t-call` en `website_sale.checkout` hay que actualizarlas si el core cambia esa
  plantilla.
- El logueado vuelve a ver CUIT/AFIP (el módulo anterior los ocultaba a todos): un usuario
  interno cuyo contacto cuelga de una empresa con facturas posteadas no puede editar el `vat` y
  podría quedar bloqueado en `/shop/address`. Riesgo **deducido**, no probado con el formulario
  real.

## Documentación

Diseño completo y checklist de deploy: `docs/11-modulo-checkout-reducido.md` (§12 y §11.1) del
repo del sistema,
<https://github.com/jerobarrionuevo/del-litoral-mates-prod/blob/main/docs/11-modulo-checkout-reducido.md>.
