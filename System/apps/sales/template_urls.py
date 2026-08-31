"""
Template URLs for Sales module
"""
from django.urls import path
from . import template_views

app_name = 'sales'

urlpatterns = [
    path('', template_views.sales_list, name='list'),
    path('orders/', template_views.sales_orders_page, name='orders_admin'),
    path('orders/<int:order_id>/edit/', template_views.order_edit_admin, name='order_edit_admin'),
    path('orders/<int:order_id>/delete/', template_views.order_delete_admin, name='order_delete_admin'),
    path('customer/create/', template_views.customer_create, name='customer_create'),
    path('customer/<int:customer_id>/delete/', template_views.customer_delete, name='customer_delete'),
    path('product/create/', template_views.product_create, name='product_create'),
    path('product/<int:product_id>/edit/', template_views.product_edit, name='product_edit'),
    path('product/<int:product_id>/delete/', template_views.product_delete, name='product_delete'),
    path('order/create/', template_views.order_create, name='order_create'),
    path('order/<int:order_id>/status/', template_views.order_status_update, name='order_status_update'),
    path('order/<int:order_id>/payment/', template_views.order_payment_update, name='order_payment_update'),
    path('order/<int:order_id>/receipt/', template_views.order_receipt_view, name='order_receipt_view'),
    path('order/<int:order_id>/delete/', template_views.order_delete, name='order_delete'),
    path('delivery/create/', template_views.delivery_create, name='delivery_create'),
    path('deliveries/', template_views.delivery_list_page, name='delivery_list'),
    path('deliveries/track/', template_views.delivery_track_page, name='delivery_track'),
    path('deliveries/logs/', template_views.delivery_logs_page, name='delivery_logs'),
    path('deliveries/<int:delivery_id>/status/', template_views.delivery_status_update, name='delivery_status_update'),
    path('deliveries/<int:delivery_id>/edit/', template_views.delivery_edit, name='delivery_edit'),
    path('deliveries/<int:delivery_id>/delete/', template_views.delivery_delete, name='delivery_delete'),
    path('riders/', template_views.rider_list_page, name='rider_list'),
    path('riders/create/', template_views.rider_create, name='rider_create'),
    path('riders/<int:rider_id>/status/', template_views.rider_status_update, name='rider_status_update'),
    path('riders/<int:rider_id>/edit/', template_views.rider_edit, name='rider_edit'),
    path('riders/<int:rider_id>/delete/', template_views.rider_delete, name='rider_delete'),
    path('rider/portal/', template_views.rider_portal, name='rider_portal'),
    path('rider/delivery/<int:delivery_id>/action/', template_views.rider_delivery_action, name='rider_delivery_action'),
    path('rider/status-toggle/', template_views.rider_portal_duty_toggle, name='rider_duty_toggle'),
    path('market/', template_views.customer_portal, name='customer_portal'),
    path('market/orders/', template_views.customer_orders_page, name='customer_orders_page'),
    path('market/orders/<int:order_id>/update-quantity/', template_views.customer_order_update_quantity, name='customer_order_update_quantity'),
    path('market/orders/<int:order_id>/delete/', template_views.customer_order_delete, name='customer_order_delete'),

    path('market/account/', template_views.customer_account_page, name='customer_account_page'),
    path('market/account/location/', template_views.customer_location_update, name='customer_location_update'),
    path('market/cart/', template_views.customer_cart_page, name='customer_cart_page'),
    path('market/order/', template_views.customer_order_create, name='customer_order_create'),
    path('market/checkout/submit/', template_views.customer_checkout_submit, name='customer_checkout_submit'),
    path('market/payment/success/', template_views.paymongo_payment_success, name='paymongo_success'),
    path('settings/payment/', template_views.payment_settings_update, name='payment_settings_update'),
]

