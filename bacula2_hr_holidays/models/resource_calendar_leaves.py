from odoo import api, fields, models


class ResourceCalendarLeaves(models.Model):
    _inherit = "resource.calendar.leaves"

    country = fields.Many2one("res.country", domain="country_domain")
    country_domain = fields.Binary(compute="_compute_country_domain", compute_sudo=True)

    @api.depends("company_id")
    def _compute_country_domain(self):
        country_ids = {}
        for record in self:
            company = record.company_id
            if company.id not in country_ids:
                country_ids[company.id] = (
                    self.env["hr.employee"]
                    .search([("company_id", "=", company.id)])
                    .mapped("country_id")
                    .ids
                )

            record.country_domain = [("id", "in", country_ids[company.id])]
