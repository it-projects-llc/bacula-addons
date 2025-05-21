from . import report


def pre_init_hook(cr):
    cr.execute("DROP VIEW IF EXISTS hr_contract_history")
