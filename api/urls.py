from django.urls import path, include
from product.views import ProductViewsets, CategoryViewsets, ReviewViewsets, ProductImageViewSet
from rest_framework_nested import routers
from order.views import CartViewSets, CartItemViewSets, OrderViewSets, initiate_payment, success_payment, fail_payment, cancel_payment, HasOrderedProduct
from product.views import ReviewByUserViewSets

router = routers.DefaultRouter()
router.register('products', ProductViewsets, basename='products')
router.register('categories', CategoryViewsets)
router.register('carts', CartViewSets, basename='carts')
router.register('orders', OrderViewSets, basename='orders')
router.register('reviews', ReviewByUserViewSets, basename='reviews')

# lookup_field(views) vs lookup(nested route)
product_router = routers.NestedDefaultRouter(router, 'products', lookup='product') # pk = product_pk/ product_id
product_router.register('reviews', ReviewViewsets, basename='product-review')
product_router.register('images', ProductImageViewSet, basename='product-image')

cart_router = routers.NestedDefaultRouter(router, 'carts', lookup='cart') #its for cart_pk
cart_router.register('items', CartItemViewSets, basename='cart-items')

# urlpatterns = router.urls

urlpatterns = [
    path('', include(router.urls)),
    path('', include(product_router.urls)),
    path('', include(cart_router.urls)),
    path('orders/has-ordered/<int:product_id>', HasOrderedProduct.as_view()),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('payment/initiate/', initiate_payment, name='initiate_payment'),
    path('payment/success/', success_payment, name='success_payment'),
    path('payment/fail/', fail_payment, name='fail_payment'),
    path('payment/cancel/', cancel_payment, name='cancel_payment'),
]