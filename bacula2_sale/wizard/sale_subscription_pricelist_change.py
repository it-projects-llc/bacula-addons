from odoo import api, fields, models


class SaleSubscriptionPricelistChange(models.TransientModel):
    _name = "sale.subscription.pricelist.change"
    _description = "Change pricelist for confirmed subscription"

    subscription = fields.Many2one("sale.order", required=True, readonly=True)
    new_pricelist = fields.Many2one("product.pricelist", required=True)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if "subscription" in fields_list:
            res["subscription"] = self.env.context.get("active_id")
            if "new_pricelist" in fields_list:
                sub = self.env["sale.order"].browse(res["subscription"])
                res["new_pricelist"] = sub.pricelist_id

        return res

    def action_change(self):
        for wizard in self:
            wizard.subscription.pricelist_id = wizard.new_pricelist
