from rest_framework.views import APIView
from rest_framework.response import Response


class Health(APIView):
    def get(self, request):
        return Response({
            "service": "catalog-service",
            "status": "ok",
        })
