from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import serializers
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.utils import get_md5_hash_password

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "role", "date_joined")
        read_only_fields = ("id", "email", "role", "date_joined")


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    password_confirmation = serializers.CharField(write_only=True, trim_whitespace=False)

    class Meta:
        model = User
        fields = ("email", "password", "password_confirmation", "first_name", "last_name")

    def validate_email(self, value: str) -> str:
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value.lower()

    def validate(self, attrs):
        if attrs["password"] != attrs.pop("password_confirmation"):
            raise serializers.ValidationError({"password_confirmation": "Passwords do not match."})
        validate_password(attrs["password"])
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class ShopFlowTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = User.EMAIL_FIELD

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        token["role"] = user.role
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data


class PasswordChangeAwareTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        refresh = RefreshToken(attrs["refresh"])
        user = User.objects.filter(pk=refresh.get("user_id"), is_active=True).first()

        if user is None:
            raise InvalidToken("No active user matches this token.")
        if refresh.get("hash_password") != get_md5_hash_password(user.password):
            raise InvalidToken("This token was issued before the password was changed.")
        return super().validate(attrs)


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate_refresh(self, value: str) -> str:
        try:
            token = RefreshToken(value)
        except Exception as exc:
            raise serializers.ValidationError("Invalid refresh token.") from exc

        if str(token["user_id"]) != str(self.context["request"].user.pk):
            raise serializers.ValidationError("Refresh token does not belong to this user.")
        return value

    def save(self, **kwargs) -> None:
        RefreshToken(self.validated_data["refresh"]).blacklist()


class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True, trim_whitespace=False)
    new_password = serializers.CharField(write_only=True, trim_whitespace=False)
    new_password_confirmation = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate_current_password(self, value: str) -> str:
        if not self.context["request"].user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value

    def validate(self, attrs):
        if attrs["new_password"] != attrs.pop("new_password_confirmation"):
            raise serializers.ValidationError(
                {"new_password_confirmation": "Passwords do not match."}
            )
        validate_password(attrs["new_password"], self.context["request"].user)
        return attrs

    def save(self) -> User:
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.mark_password_changed()
        user.save(update_fields=("password", "password_changed_at"))
        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def save(self) -> None:
        user = User.objects.filter(
            email__iexact=self.validated_data["email"], is_active=True
        ).first()
        if user is None:
            return

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_url = f"{settings.PASSWORD_RESET_URL}?uid={uid}&token={token}"
        send_mail(
            subject="ShopFlow password reset",
            message=f"Use this link to reset your password: {reset_url}",
            from_email=None,
            recipient_list=[user.email],
        )


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, trim_whitespace=False)
    new_password_confirmation = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        try:
            user_id = force_str(urlsafe_base64_decode(attrs["uid"]))
            user = User.objects.get(pk=user_id)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist) as exc:
            raise serializers.ValidationError({"uid": "Invalid password reset link."}) from exc

        if not default_token_generator.check_token(user, attrs["token"]):
            raise serializers.ValidationError({"token": "Invalid or expired password reset link."})
        if attrs["new_password"] != attrs.pop("new_password_confirmation"):
            raise serializers.ValidationError(
                {"new_password_confirmation": "Passwords do not match."}
            )
        validate_password(attrs["new_password"], user)
        attrs["user"] = user
        return attrs

    def save(self) -> User:
        user = self.validated_data["user"]
        user.set_password(self.validated_data["new_password"])
        user.mark_password_changed()
        user.save(update_fields=("password", "password_changed_at"))
        return user
