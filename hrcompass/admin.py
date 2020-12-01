from django.contrib import admin

from .models import Status, Kind, Taskname
# Register your models here.
admin.site.register(Status)

class KindAdmin(admin.ModelAdmin):
    list_display = ('kind', 'is_active')
admin.site.register(Kind, KindAdmin)
admin.site.register(Taskname)
