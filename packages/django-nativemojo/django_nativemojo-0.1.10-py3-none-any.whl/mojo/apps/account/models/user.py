from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from mojo.models import MojoModel, MojoSecrets
from mojo.helpers.settings import settings
from mojo import errors as merrors
from mojo.helpers import dates
from mojo.apps.account.utils.jwtoken import JWToken
import uuid

USER_PERMS_PROTECTION = settings.get("USER_PERMS_PROTECTION", {})
USER_LAST_ACTIVITY_FREQ = settings.get("USER_LAST_ACTIVITY_FREQ", 300)

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)

    def get_by_natural_key(self, username):
        """Required for Django authentication"""
        return self.get(**{self.model.USERNAME_FIELD: username})

class User(MojoSecrets, AbstractBaseUser, MojoModel):
    """
    Full custom user model.
    """
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now_add=True, editable=True)
    last_activity = models.DateTimeField(default=None, null=True, db_index=True)

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, db_index=True)
    username = models.TextField(unique=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=32, blank=True, null=True, default=None)
    is_active = models.BooleanField(default=True, db_index=True)
    display_name = models.CharField(max_length=80, blank=True, null=True, default=None)
    # key used for sessions and general authentication algs
    auth_key = models.TextField(null=True, default=None)
    onetime_code = models.TextField(null=True, default=None)
    # JSON-based permissions field
    permissions = models.JSONField(default=dict, blank=True)
    # JSON-based metadata field
    metadata = models.JSONField(default=dict, blank=True)

    # required default fields
    first_name = models.CharField(max_length=80, default="")
    last_name = models.CharField(max_length=80, default="")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # Required for admin access
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    is_email_verified = models.BooleanField(default=False)
    is_phone_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    objects = CustomUserManager()

    class RestMeta:
        NO_SHOW_FIELDS = ["password", "auth_key", "onetime_code"]
        SEARCH_FIELDS = ["username", "email", "display_name"]
        VIEW_PERMS = ["view_users", "manage_users", "owner"]
        SAVE_PERMS = ["manage_users", "owner"]
        LIST_DEFAULT_FILTERS = {
            "is_active": True
        }
        UNIQUE_LOOKUP = ["username", "email"]
        GRAPHS = {
            "basic": {
                "fields": [
                    'id',
                    'display_name',
                    'username',
                    'email',
                    'phone_number',
                    'last_login',
                    'last_activity',
                    'is_active'
                ]
            },
            "default": {
                "fields": [
                    'id',
                    'display_name',
                    'username',
                    'email',
                    'phone_number',
                    'last_login',
                    'last_activity',
                    'permissions',
                    'metadata',
                    'is_active'
                ],
            },
        }

    def __str__(self):
        return self.email

    def is_request_user(self, request=None):
        if request is None:
            request = self.active_request
        if request is None:
            return False
        return request.user.id == self.id

    def touch(self):
        # can't subtract offset-naive and offset-aware datetimes
        if self.last_activity is None or dates.has_time_elsapsed(self.last_activity, seconds=USER_LAST_ACTIVITY_FREQ):
            self.last_activity = dates.utcnow()
            self.atomic_save()

    def get_auth_key(self):
        if self.auth_key is None:
            self.auth_key = uuid.uuid4().hex
            self.atomic_save()
        return self.auth_key

    def set_permissions(self, value, request):
        if not isinstance(value, dict):
            return
        for key in value:
            if key in USER_PERMS_PROTECTION:
                if not request.user.has_permission(USER_PERMS_PROTECTION[key]):
                    raise merrors.PermissionDeniedException()
            elif not request.user.has_permission("manage_users"):
                raise merrors.PermissionDeniedException()
            if bool(value[key]):
                self.add_permission(key)
            else:
                self.remove_permission(key)

    def has_module_perms(self, app_label):
        """Check if user has any permissions in a given app."""
        return True  # Or customize based on your `permissions` JSON

    def has_permission(self, perm_key):
        """Check if user has a specific permission in JSON field."""
        if isinstance(perm_key, list):
            for pk in perm_key:
                if self.has_permission(pk):
                    return True
            return False
        if perm_key == "all":
            return True
        return self.permissions.get(perm_key, False)

    def add_permission(self, perm_key, value=True):
        """Dynamically add a permission."""
        if isinstance(perm_key, (list, set)):
            for pk in perm_key:
                self.permissions[pk] = value
        else:
            self.permissions[perm_key] = value
        self.save()

    def remove_permission(self, perm_key):
        """Remove a permission."""
        if isinstance(perm_key, (list, set)):
            for pk in perm_key:
                if pk in self.permissions:
                    del self.permissions[pk]
        else:
            if perm_key in self.permissions:
                del self.permissions[perm_key]
        self.save()

    def remove_all_permissions(self):
        self.permissions = {}
        self.save()

    def save_password(self, value):
        self.set_password(value)
        self.save()

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email.split("@")[0]
        if not self.display_name:
            self.display_name = self.username
        super().save(*args, **kwargs)

    def check_edit_permission(self, perms, request):
        if "owner" in perms and self.is_request_user():
            return True
        return request.user.has_permission(perms)

    @classmethod
    def validate_jwt(cls, token):
        token_manager = JWToken()
        jwt_data = token_manager.decode(token, validate=False)
        if jwt_data.uid is None:
            return None, "Invalid token data"
        user = User.objects.filter(id=jwt_data.uid).last()
        if user is None:
            return None, "Invalid token user"
        token_manager.key = user.auth_key
        if not token_manager.is_token_valid(token):
            if token_manager.is_expired:
                return user, "Token expired"
            return user, "Token has invalid signature"
        return user, None
