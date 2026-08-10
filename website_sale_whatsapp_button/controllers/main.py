from urllib.parse import quote

from odoo.http import request
from odoo.tools import formatLang

from odoo.addons.website_sale_checkout_no_payment.controllers.main import (
    WebsiteSaleCheckoutNoPayment,
)

WHATSAPP_PHONE = '5493476515524'


class WebsiteSaleWhatsappButton(WebsiteSaleCheckoutNoPayment):

    def shop_thank_you(self, **kwargs):
        sale_order_id = request.session.get('sale_last_order_id')
        order_sudo = sale_order_id and request.env['sale.order'].sudo().browse(sale_order_id).exists()
        if not order_sudo:
            return request.redirect('/shop')

        return request.render('website_sale_checkout_no_payment.thank_you', {
            'website_sale_order': order_sudo,
            'order': order_sudo,
            'whatsapp_url': self._get_whatsapp_url(order_sudo),
        })

    def _get_whatsapp_url(self, order_sudo):
        partner_name = (order_sudo.partner_id.name or '').strip()
        if partner_name:
            greeting = f"Hola! Soy {partner_name}, quiero coordinar mi pedido {order_sudo.name}."
        else:
            greeting = f"Hola! Quiero coordinar mi pedido {order_sudo.name}."

        product_lines = "\n".join(
            f"{line.product_uom_qty:g}x {line.product_id.display_name}"
            for line in order_sudo.order_line
            if not line.display_type and not line.is_delivery
        )
        total = formatLang(
            order_sudo.env, order_sudo.amount_total, currency_obj=order_sudo.currency_id
        )

        message = f"{greeting}\n\nProductos:\n{product_lines}\n\nTotal: {total}"
        return f"https://wa.me/{WHATSAPP_PHONE}?text={quote(message, safe='')}"
