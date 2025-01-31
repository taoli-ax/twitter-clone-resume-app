from accounts.models import UserProfile
from testing.testcase import TestCase

class UserProfileTest(TestCase):
    def setUp(self):
        self.clear_cache()
        self.django_client, self.django=self.create_user_and_client('django')

    def test_user_profile(self):
        self.assertEqual(UserProfile.objects.count(), 0)
        django_profile = self.django.profile
        self.assertEqual(isinstance(django_profile, UserProfile), True)
        self.assertEqual(UserProfile.objects.count(),1)