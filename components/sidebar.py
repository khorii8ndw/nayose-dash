"""
サイドバー - DMC 0.12系 NavLink
"""

import dash_mantine_components as dmc
from dash_iconify import DashIconify

NAVBAR_WIDTH = 250


def create_sidebar():
    return dmc.Navbar(
        width={"base": NAVBAR_WIDTH},
        className="app-navbar",
        children=dmc.Stack(
            children=[
                dmc.NavLink(
                    label="単一名寄せ",
                    icon=DashIconify(icon="tabler:user"),
                    href="/single",
                    className="app-navlink",
                ),
                dmc.NavLink(
                    label="複数名寄せ",
                    icon=DashIconify(icon="tabler:users"),
                    href="/batch",
                    className="app-navlink",
                ),
                dmc.NavLink(
                    label="レビュー (v1)",
                    icon=DashIconify(icon="tabler:checklist"),
                    href="/review",
                    className="app-navlink",
                ),
                dmc.NavLink(
                    label="レビュー (v2)",
                    icon=DashIconify(icon="tabler:player-play"),
                    href="/review-v2",
                    className="app-navlink",
                ),
            ],
        ),
    )
