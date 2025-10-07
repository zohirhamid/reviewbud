from rest_framework import serializers
from .models import Business, ReviewLink, CustomerReview

'''
DJANGO SERIALIZER: is a data translator between complex types
(like models) and python native or JSON formats.
'''

class BusinessSerializer(serializers.ModelSerializer):
    review_link = serializers.SerializerMethodField()
    
    class Meta:
        model = Business
        fields = ['id', 'name', 'address', 'google_review_url', 'place_id','review_link']
        read_only_fields = ['id']

    def get_review_link(self, obj):
        link = obj.get_review_link()
        return f"https://reviewbud.co/review/{link.token}"
    

class ReviewLinkSerializer(serializers.ModelSerializer):
    business_name = serializers.CharField(source='business.name', read_only=True)
    review_link = serializers.SerializerMethodField()

    class Meta:
        model = ReviewLink
        fields = ['id', 'business_name', 'token', 'click_count', 'review_link']

    def get_review_link(self, obj):
        return f"https://reviewbud.co/review/{obj.token}"
    
class CustomerReviewSerializer(serializers.ModelSerializer):
    business_name = serializers.CharField(source='business.name', read_only=True)

    class Meta:
        model = CustomerReview
        fields = [
            'id',
            'business_name',
            'rating',
            'feedback',
            'ai_review',
            'created_at',
            'ip_address'
        ]
        read_only_fields = ['ai_review', 'created_at', 'ip_address']
