from django.contrib import admin

from django_admin_json_editor.admin import JSONEditorWidget

from action.models import ActionWebhook


class ActionWebhookAdmin(admin.ModelAdmin):
    list_display = ('title', 'hook_type', 'zip')
    model = ActionWebhook

    def get_form(self, request, obj=None, **kwargs):
        self.fields = ('zip', 'title', 'hook_type', 'data')

        if obj and obj.hook_type:
            widget = JSONEditorWidget(obj.get_schema(obj.hook_type), False)
            form = super().get_form(request, obj, widgets={'data': widget},
                                    **kwargs)
        else:
            self.fields = tuple(x for x in self.fields if x != 'data')
            form = super().get_form(request, obj, **kwargs)
        return form

admin.site.register(ActionWebhook, ActionWebhookAdmin)
