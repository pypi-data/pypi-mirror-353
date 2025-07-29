# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from inspect import getmembers

from lxml import etree

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from odoo.addons.ssi_decorator import ssi_decorator


class MixinTransactionCancel(models.AbstractModel):
    _name = "mixin.transaction_cancel"
    _inherit = [
        "mixin.transaction",
    ]
    _description = "Transaction Mixin - Cancel State Mixin"
    _cancel_state = "cancel"

    # Attributes related to automatic form view
    _automatically_insert_cancel_policy_fields = True
    _automatically_insert_cancel_button = True
    _automatically_insert_cancel_reason = True

    # Attributes related to add element on search view automatically
    _automatically_insert_cancel_filter = True

    # Attributes related to add element on tree view automatically
    _automatically_insert_cancel_state_badge_decorator = True

    _method_to_run_from_wizard = "action_cancel"

    cancel_reason_id = fields.Many2one(
        string="Cancel Reason",
        comodel_name="base.cancel_reason",
        readonly=True,
    )

    def _compute_policy(self):
        _super = super()
        _super._compute_policy()

    cancel_ok = fields.Boolean(
        string="Can Cancel",
        compute="_compute_policy",
        compute_sudo=True,
        help="""Cancel policy

* If active user can see and execute 'Cancel' button""",
    )
    state = fields.Selection(
        selection_add=[
            ("cancel", "Cancelled"),
        ],
        ondelete={"cancel": "set default"},
    )

    def _prepare_cancel_data(self, cancel_reason=False):
        self.ensure_one()
        return {
            "state": "cancel",
            "cancel_reason_id": cancel_reason and cancel_reason.id or False,
        }

    def _run_pre_cancel_check(self):
        self.ensure_one()
        cls = type(self)
        methods = []
        for _attr, func in getmembers(cls):
            if self.is_decorator(func, "_pre_cancel_check"):
                methods.append(func)
        if methods:
            self.run_decorator_method(methods)

    def _run_post_cancel_check(self):
        self.ensure_one()
        cls = type(self)
        methods = []
        for _attr, func in getmembers(cls):
            if self.is_decorator(func, "_post_cancel_check"):
                methods.append(func)
        if methods:
            self.run_decorator_method(methods)

    def _run_pre_cancel_action(self):
        self.ensure_one()
        cls = type(self)
        methods = []
        for _attr, func in getmembers(cls):
            if self.is_decorator(func, "_pre_cancel_action"):
                methods.append(func)
        if methods:
            self.run_decorator_method(methods)

    def _run_post_cancel_action(self):
        self.ensure_one()
        cls = type(self)
        methods = []
        for _attr, func in getmembers(cls):
            if self.is_decorator(func, "_post_cancel_action"):
                methods.append(func)
        if methods:
            self.run_decorator_method(methods)

    def action_cancel(self, cancel_reason=False):
        for record in self.sudo():
            record._check_cancel_policy()
            record._run_pre_cancel_check()
            record._run_pre_cancel_action()
            record.write(record._prepare_cancel_data(cancel_reason))
            record._run_post_cancel_check()
            record._run_post_cancel_action()
            record._notify_cancel_action()

    def _notify_cancel_action(self):
        self.ensure_one()
        msg = self._prepare_cancel_action_notification()
        self.message_post(
            body=_(msg), message_type="notification", subtype_xmlid="mail.mt_note"
        )

    def _prepare_cancel_action_notification(self):
        self.ensure_one()
        msg = "%s %s cancelled" % (self._description, self.display_name)
        return msg

    def _check_cancel_policy(self):
        self.ensure_one()

        if not self._automatically_insert_cancel_button:
            return False

        if self.env.context.get("bypass_policy_check", False):
            return True

        if not self.cancel_ok:
            error_message = """
                Document Type: %s
                Context: Cancel document
                Database ID: %s
                Problem: Document is not allowed to cancel
                Solution: Check cancel policy prerequisite
                """ % (
                self._description.lower(),
                self.id,
            )
            raise UserError(_(error_message))

    def _prepare_restart_data(self):
        self.ensure_one()
        _super = super()
        result = _super._prepare_restart_data()
        result.update(
            {
                "cancel_reason_id": False,
            }
        )
        return result

    @api.model
    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        result = super().fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu
        )
        View = self.env["ir.ui.view"]

        view_arch = etree.XML(result["arch"])

        if view_type == "form" and self._automatically_insert_view_element:
            view_arch = self._view_add_cancel_policy_field(view_arch)
            view_arch = self._view_add_cancel_button(view_arch)
            view_arch = self._view_add_cancel_reason(view_arch)
            view_arch = self._reorder_header_button(view_arch)
            view_arch = self._reorder_policy_field(view_arch)
        elif view_type == "tree" and self._automatically_insert_view_element:
            view_arch = self._add_cancel_state_badge_decorator(view_arch)
        elif view_type == "search" and self._automatically_insert_view_element:
            view_arch = self._add_cancel_filter_on_search_view(view_arch)
            view_arch = self._reorder_state_filter_on_search_view(view_arch)

        if view_id and result.get("base_model", self._name) != self._name:
            View = View.with_context(base_model_name=result["base_model"])
        new_arch, new_fields = View.postprocess_and_fields(view_arch, self._name)
        result["arch"] = new_arch
        new_fields.update(result["fields"])
        result["fields"] = new_fields

        return result

    @api.model
    def _add_cancel_state_badge_decorator(self, view_arch):
        if self._automatically_insert_cancel_state_badge_decorator:
            _xpath = "/tree/field[@name='state']"
            if len(view_arch.xpath(_xpath)) == 0:
                return view_arch
            node_xpath = view_arch.xpath(_xpath)[0]
            node_xpath.set("decoration-muted", "state == 'cancel'")
        return view_arch

    @api.model
    def _add_cancel_filter_on_search_view(self, view_arch):
        if self._automatically_insert_cancel_filter:
            view_arch = self._add_view_element(
                view_arch,
                "ssi_transaction_cancel_mixin.cancel_filter",
                self._state_filter_xpath,
                "after",
            )
        return view_arch

    @api.model
    def _view_add_cancel_policy_field(self, view_arch):
        if self._automatically_insert_cancel_policy_fields:
            policy_element_templates = [
                "ssi_transaction_cancel_mixin.cancel_policy_field",
            ]
            for template in policy_element_templates:
                view_arch = self._add_view_element(
                    view_arch,
                    template,
                    self._policy_field_xpath,
                    "before",
                )
        return view_arch

    @api.model
    def _view_add_cancel_button(self, view_arch):
        if self._automatically_insert_cancel_button:
            view_arch = self._add_view_element(
                view_arch,
                "ssi_transaction_cancel_mixin.button_cancel",
                "/form/header/field[@name='state']",
                "before",
            )
        return view_arch

    @api.model
    def _view_add_cancel_reason(self, view_arch):
        if self._automatically_insert_cancel_reason:
            view_arch = self._add_view_element(
                view_arch,
                "ssi_transaction_cancel_mixin.cancel_reason",
                "/form/sheet/div[@class='oe_left']/div[@class='oe_title']/h1",
                "after",
            )
        return view_arch

    @ssi_decorator.insert_on_tree_view()
    def _01_view_add_tree_cancel_button(self, view_arch):
        if self._automatically_insert_cancel_button:
            view_arch = self._add_view_element(
                view_arch,
                "ssi_transaction_cancel_mixin.tree_button_cancel",
                "/tree/header",
                "inside",
            )
        return view_arch
