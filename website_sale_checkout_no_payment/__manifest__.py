{
    "name": "Website Sale Checkout No Payment",
    "version": "18.0.1.0.0",
    "license": "LGPL-3",
    "category": "Website",
    "summary": (
        "Salta el paso de pago del checkout: tras completar la dirección, "
        "el pedido queda como cotizacion (draft) y el cliente ve una "
        "pantalla de gracias en vez de /shop/payment"
    ),
    "depends": ["website_sale"],
    "data": [
        "views/templates.xml",
    ],
    "installable": True,
}
