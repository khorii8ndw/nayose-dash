"""
名寄せアプリ - エントリーポイント
DMC 0.12系 (Dash 2.x 互換)
"""

from dash import Dash
import dash_mantine_components as dmc
from components.layout import create_layout

app = Dash(
    __name__,
    use_pages=True,
    suppress_callback_exceptions=True,
)

app.layout = dmc.MantineProvider(
    theme={"colorScheme": "light"},
    withGlobalStyles=True,
    withNormalizeCSS=True,
    children=create_layout(),
)

server = app.server

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
