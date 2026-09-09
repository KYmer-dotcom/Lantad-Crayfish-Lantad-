"""
White-Box Unit Tests for Accounts & Security Middleware (Pillar 1)
"""
import base64
from django.test import TestCase
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from apps.accounts.access import is_owner, is_customer, is_rider, ensure_not_customer
from apps.sales.paymongo_service import get_auth_header
from apps.sales.models import PaymentSetting

User = get_user_model()


class SecurityAndAccessControlTestCase(TestCase):
    """
    White-Box Unit Tests for Security Guards, Authentication, and RBAC
    """

    def setUp(self):
        self.owner_user = User.objects.create_user(
            username='farm_owner',
            password='Password123!',
            role=User.Role.OWNER,
            phone='09171112233'
        )
        self.customer_user = User.objects.create_user(
            username='commercial_buyer',
            password='Password123!',
            role=User.Role.CUSTOMER,
            phone='09174445566'
        )
        self.rider_user = User.objects.create_user(
            username='delivery_rider',
            password='Password123!',
            role=User.Role.RIDER,
            phone='09177778899'
        )

    def test_tc_wsec001_owner_privilege_sync(self):
        """TC-WSec001: User model save() synchronizes is_staff privilege for Owner role."""
        self.assertTrue(self.owner_user.is_staff)
        self.assertFalse(self.customer_user.is_staff)
        self.assertFalse(self.rider_user.is_staff)

        # Switch customer to owner and verify dynamic synchronization
        self.customer_user.role = User.Role.OWNER
        self.customer_user.save()
        self.assertTrue(self.customer_user.is_staff)

    def test_tc_wsec002_role_predicate_evaluations(self):
        """TC-WSec002: Deterministic evaluation of role predicates (is_owner, is_customer, is_rider)."""
        self.assertTrue(is_owner(self.owner_user))
        self.assertFalse(is_owner(self.customer_user))
        self.assertFalse(is_owner(self.rider_user))

        self.assertTrue(is_customer(self.customer_user))
        self.assertFalse(is_customer(self.owner_user))

        self.assertTrue(is_rider(self.rider_user))
        self.assertFalse(is_rider(self.owner_user))

    def test_tc_wsec003_rbac_guard_interception(self):
        """TC-WSec003: ensure_not_customer guard intercepts unauthorized roles with PermissionDenied."""
        # Owner should pass without exception
        try:
            ensure_not_customer(self.owner_user)
        except PermissionDenied:
            self.fail("ensure_not_customer raised PermissionDenied unexpectedly for owner.")

        # Customer role must raise PermissionDenied
        with self.assertRaises(PermissionDenied) as ctx_cust:
            ensure_not_customer(self.customer_user)
        self.assertIn("Customers cannot access this section", str(ctx_cust.exception))

        # Rider role must raise PermissionDenied
        with self.assertRaises(PermissionDenied) as ctx_rider:
            ensure_not_customer(self.rider_user)
        self.assertIn("Riders only have access to the Driver Portal", str(ctx_rider.exception))

    def test_tc_wsec004_paymongo_auth_header_encoding(self):
        """TC-WSec004: PayMongo HTTP Basic Authorization Base64 header encoding."""
        test_secret = "sk_test_mock_secret_key_12345"
        headers = get_auth_header(secret_key=test_secret)

        self.assertEqual(headers["Content-Type"], "application/json")
        self.assertEqual(headers["accept"], "application/json")

        expected_b64 = base64.b64encode(f"{test_secret}:".encode('utf-8')).decode('utf-8')
        self.assertEqual(headers["Authorization"], f"Basic {expected_b64}")

    def test_tc_wsec005_payment_setting_singleton(self):
        """TC-WSec005: PaymentSetting singleton retrieval and parameter persistence."""
        setting1 = PaymentSetting.get_settings()
        setting1.gcash_number = "09998887777"
        setting1.paymongo_public_key = "pk_test_sample_public"
        setting1.save()

        setting2 = PaymentSetting.get_settings()
        self.assertEqual(setting1.id, setting2.id)
        self.assertEqual(setting2.gcash_number, "09998887777")
        self.assertEqual(setting2.paymongo_public_key, "pk_test_sample_public")
        self.assertEqual(PaymentSetting.objects.count(), 1)
