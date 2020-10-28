from django.utils.translation import ugettext as _
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from commons.request import cast_param
from notes import models
from notes.serializers.note import NoteCommandSerializer, NoteResultSerializer


class NoteViewSet(viewsets.ModelViewSet):
    queryset = models.Note.objects.all()
    serializer_class = NoteResultSerializer
    opts = getattr(models.Note, '_meta')

    def filter_by_category(self, queryset):
        """ Applies category filter to queryset """
        if 'category' not in self.request.GET:
            # ignore filter when it was not provided.
            return queryset

        category = cast_param(self.request, 'category', cast=int, default=-1)

        if category < 0:
            # returns empty list to invalid parameters.
            return queryset.none()

        return queryset.filter(category_id=category)

    def filter_by_archived(self, queryset):
        """ Applies category filter to queryset """
        if 'archived' not in self.request.GET:
            # ignore filter when it was not provided.
            return queryset

        archived = cast_param(self.request, 'archived', cast=bool, default=-1)

        if archived < 0:
            # returns empty list to invalid parameters.
            return queryset.none()

        return queryset.filter(archived=archived)

    def get_queryset(self):
        queryset = super().get_queryset() \
            .filter(user_id=self.request.user.pk)

        # optimize serializer performance when displaying category data.
        queryset = queryset.select_related('category')

        # apply queryset filters.
        queryset = self.filter_by_archived(queryset)
        queryset = self.filter_by_category(queryset)

        return queryset

    def create(self, request, *args, **kwargs):
        serializer = NoteCommandSerializer(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        serializer = self.get_serializer(instance=instance)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = NoteCommandSerializer(
            instance, data=request.data, partial=partial,
            context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(['PUT'], detail=True)
    def archive(self, request, **kwargs):
        obj = self.get_object()

        if obj.archived:
            return Response({
                'detail': _('The {name} "{obj}" is already archived.').format(
                    name=self.opts.verbose_name,
                    obj=str(obj)
                )
            }, status=status.HTTP_400_BAD_REQUEST)

        obj.archived = True
        obj.save()

        serializer = NoteResultSerializer(instance=obj, context=self.get_serializer_context())
        return Response(serializer.data, status=status.HTTP_200_OK)
