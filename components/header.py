"""
ヘッダー - DMC 0.12系
"""

import dash_mantine_components as dmc

HEADER_HEIGHT = 60


def create_header():
    return dmc.Header(
        height=HEADER_HEIGHT,
        className="app-header",
        children=dmc.Title("名寄せアプリ", order=3),
    )
