from datetime import datetime

import pytz
from dateutil.relativedelta import relativedelta

from odoo import fields, models
from odoo.exceptions import AccessError


class Digest(models.Model):
    _inherit = "digest.digest"

    kpi2_sale_activity_report = fields.Boolean("Sale Activity Report")

    def _compute_sale_activity_report_value(self, user_id):
        self.ensure_one()
        start, end, company = self._get_kpi_compute_parameters()
        return self.env["mail.activity"].search_count(
            [
                ("date_deadline", ">=", start),
                ("date_deadline", "<", end),
                ("user_id", "=", user_id),
            ]
        )

    def _compute_sale_activity_report_timeframes(self, company):
        start_datetime = datetime.utcnow()
        tz_name = company.resource_calendar_id.tz
        if tz_name:
            start_datetime = pytz.timezone(tz_name).localize(start_datetime)
        return [
            (
                self.env._("Future activities"),
                start_datetime,
                start_datetime + relativedelta(days=1000),
            ),
            (
                self.env._("Overdue activities"),
                start_datetime + relativedelta(days=-1000),
                start_datetime,
            ),
        ]

    def _compute_kpis(self, company, user):
        res = super()._compute_kpis(company, user)

        if not self.kpi2_sale_activity_report:
            return res

        self.env.cr.execute(
            """
SELECT array_agg(DISTINCT user_id)
FROM mail_activity
WHERE create_date >= NOW() - INTERVAL '1 YEAR'
            """
        )

        sales_user_ids = self.env.cr.fetchone()[0] or []

        if not sales_user_ids:
            return res

        invalid_fields = []
        kpis = [
            dict(
                kpi_name=f"kpi_sale_activity_report_{user_id}",
                kpi_fullname=self.env["res.users"].browse(user_id).name,
                kpi_action=False,
                kpi_col1=dict(),
                kpi_col2=dict(),
                kpi_col3=dict(),
                kpi_user_id=user_id,
            )
            for user_id in sales_user_ids
        ]

        for col_index, (tf_name, start_datetime, end_datetime) in enumerate(
            self._compute_sale_activity_report_timeframes(company)
        ):
            digest = (
                self.with_context(
                    start_datetime=start_datetime, end_datetime=end_datetime
                )
                .with_user(user)
                .with_company(company)
            )
            for index, user_id in enumerate(sales_user_ids):
                kpi_values = kpis[index]
                kpi_values["kpi_action"] = (
                    f"bacula2_crm.user_mail_activity_action&active_id={user_id}"
                )
                try:
                    compute_value = digest._compute_sale_activity_report_value(user_id)
                except AccessError:
                    invalid_fields.append(user_id)
                    continue
                kpi_values["kpi_col%s" % (col_index + 1)].update(
                    {
                        "value": compute_value,
                        "margin": 0,
                        "col_subtitle": tf_name,
                    }
                )

        return res + [kpi for kpi in kpis if kpi["kpi_user_id"] not in invalid_fields]
