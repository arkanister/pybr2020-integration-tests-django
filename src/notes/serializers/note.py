from rest_framework import serializers

from notes import models
from notes.serializers.category import CategorySerializer


class NoteResultSerializer(serializers.ModelSerializer):
    category = CategorySerializer(many=False)

    class Meta:
        model = models.Note
        fields = [
            'id', 'title', 'content', 'category', 'archived',
            'created_at', 'last_update'
        ]


class NoteCommandSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Note
        fields = [
            'id', 'title', 'content', 'category'
        ]

    def create(self, validated_data):
        request = self.context.get('request')
        return super().create({
            **validated_data,
            'user_id': request.user.pk
        })
