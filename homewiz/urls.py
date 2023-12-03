from django.urls import path
from django.views.generic import TemplateView, RedirectView

from .frontend.auth_views import LoginView, LogoutView, SignUpView
from .frontend.channel_views import ChannelListView, LeaveChannelView, CreateChannelView, JoinChannelView, \
    ChannelEditView
from .frontend.homework_views import TaskListView, CreateTaskView, ChangeHomeworkStatusView, TaskEditView
from .frontend.subject_views import AddSubjectView, EditSubjectView, DeleteSubjectView, GetSubjectsView

urlpatterns = [
    path('', RedirectView.as_view(url='/tasks'), name='index'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('signup/', SignUpView.as_view(), name='sign_up'),

    path('channels/', ChannelListView.as_view(), name='channel_list'),
    path('channel/leave/<uuid:channel_uuid>/', LeaveChannelView.as_view(), name='leave_channel'),
    path('channels/create/', CreateChannelView.as_view(), name='channel_create'),
    path('channels/join/', JoinChannelView.as_view(), name='channel_join'),
    path('channels/edit/<uuid:channel_uuid>/', ChannelEditView.as_view(), name='channel_edit'),

    path('channels/edit/<uuid:channel_uuid>/subjects/add/', AddSubjectView.as_view(), name='channel_edit_subject_add'),
    path('channels/edit/<uuid:channel_uuid>/subjects/<uuid:subject_uuid>/edit/', EditSubjectView.as_view(), name='channel_edit_subject_edit'),
    path('channels/edit/<uuid:channel_uuid>/subjects/<uuid:subject_uuid>/delete/', DeleteSubjectView.as_view(), name='channel_edit_subject_delete'),

    path('tasks/', TaskListView.as_view(), name='task_list'),
    path('tasks/create/', CreateTaskView.as_view(), name='task_create'),
    path('tasks/<uuid:task_uuid>/done/', ChangeHomeworkStatusView.as_view(), name='task_done'),
    path('tasks/<uuid:task_uuid>/edit/', TaskEditView.as_view(), name='task_edit'),
    path('subjects/get/', GetSubjectsView.as_view(), name='get_subjects'),
]