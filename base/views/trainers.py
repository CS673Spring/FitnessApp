from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status

from rest_framework.status import *
import os
from django.http import JsonResponse

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from base.models import Trainee, Trainer, Review, Payment, File, Note
from base.serializers import ReviewSerializer, TrainerSerializer, PaymentSerializer, ChatSerializer, NoteSerializer,\
    TrainerSerializerWithName, TraineeSerializerWithAvatar

param_keyword = openapi.Parameter('keyword', openapi.IN_QUERY, description="test manual param",
                                  type=openapi.TYPE_STRING)
param_page = openapi.Parameter('page', openapi.IN_QUERY, description="test manual param", type=openapi.TYPE_INTEGER)
param_id = openapi.Parameter('id', openapi.IN_QUERY, description="test manual param", type=openapi.TYPE_STRING)
trainer_response = openapi.Response('response description', TrainerSerializer)
trainers_response = openapi.Response('response description', TrainerSerializer(many=True))
payments_response = openapi.Response('response description', PaymentSerializer(many=True))
chats_response = openapi.Response('response description', ChatSerializer(many=True))
notes_response = openapi.Response('response description', NoteSerializer(many=True))


@swagger_auto_schema(methods=['get'], manual_parameters=[param_keyword, param_page], responses={200: trainers_response})
@api_view(['GET'])
# get the information of trainer
def getTrainers(request):
    query = request.query_params.get('keyword')
    if query is None:
        query = ''

    trainers = Trainer.objects.filter(
        first_name__icontains=query).order_by('-createdAt')
    # TODO search both first and last
    # trainers += Trainer.objects.filter(
    #     last_name__icontains=query).order_by('-createdAt')

    page = request.query_params.get('page')
    paginator = Paginator(trainers, 5)

    try:
        trainers = paginator.page(page)
    except PageNotAnInteger:
        trainers = paginator.page(1)
    except EmptyPage:
        trainers = paginator.page(paginator.num_pages)

    if page is None:
        page = 1

    page = int(page)
    serializer = TrainerSerializer(trainers, many=True)
    return Response({'trainers': serializer.data, 'page': page, 'pages': paginator.num_pages})


@swagger_auto_schema(methods=['get'], manual_parameters=[param_id], responses={200: trainer_response})
@api_view(['GET'])
# get the trainer by trainer_id (to get the user id)
def getTrainerById(request, pk):
    trainer = Trainer.objects.get(_id=pk)
    serializer = TrainerSerializerWithName(trainer, many=False)
    return Response(serializer.data)


@swagger_auto_schema(methods=['get'], manual_parameters=[param_id], responses={200: trainers_response})
@api_view(['GET'])
def getTopTrainers(request):
    trainers = Trainer.objects.filter(rating__gte=4).order_by('-rating')[0:5]
    serializer = TrainerSerializer(trainers, many=True)
    return Response(serializer.data)


@swagger_auto_schema(methods=['put', 'patch'], manual_parameters=[param_id], responses={200: 'Image was uploaded'})
@api_view(['PUT', 'PATCH'])
@permission_classes([IsAdminUser])
# TODO
# make sure this image can upload
def uploadImage(request):
    pass


@swagger_auto_schema(methods=['delete'], manual_parameters=[param_id])
@api_view(['DELETE'])
@permission_classes([IsAdminUser])
# Delete the corresponding trainer
def deleteTrainer(request, pk):
    trainer = Trainer.objects.get(_id=pk)
    trainer.delete()
    return Response({'Trainer delete'})


