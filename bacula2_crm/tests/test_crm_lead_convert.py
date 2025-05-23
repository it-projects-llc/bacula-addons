from odoo.exceptions import UserError
from odoo.tests.common import tagged, users

from odoo.addons.crm.tests.common import TestLeadConvertCommon


@tagged("lead_manage")
class TestLeadConvert(TestLeadConvertCommon):
    @users("user_sales_manager")
    def test_create_customer_01(self):
        self.lead_1.partner_name = ""
        with self.assertRaises(UserError):
            self.lead_1._create_customer()

    @users("user_sales_manager")
    def test_create_customer_02(self):
        self.lead_1.partner_name = "Test Company Customer"
        customer = self.lead_1._create_customer()
        self.assertEqual(customer.commercial_partner_id.name, "Test Company Customer")
