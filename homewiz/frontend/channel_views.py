import random
import re

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib import messages

from homewiz.models import Channel
from homewiz.utility import generate_code


# define frontend views for the app

@method_decorator(login_required, name='dispatch')
class ChannelListView(View):

    def get(self, request):
        # get current user's channels by filtering the channels with the user's id in the users
        channels = Channel.objects.filter(users__id=request.user.id)

        context = {'channels': channels}

        return render(request, 'frontend/channel_list.html', context)


@method_decorator(login_required, name='dispatch')
class LeaveChannelView(View):
    def post(self, request, channel_uuid):
        # get the channel with the uuid
        channel = Channel.objects.get(id=channel_uuid)

        # check if the user is in the channel
        if not channel.users.filter(id=request.user.id).exists():
            messages.error(request, 'Вы не в этом канале')
            return redirect('channel_list')

        if channel.users.count() > 1:
            # if the user was the owner, assign a random user as the new owner
            if channel.owner == request.user:
                users = channel.users.all().exclude(id=request.user.id)
                channel.owner = random.choice(users)

            # remove the user from the channel
            channel.users.remove(request.user)
            channel.save()

            messages.success(request, 'Вы покинули канал ' + channel.name)

        elif channel.users.count() == 1:
            channel.delete()
            messages.success(request, 'Канал ' + channel.name + ' удален')

        # redirect to channel list
        return redirect('channel_list')


@method_decorator(login_required, name='dispatch')
class CreateChannelView(View):
    def get(self, request):

        # get a random unused code
        code = generate_code()

        if code is None:
            messages.error(request, 'Не удалось создать канал')
            return redirect('channel_list')

        context = {'join_code': code}

        return render(request, 'frontend/channel_create.html', context)

    def post(self, request):
        # get the name and code from the form
        name = request.POST['name']
        code = request.POST['join_code']

        # check if the name is empty
        if name == '':
            messages.error(request, 'Имя не может быть пустым')
            return redirect('channel_create')

        # check if the code is empty
        if code == '':
            messages.error(request, 'Код не может быть пустым')
            return redirect('channel_create')

        # check if the code is valid in format XXXXX-XXXXX, where X is uppercase alphanumeric
        if re.match(r'^[A-Z0-9]{5}-[A-Z0-9]{5}$', code) is None:
            messages.error(request, 'Код неверен')
            return redirect('channel_create')

        # check if the code is unique
        if Channel.objects.filter(code=code).first() is not None:
            messages.error(request, 'Код уже используется')
            return redirect('channel_create')

        # create the channel
        channel = Channel.objects.create(name=name, code=code, owner=request.user)

        # add the user to the channel
        channel.users.add(request.user)

        messages.success(request, 'Канал ' + channel.name + ' создан')

        # redirect to channel list
        return redirect('channel_list')


@method_decorator(login_required, name='dispatch')
class JoinChannelView(View):
    def post(self, request):
        # get the code from the form
        code = request.POST['join_code']

        # check if the code is empty
        if code == '':
            messages.error(request, 'Код не может быть пустым')
            return redirect('channel_list')

        # get the channel with the code
        channel = Channel.objects.filter(code=code).first()

        # check if the channel exists
        if channel is None:
            messages.error(request, 'Канал не найден')
            return redirect('channel_list')

        # check if the user is already in the channel
        if channel.users.filter(id=request.user.id).exists():
            messages.error(request, 'Вы уже в этом канале')
            return redirect('channel_list')

        # add the user to the channel
        channel.users.add(request.user)

        messages.success(request, 'Вы присоединились к каналу ' + channel.name)

        # redirect to channel list
        return redirect('channel_list')


@method_decorator(login_required, name='dispatch')
class ChannelEditView(View):
    def get(self, request, channel_uuid):
        channel = Channel.objects.get(id=channel_uuid)

        if channel is None:
            messages.error(request, 'Канал не найден')
            return redirect('channel_list')

        # if user is not the owner, redirect to channel list
        if channel.owner != request.user:
            messages.error(request, 'Вы не владелец этого канала')
            return redirect('channel_list')

        context = {'channel': channel}
        return render(request, 'frontend/channel_edit.html', context)

    def post(self, request, channel_uuid):
        # if form contains name, change only the name of the channel.
        # if form contains user_id, make the user with that id the owner of the channel

        channel = Channel.objects.get(id=channel_uuid)

        if channel is None:
            messages.error(request, 'Канал не найден')
            return redirect('channel_list')

        # if user is not the owner, redirect to channel list
        if channel.owner != request.user:
            messages.error(request, 'Вы не владелец этого канала')
            return redirect('channel_list')

        if 'name' in request.POST:
            name = request.POST['name']
            if name == '':
                messages.error(request, 'Имя не может быть пустым')
                return redirect('channel_edit', channel_uuid=channel_uuid)
            channel.name = name
            channel.save()
            messages.success(request, 'Имя канала изменено')
            return redirect('channel_edit', channel_uuid=channel_uuid)

        if 'user_id' in request.POST:
            user_id = request.POST['user_id']
            user = channel.users.filter(id=user_id).first()
            if user is None:
                messages.error(request, 'Пользователь не найден')
                return redirect('channel_edit', channel_uuid=channel_uuid)
            channel.owner = user
            channel.save()
            messages.success(request, 'Владелец канала изменен')
            return redirect('channel_list')

        messages.error(request, 'Неверный запрос')
        return redirect('channel_edit', channel_uuid=channel_uuid)
