"""
ページ共通レイアウト

全ページで使用する3分割レイアウト（top / middle / bottom）を提供。
"""

import dash_mantine_components as dmc

def page_layout(top, middle, bottom, *, py: str = "xl"):
    """
    ページ共通レイアウト
    - top: ヘッダー部分
    - middle: メインコンテンツ（スクロール対象）
    - bottom: フッター部分
    """
    return dmc.Stack(
        className="page-root",
        py=py,
        children=[
            dmc.Stack(
                className="page-stack",
                children=[
                    top,
                    dmc.ScrollArea(
                        className="page-scroll",
                        type="auto",
                        children=middle,
                    ),
                    bottom,
                ],
            )
        ],
    )