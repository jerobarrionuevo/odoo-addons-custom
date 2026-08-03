from odoo.http import request, route

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleCheckoutNoPayment(WebsiteSale):

    def shop_confirm_order(self, **post):
        order_sudo = request.website.sale_get_order()

        if redirection := self._check_cart_and_addresses(order_sudo):
            return redirection

        order_sudo._recompute_taxes()
        order_sudo._recompute_prices()

        extra_step = request.website.viewref('website_sale.extra_info')
        if extra_step.active:
            return request.redirect("/shop/extra_info")

        # No payment provider is used: the order is left as a draft quotation
        # and the customer is sent to a thank-you page instead of /shop/payment.
        request.session['sale_last_order_id'] = order_sudo.id
        return request.redirect("/shop/thank-you")

    @route(['/shop/thank-you'], type='http', auth='public', website=True, sitemap=False)
    def shop_thank_you(self, **kwargs):
        sale_order_id = request.session.get('sale_last_order_id')
        order_sudo = sale_order_id and request.env['sale.order'].sudo().browse(sale_order_id).exists()
        if not order_sudo:
            return request.redirect('/shop')

        return request.render('website_sale_checkout_no_payment.thank_you', {
            'website_sale_order': order_sudo,
            'order': order_sudo,
        })
