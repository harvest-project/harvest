import json

from django.db import transaction, OperationalError
from rest_framework import serializers

from Harvest.path_utils import list_rel_files
from upload_studio.models import Project, ProjectStep, ProjectStepWarning, ProjectStepError


class ProjectShallowSerializer(serializers.ModelSerializer):
    status = serializers.CharField(read_only=True)

    class Meta:
        model = Project
        fields = '__all__'


class ProjectStepWarningSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectStepWarning
        fields = '__all__'


class ProjectStepErrorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectStepError
        fields = '__all__'


class ProjectStepSerializer(serializers.ModelSerializer):
    executor_kwargs = serializers.DictField()
    description = serializers.CharField(read_only=True)
    metadata = serializers.JSONField(source='metadata_json')
    warnings = ProjectStepWarningSerializer(source='projectstepwarning_set', many=True)
    errors = ProjectStepWarningSerializer(source='projectsteperror_set', many=True)

    class Meta:
        model = ProjectStep
        exclude = ('executor_kwargs_json',)


class ProjectDeepSerializer(serializers.ModelSerializer):
    steps = ProjectStepSerializer(many=True)
    files = serializers.SerializerMethodField()
    metadata = serializers.SerializerMethodField()
    is_locked = serializers.SerializerMethodField()
    current_step = serializers.SerializerMethodField()

    def get_current_step(self, obj):
        step = obj.next_step
        if step:
            return step.index
        return None

    def get_is_locked(self, obj):
        with transaction.atomic():
            try:
                Project.objects.select_for_update(nowait=True).get(id=obj.id)
                return False
            except OperationalError:
                return True

    def get_files(self, obj):
        last_complete_step = obj.last_complete_step
        if last_complete_step is None:
            return None
        return [{
            'path': rel_file,
        } for rel_file in list_rel_files(last_complete_step.data_path)]

    def get_metadata(self, obj):
        last_complete_step = obj.last_complete_step
        if last_complete_step is None:
            return None
        return json.loads(last_complete_step.metadata_json)

    class Meta:
        model = Project
        fields = '__all__'
