from order.models import Cart, Order, OrderItem
from users.models import User
from django.db import transaction

class OrderServices:
    @staticmethod
    def create_order(cart_id, user_id):
        with transaction.atomic():
            user = User.objects.get(pk=user_id)
            cart = Cart.objects.get(pk=cart_id)
            cart_items = cart.items.select_related('product').all()
            total_price = sum([item.product.price * item.quantity for item in cart_items])
            order = Order.objects.create(user=user, total_price=total_price)

            order_items = [
                OrderItem(
                    order = order,
                    product = item.product,
                    quantity = item.quantity,
                    price = item.product.price,
                    total_price = item.product.price * item.quantity
                )
                for item in cart_items
            ]
            # [<OrderItem(1)>, <OrderItem(2),..>]
            OrderItem.objects.bulk_create(order_items)
            cart.delete()

            return order
    
