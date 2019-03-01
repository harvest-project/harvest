from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView


class TokenView(APIView):
    def get(self, request):
        try:
            token = Token.objects.get(user=request.user)
            return Response({'token': token.key})
        except Token.DoesNotExist:
            return Response({'token': None})

    def post(self, request):
        token, _ = Token.objects.get_or_create(user=request.user)
        return Response({'token': token.key})
