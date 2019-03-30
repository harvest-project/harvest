from rest_framework import serializers

from upload_studio.models import Project, ProjectStep


class ProjectShallowSerializer(serializers.ModelSerializer):
    status = serializers.CharField(read_only=True)

    class Meta:
        model = Project
        fields = ('id', 'name', 'media_type', 'status')


class ProjectStepSerializer(serializers.ModelSerializer):
    executor_kwargs = serializers.JSONField(source='executor_kwargs_json')
    metadata = serializers.JSONField(source='metadata_json')

    class Meta:
        model = ProjectStep
        fields = ('id', 'index', 'status', 'executor_name', 'executor_kwargs', 'metadata')


class ProjectDeepSerializer(serializers.ModelSerializer):
    steps = ProjectStepSerializer(many=True)

    class Meta:
        model = Project
        fields = ('id', 'name', 'media_type', 'steps')
