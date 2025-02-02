from django.core import serializers

from utils.json_encoder import JSONEncoder


class DjangoModelSerializer:

    @classmethod
    def serialize(cls, instance):
        """
        serializer to json
        instance: must be iterable,list
        """
        return serializers.serialize('json', [instance], cls=JSONEncoder)

    @classmethod
    def deserialize(cls, serialized_data):
        """
        to model object
        """
        return list(serializers.deserialize('json', serialized_data))[0].object