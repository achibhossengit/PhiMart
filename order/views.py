from django.shortcuts import render
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from order.serializers import CartSerializer, CartItemSerializer, AddCartItemSerializer, UpdateCartItemSerializer, OrderSerializer, CreateOrderSerializer, UpdateOrderSerializer, EmptySerializer
from order.models import Cart, CartItem, Order, OrderItem
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from order.permissions import IsCartOwnerUser
from rest_framework.decorators import action
from order.services import OrderService
from rest_framework.response import Response

# not inherite ListModelMixins
class CartViewSets(CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

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
    