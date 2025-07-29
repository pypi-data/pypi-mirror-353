# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "Transaction Mixin - Win & Lost State",
    "version": "14.0.1.9.1",
    "website": "https://simetri-sinergi.id",
    "author": "OpenSynergy Indonesia, PT. Simetri Sinergi Indonesia",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "ssi_transaction_mixin",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizards/base_select_lost_reason_views.xml",
        "templates/mixin_transaction_win_lost_templates.xml",
        "views/ir_model_views.xml",
        "views/base_lost_reason_views.xml",
    ],
    "demo": [
        "demo/base_lost_reason_demo.xml",
    ],
}
