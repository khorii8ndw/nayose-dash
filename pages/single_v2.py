"""
単一名寄せ（骨格整理）
"""

import dash
from dash import html
import dash_mantine_components as dmc

dash.register_page(__name__, path="/single_v2")


def labeled_divider(label):
    return dmc.Group(
        align = "center",
        children=[
            dmc.Divider(style = {"width": 30}),
            dmc.Text(label, size="sm"),
            dmc.Divider(style = {"flex": 10}),
        ],
    )

def header_cell(label, **text_props):
    default = {
        "className":"header_cell",
        "size": "sm",
        "ta": "center",
    }
    return dmc.Text(
        label,
        **{**default, **text_props}
    )

def value_cell_text(val, **text_props):
    default = {
        "className":"value_cell_text",
        "size": "sm",
    }
    return dmc.Text(
        val,
        **{**default, **text_props}
    )

def row_frame(fixed, flexible):
    return dmc.Group(
        className = "row",
        children = [
            dmc.Group(
                grow = False,
                children = fixed
            ),
            dmc.Group(
                grow     = True,
                style    = {"flex": 1},
                children = flexible
            ),
        ]
        
    )

def header_row(kbn, upd, *col_flexible):
    return row_frame(
        fixed = [
            header_cell(label=kbn, w=60),
            header_cell(label=upd, w=120),
        ],
        flexible = [
            header_cell(label=v) for v in col_flexible
        ],
    )

def data_row(record):
    cell_style = {
        "whiteSpace": "normal",
        "wordBreak" : "break-word",
        "minWidth"  : 0,
    }
    return row_frame(
        fixed = [
            value_cell_text(val=record["kbn"], w=60, ta="center"),
            value_cell_text(val=record["upd"], w=120, ta="center"),
        ],
        flexible = [
            value_cell_text(val=v, style=cell_style) for k, v in record.items() if k not in {"kbn", "upd"}
        ],
    )

def baseline_section(records):
    return dmc.Stack(
        className = "baseline_section",
        children=[
            data_row(r) for r in records
        ]
    )

def comparisons_section(records):
    return dmc.Stack(
        className = "comparisons_section",
        children=[
            data_row(r) for r in records
        ]
    )

baseline_data = [
        {
            "kbn":"a",
            "upd":"b",
            "name":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "address":"d",
            "phone":"e",
        },
    ]

comparisons_data = [
        {
            "kbn":"a",
            "upd":"b",
            "name":"c",
            "address":"d",
            "phone":"e",
        },
        {
            "kbn":"a",
            "upd":"b",
            "name":"c",
            "address":"d",
            "phone":"e",
        },
        {
            "kbn":"a",
            "upd":"b",
            "name":"c",
            "address":"d",
            "phone":"e",
        },
    ]


layout = dmc.Container(
    className = "container",
    size = "xl",
    px   = "lg",
    py   = "xl",

    children=[
        dmc.Stack(
            className="stack",
            children=[
                dmc.Title("単一名寄せ", order=2),
                header_row("区分", "更新日時", "氏名", "住所", "電話番号"),
                labeled_divider("比較元レコード"),
                baseline_section(baseline_data),
                labeled_divider("比較先レコード"),
                comparisons_section(comparisons_data),
            ]
        )
    ],
)

