from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import SavedPassword
from .utils import password_strength
from .views import encrypt_password


class StrengthTests(TestCase):
    def test_levels(self):
        self.assertEqual(password_strength("abc"), "weak")
        self.assertEqual(password_strength("password123"), "weak")
        self.assertEqual(password_strength("Tr0ub4dor&3"), "medium")
        self.assertEqual(password_strength("k9#Vm2$xQp7!Lz4w"), "strong")


class VaultTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("ann", password="master-pass-1")
        self.other = User.objects.create_user("bob", password="other-pass-1")
        self.entry = SavedPassword.objects.create(
            user=self.user, website="example.com", username="ann@x.com",
            encrypted_password=encrypt_password("hunter2-hunter2"),
        )
        self.client.login(username="ann", password="master-pass-1")

    def test_reveal_needs_master_password(self):
        url = reverse("reveal_password", args=[self.entry.pk])
        bad = self.client.post(url, {"master_password": "nope"})
        self.assertEqual(bad.status_code, 403)
        ok = self.client.post(url, {"master_password": "master-pass-1"})
        self.assertEqual(ok.json()["password"], "hunter2-hunter2")

    def test_reveal_is_throttled(self):
        url = reverse("reveal_password", args=[self.entry.pk])
        for _ in range(5):
            self.client.post(url, {"master_password": "nope"})
        locked = self.client.post(url, {"master_password": "master-pass-1"})
        self.assertEqual(locked.status_code, 429)

    def test_edit_is_locked_until_master_password(self):
        url = reverse("edit_password", args=[self.entry.pk])
        self.assertTrue(self.client.get(url).context["locked"])
        self.client.post(url, {"action": "unlock", "master_password": "master-pass-1"})
        self.assertFalse(self.client.get(url).context["locked"])
        self.client.post(url, {
            "action": "save", "website": "new.com", "username": "ann",
            "password": "brand-new-pass-9", "url": "new.com", "category": "Work",
        })
        self.entry.refresh_from_db()
        self.assertEqual(self.entry.website, "new.com")
        self.assertEqual(self.entry.url, "https://new.com")

    def test_other_users_cannot_touch_entry(self):
        self.client.login(username="bob", password="other-pass-1")
        for name in ("edit_password", "reveal_password", "toggle_favorite"):
            r = self.client.post(reverse(name, args=[self.entry.pk]))
            self.assertEqual(r.status_code, 404)

    def test_toggle_favorite(self):
        self.client.post(reverse("toggle_favorite", args=[self.entry.pk]))
        self.entry.refresh_from_db()
        self.assertTrue(self.entry.is_favorite)

    def test_summary_counts_reused_and_weak(self):
        SavedPassword.objects.create(
            user=self.user, website="b.com", username="u",
            encrypted_password=encrypt_password("hunter2-hunter2"),
        )
        SavedPassword.objects.create(
            user=self.user, website="c.com", username="u",
            encrypted_password=encrypt_password("abc"),
        )
        s = self.client.get(reverse("vault_list")).context["summary"]
        self.assertEqual(s, {"total": 3, "reused": 2, "weak": 1})

from django.test import TestCase
