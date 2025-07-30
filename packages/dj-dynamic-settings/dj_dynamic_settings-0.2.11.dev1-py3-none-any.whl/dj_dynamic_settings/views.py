from __future__ import unicode_literals

from rest_framework import permissions, viewsets
from rest_framework.response import Response

from dj_dynamic_settings.compat import action
from dj_dynamic_settings.models import Setting
from dj_dynamic_settings.registry import registry
from dj_dynamic_settings.serializers import (
    DynamicSettingSerializer,
    RegistryItemSerializer,
)


class DynamicSettingsViewSet(viewsets.ModelViewSet):
    queryset = Setting.objects.all()
    serializer_class = DynamicSettingSerializer
    permission_classes = (permissions.IsAdminUser,)

    def get_queryset(self):
        queryset = super(DynamicSettingsViewSet, self).get_queryset()
        return queryset.filter(key__in=registry.keys())

    @action(detail=False, methods=["GET"], url_path="registry")
    def get_registry(self, *args, **kwargs):
        items = [registry[key] for key in registry.keys()]
        serializer = RegistryItemSerializer(items, many=True)
        return Response(serializer.data)
