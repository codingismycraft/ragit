"""Tests the User Registry module."""

import unittest

import mygenai.libs.common as common
import mygenai.libs.user_registry as user_registry

# Aliases.
UserRegistry = user_registry.UserRegistry


class TestUserRegistry(unittest.TestCase):
    """Tests the user registry."""

    def setUp(self):
        """Set the root directory for the registry db."""
        base_dir = common.get_testing_output_dir("sqlite_db", wipe_out=True)
        UserRegistry.set_base_dir(base_dir)

    def test_user_registry(self):
        """Tests inserting a new user."""
        UserRegistry.create_db_if_needed()
        user_name = "john"
        email_address = "someone@someserver.com"
        password = "mypassword"
        UserRegistry.add_new_user(user_name, email_address, password)

        user_name_1 = "someone else"
        email_address_1 = "someoneelse@someserver.com"

        # Try inserting same name.
        with self.assertRaises(common.MyGenAIException):
            UserRegistry.add_new_user(user_name, email_address_1, password)

        # Try inserting same email.
        with self.assertRaises(common.MyGenAIException):
            UserRegistry.add_new_user(user_name_1, email_address, password)

        # Try inserting very long user name.
        with self.assertRaises(common.MyGenAIException):
            UserRegistry.add_new_user(user_name * 30, email_address_1, password)

        # Try inserting very long email address.
        with self.assertRaises(common.MyGenAIException):
            UserRegistry.add_new_user(user_name_1, email_address * 50, password)

        # Try inserting very long password.
        with self.assertRaises(common.MyGenAIException):
            UserRegistry.add_new_user(user_name_1, email_address_1, password * 50)

        # Try getting the email for existing user.
        retrieved_email = UserRegistry.get_email_address(user_name)
        self.assertEqual(retrieved_email, email_address)

        # Try getting the email for non-existing user.
        with self.assertRaises(common.MyGenAIException):
            UserRegistry.get_email_address("junk-user")

        # Check valid password.
        UserRegistry.validate_password(user_name, password)

        # Check invalid password.
        with self.assertRaises(common.MyGenAIException):
            UserRegistry.validate_password(user_name, "junk")

        # Validate password for non existing user.
        with self.assertRaises(common.MyGenAIException):
            UserRegistry.validate_password("junk", "junk")

        # Try invalid email.
        with self.assertRaises(common.MyGenAIException):
            UserRegistry.add_new_user("new_user", "invalid-email", password)

        # Set invalid base directory.
        with self.assertRaises(common.MyGenAIException):
            UserRegistry.set_base_dir("junk")
