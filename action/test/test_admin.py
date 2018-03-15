from django.test import TestCase
from unittest import mock

from action.admin import ActionWebhookAdmin
from action.models import ActionWebhook


class ActionWebhookAdminTest(TestCase):
    def setUp(self):
        self.admin = ActionWebhookAdmin(model=ActionWebhook, admin_site=1)
        self.fields = ('zip', 'title', 'hook_type', 'data')
        self.fields_no_data = ('zip', 'title', 'hook_type')

    @mock.patch('django.contrib.admin.ModelAdmin.get_form')
    def test_get_form_create(self, super_get_form):
        request = mock.MagicMock()
        obj = None

        self.admin.get_form(request)

        super_get_form.assert_called_once_with(request, obj)
        self.assertEqual(self.admin.fields, self.fields_no_data)

    @mock.patch('action.admin.JSONEditorWidget')
    @mock.patch('django.contrib.admin.ModelAdmin.get_form')
    def test_get_form(self, super_get_form, json_widget):
        request = mock.MagicMock()
        obj = mock.MagicMock()
        obj.hook_type = 'get'
        obj.get_schema = mock.MagicMock()
        obj.get_schema.return_value = {'schema': 'itsaschema'}
        json_widget.return_value = 'json_widget'

        self.admin.get_form(request, obj)

        json_widget.assert_called_once_with({'schema': 'itsaschema'}, False)
        super_get_form.assert_called_once_with(
            request, obj, widgets={'data': 'json_widget'})
        self.assertEqual(self.admin.fields, self.fields)
