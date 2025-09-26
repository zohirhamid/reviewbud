from rest_framework import serializers
from .models import Business, ReviewLink

class BusinessSerializer(serializers.ModelSerializer):
    review_link = serializers.SerializerMethodField()

    class Meta:
        model = Business
        fields = [
            "id",
            "name",
            "address",
            "google_review_url",
            "created_at",
            "is_active",
            "review_link",
        ]

        read_only_fields = ["id", "created_at", "owner", "review_link"]

    def get_review_link(self, obj):
        # check if link exists
        link = obj.get_review_link()
        return {
            "token": str(link.token),
            "url": link.get_absolute_url(),
            "click_count": link.click_count,
        }