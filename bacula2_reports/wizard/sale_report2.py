from datetime import datetime

from odoo import api, fields, models
from odoo.tools.date_utils import end_of


@api.model
def _period_get(self):
    self.env.cr.execute(
        """
SELECT to_char(d, 'YYYY-MM')
FROM (
    SELECT date_trunc('month', create_date) AS d
    FROM crm_lead
    GROUP by 1
) t
ORDER BY d
    """
    )
    res = []
    for row in self.env.cr.fetchall():
        res.append((row[0], row[0]))

    return res


class SaleReport2(models.TransientModel):
    _name = "sale.report2"
    _description = "Sales Reports 2"

    company = fields.Many2one("res.company", default=lambda self: self.env.company.id)
    period = fields.Selection(_period_get)
    opportunities_count_all = fields.Integer()
    opportunities_count_won = fields.Integer()

    def action_make_report(self):
        Leads = self.env["crm.lead"].with_context(active_test=False)

        for w in self:
            if not w.period:
                continue

            p = datetime.strptime(w.period, "%Y-%m")
            period = (p, end_of(p, "month"))

            w.opportunities_count_all = Leads.search_count(
                [
                    ("company_id", "=", w.company.id),
                    ("type", "=", "opportunity"),
                    ("create_date", ">=", period[0]),
                    ("create_date", "<", period[1]),
                ]
            )

            w.opportunities_count_won = Leads.search_count(
                [
                    ("company_id", "=", w.company.id),
                    ("type", "=", "opportunity"),
                    ("stage_id.is_won", "=", True),
                    ("create_date", ">=", period[0]),
                    ("create_date", "<", period[1]),
                ]
            )
