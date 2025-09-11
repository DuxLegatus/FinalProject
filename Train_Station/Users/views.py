from rest_framework.views import APIView
from .serializers import RegisterSerializer,LoginSerializer,LogoutSerializer
from rest_framework.response import Response
from rest_framework import status

class RegisterView(APIView):
    serializer_class = RegisterSerializer
    def post(self,request):
        serializer = self.serializer_class(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail":"user registered succesfully"},status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    serializer_class = LoginSerializer  
    def post(self,request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            return Response({
                "access":serializer.validated_data["access"],
                "refresh":serializer.validated_data["refresh"]
            })
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    

class LogoutView(APIView):
    serializer_class = LogoutSerializer
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Successfully logged out."})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
