from rest_framework import serializers
from decimal import Decimal
from product.models import Product,Category, Review, ProductImage
from django.contrib.auth import get_user_model

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'product_count']
    product_count = serializers.IntegerField(read_only=True)
    
    # its for customization before save an object
    def create(self, validated_data):
        return super().create(validated_data)

class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()
    class Meta:
        model = ProductImage
        fields = ['image']

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'price_with_tax','stock', 'category','created_at', 'updated_at', 'images']

    price_with_tax = serializers.SerializerMethodField(method_name='calculate_tax')

    def calculate_tax(self, product):
        return round(product.price * Decimal(1.1), 2)
    # field lavel validation: validate_<field name>
    def validate_price(self, price):
        if price < 0 :
            raise serializers.ValidationError('Price could not be negetive!')
        else:
            return price

class SimpleUserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(method_name='get_current_user_name')
    class Meta:
        model = get_user_model()
        fields = ['id', 'name']

    def get_current_user_name(self, obj):
        return obj.get_full_name()

class ReviewSerializer(serializers.ModelSerializer):
    # user = SimpleUserSerializer()
    user = serializers.SerializerMethodField(method_name='get_user')

    class Meta:
        model = Review
        fields = ['id', 'product','user', 'ratings' ,'comment', 'created_at', 'updated_at']
        read_only_fields = ['product', 'user']

    def create(self, validated_data):
        product_id = self.context['product_id']
        review = Review.objects.create(product_id = product_id, **validated_data)
        return review

    def get_user(slef, obj):
        return SimpleUserSerializer(obj.user).data
    