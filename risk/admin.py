from django.contrib import admin
from .models import Score


class ScoreAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
    list_filter = ('status', )
    readonly_fields = ("user", "status", "result")

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.user = request.user
        super(ScoreAdmin, self).save_model(request, obj, form, change)


admin.site.register(Score, ScoreAdmin)
