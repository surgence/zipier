from django.test import TestCase
from model_mommy import mommy


class ActionWebhookTest(TestCase):

    def test_str(self):
        zipp = mommy.make('zip.Zip', title='Zip title')
        self.assertEqual(str(zipp), u'Zip title')
