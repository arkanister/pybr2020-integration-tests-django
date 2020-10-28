from rest_framework import viewsets

from notes import models
from notes.serializers.category import CategorySerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = models.Category.objects.all()
    serializer_class = CategorySerializer

    def get_queryset(self):
        return super().get_queryset() \
            .filter(user_id=self.request.user.pk)
