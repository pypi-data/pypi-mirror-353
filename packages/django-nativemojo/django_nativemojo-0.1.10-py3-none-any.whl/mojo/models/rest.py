# from django.http import JsonResponse
from mojo.helpers.response import JsonResponse
from mojo.serializers.models import GraphSerializer
from mojo.helpers import modules
from mojo.helpers.settings import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction, models as dm
import objict
from mojo.helpers import dates, logit


logger = logit.get_logger("debug", "debug.log")
ACTIVE_REQUEST = None
LOGGING_CLASS = None
MOJO_APP_STATUS_200_ON_ERROR = settings.MOJO_APP_STATUS_200_ON_ERROR

class MojoModel:
    """Base model class for REST operations with GraphSerializer integration."""

    @property
    def active_request(self):
        """Returns the active request being processed."""
        return ACTIVE_REQUEST

    @classmethod
    def get_rest_meta_prop(cls, name, default=None):
        """
        Retrieve a property from the RestMeta class if it exists.

        Args:
            name (str or list): Name of the property to retrieve.
            default: Default value to return if the property does not exist.

        Returns:
            The value of the requested property or the default value.
        """
        if getattr(cls, "RestMeta", None) is None:
            return default
        if isinstance(name, list):
            for n in name:
                res = getattr(cls.RestMeta, n, None)
                if res is not None:
                    return res
            return default
        return getattr(cls.RestMeta, name, default)

    @classmethod
    def rest_error_response(cls, request, status=500, **kwargs):
        """
        Create a JsonResponse for an error.

        Args:
            request: Django HTTP request object.
            status (int): HTTP status code for the response.
            kwargs: Additional data to include in the response.

        Returns:
            JsonResponse representing the error.
        """
        payload = dict(kwargs)
        payload["is_authenticated"] = request.user.is_authenticated
        payload["status"] = False
        if "code" not in payload:
            payload["code"] = status
        if MOJO_APP_STATUS_200_ON_ERROR:
            status = 200
        return JsonResponse(payload, status=status)

    @classmethod
    def on_rest_request(cls, request, pk=None):
        """
        Handle REST requests dynamically based on HTTP method.

        Args:
            request: Django HTTP request object.
            pk: Primary key of the object, if available.

        Returns:
            JsonResponse representing the result of the request.
        """
        cls.__rest_field_names__ = [f.name for f in cls._meta.get_fields()]
        if pk:
            instance = cls.get_instance_or_404(pk)
            if isinstance(instance, dict):  # If it's a response, return early
                return instance

            if request.method == 'GET':
                return cls.on_rest_handle_get(request, instance)

            elif request.method in ['POST', 'PUT']:
                return cls.on_rest_handle_save(request, instance)

            elif request.method == 'DELETE':
                return cls.on_rest_handle_delete(request, instance)
        else:
            return cls.on_handle_list_or_create(request)

        return cls.rest_error_response(request, 500, error=f"{cls.__name__} not found")

    @classmethod
    def get_instance_or_404(cls, pk):
        """
        Helper method to get an instance or return a 404 response.

        Args:
            pk: Primary key of the instance to retrieve.

        Returns:
            The requested instance or a JsonResponse for a 404 error.
        """
        try:
            return cls.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return cls.rest_error_response(None, 404, error=f"{cls.__name__} not found")

    @classmethod
    def rest_check_permission(cls, request, permission_keys, instance=None):
        """
        Check permissions for a given request.

        Args:
            request: Django HTTP request object.
            permission_keys: Keys to check for permissions.
            instance: Optional instance to check instance-specific permissions.

        Returns:
            True if the request has the necessary permissions, otherwise False.
        """
        perms = cls.get_rest_meta_prop(permission_keys, [])
        if perms is None or len(perms) == 0:
            return True
        if "all" not in perms:
            if request.user is None or not request.user.is_authenticated:
                return False
        if instance is not None:
            if hasattr(instance, "check_edit_permission"):
                return instance.check_edit_permission(perms, request)
            if "owner" in perms and getattr(instance, "user", None) is not None:
                if instance.user.id == request.user.id:
                    return True
        if request.group and hasattr(cls, "group"):
            # lets check our group member permissions
            # this will now force any queries to include the group
            return request.group.member_has_permission(request.user, perms)
        return request.user.has_permission(perms)

    @classmethod
    def on_rest_handle_get(cls, request, instance):
        """
        Handle GET requests with permission checks.

        Args:
            request: Django HTTP request object.
            instance: The instance to retrieve.

        Returns:
            JsonResponse representing the result of the GET request.
        """
        if cls.rest_check_permission(request, "VIEW_PERMS", instance):
            return instance.on_rest_get(request)
        return cls.rest_error_response(request, 403, error=f"GET permission denied: {cls.__name__}")

    @classmethod
    def on_rest_handle_save(cls, request, instance):
        """
        Handle POST and PUT requests with permission checks.

        Args:
            request: Django HTTP request object.
            instance: The instance to save or update.

        Returns:
            JsonResponse representing the result of the save operation.
        """
        if cls.rest_check_permission(request, ["SAVE_PERMS", "VIEW_PERMS"], instance):
            return instance.on_rest_save_and_respond(request)
        return cls.rest_error_response(request, 403, error=f"{request.method} permission denied: {cls.__name__}")

    @classmethod
    def on_rest_handle_delete(cls, request, instance):
        """
        Handle DELETE requests with permission checks.

        Args:
            request: Django HTTP request object.
            instance: The instance to delete.

        Returns:
            JsonResponse representing the result of the delete operation.
        """
        if not cls.get_rest_meta_prop("CAN_DELETE", False):
            return cls.rest_error_response(request, 403, error=f"DELETE not allowed: {cls.__name__}")

        if cls.rest_check_permission(request, ["DELETE_PERMS", "SAVE_PERMS", "VIEW_PERMS"], instance):
            return instance.on_rest_delete(request)
        return cls.rest_error_response(request, 403, error=f"DELETE permission denied: {cls.__name__}")

    @classmethod
    def on_rest_handle_list(cls, request):
        """
        Handle GET requests for listing resources with permission checks.

        Args:
            request: Django HTTP request object.

        Returns:
            JsonResponse representing the list of resources.
        """
        if cls.rest_check_permission(request, "VIEW_PERMS"):
            return cls.on_rest_list(request)
        return cls.rest_error_response(request, 403, error=f"GET permission denied: {cls.__name__}")

    @classmethod
    def on_rest_handle_create(cls, request):
        """
        Handle POST and PUT requests for creating resources with permission checks.

        Args:
            request: Django HTTP request object.

        Returns:
            JsonResponse representing the result of the create operation.
        """
        if cls.rest_check_permission(request, ["SAVE_PERMS", "VIEW_PERMS"]):
            instance = cls()
            return instance.on_rest_save_and_respond(request)
        return cls.rest_error_response(request, 403, error=f"CREATE permission denied: {cls.__name__}")

    @classmethod
    def on_handle_list_or_create(cls, request):
        """
        Handle listing (GET without pk) and creating (POST/PUT without pk) operations.

        Args:
            request: Django HTTP request object.

        Returns:
            JsonResponse representing the result of the operation.
        """
        if request.method == 'GET':
            return cls.on_rest_handle_list(request)
        elif request.method in ['POST', 'PUT']:
            return cls.on_rest_handle_create(request)

    @classmethod
    def on_rest_list(cls, request, queryset=None):
        """
        List objects with filtering, sorting, and pagination.

        Args:
            request: Django HTTP request object.
            queryset: Optional initial queryset to use.

        Returns:
            JsonResponse representing the paginated and serialized list of objects.
        """
        if queryset is None:
            queryset = cls.objects.all()
        if request.group is not None and hasattr(cls, "group"):
            if "group" in request.DATA:
                del request.DATA["group"]
            queryset = queryset.filter(group=request.group)
        queryset = cls.on_rest_list_filter(request, queryset)
        queryset = cls.on_rest_list_date_range_filter(request, queryset)
        queryset = cls.on_rest_list_sort(request, queryset)
        return cls.on_rest_list_response(request, queryset)

    @classmethod
    def on_rest_list_response(cls, request, queryset):
        # Implement pagination
        page_size = request.DATA.get_typed("size", 10, int)
        page_start = request.DATA.get_typed("start", 0, int)
        page_end = page_start+page_size
        paged_queryset = queryset[page_start:page_end]
        graph = request.DATA.get("graph", "list")
        serializer = GraphSerializer(paged_queryset, graph=graph, many=True)
        return serializer.to_response(request, count=queryset.count(), start=page_start, size=page_size)

    @classmethod
    def on_rest_list_date_range_filter(cls, request, queryset):
        """
        Filter queryset based on a date range provided in the request.

        Args:
            request: Django HTTP request object.
            queryset: The queryset to filter.

        Returns:
            The filtered queryset.
        """
        dr_field = request.DATA.get("dr_field", "created")
        dr_start = request.DATA.get("dr_start")
        dr_end = request.DATA.get("dr_end")

        if dr_start:
            dr_start = dates.parse_datetime(dr_start)
            if request.group:
                dr_start = request.group.get_local_time(dr_start)
            queryset = queryset.filter(**{f"{dr_field}__gte": dr_start})

        if dr_end:
            dr_end = dates.parse_datetime(dr_end)
            if request.group:
                dr_end = request.group.get_local_time(dr_end)
            queryset = queryset.filter(**{f"{dr_field}__lte": dr_end})
        return queryset

    @classmethod
    def on_rest_list_filter(cls, request, queryset):
        """
        Apply filtering logic based on request parameters, including foreign key fields.

        Args:
            request: Django HTTP request object.
            queryset: The queryset to filter.

        Returns:
            The filtered queryset.
        """
        filters = {}
        for key, value in request.GET.items():
            # Split key to check for foreign key relationships
            key_parts = key.split('__')
            field_name = key_parts[0]
            if hasattr(cls, field_name):
                filters[key] = value
            elif field_name in cls.__rest_field_names__ and cls._meta.get_field(field_name).is_relation:
                filters[key] = value
        # logger.info("filters", filters)
        queryset = cls.on_rest_list_search(request, queryset)
        return queryset.filter(**filters)

    @classmethod
    def on_rest_list_search(cls, request, queryset):
        """
        Search queryset based on 'q' param in the request for fields defined in 'SEARCH_FIELDS'.

        Args:
            request: Django HTTP request object.
            queryset: The queryset to search.

        Returns:
            The filtered queryset based on the search criteria.
        """
        search_query = request.GET.get('q', None)
        if not search_query:
            return queryset

        search_fields = getattr(cls.RestMeta, 'SEARCH_FIELDS', None)
        if search_fields is None:
            search_fields = [
                field.name for field in cls._meta.get_fields()
                if field.get_internal_type() in ["CharField", "TextField"]
            ]

        query_filters = dm.Q()
        for field in search_fields:
            query_filters |= dm.Q(**{f"{field}__icontains": search_query})

        logger.info("search_filters", query_filters)
        return queryset.filter(query_filters)

    @classmethod
    def on_rest_list_sort(cls, request, queryset):
        """
        Apply sorting to the queryset.

        Args:
            request: Django HTTP request object.
            queryset: The queryset to sort.

        Returns:
            The sorted queryset.
        """
        sort_field = request.DATA.pop("sort", "-id")
        if sort_field.lstrip('-') in cls.__rest_field_names__:
            return queryset.order_by(sort_field)
        return queryset

    @classmethod
    def return_rest_response(cls, data, flat=False):
        """
        Return the passed in data as a JSONResponse with root values of status=True and data=.

        Args:
            data: Data to include in the response.

        Returns:
            JsonResponse representing the data.
        """
        if flat:
            response_payload = data
        else:
            response_payload = {
                "status": True,
                "data": data
            }
        return JsonResponse(response_payload)

    @classmethod
    def on_rest_create(cls, request):
        """
        Handle the creation of an object.

        Args:
            request: Django HTTP request object.

        Returns:
            JsonResponse representing the newly created object.
        """
        instance = cls()
        return instance.on_rest_save_and_respond(request)

    def on_rest_get(self, request):
        """
        Handle the retrieval of a single object.

        Args:
            request: Django HTTP request object.

        Returns:
            JsonResponse representing the object.
        """
        graph = request.GET.get("graph", "default")
        serializer = GraphSerializer(self, graph=graph)
        return serializer.to_response(request)

    def on_rest_save(self, request, data_dict):
        """
        Create a model instance from a dictionary.

        Args:
            request: Django HTTP request object.

        Returns:
            None
        """
        for field in self._meta.get_fields():
            field_name = field.name
            if field_name in data_dict:
                field_value = data_dict[field_name]
                set_field_method = getattr(self, f'set_{field_name}', None)
                if callable(set_field_method):
                    set_field_method(field_value, request)
                elif field.is_relation and hasattr(field, 'related_model'):
                    self.on_rest_save_related_field(field, field_value, request)
                elif field.get_internal_type() == "JSONField":
                    self.on_rest_update_jsonfield(field_name, field_value)
                else:
                    setattr(self, field_name, field_value)
        self.atomic_save()

    def on_rest_save_and_respond(self, request):
        self.on_rest_save(request, request.DATA)
        return self.on_rest_get(request)

    def on_rest_save_related_field(self, field, field_value, request):
        if isinstance(field_value, dict):
            # we want to check if we have an existing field and if so we will update it after security
            related_instance = getattr(self, field.name)
            if related_instance is None:
                # skip None fields for now
                # FUTURE look at creating a new instance
                return
            if hasattr(field.related_model, "rest_check_permission"):
                if field.related_model.rest_check_permission(request, ["SAVE_PERMS", "VIEW_PERMS"], related_instance):
                    related_instance.on_rest_save(request, field_value)
            return
        try:
            related_instance = field.related_model.objects.get(pk=field_value)
            setattr(self, field.name, related_instance)
        except field.related_model.DoesNotExist:
            pass  # Skip invalid related instances

    def on_rest_update_jsonfield(self, field_name, field_value):
        """helper to update jsonfield by merge in changes"""
        existing_value = getattr(self, field_name, {})
        # logger.info("JSONField", existing_value, "New Value", field_value)
        if isinstance(field_value, dict) and isinstance(existing_value, dict):
            merged_value = objict.merge_dicts(existing_value, field_value)
            setattr(self, field_name, merged_value)

    def jsonfield_as_objict(self, field_name):
        existing_value = getattr(self, field_name, {})
        if not isinstance(existing_value, objict.objict):
            existing_value = objict.objict.fromdict(existing_value)
            setattr(self, field_name, existing_value)
        return existing_value

    def on_rest_delete(self, request):
        """
        Handle the deletion of an object.

        Args:
            request: Django HTTP request object.

        Returns:
            JsonResponse representing the result of the delete operation.
        """
        try:
            with transaction.atomic():
                self.delete()
            return JsonResponse({"status": "deleted"}, status=204)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    def to_dict(self, graph="default"):
        serializer = GraphSerializer(self, graph=graph)
        return serializer.serialize()

    @classmethod
    def queryset_to_dict(cls, qset, graph="default"):
        serializer = GraphSerializer(qset, graph=graph)
        return serializer.serialize()

    def atomic_save(self):
        """
        Save the object atomically to the database.
        """
        with transaction.atomic():
            self.save()

    def report_incident(self, description, kind="error", level="critical", **kwargs):
        self.model_logit(ACTIVE_REQUEST, description, kind=kind, level=level)
        Event = modules.get_model("incidents", "Event")
        if Event is None:
            Event.report(description, kind, **kwargs)

    def log(self, log, kind="model_log", level="info", **kwargs):
        return self.class_logit(ACTIVE_REQUEST, log, kind, self.id, level, **kwargs)

    def model_logit(self, request, log, kind="model_log", level="info", **kwargs):
        return self.class_logit(request, log, kind, self.id, level, **kwargs)

    @classmethod
    def class_logit(cls, request, log, kind="cls_log", model_id=0, level="info", **kwargs):
        from mojo.apps.logit.models import Log
        return Log.logit(request, log, kind, cls.__name__, model_id, level, **kwargs)
