# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from inspect import getmembers

from lxml import etree

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from odoo.addons.ssi_decorator import ssi_decorator


class MixinTransactionConfirm(models.AbstractModel):
    _name = "mixin.transaction_confirm"
    _inherit = [
        "mixin.transaction",
        "mixin.multiple_approval",
    ]
    _description = "Transaction Mixin - Waiting for Approval Mixin"
    _confirm_state = "confirm"

    # Attributes related to automatic form view
    _automatically_insert_confirm_policy_fields = True
    _automatically_insert_confirm_button = True
    _automatically_insert_approve_button = True
    _automatically_insert_reject_button = True
    _automatically_insert_restart_approval_button = True

    # Attributes related to add element on search view automatically
    _automatically_insert_confirm_filter = True
    _automatically_insert_reject_filter = True

    # Attributes related to add element on tree view automatically
    _automatically_insert_confirm_state_badge_decorator = True
    _automatically_insert_reject_state_badge_decorator = True

    def _compute_policy(self):
        _super = super()
        _super._compute_policy()

    confirm_ok = fields.Boolean(
        string="Can Confirm",
        compute="_compute_policy",
        compute_sudo=True,
        help="""Confirm policy

* If active user can see and execute 'Confirm' button""",
    )
    approve_ok = fields.Boolean(
        string="Can Approve",
        compute="_compute_policy",
        compute_sudo=True,
        help="""Approve policy

* If active user can see and execute 'Approve' button""",
    )
    reject_ok = fields.Boolean(
        string="Can Reject",
        compute="_compute_policy",
        compute_sudo=True,
        help="""Reject policy

* If active user can see and execute 'Reject' button""",
    )
    restart_approval_ok = fields.Boolean(
        string="Can Restart Approval",
        compute="_compute_policy",
        compute_sudo=True,
        help="""Restart approval policy

* If active user can see and execute 'Restart Approval' button""",
    )
    state = fields.Selection(
        selection_add=[
            ("confirm", "Waiting for Approval"),
            ("reject", "Rejected"),
        ],
        ondelete={
            "confirm": "set default",
            "reject": "set default",
        },
    )

    def _run_pre_confirm_check(self):
        self.ensure_one()
        cls = type(self)
        methods = []
        for _attr, func in getmembers(cls):
            if self.is_decorator(func, "_pre_confirm_check"):
                methods.append(func)
        if methods:
            self.run_decorator_method(methods)

    def _run_post_confirm_check(self):
        self.ensure_one()
        cls = type(self)
        methods = []
        for _attr, func in getmembers(cls):
            if self.is_decorator(func, "_post_confirm_check"):
                methods.append(func)
        if methods:
            self.run_decorator_method(methods)

    def _run_pre_confirm_action(self):
        self.ensure_one()
        cls = type(self)
        methods = []
        for _attr, func in getmembers(cls):
            if self.is_decorator(func, "_pre_confirm_action"):
                methods.append(func)
        if methods:
            self.run_decorator_method(methods)

    def _run_post_confirm_action(self):
        self.ensure_one()
        cls = type(self)
        methods = []
        for _attr, func in getmembers(cls):
            if self.is_decorator(func, "_post_confirm_action"):
                methods.append(func)
        if methods:
            self.run_decorator_method(methods)

    def action_confirm(self):
        for record in self.sudo():
            record._check_confirm_policy()
            record._run_pre_confirm_check()
            record._run_pre_confirm_action()
            record.write(record._prepare_confirm_data())
            record._run_post_confirm_check()
            record._run_post_confirm_action()
            record.action_request_approval()
            record._notify_confirm_action()

    def _notify_confirm_action(self):
        self.ensure_one()
        msg = self._prepare_confirm_action_notification()
        self.message_post(
            body=_(msg), message_type="notification", subtype_xmlid="mail.mt_note"
        )

    def _prepare_confirm_action_notification(self):
        self.ensure_one()
        msg = "%s %s confirmed" % (self._description, self.display_name)
        return msg

    def _check_confirm_policy(self):
        self.ensure_one()
        if not self._automatically_insert_confirm_button:
            return True

        if self.env.context.get("bypass_policy_check", False):
            return True

        if not self.confirm_ok:
            error_message = """
                Document Type: %s
                Context: Confirm document
                Database ID: %s
                Problem: Document is not allowed to confirm
                Solution: Check confirm policy prerequisite
                """ % (
                self._description.lower(),
                self.id,
            )
            raise UserError(_(error_message))

    def _prepare_confirm_data(self):
        self.ensure_one()
        return {
            "state": self._confirm_state,
        }

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
            view_arch = self._view_add_policy_field(view_arch)
            view_arch = self._view_add_confirm_button(view_arch)
            view_arch = self._view_add_approve_button(view_arch)
            view_arch = self._view_add_reject_button(view_arch)
            view_arch = self._view_add_restart_approval_button(view_arch)
            view_arch = self._reorder_header_button(view_arch)
            view_arch = self._reorder_policy_field(view_arch)
        elif view_type == "tree" and self._automatically_insert_view_element:
            view_arch = self._add_confirm_state_badge_decorator(view_arch)
            view_arch = self._add_reject_state_badge_decorator(view_arch)
        elif view_type == "search" and self._automatically_insert_view_element:
            view_arch = self._add_confirm_filter_on_search_view(view_arch)
            view_arch = self._add_reject_filter_on_search_view(view_arch)
            view_arch = self._reorder_state_filter_on_search_view(view_arch)

        if view_id and result.get("base_model", self._name) != self._name:
            View = View.with_context(base_model_name=result["base_model"])
        new_arch, new_fields = View.postprocess_and_fields(view_arch, self._name)
        result["arch"] = new_arch
        new_fields.update(result["fields"])
        result["fields"] = new_fields

        return result

    @api.model
    def _add_confirm_state_badge_decorator(self, view_arch):
        if self._automatically_insert_confirm_state_badge_decorator:
            _xpath = "/tree/field[@name='state']"
            if len(view_arch.xpath(_xpath)) == 0:
                return view_arch
            node_xpath = view_arch.xpath(_xpath)[0]
            node_xpath.set("decoration-warning", "state == 'confirm'")
        return view_arch

    @api.model
    def _add_reject_state_badge_decorator(self, view_arch):
        if self._automatically_insert_reject_state_badge_decorator:
            _xpath = "/tree/field[@name='state']"
            if len(view_arch.xpath(_xpath)) == 0:
                return view_arch
            node_xpath = view_arch.xpath(_xpath)[0]
            node_xpath.set("decoration-danger", "state == 'reject'")
        return view_arch

    @api.model
    def _add_confirm_filter_on_search_view(self, view_arch):
        if self._automatically_insert_confirm_filter:
            view_arch = self._add_view_element(
                view_arch,
                "ssi_transaction_confirm_mixin.confirm_filter",
                self._state_filter_xpath,
                "after",
            )
        return view_arch

    @api.model
    def _add_reject_filter_on_search_view(self, view_arch):
        if self._automatically_insert_reject_filter:
            view_arch = self._add_view_element(
                view_arch,
                "ssi_transaction_confirm_mixin.reject_filter",
                self._state_filter_xpath,
                "after",
            )
        return view_arch

    @api.model
    def _view_add_policy_field(self, view_arch):
        if self._automatically_insert_confirm_policy_fields:
            policy_element_templates = [
                "ssi_transaction_confirm_mixin.confirm_policy_field",
                "ssi_transaction_confirm_mixin.approve_policy_field",
                "ssi_transaction_confirm_mixin.reject_policy_field",
                "ssi_transaction_confirm_mixin.restart_approval_policy_field",
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
    def _view_add_confirm_button(self, view_arch):
        if self._automatically_insert_confirm_button:
            view_arch = self._add_view_element(
                view_arch,
                "ssi_transaction_confirm_mixin.button_confirm",
                "/form/header/field[@name='state']",
                "before",
            )
        return view_arch

    @api.model
    def _view_add_approve_button(self, view_arch):
        if self._automatically_insert_approve_button:
            view_arch = self._add_view_element(
                view_arch,
                "ssi_transaction_confirm_mixin.button_approve",
                "/form/header/field[@name='state']",
                "before",
            )
        return view_arch

    @api.model
    def _view_add_restart_approval_button(self, view_arch):
        if self._automatically_insert_restart_approval_button:
            view_arch = self._add_view_element(
                view_arch,
                "ssi_transaction_confirm_mixin.button_restart_approval",
                "/form/header/field[@name='state']",
                "before",
            )
        return view_arch

    @api.model
    def _view_add_reject_button(self, view_arch):
        if self._automatically_insert_reject_button:
            view_arch = self._add_view_element(
                view_arch,
                "ssi_transaction_confirm_mixin.button_reject",
                "/form/header/field[@name='state']",
                "before",
            )
        return view_arch

    @ssi_decorator.insert_on_tree_view()
    def _03_view_add_tree_confirm_button(self, view_arch):
        if self._automatically_insert_confirm_button:
            view_arch = self._add_view_element(
                view_arch,
                "ssi_transaction_confirm_mixin.tree_button_confirm",
                "/tree/header",
                "inside",
            )
        return view_arch

    @ssi_decorator.insert_on_tree_view()
    def _03_view_add_tree_approve_button(self, view_arch):
        if self._automatically_insert_approve_button:
            view_arch = self._add_view_element(
                view_arch,
                "ssi_transaction_confirm_mixin.tree_button_approve",
                "/tree/header",
                "inside",
            )
        return view_arch

    @ssi_decorator.insert_on_tree_view()
    def _02_view_add_tree_reject_button(self, view_arch):
        if self._automatically_insert_reject_button:
            view_arch = self._add_view_element(
                view_arch,
                "ssi_transaction_confirm_mixin.tree_button_reject",
                "/tree/header",
                "inside",
            )
        return view_arch

    @ssi_decorator.insert_on_tree_view()
    def _01_view_add_tree_reject_button(self, view_arch):
        if self._automatically_insert_restart_approval_button:
            view_arch = self._add_view_element(
                view_arch,
                "ssi_transaction_confirm_mixin.tree_button_restart_approval",
                "/tree/header",
                "inside",
            )
        return view_arch
