# from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response

from .serializer import ModelSerializer
import dill
import numpy as np
# Create your views here.


class ModelViewSet(viewsets.ModelViewSet):
    serializer_class = ModelSerializer
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):
        pregnancies = int(request.data['Pregnancies'])
        glucose = int(request.data['Glucose'])
        blood_pressure = int(request.data['BloodPressure'])
        skin_thickness = int(request.data['SkinThickness'])
        insulin = int(request.data['Insulin'])
        bmi = float(request.data['BMI'])
        diabetes_pedigree_function = float(request.data['DiabetesPedigreeFunction'])
        age = int(request.data['Age'])

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            input_data = np.array(
                [[pregnancies, glucose, blood_pressure, skin_thickness,
                  insulin, bmi, diabetes_pedigree_function, age]])

            with open('ml_model/diabetes_model.pkl', 'rb') as file:
                model = dill.load(file)
            map_ = {0: 'No Diabetes', 1: 'Diabetes'}
            prediction = model.predict(input_data)
            prediction = map_[prediction[0]]
            return Response({"detail": prediction}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

