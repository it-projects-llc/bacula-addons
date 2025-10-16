import traceback

from requests import request
from requests.utils import requote_uri

from odoo import models

try:
    from cerbapi import Cerb
except ImportError:
    Cerb = None


class IrActionsServer(models.Model):
    _inherit = "ir.actions.server"

    def _get_eval_context(self, action=None):
        eval_context = super()._get_eval_context(action)

        def get_stack():
            return "\n".join(traceback.format_stack())

        eval_context.update(
            Cerb=Cerb,
            requote_uri=requote_uri,
            get_stack=get_stack,
            make_request=request,
        )
        return eval_context
