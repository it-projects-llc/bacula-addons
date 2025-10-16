from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestMinimal(TransactionCase):
    def test_eval_context(self):
        action = self.env["ir.actions.server"].create(
            {
                "name": "TestAction",
                "model_id": self.env.ref("base.model_res_partner").id,
                "model_name": "res.partner",
                "state": "code",
                "code": 'record.write({"comment": "test"})',
            }
        )

        ectx = self.env["ir.actions.server"]._get_eval_context(action)

        # in previous versions of Odoo, b64* methods did not exist
        self.assertEqual(ectx["b64encode"](b"a"), b"YQ==")
        self.assertEqual(ectx["b64decode"](b"YQ=="), b"a")

        stack = ectx["get_stack"]()
        self.assertIn("test_eval_context", stack)

        self.assertEqual(
            "https://www.somerandom.com/?name=Something%20Cool",
            ectx["requote_uri"]("https://www.somerandom.com/?name=Something Cool"),
        )

        self.assertIn("Cerb", ectx)
