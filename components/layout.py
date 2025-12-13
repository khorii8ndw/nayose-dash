"""
全体レイアウト - DMC 0.12系 AppShell
"""

from dash import page_container
import dash_mantine_components as dmc
from components.header import create_header
from components.sidebar import create_sidebar


def create_layout():
    return dmc.AppShell(
        header=create_header(),
        navbar=create_sidebar(),
        children=page_container,
    )
