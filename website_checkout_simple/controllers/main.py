import logging

from odoo.http import request, route

from odoo.addons.website_sale.controllers.main import WebsiteSale

_logger = logging.getLogger(__name__)

# ===== EMAIL EN EL CHECKOUT DEL VISITANTE SIN CUENTA — ÚNICO LUGAR PARA CAMBIARLO =====
#   'required' -> se muestra y es obligatorio (lo valida el servidor)
#   'optional' -> se muestra, marcado como opcional, y puede quedar vacío
#   'hidden'   -> no se muestra ni se pide (el form no manda el campo).
# Solo rige para el visitante sin cuenta; el cliente logueado usa el flujo estándar.
PUBLIC_CHECKOUT_EMAIL_MODE = 'optional'
# =====================================================================================

if PUBLIC_CHECKOUT_EMAIL_MODE not in ('required', 'optional', 'hidden'):
    raise ValueError(
        "PUBLIC_CHECKOUT_EMAIL_MODE inválido: %r (usar 'required', 'optional' o 'hidden')"
        % PUBLIC_CHECKOUT_EMAIL_MODE
    )

# Campos que el contacto nuevo toma de los valores por defecto del sistema (ir.default).
# La provincia queda afuera a propósito: no se completa por defecto.
_SYSTEM_DEFAULT_FIELDS = (
    'l10n_ar_afip_responsibility_type_id',  # Consumidor Final
    'l10n_latam_identification_type_id',    # DNI
    'country_id',                           # Argentina
)


