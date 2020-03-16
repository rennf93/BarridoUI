from rest_framework import serializers
from core.models import SnapshotRestore

class SnapshotCallbackSerializer(serializers.Serializer):
    pass

class SnapshotRestoreLastSerializer(serializers.ModelSerializer):
    class Meta:
        model = SnapshotRestore
        fields = ('id', 'status', 'database_name', 'updated_at')