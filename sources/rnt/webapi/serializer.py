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

    def __init__(
            self,
            instance=None,
            include_content=True,
            include_transient=True,
            include_public=True,
            *args,
            **kwargs
    ):
        if not include_content:
            del self.fields["content"]
        if not include_transient:
            del self.fields["transient"]
        if not include_public:
            del self.fields["public"]
        super(DataSetSerializer, self).__init__(instance, *args, **kwargs)

    def create(self, validated_data):
        validated_data["owner"] = self.context["request"].user
        return super(DataSetSerializer, self).create(validated_data)


class JobSerializer(serializers.HyperlinkedModelSerializer):
    dist = serializers.StringRelatedField(many=False)
    norm = serializers.StringRelatedField(many=False)
    owner = serializers.StringRelatedField(many=False)
    creation = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = Job
        fields = ('identifier', 'dist', 'norm', 'owner', 'creation', 'bench', 'task_count', 'status', 'name',)
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


class SimpleDataSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataSet
        fields = (
            'id',
            'name',
            'n',
            'm',
            'step',
        )


class ResultSerializer(serializers.ModelSerializer):
    job = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='identifier'
    )
    algo = SimpleAlgorithmSerializer(many=False)

    def __init__(self, instance=None, include_consensuses=False, detailed_dataset=False, *args, **kwargs):
        if detailed_dataset:
            self.fields["dataset"] = SimpleDataSetSerializer()
        if not include_consensuses:
            del self.fields["consensuses"]
        super(ResultSerializer, self).__init__(instance, *args, **kwargs)

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
