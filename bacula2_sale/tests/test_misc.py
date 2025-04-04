from odoo.tests import Form

from odoo.addons.sale.tests.common import SaleCommon


class TestMisc(SaleCommon):
    def test_change_pricelist_wizard(self):
        self.sale_order.action_confirm()

        pricelist2 = self.env["product.pricelist"].create(
            {
                "name": "Test Pricelist 2",
            }
        )

        Wizard = self.env["sale.subscription.pricelist.change"].with_context(
            active_model=self.sale_order.name,
            active_id=self.sale_order.id,
        )
        form = Form(Wizard)

        # default pricelist is from sale order
        self.assertEqual(form.new_pricelist, self.sale_order.pricelist_id)

        form.new_pricelist = pricelist2
        wizard = form.save()
        wizard.action_change()

        self.assertEqual(self.sale_order.pricelist_id, pricelist2)
