from rest_framework import serializers
from .models import Business, ReviewLink

'''
DJANGO SERIALIZER: is a data translator between complex types
(like models) and python native or JSON formats.
'''

class BusinessSerializer(serializers.ModelSerializer):
    review_link = serializers.SerializerMethodField()
    
    class Meta:
        model = Business
        fields = ['id', 'name', 'address', 'review_link']
    
    def get_review_link(self, obj):
        link = obj.get_review_link()
        return f"https://reviewbud.co/review/{link.token}"