class WebsiteCheckoutSimple(WebsiteSale):
    """Formulario de dirección reducido, solo para el visitante sin cuenta.

    Todo lo que sigue se aplica únicamente si `_is_public_checkout()` es verdadero.
    Para un cliente logueado cada método cae en `super()` y el flujo es el de Odoo.
    """

    def _is_public_checkout(self):
        return request.website.is_public_user()

    # ------------------------------------------------------------------
    # Pantalla de contacto (/shop/contact) y desvíos del visitante
    # ------------------------------------------------------------------

    @route('/shop/contact', type='http', methods=['GET'], auth='public', website=True, sitemap=False)
    def shop_contact(self, **_query_params):
        """Paso 1 del visitante sin cuenta: nombre, teléfono y correo (sin dirección).

        Es el mismo formulario y el mismo submit del core (`/shop/address/submit`, fijo en
        address.js), con las direcciones ocultas y `callback` hacia el checkout. Si el
        visitante vuelve a editar, se pasa el contacto del pedido para actualizar el mismo
        partner en vez de crear otro.
        """
        if not self._is_public_checkout():
            return request.redirect('/shop/address')
        order_sudo = request.website.sale_get_order()
        partner_id = None
        if order_sudo and not order_sudo._is_anonymous_cart():
            partner_id = order_sudo.partner_id.id
        # `super()` salta el desvío de `shop_address` de más abajo (si no, redirigiría acá).
        return super().shop_address(
            partner_id=partner_id,
            address_type='billing',
            use_delivery_as_billing='false',
            callback='/shop/checkout',
            contact_step=True,
        )

    @route()
    def shop_address(self, *args, **kwargs):
        # /shop/address queda solo para dirección: el visitante que todavía no cargó su
        # contacto va a /shop/contact.
        if self._is_public_checkout():
            order_sudo = request.website.sale_get_order()
            if order_sudo and order_sudo._is_anonymous_cart():
                return request.redirect('/shop/contact')
        return super().shop_address(*args, **kwargs)

    def _check_addresses(self, order_sudo):
        # Sin contacto, el core manda a /shop/address (main.py _check_addresses); al visitante
        # se lo manda a /shop/contact. Lo demás (dirección de entrega incompleta, etc.) sigue igual.
        if self._is_public_checkout() and order_sudo._is_anonymous_cart():
            return request.redirect('/shop/contact')
        return super()._check_addresses(order_sudo)

    # ------------------------------------------------------------------
    # Campos obligatorios
    # ------------------------------------------------------------------

    def _public_checkout_mandatory_fields(self):
        mandatory = {'name', 'phone'}
        if PUBLIC_CHECKOUT_EMAIL_MODE == 'required':
            mandatory.add('email')
        return mandatory

    # Se devuelve el conjunto completo sin llamar a super(): el core y
    # l10n_ar_website_sale agregan calle, ciudad, provincia, CP, VAT y los campos AFIP,
    # y ninguno de esos debe ser obligatorio para este visitante.
    def _get_mandatory_delivery_address_fields(self, country_sudo):
        if self._is_public_checkout():
            return self._public_checkout_mandatory_fields()
        return super()._get_mandatory_delivery_address_fields(country_sudo)

    def _get_mandatory_billing_address_fields(self, country_sudo):
        if self._is_public_checkout():
            return self._public_checkout_mandatory_fields()
        return super()._get_mandatory_billing_address_fields(country_sudo)

    # ------------------------------------------------------------------
    # Valores por defecto del sistema (ir.default)
    # ------------------------------------------------------------------

    def _get_company_defaults(self):
        """Lee de `ir.default` los valores por defecto de res.partner de la compañía
        del sitio, sin depender del usuario que crea el contacto.

        Se leen directamente (`user_id=False` = vale para todos los usuarios) y no se
        redefinen. Si la compañía no tiene un default propio, se usa el global.
        """
        company = request.website.sudo().company_id
        IrDefault = request.env['ir.default'].sudo()
        values = {}
        for fname in _SYSTEM_DEFAULT_FIELDS:
            value = IrDefault._get('res.partner', fname, user_id=False, company_id=company.id)
            if value is None:
                value = IrDefault._get('res.partner', fname, user_id=False, company_id=False)
            if value:
                values[fname] = value
            else:
                _logger.warning(
                    "Sin valor por defecto de res.partner.%s para la compañía %s", fname, company.id
                )
        return values

    def _validate_address_values(self, address_values, partner_sudo, address_type, *args, **kwargs):
        # Los defaults de ir.default recién se aplican en el create, que ocurre DESPUÉS de
        # validar. l10n_ar_website_sale bloquea con el aviso "Please go to 'My Account'..." si
        # la responsabilidad AFIP y el tipo de identificación no vienen en el POST, así que se
        # inyectan acá, antes de la validación. Es el mismo diccionario que luego usa el create.
        if self._is_public_checkout():
            defaults = self._get_company_defaults()
            # País: el campo está oculto, siempre se usa el del sistema.
            if 'country_id' in defaults:
                address_values['country_id'] = defaults['country_id']
            # Provincia: sin default. Si el form la manda vacía (o no la manda) queda vacía;
            # la clave explícita evita que el create le aplique el default de ir.default.
            address_values.setdefault('state_id', False)
            # Contacto nuevo: Consumidor Final + DNI.
            if not partner_sudo:
                for fname in ('l10n_ar_afip_responsibility_type_id', 'l10n_latam_identification_type_id'):
                    if not address_values.get(fname) and fname in defaults:
                        address_values[fname] = defaults[fname]
        return super()._validate_address_values(
            address_values, partner_sudo, address_type, *args, **kwargs
        )

    # ------------------------------------------------------------------
    # Valores para renderizar el formulario
    # ------------------------------------------------------------------

    def _prepare_address_form_values(self, *args, **kwargs):
        rendering_values = super()._prepare_address_form_values(*args, **kwargs)
        is_public = self._is_public_checkout()
        rendering_values['is_public_checkout'] = is_public
        # Paso de contacto (/shop/contact) o paso de dirección (/shop/address): el template
        # oculta con d-none lo que no corresponde, sin sacarlo del DOM.
        contact_step = bool(is_public and kwargs.get('contact_step'))
        rendering_values['is_contact_step'] = contact_step
        rendering_values['is_address_step'] = is_public and not contact_step
        rendering_values['email_mode'] = PUBLIC_CHECKOUT_EMAIL_MODE
        if is_public:
            country_id = self._get_company_defaults().get('country_id')
            country = request.env['res.country'].sudo().browse(country_id).exists()
            if country:
                address_fields = country.get_address_fields()
                rendering_values.update({
                    'country': country,
                    'country_states': country.state_ids,
                    'zip_before_city': (
                        'zip' in address_fields
                        and address_fields.index('zip') < address_fields.index('city')
                    ),
                })
        return rendering_values
