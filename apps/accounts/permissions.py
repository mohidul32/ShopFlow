from rest_framework.permissions import BasePermission

from .models import User


class IsCustomer(BasePermission):
    message = "Customer access is required."

    def has_permission(self, request, view) -> bool:
        return bool(request.user.is_authenticated and request.user.role == User.Role.CUSTOMER)


class IsSeller(BasePermission):
    message = "Seller access is required."

    def has_permission(self, request, view) -> bool:
        return bool(request.user.is_authenticated and request.user.role == User.Role.SELLER)


class IsMarketplaceAdmin(BasePermission):
    message = "Administrative access is required."

    def has_permission(self, request, view) -> bool:
        return bool(request.user.is_authenticated and request.user.is_staff)
