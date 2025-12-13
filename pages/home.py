"""
ホームページ - /single へリダイレクト
"""

import dash
from dash import dcc

dash.register_page(__name__, path="/")

layout = dcc.Location(pathname="/single", id="redirect-home", refresh=True)