@swagger_auto_schema(methods=['post'], manual_parameters=[param_id], request_body=ReviewSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
# create the review of the trainer
def createTrainerReview(request, pk):
    data = request.data
    # to get trainee from access token
    trainee_id = request.user.id
    trainee = Trainee.objects.get(_id=trainee_id)
    trainer = Trainer.objects.get(_id=pk)

    if trainer.review_set.filter(trainee=trainee).first():
        return Response({'detail': 'This trainer is already reviewed'}, status=status.HTTP_400_BAD_REQUEST)
    elif data['rating'] is None:
        return Response({'detail': 'Please select rating'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        Review.objects.create(
            trainee=trainee,
            trainer=trainer,
            name=trainee.user.username,
            rating=data['rating'],
            comment=data['comment'],
        )

        reviews = trainer.review_set.all()
        trainer.numReviews = len(reviews)

        total = 0
        for i in reviews:
            total += i.rating

        trainer.rating = total/len(reviews)
        trainer.save()

        return Response({'Review Add'})


@swagger_auto_schema(methods=['post'], request_body=PaymentSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createPayment(request):
    data = request.data
    # get the trainer from the token
    trainer_id = request.user.trainer.pk
    trainer = Trainer.objects.get(_id=trainer_id)

    # try:
    payment = Payment.objects.create(
        trainer=trainer,
        price1=data['price1'],
        price2=data['price2'],
        price3=data['price3'],
        description1=data['description1'],
        description2=data['description2'],
        description3=data['description3'],
    )
    serializer = PaymentSerializer(payment, many=False)
    return Response(serializer.data)


@swagger_auto_schema(methods=['get'], responses={200: payments_response})
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getMyPayment(request):
    # get the trainer from the token
    trainer_id = request.user.trainer.pk
    payment = Payment.objects.get(trainer___id=trainer_id)
    if payment is None:
        return Response({'detail': 'Payment does not exist'}, status=HTTP_404_NOT_FOUND)
    serializer = PaymentSerializer(payment, many=False)
    return Response(serializer.data)


@swagger_auto_schema(methods=['get'], responses={200: payments_response})
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getMyPaymentById(request, pk):
    payment = Payment.objects.get(trainer___id=pk)
    if payment is None:
        return Response({'detail': 'Payment does not exist'}, status=HTTP_404_NOT_FOUND)
    serializer = PaymentSerializer(payment, many=False)
    return Response(serializer.data)


@swagger_auto_schema(methods=['get'], responses={200: chats_response})
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getTrainerChats(request):
    # get the trainer from the token
    trainer_id = request.user.trainer.pk
    obj = Trainer.objects.filter(_id=trainer_id).first()
    # get the chat of trainer
    chat = obj.chat_set.all()
    if chat is None:
        return Response({'detail': 'Order does not exist'}, status=HTTP_404_NOT_FOUND)
    serializer = ChatSerializer(chat, many=True)
    return Response(serializer.data)


@swagger_auto_schema(methods=['get'], responses={200: notes_response})
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getMyNotes(request):
    # get the trainer from the token
    trainer_id = request.user.trainer.pk
    obj = Trainer.objects.filter(_id=trainer_id).first()
    # duplicate notes are displayed only once
    note = obj.note_set.all().values('trainee').distinct()
    list_trainees = list(set([i['trainee'] for i in note]))
    # get the trainee in the list
    trainee = Trainee.objects.filter(_id__in=list_trainees)

    serializer = TraineeSerializerWithAvatar(trainee, many=True)

    if note is None:
        return Response({'detail': 'Note does not exist'}, status=HTTP_404_NOT_FOUND)
    return Response(serializer.data)


@swagger_auto_schema(methods=['delete'], responses={204: 'Notification deleted'})
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
# delete the note from trainer side
def deleteMyNotes(request):
    # get the trainer from the token
    trainer_id = request.user.trainer.pk
    trainee_id = request.data['trainee_id']
    count = Note.objects.filter(trainer___id=trainer_id, trainee=trainee_id).delete()
    return Response({'message': 'Notification were deleted successfully!'}, status=HTTP_204_NO_CONTENT)


@swagger_auto_schema(methods=['post'])
@api_view(['POST'])
@permission_classes([IsAuthenticated])
# upload the video
def index(request):
    file = request.FILES['file'].read()
    fileName = request.POST['filename']
    existingPath = request.POST['existingPath']
    end = request.POST['end']
    nextSlice = request.POST['nextSlice']

    trainer_id = request.user.trainer.pk
    trainer = Trainer.objects.get(_id=trainer_id)
    if file == "" or fileName == "" or existingPath == "" or end == "" or nextSlice == "":
        res = JsonResponse({'data': 'Invalid Request'})
        return res
    else:
        if existingPath == 'null':
            path = 'media/' + fileName
            with open(path, 'wb+') as destination:
                destination.write(file)
            FileFolder = File()
            FileFolder.existingPath = fileName
            FileFolder.trainer = trainer
            FileFolder.eof = end
            FileFolder.name = fileName
            FileFolder.save()
            if int(end):
                res = JsonResponse({'data': 'Uploaded Successfully', 'existingPath': fileName})
            else:
                res = JsonResponse({'existingPath': fileName})
            return res

        else:
            path = 'media/' + existingPath
            model_id = File.objects.get(existingPath=existingPath)
            if model_id.name == fileName:
                if not model_id.eof:
                    with open(path, 'ab+') as destination:
                        destination.write(file)
                    if int(end):
                        model_id.trainer = trainer
                        model_id.eof = int(end)
                        model_id.save()
                        res = JsonResponse({'data': 'Uploaded Successfully', 'existingPath': model_id.existingPath})
                    else:
                        res = JsonResponse({'existingPath': model_id.existingPath})
                    return res
                else:
                    res = JsonResponse({'data': 'EOF found. Invalid request'})
                    return res
            else:
                res = JsonResponse({'data': 'No such file exists in the existingPath'})
                return res


@swagger_auto_schema(methods=['get'])
@api_view(['GET'])
@permission_classes([IsAuthenticated])
# get the video path
def getIndex(request):
    # get the trainer from the token
    trainer_id = request.user.trainer.pk
    obj = File.objects.filter(trainer___id=trainer_id).values('name')
    x = list(os.path.join('http://35.227.26.131:8000/media', obj[i]['name']) for i in range(len(obj)))
    return Response(x)


@swagger_auto_schema(methods=['put'], responses={201: 'Payment updated'})
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
# update the payment
def updatePayment(request):
    # get the trainer from the token
    trainer_id = request.user.trainer.pk
    payment = Payment.objects.get(trainer___id=trainer_id)

    data = request.data

    payment.price1 = data['price1']
    payment.price2 = data['price2']
    payment.price3 = data['price3']
    payment.description1 = data['description1']
    payment.description2 = data['description2']
    payment.description3 = data['description3']

    payment.save()

    serializer = PaymentSerializer(payment, many=False)
    return Response(serializer.data)


@swagger_auto_schema(methods=['get'])
@api_view(['GET'])
@permission_classes([IsAuthenticated])
# get the video by the Trainer_id
def getIndexByid(request, pk):
    obj = File.objects.filter(trainer___id=pk).values('name')
    x = list(os.path.join('http://35.227.26.131:8000/media', obj[i]['name']) for i in range(len(obj)))
    return Response(x)