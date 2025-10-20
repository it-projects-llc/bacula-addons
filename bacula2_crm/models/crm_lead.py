from odoo import fields, models
from odoo.exceptions import UserError


class Lead(models.Model):
    _inherit = "crm.lead"

    date_closed = fields.Datetime(tracking=True)

    def _create_customer(self):
        if not self.partner_name:
            raise UserError(
                self.env._("Creating customer without company is not allowed")
            )
        return super()._create_customer()
