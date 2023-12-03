import re

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib import messages

from homewiz.models import Channel, Subject
from homewiz.utility import generate_code


# define frontend views for the app

@method_decorator(login_required, name='dispatch')
class AddSubjectView(View):
    def post(self, request, channel_uuid):
        # add the subject to the channel if the user is the owner, and if the subject form is correct
        channel = Channel.objects.get(id=channel_uuid)

        if channel.owner != request.user:
            messages.error(request, 'Вы не владелец этого канала')
            return redirect('channel_list')

        name = request.POST['subject_name']
        color = request.POST['subject_color']

        if name == '':
            messages.error(request, 'Название не может быть пустым')
            return redirect('channel_edit', channel_uuid=channel.id)

        if re.match(r'^#[0-9a-fA-F]{6}$', color) is None:
            messages.error(request, 'Цвет должен быть в формате #000000')
            return redirect('channel_edit', channel_uuid=channel.id)

        subject = Subject(name=name, channel=channel, color=color)

        subject.save()

        messages.success(request, 'Предмет ' + name + ' добавлен')

        return redirect('channel_edit', channel_uuid=channel_uuid)


@method_decorator(login_required, name='dispatch')
class EditSubjectView(View):
    def post(self, request, channel_uuid, subject_uuid):

        channel = Channel.objects.get(id=channel_uuid)

        if channel.owner != request.user:
            messages.error(request, 'Вы не владелец этого канала')
            return redirect('channel_list')

        # edit the subject if the subject is in the channel, and if the subject form is correct
        subject = Subject.objects.filter(id=subject_uuid).first()

        if subject is None:
            messages.error(request, 'Предмет не найден')
            return redirect('channel_edit', channel_uuid=channel.id)

        if subject.channel != channel:
            messages.error(request, 'Предмет не в этом канале')
            return redirect('channel_list')

        name = request.POST['subject_name']
        color = request.POST['subject_color']

        if name == '':
            messages.error(request, 'Название не может быть пустым')
            return redirect('channel_edit', channel_uuid=subject.channel.id)

        if re.match(r'^#[0-9a-fA-F]{6}$', color) is None:
            messages.error(request, 'Цвет должен быть в формате #000000')
            return redirect('channel_edit', channel_uuid=subject.channel.id)

        subject.name = name
        subject.color = color

        subject.save()

        messages.success(request, 'Предмет ' + name + ' изменен')

        return redirect('channel_edit', channel_uuid=subject.channel.id)


@method_decorator(login_required, name='dispatch')
class DeleteSubjectView(View):
    def post(self, request, channel_uuid, subject_uuid):
        channel = Channel.objects.get(id=channel_uuid)

        if channel.owner != request.user:
            messages.error(request, 'Вы не владелец этого канала')
            return redirect('channel_list')

        # delete the subject if the subject is in the channel, and if the subject form is correct
        subject = Subject.objects.get(id=subject_uuid)

        if subject.channel != channel:
            messages.error(request, 'Предмет не в этом канале')
            return redirect('channel_edit', channel_uuid=subject.channel.id)

        name = subject.name

        subject.delete()

        messages.success(request, 'Предмет ' + name + ' удален')

        return redirect('channel_edit', channel_uuid=subject.channel.id)


@method_decorator(login_required, name='dispatch')
class GetSubjectsView(View):
    def get(self, request):

        channel_uuid = request.GET['channel_uuid']
        channel = Channel.objects.get(id=channel_uuid)

        if channel is None:
            messages.error(request, 'Канал не найден')
            return redirect('channel_list')

        if channel.owner != request.user:
            messages.error(request, 'Вы не владелец этого канала')
            return redirect('channel_list')

        subjects = channel.subjects.all()

        subjects_list = []
        for subject in subjects:
            subjects_list.append({'id': subject.id, 'name': subject.name, 'color': subject.color})

        return JsonResponse({'subjects': subjects_list})
