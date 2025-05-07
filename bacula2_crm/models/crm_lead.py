from odoo import fields, models


class Lead(models.Model):
    _inherit = "crm.lead"

    date_closed = fields.Datetime(tracking=True)
