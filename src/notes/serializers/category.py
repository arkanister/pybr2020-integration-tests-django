from rest_framework import serializers

from notes import models


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Category
        fields = ['id', 'name']

    def create(self, validated_data):
        request = self.context.get('request')
        return super().create({
            **validated_data,
            'user_id': request.user.pk
        })
