import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.contrib.auth.models import Group

# Homewiz (WIP name) is a project that aims to make the life of students easier. It is a homework tracker that is synced between groups, or "channels" of students.
#
# The main flow is this: group's leader creates a new channel, and starts adding homework to it. They also add subjects and set the schedule for the group.
#
# Then, students connect to that channel via a code, and can see the homework (and possibly add it, too, if the channel admin has enabled it). The homework is synced between all the students.
#
# Each student can set their own reminder settings for different subjects, and the app will notify them when the homework is due, or some time before it.
#
# Each homework has a subject, a description, a due date. It can also have a file(s) attached to it. For each student, it can also has a status (done/not done).

# define the user model from the settings if it has been changed
User = get_user_model()


# Create your models here.
# provide verbose names for the models
class Channel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='channels', verbose_name="Владелец")
    name = models.CharField(max_length=200, verbose_name="Название")
    users = models.ManyToManyField(User, related_name='channels_joined', verbose_name="Пользователи")
    # code is automatically generated when the channel is created
    code = models.CharField(max_length=20, unique=True, verbose_name="Код")

    def __str__(self):
        return f"{self.name} -> {self.owner}"

    class Meta:
        verbose_name = 'Канал'
        verbose_name_plural = 'Каналы'


class Subject(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name="Название")
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='subjects', verbose_name="Канал")
    color = models.CharField(max_length=7, default='#000000', verbose_name="Цвет")

    def __str__(self):
        return f"{self.name} -> {self.channel}"

    class Meta:
        verbose_name = 'Предмет'
        verbose_name_plural = 'Предметы'


class Homework(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='homework', verbose_name="Предмет")
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='homework', verbose_name="Канал")
    description = models.TextField(verbose_name="Описание")
    due_date = models.DateTimeField(verbose_name="Срок сдачи")

    def __str__(self):
        return f"'{self.description}' -> {self.subject}"

    class Meta:
        verbose_name = 'Задание'
        verbose_name_plural = 'Задания'


# homework completion status
class HomeworkStatus(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    homework = models.ForeignKey(Homework, on_delete=models.CASCADE, related_name='status', verbose_name="Задание")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='homework_status', verbose_name="Пользователь")
    done = models.BooleanField(default=False, verbose_name="Выполнено")

    def __str__(self):
        return f"'{self.homework}' {('+' if self.done else '-')} for {self.user}"

    class Meta:
        verbose_name = 'Статус задания'
        verbose_name_plural = 'Статусы задания'
