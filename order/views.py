from django.shortcuts import redirect
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from order.serializers import CartSerializer, CartItemSerializer, AddCartItemSerializer, UpdateCartItemSerializer, OrderSerializer, CreateOrderSerializer, UpdateOrderSerializer, EmptySerializer
from order.models import Cart, CartItem, Order, OrderItem
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from order.permissions import IsCartOwnerUser
from rest_framework.decorators import action
from order.services import OrderService
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from sslcommerz_lib import SSLCOMMERZ 
from django.conf import settings as django_settings
from decouple import config
from rest_framework.views import APIView


# not inherite ListModelMixins
class CartViewSets(CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        existing_cart = Cart.objects.filter(user=request.user).first()
        if existing_cart:
            serializer = self.get_serializer(existing_cart)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return super().create(request, *args, **kwargs)

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Cart.objects.none()

        return Cart.objects.prefetch_related('items__product').filter(user=self.request.user)

class CartItemViewSets(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = [IsCartOwnerUser]

    def get_queryset(self):
        return CartItem.objects.select_related('product').filter(cart_id=self.kwargs.get('cart_pk'))

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        return CartItemSerializer
    
    def get_serializer_context(self):
        return {'cart_id':self.kwargs.get('cart_pk')}


class OrderViewSets(ModelViewSet):
    http_method_names = ['get', 'post', 'delete', 'patch', 'head', 'options']

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        order = self.get_object()
        OrderService.cancel_order(order=order, user=request.user)
        return Response({'status': 'Order canceled'})

    def get_serializer_class(self):
        if self.action == 'cancel':
            return EmptySerializer
        if self.action == 'create':
            return CreateOrderSerializer
        if self.action == 'partial_update':
            return UpdateOrderSerializer
        return OrderSerializer
    
    def get_permissions(self):
        if self.action in ['partial_update', 'destroy']:
            return [IsAdminUser(),]
        return [IsAuthenticated()]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Order.objects.none()

        if self.request.user.is_staff:
            return Order.objects.prefetch_related('items__product').all()
        return Order.objects.prefetch_related('items__product').filter(user=self.request.user)
    
    def get_serializer_context(self):
        return {'user_id':self.request.user.id, 'user':self.request.user}
    
    
    
# payment gateway
@api_view(['POST'])
def initiate_payment(request):
    user = request.user
    amount = request.data.get('amount')
    order_id = request.data.get('order_id')
    num_itmes = request.data.get('num_items')
    
    settings = { 'store_id': {config('STORE_NAME')}, 'store_pass': {config('STORE_PASSWORD')}, 'issandbox': True }
    
    sslcz = SSLCOMMERZ(settings)
    post_body = {}
    post_body['total_amount'] = amount
    post_body['currency'] = "BDT"
    post_body['tran_id'] = f"trn_{order_id}"
    post_body['success_url'] = f"{django_settings.BACK_END_HOST}api/v1/payment/success/"
    post_body['fail_url'] = f"{django_settings.BACK_END_HOST}api/v1/payment/fail/"
    post_body['cancel_url'] = F"{django_settings.BACK_END_HOST}api/v1/payment/cancel/"
    post_body['emi_option'] = 0
    post_body['cus_name'] = f"{user.first_name} {user.last_name}"
    post_body['cus_email'] = user.email
    post_body['cus_phone'] = user.phone_number
    post_body['cus_add1'] = user.address
    post_body['cus_city'] = "Dhaka"
    post_body['cus_country'] = "Bangladesh"
    post_body['shipping_method'] = "NO"
    post_body['multi_card_name'] = ""
    post_body['num_of_item'] = num_itmes
    post_body['product_name'] = "E-comarce Product"
    post_body['product_category'] = "General"
    post_body['product_profile'] = "general"


    response = sslcz.createSession(post_body) # API response
    
    # Need to redirect user to response['GatewayPageURL']
    if response.get('status') == 'SUCCESS':
        return Response({'payment_url': response['GatewayPageURL']})
    return Response({'error': 'Payment initiation failed!'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def success_payment(request):
    order_id = request.data.get('tran_id').split('_')[1]
    order = Order.objects.get(id=order_id)
    order.status = 'R'
    order.save()
    return redirect(f"{django_settings.FRONT_END_HOST}dashboard/orders/")

@api_view(['POST'])
def fail_payment(request):
    return redirect(f"{django_settings.FRONT_END_HOST}dashboard/orders/")
    
@api_view(['POST'])
def cancel_payment(request):
    return redirect(f"{django_settings.FRONT_END_HOST}dashboard/orders/")


class HasOrderedProduct(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, product_id):
        has_ordered = OrderItem.objects.filter(order__user = request.user, product_id = product_id).exists()
        return Response({'hasOrdered':has_ordered})
