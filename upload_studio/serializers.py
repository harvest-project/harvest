from django.db import transaction, OperationalError
from rest_framework import serializers

from upload_studio.models import Project, ProjectStep, ProjectStepWarning, ProjectStepError
from upload_studio.utils import list_rel_files


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
    executor_kwargs = serializers.JSONField(source='executor_kwargs_json')
    description = serializers.CharField(read_only=True)
    metadata = serializers.JSONField(source='metadata_json')
    warnings = ProjectStepWarningSerializer(source='projectstepwarning_set', many=True)
    errors = ProjectStepWarningSerializer(source='projectsteperror_set', many=True)

    class Meta:
        model = ProjectStep
        fields = '__all__'


class ProjectDeepSerializer(serializers.ModelSerializer):
    steps = ProjectStepSerializer(many=True)
    files = serializers.SerializerMethodField()
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
        complete_steps = [s for s in obj.steps if s.status == Project.STATUS_COMPLETE]
        if not complete_steps:
            return []
        last_complete_step = complete_steps[-1]
        result = []
        for rel_file in list_rel_files(last_complete_step.data_path):
            result.append({
                'path': rel_file,
            })
        return result

    class Meta:
        model = Project
        fields = '__all__'
