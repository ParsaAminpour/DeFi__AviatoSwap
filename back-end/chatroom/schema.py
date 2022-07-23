from graphene_django import DjangoObjectType
from graphene_django import DjangoListField
import graphene
from .models import Message, Room
from swap.models import User, Wallet
from datetime import datetime as dt
from swap.models import User

class MessageType(DjangoObjectType):
    class Meta:
        model = Message
        fields = '__all__'

class RoomType(DjangoObjectType):
    class Meta:
        model = Room
        fields = ('name','info')        

class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ('id', 'username')

class WalletType(DjangoObjectType):
    class Meta:
        model = Wallet
        fields = ('address', 'balance')

class Query(graphene.ObjectType):
    all_rooms = graphene.List(
        RoomType ,id=graphene.Int())

    all_messages = graphene.List(
        MessageType, id=graphene.Int()
    )
    
    all_users = graphene.List(
        UserType, id = graphene.Int())


    def resolve_all_romos(root, info, id):
        return Room.objects.get(pk=id)

    def resolve_all_messages(root, info, id):
        return Room.objects.get(pk=id).message.all()
    
    def resolve_all_users(root, info, id):
        return Room.objects.get(pk=1).online.all()


class RoomMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        name = graphene.String(required=True)
    
    room = graphene.Field(RoomType)

    @classmethod
    def mutate(cls, root, info, name, id):
        room = Room.objects.get(pk=id)
        room.name = name
        room.save()
        return cls(room=room)


class MessageMutation(graphene.Mutation):
    class Arguments:
        message = graphene.String()
        owner = graphene.Int()
    
    message = graphene.Field(MessageType)

    @classmethod
    def mutate(cls, root, info, message, owner):
        message = Message.objects.create(
            message=message, time=dt.now(),
            owner = User.objects.get(pk=owner) 
        )
        message.save()
        return cls(message=message)



class Mutation(graphene.ObjectType):
    change_room = RoomMutation.Field()
    add_message = MessageMutation.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
