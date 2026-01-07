from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .serializers import BusinessSerializer, ReviewLinkSerializer, CustomerReviewSerializer
from .models import Business, ReviewLink, CustomerReview

class DashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        queryset = Business.objects.filter(owner = request.user) # multiple rows
        serializer = BusinessSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CreateBusinessView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = BusinessSerializer(data=request.data)
        if serializer.is_valid():
            business = serializer.save(owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class BusinessDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, id):
        business = get_object_or_404(Business, id=id, owner=request.user)
        serializer = BusinessSerializer(business)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, id):
        business = get_object_or_404(Business, id=id, owner=request.user)
        serializer = BusinessSerializer(business, data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        business = get_object_or_404(Business, id=id, owner=request.user)
        business.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class ReviewLinkDetailView(APIView): # read only 'GET'
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, id):
        business = get_object_or_404(Business, id=id, owner = request.user)
        reviewlink = business.get_review_link()
        serializer = ReviewLinkSerializer(reviewlink)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SubmitReviewView(APIView):
    """Public endpoint for submitting reviews via token link"""

    def post(self, request, token):
        review_link = get_object_or_404(ReviewLink, token=token)
        serializer = CustomerReviewSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(
                business=review_link.business,
                review_link=review_link,
                ip_address=self.get_client_ip(request)
            )
            review_link.increment_clicks()  # optional: track form submissions
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class ReviewListView(APIView):
    """List all reviews for the current user's businesses"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        reviews = CustomerReview.objects.filter(
            business__owner=request.user
        ).select_related('business', 'review_link')
        serializer = CustomerReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)