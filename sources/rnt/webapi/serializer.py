from rest_framework import serializers

# Serializers define the API representation.
from mediane.models import DataSet, Job


class DataSetSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DataSet
        fields = (
            'pk',
            'name',
            'content',
            'm',
            'n',
            'complete',
            'step',
            'transient',
        )


class DataSetSerializerNoContent(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DataSet
        fields = (
            'pk',
            'name',
            'm',
            'n',
            'complete',
            'step',
        )


class JobSerializer(serializers.HyperlinkedModelSerializer):
    dist = serializers.StringRelatedField(many=False)
    norm = serializers.StringRelatedField(many=False)
    owner = serializers.StringRelatedField(many=False)
    creation = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = Job
        fields = ('identifier', 'dist', 'norm', 'owner', 'creation', 'bench', 'task_count', 'status',)
        lookup_field = 'identifier'
        extra_kwargs = {
            'url': {'lookup_field': 'identifier'}
        }
        read_only_fields = ('identifier', 'dist', 'norm', 'owner', 'creation', 'bench', 'task_count',)
