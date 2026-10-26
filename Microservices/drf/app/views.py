from django.shortcuts import render
from rest_framework.response import Response
from .models import *
from .serializes import *
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .tokens import *
from .pagination import StudentPagination
from .services import fastapi_client, FastAPIError
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView

from rest_framework import status
from .services import fastapi_client, FastAPIError

# GET METHOD:
@api_view(['GET'])
def home(request):
    return Response({'status': 200, 'message': 'This is Home page'})

@api_view(['GET'])
def get_student(request):
    student = Student.objects.all()
    serialize = StudentSerializer(student, many=True)
    return Response({'status': 200, 'data': serialize.data})

#POST METHOD:

@api_view(['POST'])
def create_student(request):
    name = request.POST.get('name')
    age = request.POST.get('age')
    email = request.POST.get('email')
    number = request.POST.get('number')

    if request.method == 'POST':
        Student.objects.create(name=name, age=age, email=email, number=number)
        return Response({'status': 200, 'message': 'Student Created'})


@api_view(['POST'])
def createstudentJSON(request):
    name = request.data.get('name')
    age = request.data.get('age')
    email = request.data.get('email')
    number = request.data.get('number')

    if request.method == 'POST':
        Student.objects.create(name=name, age=age, email=email, number=number)
        return Response({'status': 200, 'message': 'Student Created'})

# SERIALIZER :

@api_view(['POST'])
def CreateStudentSerializer(request):
    data = request.data
    serialize = StudentSerializer(data=data)  # Here we doing de-serialization
    if serialize.is_valid():
        serialize.save()
        return Response({'message': 'succesfull'})
    else:
        return Response({'message': serialize.errors})




# # @api_view(['GET'])
# # @authentication_classes([TokenAuthentication])
# # @permission_classes([IsAuthenticated])
# # def dumy(request):
# #     return Response({'status': 200, 'message' : 'this is my dumy page',
# #                      "username" : request.user.username,
# #                      "email" : request.user.email,
# #                      "first_name" : request.user.first_name               
#     })

# PUT METHOD :

@api_view(['PUT'])
def UpdateStudent(request, id):
    try:
        student = Student.objects.get(id=id)
    except Student.DoesNotExist:
        return Response({'status': 404, 'message': 'Student not found'})

    serialize = StudentSerializer(student, data=request.data)
    if serialize.is_valid():
        serialize.save()
        return Response({'status': 200, 'message': 'Student Updated', 'data': serialize.data})
    else:
        return Response({'status': 400, 'message': serialize.errors})

# PATCH METHOD :

@api_view(['PATCH'])
def PatchStudent(request, id):
    try:
        student = Student.objects.get(id=id)
    except Student.DoesNotExist:
        return Response({'status': 404, 'message': 'Student not found'})

    serialize = StudentSerializer(student, data=request.data, partial=True)
    if serialize.is_valid():
        serialize.save()
        return Response({'status': 200, 'message': 'Student PATCH Updated', 'data': serialize.data})
    else:
        return Response({'status': 400, 'message': serialize.errors})



# PAGINATION :

@api_view(['GET'])
def get_student(request):
    students = Student.objects.all().order_by('id')

    paginator = StudentPagination() 
    page = paginator.paginate_queryset(students, request)

    serializer = StudentSerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)

# JWT AUTHENTICATION :

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def dumy(request):
    return Response({'tatus': 200, 'message' : 'this is my dumy page',
                     "username" : request.user.username,
                     "email" : request.user.email,
                     "first_name" : request.user.first_name          })



# TO FETCH TOKEN AND LOGIN :

# @api_view(['POST'])
# def login_user(request):
#     username = request.data.get('username')
#     password = request.data.get('password')

#     user = authenticate(username=username, password=password)

#     if user is not None:
#         refresh = RefreshToken.for_user(user)
#         return Response({
#             'message': 'Login successful',
#             'refresh': str(refresh),
#             'access': str(refresh.access_token),
#         })

#     return Response({'message': 'Invalid username or password'})

# CUSTOM TOKEN :

@api_view(['POST'])
def login_user(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)

    if user is not None:
        refresh = MyToken.for_user(user)
        return Response({
            'message': 'Login successful',
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })

    return Response({'message': 'Invalid username or password'})

# GENERIC VIEW :

# Create and read
class StudentGenericView(ListAPIView, CreateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer


# PUT, PATCH, RETRIEVE :
class StudentGenericRUDView(RetrieveAPIView, UpdateAPIView, DestroyAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    lookup_field = 'id'







# FASTAPI SERVICE CONNECTION :

# DJANGO CALLING FASTAPI (reusable client) :

# copy the caller's JWT so FastAPI can check it too (token propagation)
def forward_token(request):
    return {'Authorization': request.headers.get('Authorization', '')}

@api_view(['GET'])                       # (POST for assign_mentor)
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def fastapi_students(request):
    try:
        students = fastapi_client.get('/service/students/', headers=forward_token(request))
    except FastAPIError as e:
        return Response({'message': str(e)}, status=e.status_code or 502)
    return Response({'status': 200, 'data': students})


# assign a mentor (from FastAPI) to a student (in DRF)
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def assign_mentor(request, id):
    try:
        student = Student.objects.get(id=id)
    except Student.DoesNotExist:
        return Response({'message': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)

    mentor_id = request.data.get('mentor_id')
    if not mentor_id:
        return Response({'message': 'mentor_id is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
         mentor = fastapi_client.get(f'/mentor/{mentor_id}', headers=forward_token(request))     # <-- the call to FastAPI
    except FastAPIError as e:
        if e.status_code == 404:
            return Response({'message': 'Mentor not found in FastAPI service'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'message': str(e)}, status=e.status_code or 502)

    student.mentor_id = mentor['id']
    student.mentor_name = mentor['name']
    student.save()

    return Response({
        'message': 'Mentor assigned',
        'student': student.name,
        'mentor': mentor['name'],
    }, status=status.HTTP_200_OK)


# show a student together with live mentor details from FastAPI
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def student_mentor(request, id):
    try:
        student = Student.objects.get(id=id)
    except Student.DoesNotExist:
        return Response({'message': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)

    if student.mentor_id is None:
        return Response({'message': 'No mentor assigned yet'}, status=status.HTTP_404_NOT_FOUND)

    try:
        mentor = fastapi_client.get(f'/mentor/{student.mentor_id}', headers=forward_token(request))   # <-- the call to FastAPI
    except FastAPIError as e:
        if e.status_code == 404:
            return Response({'message': 'Mentor no longer exists in FastAPI service'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'message': str(e)}, status=e.status_code or 502)

    return Response({'student': student.name, 'mentor': mentor}, status=status.HTTP_200_OK)