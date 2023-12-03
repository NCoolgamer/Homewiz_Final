from django.contrib import admin
from django.utils.html import format_html

from .form import SubjectForm
# Register your models here.
from .models import *

@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'code', 'user_count')

    def user_count(self, obj):
        return obj.users.count()

    user_count.short_description = 'User Count'

    def get_ordering(self, request):
        return ['owner', 'name']



@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    form = SubjectForm

    list_display = ('name', 'channel', 'color_field', 'id')

    def color_field(self, obj):

        # get the inverse of the color obj.color using simple math
        hex = obj.color.lstrip('#')
        r, g, b = tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))
        r = 255 - r
        g = 255 - g
        b = 255 - b
        hex = '#%02x%02x%02x' % (r, g, b)

        return format_html('<span style="background: {}; color: {}; padding: 2px;">{}</span>', obj.color, hex, hex)

    def get_ordering(self, request):
        return ['channel', 'name']

@admin.register(Homework)
class HomeworkAdmin(admin.ModelAdmin):
    list_display = ('description', 'subject', 'due_date', 'channel', 'id')

    def get_ordering(self, request):
        return ['due_date']


admin.site.register(HomeworkStatus)
