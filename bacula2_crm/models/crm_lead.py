from odoo import _, fields, models
from odoo.exceptions import UserError


class Lead(models.Model):
    _inherit = "crm.lead"

    date_closed = fields.Datetime(tracking=True)

    def _create_customer(self):
        if not self.partner_name:
            raise UserError(_("Creating customer without company is not allowed"))
        return super()._create_customer()
