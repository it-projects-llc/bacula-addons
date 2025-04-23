import json
from collections import defaultdict
from datetime import timedelta

from odoo import api, fields, models
from odoo.tools.date_utils import end_of, start_of

from ..tools import prepare_pipeline_chart


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

    period_start = fields.Date(
        default=lambda self: fields.Date.today() - timedelta(days=30)
    )
    period_end = fields.Date(default=lambda self: fields.Date.today())
    opportunities_count_all = fields.Integer()
    opportunities_count_won = fields.Integer()
    opportunities_emails = fields.Text()
    pipeline_chart = fields.Char(default=json.dumps({"div": "", "script": ""}))

    def action_make_report(self):
        Leads = self.env["crm.lead"].with_context(active_test=False)

        for w in self:
            if not w.period_start or not w.period_end:
                continue

            period = (
                start_of(fields.Datetime.to_datetime(w.period_start), "hour"),
                end_of(fields.Datetime.to_datetime(w.period_end), "hour"),
            )

            records = Leads.search(
                [
                    ("company_id", "=", w.company.id),
                    ("type", "=", "opportunity"),
                    ("create_date", ">=", period[0]),
                    ("create_date", "<", period[1]),
                ]
            )

            w.opportunities_count_all = len(records)
            w.opportunities_count_won = len(records.filtered("stage_id.is_won"))
            w.opportunities_emails = "\n".join(
                records.filtered("email_from").mapped("email_from")
            )
            stage_records = records.mapped("stage_id").sorted("sequence")

            s2v = defaultdict(float)
            for record in records:
                stage_record = record.stage_id
                s2v[stage_record] += record.expected_revenue

            stages = []
            values = []
            for stage in stage_records:
                stages.append(stage.display_name)
                values.append(s2v[stage])

            script, div = prepare_pipeline_chart(stages, values, "Sales Pipeline")
            w.pipeline_chart = json.dumps({"div": div, "script": script})
