# from django.contrib.auth.hashers import make_password
# from rest_framework import serializers
# from rest_framework.exceptions import ValidationError
#
# from core.models import User
#
#
# class CreateUserSerializer(serializers.ModelSerializer):
#     password = PasswordField(required=True)
#     password_repeat = PasswordField(required=True)
#
#     class Meta:
#         model = User
#         fields = ['id', 'username', 'first_name', 'last_name', 'email', 'password', 'password_repeat']
#
#     def validate(self, attrs):
#         if attrs['password'] != attrs['password_repeat']:
#             raise ValidationError('Пароли должны совпадать')
#         return attrs
#
#     def create(self, validated_data):
#         del validated_data['password_repeat']
#         validated_data['password'] = make_password(validated_data['password'])
#         return super().create(validated_data)