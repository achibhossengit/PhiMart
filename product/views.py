from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from product.models import Product, Category, Review
from rest_framework import status
from django.db.models import Count
from product.serializers import ProductSerializer, CategorySerializer, ReviewSerializer
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from product.filters import ProductFilter
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from product.paginations import CustomPageNumberPagination
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly
from api.permissions import IsAdminOrReadonly, FullDjangoModelPermission
from product.permissions import IsReviewAuthorOrReadonly



class ProductViewsets(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # filterset_fields = ['category_id', 'price']
    filterset_class = ProductFilter
    search_fields = ['name', 'description', 'category__name'] # double underscore: category_id is a related field of product but, category name isn't. so, category__name to access
    ordering_fields = ['price', 'updated_at']
    pagination_class = CustomPageNumberPagination
    # permission_classes = [DjangoModelPermissionsOrAnonReadOnly]
    permission_classes = [IsAdminOrReadonly]
    # permission_classes = [FullDjangoModelPermission]

    # def get_permissions(self):
    #     if self.request.method == 'GET':
    #         return [AllowAny()]
    #     return [IsAdminUser()]


    def destroy(self, request, *args, **kwargs):
        product = self.get_object()
        if product.stock > 10:
            return Response("{'message': 'This product price is more than 10. so, its not to be deleted!'}")
        self.perform_destroy(product)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class CategoryViewsets(ModelViewSet):
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly]
    queryset = Category.objects.annotate(product_count=Count('products')).all()
    serializer_class = CategorySerializer

class ReviewViewsets(ModelViewSet):
    permission_classes = [IsReviewAuthorOrReadonly]
    serializer_class = ReviewSerializer

    def get_queryset(self):
        queryset = Review.objects.filter(product_id = self.kwargs['product_pk'])
        return queryset
    
    # now we can also pass product from here
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}
    

# Building an API steps-
# Create a Model
# serializer
# viewsets
# router