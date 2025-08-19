#--------------------------------------------   APIView------------------------------------------
from rest_framework.view import APIView
from rest_framework.response import Response
from rest_framework import status

class EmployeAPIView(APIView):
    """
    APIView pour gérer les employés.
    """

    def get(self, request, pk=None):
        """
        Récupère un employé par son ID ou tous les employés si aucun ID n'est fourni.
        """
        if pk:
            try:
                employe = Employe.objects.get(pk=pk)
                serializer = EmployeSerializer(employe)
                return Response(serializer.data)
            except Employe.DoesNotExist:
                return Response({"detail": "Employé non trouvé."}, status=status.HTTP_404_NOT_FOUND)
        else:
            employes = Employe.objects.all()
            serializer = EmployeSerializer(employes, many=True)
            return Response(serializer.data)

    def post(self, request):
        """
        Crée un nouvel employé.
        """
        serializer = EmployeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    


        class PresenceAPIView(APIView):
    """
    APIView pour gérer les présences.
    """

    def get(self, request, pk=None):
        """
        Récupère une présence par son ID ou toutes les présences si aucun ID n'est fourni.
        """
        if pk:
            try:
                presence = Presence.objects.get(pk=pk)
                serializer = PresenceSerializer(presence)
                return Response(serializer.data)
            except Presence.DoesNotExist:
                return Response({"detail": "Présence non trouvée."}, status=status.HTTP_404_NOT_FOUND)
        else:
            presences = Presence.objects.all()
            serializer = PresenceSerializer(presences, many=True)
            return Response(serializer.data)

    def post(self, request):
        """
        Crée une nouvelle présence.
        """
        serializer = PresenceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        """
        Met à jour une présence existante.
        """
        try:
            presence = Presence.objects.get(pk=pk)
            serializer = PresenceSerializer(presence, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Presence.DoesNotExist:
            return Response({"detail": "Présence non trouvée."}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        """
        Supprime une présence existante.
        """
        try:
            presence = Presence.objects.get(pk=pk)
            presence.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Presence.DoesNotExist:
            return Response({"detail": "Présence non trouvée."}, status=status.HTTP_404_NOT_FOUND)
        serializer = PresenceSerializer(presence)
        return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = PresenceSerializer(presence)
        return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = PresenceSerializer(presence)
        return Response(serializer.data, status=status.HTTP_200_OK) 



class RapportAPIView(APIView):
    """
    APIView pour gérer les rapports.
    """

    def get(self, request, pk=None):
        """
        Récupère un rapport par son ID ou tous les rapports si aucun ID n'est fourni.
        """
        if pk:
            try:
                rapport = Rapport.objects.get(pk=pk)
                serializer = RapportSerializer(rapport)
                return Response(serializer.data)
            except Rapport.DoesNotExist:
                return Response({"detail": "Rapport non trouvé."}, status=status.HTTP_404_NOT_FOUND)
        else:
            rapports = Rapport.objects.all()
            serializer = RapportSerializer(rapports, many=True)
            return Response(serializer.data)

    def post(self, request):
        """
        Crée un nouveau rapport.
        """
        serializer = RapportSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        """
        Met à jour un rapport existant.
        """
        try:
            rapport = Rapport.objects.get(pk=pk)
            serializer = RapportSerializer(rapport, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Rapport.DoesNotExist:
            return Response({"detail": "Rapport non trouvé."}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        """
        Supprime un rapport existant.
        """
        try:
            rapport = Rapport.objects.get(pk=pk)
            rapport.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Rapport.DoesNotExist:
            return Response({"detail": "Rapport non trouvé."}, status=status.HTTP_404_NOT_FOUND)                            




# class PresenceAPIView(APIView,PageNumberPagination):
#     serializer_class = PresenceSerializer
    
#     def get(self, request):
#         entity = models.objects.all()
#         results = self.paginate_queryset(entity, request, view= self)
#         serializer = PresenceSerializer(results, many=True)
#         return self.get_paginated_response(serializer.data)