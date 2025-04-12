from rest_framework import serializers
from order.models import Cart, CartItem
from product.serializers import ProductSerializer
from rest_framework.serializers import ModelSerializer
from product.models import Product
from order.models import Order, OrderItem
from users.models import User

class SimpleProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price']

class CartItemSerializer(ModelSerializer):
    product = SimpleProductSerializer()
    total_price = serializers.SerializerMethodField(method_name='get_total_price')
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'total_price']

    def get_total_price(self, cart_item: CartItem):
        return cart_item.quantity * cart_item.product.price


class AddCartItemSerializer(ModelSerializer):
    product_id = serializers.IntegerField()
    class Meta:
        model = CartItem
        fields = ['id', 'product_id', 'quantity']

    def save(self, **kwargs):
        cart_id = self.context.get('cart_id')
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']
        try:
            cart_item = CartItem.objects.get(cart_id=cart_id, product_id=product_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(cart_id=cart_id, **self.validated_data)
            self.instance = cart_item
        return self.instance

    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError(f"Product with id {value} does not exits!")
        return value
    
class UpdateCartItemSerializer(ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']

class CartSerializer(ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField(method_name='get_total_price')
    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'total_price']
        read_only_fields = ['user']

    def get_total_price(self, cart: Cart):
        return sum([item.product.price*item.quantity for item in cart.items.all()])


class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()
    # cart_id = serializers.UUIDField(write_only=True)

    def validate_cart_id(self, cart_id):
        if not Cart.objects.filter(pk=cart_id).exists():
            raise serializers.ValidationError('No Cart found with this ID.')
        if not CartItem.objects.filter(cart_id = cart_id).exists():
            raise serializers.ValidationError('Cart is empty')
        return cart_id
    
    def create(self, validated_data):
        user_id = self.context['user_id']
        cart_id = validated_data['cart_id']

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
    
    # show something after creating order
    def to_representation(self, instance):
        return OrderSerializer(instance).data


class OrderItemSerializer(ModelSerializer):
    product = SimpleProductSerializer()
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price', 'total_price']

class OrderSerializer(ModelSerializer):
    items = OrderItemSerializer(many=True)
    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'total_price', 'created_at', 'items']

    