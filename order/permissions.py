from rest_framework.permissions import BasePermission
from order.models import CartItem

class IsCartOwnerUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    # its not working 
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, CartItem):
            is_owner = obj.cart.user == request.user
            print(f"Checking permission for user: {request.user}, is owner: {is_owner}")
            return is_owner
        print('out of isinstance')
        return False