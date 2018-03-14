# from django.views import View
# from django.http import JsonResponse
#
# from action.models import ActionWebhook
#
#
# class ActionWebhookView(View):
#     def get(self, request):
#         return JsonResponse({'some': 'data'})
#
#
# class ActionWebhookSchemaView(View):
#     def get(self, request, **kwargs):
#         schema_type = kwargs.get('schema_type', '')
#
#         if schema_type:
#             return JsonResponse(ActionWebhook().get_schema(schema_type))
