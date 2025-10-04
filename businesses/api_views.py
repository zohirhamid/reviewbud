from rest_framework import status, permissions
from rest_framework.decorators import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .serializers import BusinessSerializer
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
            serializer.save(owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class BusinessDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, id):
        business = get_object_or_404(Business, id=id, owner = request.user)
        serializer = BusinessSerializer(business)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class UpdateBusinessView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, id):
        business = get_object_or_404(Business, id=id, owner=request.user)
        serializer = BusinessSerializer(business, data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        business = get_object_or_404(Business, id=id, owner=request.user)
        business.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)