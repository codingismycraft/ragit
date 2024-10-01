"""Tests the User Registry module."""
import datetime
import unittest

import ragit.libs.common as common
import ragit.libs.user_registry as user_registry
import ragit.libs.impl.query_executor as query_executor

# Aliases.
UserRegistry = user_registry.UserRegistry
QueryResponse = query_executor.QueryResponse


class TestUserRegistry(unittest.TestCase):
    """Tests the user registry."""

    def setUp(self):
        """Set the root directory for the registry db."""
        base_dir = common.get_testing_output_dir("sqlite_db", wipe_out=True)
        UserRegistry.set_rag_collection_name("some-rag-collection")
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
            UserRegistry.add_new_user(user_name_1, email_address_1,
                                      password * 50)

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

        invalid_user_names = [
            " asdf",
            "asdf*",
            "asdf_+",
            "Aadfa asdf"
        ]

        for name in invalid_user_names:
            try:
                UserRegistry.add_new_user(name, "junk@junk.com", password)
            except common.MyGenAIException as ex:
                self.assertIn("Invalid Name", str(ex))

    def test_inserting_messages(self):
        """Tests the inserting of messages to the db."""
        UserRegistry.create_db_if_needed()
        user_name = "john"
        email_address = "someone@someserver.com"
        password = "mypassword"
        UserRegistry.add_new_user(user_name, email_address, password)
        t1 = datetime.datetime.now()
        t2 = datetime.datetime.now()
        question = "what time it is?"
        response = QueryResponse(
            response="i have no idea..",
            temperature=0.6,
            max_tokens=1000,
            matches_count=3,
            prompt=question,
            matches=["abc"]
        )
        msg_id = UserRegistry.insert_message(
            user_name, t1, question, response, t2
        )
        expected = 1
        self.assertEqual(msg_id, expected)

        thumps_up, t1 = UserRegistry.get_thumps_up(msg_id)
        self.assertIsNone(thumps_up)
        self.assertIsNone(t1)

        UserRegistry.set_thumps_up(msg_id)
        thumps_up, t2 = UserRegistry.get_thumps_up(msg_id)
        self.assertEqual(thumps_up, 1)
        self.assertIsInstance(t2, str)

        UserRegistry.set_thumps_down(msg_id)
        thumps_up, t3 = UserRegistry.get_thumps_up(msg_id)
        self.assertEqual(thumps_up, 0)
        self.assertIsInstance(t3, str)

        # Test the get_all_queries
        queries = UserRegistry.get_all_queries()
        self.assertIsInstance(queries, list)
        for query in queries:
            self.assertIsInstance(query, dict)
            print(query)
