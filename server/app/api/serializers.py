from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from core.models import Stream


class AuthTokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username

        return token


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'password')
        extra_kwargs = {'password': {'write_only': True, 'min_length': 8}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class StreamSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source="user.username")

    class Meta:
        model = Stream
        fields = '__all__'
        read_only_fields = ('username',)


class StartStreamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stream
        fields = '__all__'

    def update(self, instance, validated_data):
        if instance.user == validated_data.user:
            instance.is_started = True
            instance.save()

        return instance
