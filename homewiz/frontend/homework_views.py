import random
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.timezone import make_aware
from django.views import View
from django.contrib import messages

from homewiz.models import Channel, Homework, HomeworkStatus
from homewiz.utility import generate_code


# define frontend views for the app

@method_decorator(login_required, name='dispatch')
class TaskListView(View):
    def get(self, request):
        # get all tasks in all channels the user is in
        channels = Channel.objects.filter(users__id=request.user.id)

        is_admin = channels.filter(owner=request.user).exists()

        tasks = Homework.objects.filter(channel__in=channels).order_by('due_date')
        tasks_status = []

        current_date = timezone.now()

        # for each task, search for the user's status
        for task in tasks:
            status_e = "not_done"
            if task.due_date < current_date:
                status_e = "overdue"
            status = task.status.filter(user=request.user).first()
            if status is None:
                tasks_status.append((task, status_e))
            else:
                status_e = "done" if status.done else status_e
                tasks_status.append((task, status_e))

        context = {'tasks_status': tasks_status,
                   'is_channel_admin': is_admin}

        return render(request, 'frontend/task_list.html', context)


@method_decorator(login_required, name='dispatch')
class CreateTaskView(View):
    def get(self, request):
        # get all channels that the user is admin of
        channels = Channel.objects.filter(owner=request.user)

        context = {'channels': channels}

        return render(request, 'frontend/task_create.html', context)

    def post(self, request):
        # check if channel id, subject id, description, due date and due time are provided
        channel_id = request.POST['channel_uuid']
        subject_id = request.POST['subject_uuid']
        description = request.POST['description']
        due_date = request.POST['due_date']
        due_time = request.POST['due_time']

        if channel_id == '' or subject_id == '' or description == '' or due_date == '' or due_time == '':
            messages.error(request, 'Заполните все поля')
            return redirect('task_create')

        # check if the channel exists
        channel = Channel.objects.filter(id=channel_id).first()

        if channel is None:
            messages.error(request, 'Канал не найден')
            return redirect('task_create')

        # check if the user is admin of the channel
        if channel.owner != request.user:
            messages.error(request, 'Вы не владелец этого канала')
            return redirect('task_create')

        # check if the subject exists
        subject = channel.subjects.filter(id=subject_id).first()

        if subject is None:
            messages.error(request, 'Предмет не найден')
            return redirect('task_create')

        if subject.channel != channel:
            messages.error(request, 'Предмет не в этом канале')
            return redirect('task_create')

        # check if the due date is valid
        try:
            due_date = datetime.strptime(due_date, '%Y-%m-%d')
            due_time = datetime.strptime(due_time, '%H:%M')
        except ValueError:
            messages.error(request, 'Неверный формат даты')
            return redirect('task_create')

        timed_date = datetime.combine(due_date, due_time.time())

        # add moscow timezone to the date
        moscow_tz = timezone.get_default_timezone()
        # tzinfo
        due_date = make_aware(timed_date, moscow_tz)

        # create the task
        task = channel.homework.create(subject=subject, description=description, due_date=due_date)

        messages.success(request, 'Задание добавлено')

        return redirect('task_list')


@method_decorator(login_required, name='dispatch')
class TaskEditView(View):
    def get(self, request, task_uuid):
        # render the edit task page
        task = Homework.objects.filter(id=task_uuid).first()

        if task is None:
            messages.error(request, 'Задание не найдено')
            return redirect('task_list')

        if task.channel.owner != request.user:
            messages.error(request, 'Вы не владелец этого канала')
            return redirect('task_list')

        due_date = task.due_date.strftime('%Y-%m-%d')
        due_time = task.due_date.strftime('%H:%M')

        context = {'task': task, 'due_date': due_date, 'due_time': due_time}

        return render(request, 'frontend/task_edit.html', context)

    def post(self, request, task_uuid):
        # check if description, due date and time are provided, do not allow changing anything else
        task = Homework.objects.filter(id=task_uuid).first()

        if task is None:
            messages.error(request, 'Задание не найдено')
            return redirect('task_list')

        if task.channel.owner != request.user:
            messages.error(request, 'Вы не владелец этого канала')
            return redirect('task_list')

        # if 'save' in request.POST, edit task, if 'delete' in request.POST, delete task

        if 'delete' in request.POST:
            task.delete()
            messages.success(request, 'Задание удалено')

            return redirect('task_list')

        description = request.POST['description']
        due_date = request.POST['due_date']
        due_time = request.POST['due_time']

        if description == '' or due_date == '' or due_time == '':
            messages.error(request, 'Заполните все поля')
            return redirect('task_edit', task_uuid=task.id)

        # check if the due date is valid
        try:
            due_date = datetime.strptime(due_date, '%Y-%m-%d')
            due_time = datetime.strptime(due_time, '%H:%M')

        except ValueError:
            messages.error(request, 'Неверный формат даты')
            return redirect('task_edit', task_uuid=task.id)

        timed_date = datetime.combine(due_date, due_time.time())

        # add moscow timezone to the date
        moscow_tz = timezone.get_default_timezone()
        # tzinfo
        due_date = make_aware(timed_date, moscow_tz)

        # change the task
        task.description = description
        task.due_date = due_date
        task.save()

        messages.success(request, 'Задание изменено')

        return redirect('task_list')


@method_decorator(login_required, name='dispatch')
class ChangeHomeworkStatusView(View):
    def post(self, request, task_uuid):
        # check that the user is in the channel of the task
        task = Homework.objects.filter(id=task_uuid).first()

        if task is None:
            messages.error(request, 'Задание не найдено')
            return redirect('task_list')

        if not task.channel.users.filter(id=request.user.id).exists():
            messages.error(request, 'Вы не в этом канале')
            return redirect('task_list')

        # check if the user has a status for the task
        status = task.status.filter(user=request.user).first()

        if status is None:
            # create a status for the user
            status = HomeworkStatus.objects.create(user=request.user, homework=task)

        # change the status
        status.done = not status.done
        status.save()

        messages.success(request, 'Статус изменен')

        return redirect('task_list')