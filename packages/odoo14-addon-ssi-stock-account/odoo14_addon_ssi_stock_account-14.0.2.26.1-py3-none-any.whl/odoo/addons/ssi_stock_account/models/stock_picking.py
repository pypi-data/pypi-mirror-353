# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _name = "stock.picking"
    _inherit = ["stock.picking"]

    journal_id = fields.Many2one(
        string="Journal",
        comodel_name="account.journal",
    )
    account_move_ids = fields.Many2many(
        string="Journal Entries",
        comodel_name="account.move",
        compute="_compute_account_move_ids",
        store=False,
    )
    stock_valuation_layer_ids = fields.Many2many(
        string="Stock Valuation Layes",
        comodel_name="stock.valuation.layer",
        compute="_compute_stock_valuation_layer_ids",
        store=False,
    )
    create_accounting_entry_ok = fields.Boolean(
        string="Can Create Accounting Entries",
        compute="_compute_create_accounting_entry_ok",
        store=False,
    )
    account_move_created = fields.Boolean(
        string="All Accounting Entries Created?",
        compute="_compute_account_move_created",
        store=True,
        compute_sudo=True,
    )

    @api.depends(
        "move_lines.stock_valuation_layer_ids",
        "move_lines.stock_valuation_layer_ids.account_move_id",
        "move_lines.stock_valuation_layer_ids.quantity",
        "state",
    )
    def _compute_account_move_created(self):
        SVL = self.env["stock.valuation.layer"]
        for record in self:
            result = False
            if record.state == "done":
                result = True
                criteria = [
                    ("account_move_id", "=", False),
                    ("stock_move_id.picking_id.id", "=", record.id),
                    ("quantity", "!=", 0.0),
                ]
                if SVL.search_count(criteria) > 0:
                    result = False
            record.account_move_created = result

    @api.onchange(
        "picking_type_id",
    )
    def onchange_journal_id(self):
        self.journal_id = False
        if self.picking_type_id:
            self.journal_id = self.picking_type_id.journal_id

    def _compute_create_accounting_entry_ok(self):
        for record in self:
            result = True

            if record.state != "done":
                result = False

            if record.account_move_ids:
                result = False

            record.create_accounting_entry_ok = result

    def _compute_account_move_ids(self):
        for record in self:
            result = self.env["account.move"]
            for move in self.move_lines:
                result += move.account_move_ids
            record.account_move_ids = result

    @api.constrains(
        "state",
    )
    def constrain_no_cancel_if_accounting_entry_exists(self):
        for record in self.sudo():
            if record.state == "cancel" and record.account_move_ids:
                error_message = _(
                    """
                Context: Cancel stock transfer
                Database ID: %s
                Problem: Accounting entry already exist
                Solution: Delete accounting entry
                """
                    % (record.id)
                )
                raise UserError(error_message)

    def _compute_stock_valuation_layer_ids(self):
        for record in self:
            result = self.env["stock.valuation.layer"]
            for move in self.move_lines:
                result += move.stock_valuation_layer_ids
            record.stock_valuation_layer_ids = result

    def action_create_accounting_entry(self):
        for record in self.sudo():
            record._create_accounting_entry()

    def action_delete_accounting_entry(self):
        for record in self.sudo():
            record._delete_accounting_entry()

    def action_reload_accounting_setting(self):
        for record in self.sudo():
            record._reload_accounting_setting()

    def action_open_svl(self):
        for record in self.sudo():
            result = record._open_svl()
        return result

    def _open_svl(self):
        waction = self.env.ref("stock_account.stock_valuation_layer_action").read()[0]
        waction.update(
            {
                "view_mode": "tree,form",
                "domain": [("id", "in", self.stock_valuation_layer_ids.ids)],
                "context": {},
            }
        )
        return waction

    def _create_accounting_entry(self):
        self.ensure_one()
        for svl in self.stock_valuation_layer_ids.filtered(lambda r: r.quantity != 0.0):
            svl._create_accounting_entry()

    def _delete_accounting_entry(self):
        self.ensure_one()
        for svl in self.stock_valuation_layer_ids:
            svl._delete_accounting_entry()

    def _reload_accounting_setting(self):
        self.ensure_one()
        if self.account_move_ids:
            return True

        self.onchange_journal_id()

        for move in self.move_ids_without_package:
            move.onchange_debit_usage_id()
            move.onchange_credit_usage_id()
            move.onchange_debit_account_id()
            move.onchange_credit_account_id()
