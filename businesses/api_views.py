from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Business
from .serializers import BusinessSerializer

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def business_list(request):
    businesses = Business.objects.filter(owner=request.user)
    serializer = BusinessSerializer(businesses, many=True)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def business_create(request):
    serializer = BusinessSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(owner=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def business_detail(request, pk):
    business = get_object_or_404(Business, pk=pk, owner=request.user)
    serializer = BusinessSerializer(business)
    return Response(serializer.data)


@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def business_update(request, pk):
    business = get_object_or_404(Business, pk=pk, owner=request.user)
    serializer = BusinessSerializer(business, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def business_delete(request, pk):
    business = get_object_or_404(Business, pk=pk, owner=request.user)
    business.delete()
    return Response({"detail": "Business deleted"}, status=status.HTTP_204_NO_CONTENT)
