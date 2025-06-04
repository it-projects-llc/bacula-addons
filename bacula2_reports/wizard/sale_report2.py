import json
from datetime import timedelta

from odoo import api, fields, models
from odoo.tools.date_utils import end_of, start_of
from odoo.tools.misc import formatLang

from ..tools import prepare_pipeline_chart, prepare_sales_target_chart


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

    def _default_challenge(self):
        return (
            self.env["gamification.challenge"]
            .search([("name", "=", "Annual Sales Quota")], order="id DESC", limit=1)
            .id
        )

    company = fields.Many2one("res.company", default=lambda self: self.env.company.id)

    period_start = fields.Date(
        default=lambda self: fields.Date.today() - timedelta(days=30)
    )
    period_end = fields.Date(default=lambda self: fields.Date.today())
    challenge = fields.Many2one(
        "gamification.challenge", required=True, default=_default_challenge
    )

    currency_id = fields.Many2one("res.currency", related="company.currency_id")

    opportunities_count_all = fields.Integer()
    opportunities_count_won = fields.Integer()
    opportunities_count_lost = fields.Integer()
    opportunities_emails = fields.Text()

    pipeline_chart = fields.Char(default=json.dumps({"div": "", "script": ""}))
    sales_target_chart = fields.Char(default=json.dumps({"div": "", "script": ""}))

    def action_make_report(self):
        Leads = self.env["crm.lead"].with_context(active_test=False)
        Goals = self.sudo().env["gamification.goal"]

        for w in self:
            if not w.period_start or not w.period_end:
                continue

            period = (
                start_of(fields.Datetime.to_datetime(w.period_start), "hour"),
                end_of(fields.Datetime.to_datetime(w.period_end), "hour"),
            )

            domain = [
                ("company_id", "=", w.company.id),
                ("type", "=", "opportunity"),
                ("create_date", ">=", period[0]),
                ("create_date", "<", period[1]),
            ]
            records = Leads.search([("active", "=", True)] + domain)

            w.opportunities_count_all = len(records)
            w.opportunities_count_won = len(records.filtered("stage_id.is_won"))
            w.opportunities_emails = "\n".join(
                records.filtered("email_from").mapped("email_from")
            )
            w.opportunities_count_lost = Leads.search_count(
                [("active", "=", False)] + domain
            )

            group_stage_data = Leads.read_group(
                domain, ["expected_revenue"], ["stage_id"]
            )

            stages = []
            values = []
            descriptions = []
            for stage in group_stage_data:
                value = stage["expected_revenue"]
                if not value:
                    continue

                values.append(value)
                stages.append(str(stage["stage_id"][1]))
                descriptions.append(
                    formatLang(self.env, value, currency_obj=w.company.currency_id)
                )

            if not values:
                script = div = ""
            else:
                script, div = prepare_pipeline_chart(
                    stages, values, "Sales Pipeline", descriptions
                )

            w.pipeline_chart = json.dumps({"div": div, "script": script})

            goals = Goals.search(
                [
                    ("challenge_id", "=", w.challenge.id),
                ]
            )
            sales_target_chart_data = {}

            for g in goals:
                sales_target_chart_data[g.user_id.name] = [g.current, g.target_goal]

            script, div = prepare_sales_target_chart(sales_target_chart_data)

            w.sales_target_chart = json.dumps({"div": div, "script": script})
