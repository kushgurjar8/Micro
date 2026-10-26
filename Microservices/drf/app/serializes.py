from rest_framework import serializers
from .models import *

# class StudentSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Student
#         fields = '__all__'

# class Meta:
#     model = Student
#     fields = ['id', 'name', 'email']        # only these fields
#     # exclude = ['number']                  # everything except these (use fields OR exclude)
#     read_only_fields = ['id']               # shown in GET, can't be sent in POST
#     extra_kwargs = {'number': {'write_only': True}}  # can be sent, but hidden in responses

# class StudentSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Student
#         fields = '__all__'

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'
        read_only_fields = ['mentor_id', 'mentor_name']    # only set through assign_mentor

    def validate_age(self, value):
        if value < 18:
            raise serializers.ValidationError("Age must be 18 or above")
        return value
    