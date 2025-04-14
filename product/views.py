from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view
from product.models import Product, Category, Review, ProductImage
from django.db.models import Count
from product.serializers import ProductSerializer, CategorySerializer, ReviewSerializer, ProductImageSerializer
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from product.filters import ProductFilter
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from product.paginations import CustomPageNumberPagination
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly
from api.permissions import IsAdminOrReadonly, FullDjangoModelPermission
from product.permissions import IsReviewAuthorOrReadonly
from drf_yasg.utils import swagger_auto_schema



class ProductViewsets(ModelViewSet):
    """
    API endpoint for manage product.
    - Allow authenticated admin to create, update and delete product
    - Allow anyone to access product list
    - Support serching by name, description and category
    - Support ordering by price and update_at
    """

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description', 'category__name']
    ordering_fields = ['price', 'updated_at']
    pagination_class = CustomPageNumberPagination
    permission_classes = [IsAdminOrReadonly]


    @swagger_auto_schema(
        operation_summary='Update product items ',
        operation_description='Anyone can access this endpoint',
        request_body=ProductSerializer,
        responses={
            201: ProductSerializer,
            400: 'Bad Request'
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """ Only admin can create a product"""
        return super().create(request, *args, **kwargs)

class ProductImageViewSet(ModelViewSet):
    serializer_class = ProductImageSerializer
    permission_classes = [IsAdminOrReadonly]
    
    def get_queryset(self):
        return ProductImage.objects.filter(product_id=self.kwargs.get('product_pk'))
    
    def perform_create(self, serializer):
        serializer.save(product_id=self.kwargs.get('product_pk'))

class CategoryViewsets(ModelViewSet):
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly]
    queryset = Category.objects.annotate(product_count=Count('products')).all()
    serializer_class = CategorySerializer

class ReviewViewsets(ModelViewSet):
    permission_classes = [IsReviewAuthorOrReadonly]
    serializer_class = ReviewSerializer

    def get_queryset(self):
        queryset = Review.objects.filter(product_id = self.kwargs.get('product_pk'))
        return queryset
    
    # now we can also pass product from here
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_context(self):
        return {'product_id': self.kwargs.get('product_pk')}
    

# Building an API steps-
# Create a Model
# serializer
# viewsets
# router