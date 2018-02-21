from rest_framework import serializers

# Serializers define the API representation.
from mediane.models import DataSet, Job, Result, Algorithm


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
            'public',
        )

    def create(self, validated_data):
        validated_data["owner"] = self.context["request"].user
        return super().create(validated_data)


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


class SimpleAlgorithmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Algorithm
        fields = (
            'id',
            'key_name',
        )


class ResultSerializer(serializers.ModelSerializer):
    job = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='identifier'
    )
    algo = SimpleAlgorithmSerializer(many=False)

    class Meta:
        model = Result
        fields = (
            'algo',
            'dataset',
            'job',
            'distance_value',
            'duration',
            'consensuses',
        )


class ResultSerializerNoContent(serializers.ModelSerializer):
    job = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='identifier'
    )
    algo = SimpleAlgorithmSerializer(many=False)

    class Meta:
        model = Result
        fields = (
            'algo',
            'dataset',
            'job',
            'distance_value',
            'duration',
        )
