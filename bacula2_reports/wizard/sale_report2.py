from odoo import api, fields, models


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

    period = fields.Selection(_period_get)

    def action_make_report(self):
        pass
