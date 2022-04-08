from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Source, Station, Parameter, StationBySource, ParamatersOfStationBySource

# Register your models here.
@admin.register(User)
class UserAdmin(BaseUserAdmin):

    add_fieldsets = (
        (None, {
            'fields': ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
        }),
    )
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff',
         'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    list_display = ['username', 'email', 'first_name',
                    'last_name', 'is_active', 'is_staff']

    def __init__(self, *args, **kwargs):
        super(BaseUserAdmin, self).__init__(*args, **kwargs)
        BaseUserAdmin.list_display = list(BaseUserAdmin.list_display)


admin.register(UserAdmin)


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):

    fieldsets = (
        (None, {
            'fields': ('name',)
        }),
        ('Details', {
            'fields': ('url', 'infos')
        })
    )

    list_display = ['name', 'url', 'infos']

admin.register(Source, SourceAdmin)


@admin.register(Station)
class StationAdmin(admin.ModelAdmin):

    fieldsets = (
        (None, {
            'fields': ('name',)
        }),
        ('Details', {
            'fields': ('infos', 'latitude', 'longitude', 'height')
        })
    )

    list_display = ['name', 'infos', 'latitude', 'longitude', 'height']

admin.register(Station, StationAdmin)


@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):

    fieldsets = (
        (None, {
            'fields': ('name',)
        }),
        ('Details', {
            'fields': ('infos',)
        })
    )

    list_display = ['name', 'infos']

admin.register(Parameter, ParameterAdmin)


@admin.register(StationBySource)
class StationBySourceAdmin(admin.ModelAdmin):

    list_display = ['source', 'station']

admin.register(StationBySource, StationBySourceAdmin)
