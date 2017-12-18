from rest_framework import serializers

# Serializers define the API representation.
from mediane.models import DataSet


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
