from odoo.http import request

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteCheckoutSimple(WebsiteSale):

    # Only these fields stay mandatory on /shop/address. Everything else
    # (street, city, zip, state, country, company, AFIP fields) becomes
    # optional, regardless of what the base module or l10n_ar_website_sale
    # add to the mandatory set.
    _ALLOWED_MANDATORY_FIELDS = {'name', 'phone', 'email'}

    def _get_mandatory_address_fields(self, country_sudo):
        mandatory_fields = super()._get_mandatory_address_fields(country_sudo)
        return mandatory_fields & self._ALLOWED_MANDATORY_FIELDS

    def _get_mandatory_delivery_address_fields(self, country_sudo):
        mandatory_fields = super()._get_mandatory_delivery_address_fields(country_sudo)
        # Keep email mandatory even when the delivery address is validated on
        # its own (use_delivery_as_billing=False), since the base module only
        # requires it through the billing branch.
        return (mandatory_fields & self._ALLOWED_MANDATORY_FIELDS) | {'email'}

    def _get_mandatory_billing_address_fields(self, country_sudo):
        mandatory_fields = super()._get_mandatory_billing_address_fields(country_sudo)
        return mandatory_fields & self._ALLOWED_MANDATORY_FIELDS

    def _get_ar_country(self):
        return request.env['res.country'].sudo().search([('code', '=', 'AR')], limit=1)

    def _prepare_address_form_values(self, *args, **kwargs):
        rendering_values = super()._prepare_address_form_values(*args, **kwargs)
        if not rendering_values.get('country'):
            ar_country = self._get_ar_country()
            if ar_country:
                rendering_values['country'] = ar_country
                rendering_values['country_states'] = ar_country.state_ids
        return rendering_values

    def _complete_address_values(
        self, address_values, address_type, use_delivery_as_billing, order_sudo
    ):
        super()._complete_address_values(
            address_values, address_type, use_delivery_as_billing, order_sudo
        )
        if not address_values.get('country_id'):
            ar_country = self._get_ar_country()
            if ar_country:
                address_values['country_id'] = ar_country.id
