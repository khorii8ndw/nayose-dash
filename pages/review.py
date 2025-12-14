"""
レビュー一覧 - クラスタ一覧とフィルタ
Step 1 改善: 確認サマリを追加
"""

import dash
from dash import html, dcc, callback, Input, Output, State, ctx, ALL, no_update
import dash_mantine_components as dmc

dash.register_page(__name__, path="/review")


# ========================================
# Data (Mock)
# ========================================

CLUSTERS = [
    {"id": 1, "cluster_id": "C-0001", "representative": {"name": "N***", "phone": "+81-*-****-****", "email": "a***@example.com"}, "last_seen": "2025/11/12 14:22", "status": "要承認", "source_table": "tbl_a"},
    {"id": 2, "cluster_id": "C-0002", "representative": {"name": "K***", "phone": "+81-*-****-****", "email": "s***@example.com"}, "last_seen": "2025/11/13 09:01", "status": "保留", "source_table": "tbl_b"},
    {"id": 3, "cluster_id": "C-0003", "representative": {"name": "M***", "phone": "+81-*-****-****", "email": "m***@example.com"}, "last_seen": "2025/11/13 18:20", "status": "要承認", "source_table": "tbl_a"},
]

DETAILS = {
    "C-0001": {
        "cluster_id": "C-0001",
        "diff": {"added": 1, "removed": 0, "rep_changed": False, "last_approved_at": "2025/11/12 14:22",
                 "added_members": [{"pk": ["customer_id=1003", "system=X"], "reason": "氏名一致/住所階層一致"}], "removed_members": []},
        "rep_candidates": [
            {"pk": ["customer_id=1001", "system=A"], "tag": "自動選定", "reasons": "出所信頼度 > 新鮮度 > 観測回数", "preview": {"name": "佐々木 太郎", "phone": "+81-90-1234-5678", "email": "sasaki@example.com"}, "score": 0.92},
            {"pk": ["customer_id=88", "system=B"], "tag": "候補", "reasons": "新鮮度", "preview": {"name": "佐々木 太郎", "phone": "+81-80-9999-8888", "email": "sasaki2@example.com"}, "score": 0.84},
        ],
        "members": [
            {"pk": ["customer_id=1001", "system=A"], "preview": {"name": "佐々木 太郎", "phone": "+81-90-1234-5678", "email": "sasaki@example.com"}, "matches": {"name": True, "phone": True, "email": True, "address": False}, "last_seen": "2025/11/12 14:22", "constraint": None},
            {"pk": ["customer_id=1002", "system=A"], "preview": {"name": "佐々木 太郎", "phone": "+81-90-1234-5678", "email": "x_sasaki@example.com"}, "matches": {"name": True, "phone": True, "email": False, "address": True}, "last_seen": "2025/11/10 10:05", "constraint": {"reason": "共有値のみ一致"}},
        ],
        "attrs": {
            "name": [{"id": "name1", "label": "佐々木 太郎", "seen": 4, "recency": 0.9, "trust": 0.8, "shared": False}, {"id": "name2", "label": "ササキ タロウ", "seen": 2, "recency": 0.7, "trust": 0.6, "shared": False}],
            "phone": [{"id": "phone1", "label": "+81-90-1234-5678", "seen": 3, "recency": 0.8, "trust": 0.8, "shared": False}, {"id": "phone2", "label": "+81-80-9999-8888", "seen": 5, "recency": 0.4, "trust": 0.7, "shared": True}],
            "email": [{"id": "email1", "label": "sasaki@example.com", "seen": 3, "recency": 0.9, "trust": 0.8, "shared": False}],
            "address": [{"id": "addr1", "label": "東京都千代田区千代田1-1", "seen": 2, "recency": 0.8, "trust": 0.7, "shared": False}],
        },
        "history": [{"at": "2025/11/12 14:22", "by": "reviewer_A", "event": "承認", "note": "初回承認"}, {"at": "2025/11/10 10:05", "by": "auto", "event": "スコア再計算", "note": "共有値辞書更新"}],
    },
    "C-0002": {
        "cluster_id": "C-0002",
        "diff": {"added": 0, "removed": 1, "rep_changed": True, "last_approved_at": "2025/11/10 10:00",
                 "added_members": [], "removed_members": [{"pk": ["customer_id=2002", "system=B"], "reason": "cannot制約"}]},
        "rep_candidates": [{"pk": ["customer_id=2001", "system=B"], "tag": "自動選定", "reasons": "観測回数", "preview": {"name": "鈴木 花子", "phone": "+81-70-1111-2222", "email": "suzuki@example.com"}, "score": 0.88}],
        "members": [{"pk": ["customer_id=2001", "system=B"], "preview": {"name": "鈴木 花子", "phone": "+81-70-1111-2222", "email": "suzuki@example.com"}, "matches": {"name": True, "phone": True, "email": True, "address": True}, "last_seen": "2025/11/13 09:01", "constraint": None}],
        "attrs": {"name": [{"id": "name1", "label": "鈴木 花子", "seen": 5, "recency": 0.95, "trust": 0.9, "shared": False}], "phone": [{"id": "phone1", "label": "+81-70-1111-2222", "seen": 5, "recency": 0.95, "trust": 0.9, "shared": False}], "email": [{"id": "email1", "label": "suzuki@example.com", "seen": 5, "recency": 0.95, "trust": 0.9, "shared": False}], "address": [{"id": "addr1", "label": "大阪府大阪市北区梅田1-1", "seen": 3, "recency": 0.8, "trust": 0.85, "shared": False}]},
        "history": [{"at": "2025/11/13 09:01", "by": "reviewer_B", "event": "保留", "note": "代表変更の確認が必要"}],
    },
    "C-0003": {
        "cluster_id": "C-0003",
        "diff": {"added": 2, "removed": 0, "rep_changed": False, "last_approved_at": "2025/11/11 15:30",
                 "added_members": [{"pk": ["customer_id=3002", "system=C"], "reason": "氏名一致"}, {"pk": ["customer_id=3003", "system=A"], "reason": "住所一致"}], "removed_members": []},
        "rep_candidates": [
            {"pk": ["customer_id=3001", "system=A"], "tag": "自動選定", "reasons": "出所信頼度", "preview": {"name": "田中 一郎", "phone": "+81-90-5555-6666", "email": "tanaka@example.com"}, "score": 0.95},
            {"pk": ["customer_id=3002", "system=C"], "tag": "候補", "reasons": "新鮮度", "preview": {"name": "田中 一郎", "phone": "+81-80-7777-8888", "email": "tanaka2@example.com"}, "score": 0.80},
        ],
        "members": [
            {"pk": ["customer_id=3001", "system=A"], "preview": {"name": "田中 一郎", "phone": "+81-90-5555-6666", "email": "tanaka@example.com"}, "matches": {"name": True, "phone": True, "email": True, "address": True}, "last_seen": "2025/11/13 18:20", "constraint": None},
            {"pk": ["customer_id=3002", "system=C"], "preview": {"name": "田中 一郎", "phone": "+81-80-7777-8888", "email": "tanaka2@example.com"}, "matches": {"name": True, "phone": False, "email": False, "address": True}, "last_seen": "2025/11/12 12:00", "constraint": None},
        ],
        "attrs": {"name": [{"id": "name1", "label": "田中 一郎", "seen": 6, "recency": 0.9, "trust": 0.85, "shared": False}, {"id": "name2", "label": "タナカ イチロウ", "seen": 2, "recency": 0.6, "trust": 0.5, "shared": False}], "phone": [{"id": "phone1", "label": "+81-90-5555-6666", "seen": 4, "recency": 0.9, "trust": 0.8, "shared": False}, {"id": "phone2", "label": "+81-80-7777-8888", "seen": 2, "recency": 0.7, "trust": 0.6, "shared": True}], "email": [{"id": "email1", "label": "tanaka@example.com", "seen": 4, "recency": 0.9, "trust": 0.8, "shared": False}], "address": [{"id": "addr1", "label": "神奈川県横浜市中区本町1-1", "seen": 5, "recency": 0.85, "trust": 0.8, "shared": False}]},
        "history": [{"at": "2025/11/13 18:20", "by": "auto", "event": "メンバ追加", "note": "+2件"}, {"at": "2025/11/11 15:30", "by": "reviewer_A", "event": "承認", "note": "初回承認"}],
    },
}


# ========================================
# Helper Functions
# ========================================

def analyze_cluster(detail):
    """クラスタを分析して確認ポイントを抽出"""
    checks = []
    warnings = []
    
    diff = detail["diff"]
    
    # 代表変更チェック
    if diff["rep_changed"]:
        warnings.append({"type": "rep_changed", "label": "代表レコードが変更されています", "detail": "前回承認時と異なる代表が選定されました"})
    else:
        checks.append({"type": "rep_ok", "label": "代表レコード：変更なし"})
    
    # 構成員変更チェック
    added = diff.get("added", 0)
    removed = diff.get("removed", 0)
    if removed > 0:
        warnings.append({"type": "member_removed", "label": f"構成員：{removed}件が削除されました", "detail": "cannot制約等により除外"})
    if added > 0:
        checks.append({"type": "member_added", "label": f"構成員：+{added}件（新規追加）"})
    if added == 0 and removed == 0:
        checks.append({"type": "member_ok", "label": "構成員：変更なし"})
    
    # 属性チェック（共有値・複数候補）
    attrs = detail.get("attrs", {})
    attr_warnings = []
    for attr_name, items in attrs.items():
        attr_label = {"name": "氏名", "phone": "電話", "email": "メール", "address": "住所"}.get(attr_name, attr_name)
        
        # 共有値チェック
        has_shared = any(it.get("shared") for it in items)
        if has_shared:
            attr_warnings.append(f"「{attr_label}」に共有値あり")
        
        # 複数候補チェック
        if len(items) > 1:
            attr_warnings.append(f"「{attr_label}」に複数候補（{len(items)}件）")
        
        # 信頼度低チェック
        low_trust = any(it.get("trust", 1) < 0.7 for it in items)
        if low_trust:
            attr_warnings.append(f"「{attr_label}」に低信頼度の値あり")
    
    if attr_warnings:
        warnings.append({"type": "attr_attention", "label": "属性の確認が必要", "detail": "、".join(attr_warnings)})
    else:
        checks.append({"type": "attr_ok", "label": "属性：問題なし"})
    
    # constraint（cannot）チェック
    members = detail.get("members", [])
    constrained = [m for m in members if m.get("constraint")]
    if constrained:
        warnings.append({"type": "constraint", "label": f"cannot制約あり（{len(constrained)}件）", "detail": "結合禁止の制約が適用されています"})
    
    return checks, warnings


# ========================================
# UI Components
# ========================================

def Badge(label, color="gray"):
    """ステータスバッジ"""
    return html.Span(label, className=f"badge badge--{color}")


def KeyChips(keys):
    """複合キー表示"""
    return html.Div([html.Span(k, className="key-chip") for k in keys], className="key-chips")


def PreviewBlock(label, lines):
    """プレビューブロック"""
    return html.Div([
        html.Div(label, className="preview-block__label"),
        *[html.Div(line, className="preview-block__item") for line in lines],
    ], className="preview-block")


def SectionCard(title, children, right=None, title_extra=None):
    """セクションカード"""
    title_content = [html.Span(title, className="section-card__title-text")]
    if title_extra:
        title_content.append(title_extra)
    
    return html.Div([
        html.Div([
            html.Div(title_content, className="section-card__title"),
            html.Div(right) if right else None,
        ], className="section-card__header"),
        html.Div(children, className="section-card__body"),
    ], className="section-card")


def CheckSummary(checks, warnings):
    """確認サマリコンポーネント"""
    # 全体の状態を判定
    if not warnings:
        status = "ok"
        status_text = "問題なし — このまま承認できます"
        status_class = "check-summary--ok"
    else:
        status = "attention"
        status_text = f"{len(warnings)}件の確認が必要です"
        status_class = "check-summary--attention"
    
    # チェック項目のリスト
    check_items = []
    for c in checks:
        check_items.append(
            html.Div([
                html.Span("✓", className="check-summary__icon check-summary__icon--ok"),
                html.Span(c["label"], className="check-summary__label"),
            ], className="check-summary__item")
        )
    
    for w in warnings:
        check_items.append(
            html.Div([
                html.Span("⚠", className="check-summary__icon check-summary__icon--warn"),
                html.Span(w["label"], className="check-summary__label check-summary__label--warn"),
                html.Span(w.get("detail", ""), className="check-summary__detail") if w.get("detail") else None,
            ], className="check-summary__item check-summary__item--warn")
        )
    
    return html.Div([
        html.Div([
            html.Span("📋", className="check-summary__header-icon"),
            html.Span("確認サマリ", className="check-summary__header-title"),
            html.Span(status_text, className=f"check-summary__status check-summary__status--{status}"),
        ], className="check-summary__header"),
        html.Div(check_items, className="check-summary__body"),
    ], className=f"check-summary {status_class}")


def MemberCard(member, index):
    """構成員カード"""
    has_constraint = member.get("constraint") is not None
    pk_str = " ".join(member["pk"])
    
    # 一致バッジ
    badges = []
    for key, label in [("name", "氏名"), ("phone", "電話"), ("email", "メール"), ("address", "住所")]:
        if member["matches"].get(key):
            badges.append(Badge(f"{label}一致", "blue"))
    if has_constraint:
        badges.append(Badge(f"cannot: {member['constraint']['reason']}", "red"))
    
    card_class = "member-card member-card--constrained" if has_constraint else "member-card"
    btn_type = "btn-retract" if has_constraint else "btn-cannot"
    btn_label = "撤回申請" if has_constraint else "🚫 cannot"
    
    return html.Div([
        html.Div([
            html.Div([
                html.Div("レコードキー（複合）", className="preview-block__label"),
                KeyChips(member["pk"]),
                PreviewBlock("最小プレビュー", [member["preview"]["name"], member["preview"]["phone"], member["preview"]["email"]]),
                html.Div(f"last_seen: {member['last_seen']}", className="text-xs text-muted mt-sm"),
            ], className="member-card__info"),
            html.Div(badges, className="member-card__badges"),
        ], className="member-card__main"),
        html.Div([
            dmc.Button(btn_label, id={"type": btn_type, "index": index, "pk": pk_str}, variant="outline", color="gray" if has_constraint else "red", size="xs"),
        ], className="member-card__actions"),
    ], className=card_class)


def AttrGroup(label, items):
    """属性グループ"""
    if not items:
        return None
    
    needs_attention = len(items) > 1 or any(it.get("trust", 1) < 0.75 or it.get("shared") for it in items)
    
    pills = []
    for i, item in enumerate(items):
        classes = ["attr-pill"]
        if i == 0:
            classes.append("attr-pill--selected")
        if item.get("shared"):
            classes.append("attr-pill--shared")
        
        content = [html.Span(item["label"])]
        if item.get("shared"):
            content.append(html.Span("共有値", className="ml-sm text-xs"))
        content.append(html.Span(f"seen:{item['seen']} rec:{item['recency']:.1f} trust:{item['trust']:.1f}", className="attr-pill__meta"))
        
        pills.append(html.Div(content, className=" ".join(classes)))
    
    pills.append(dmc.Button("+ 新規値", variant="outline", color="gray", size="xs"))
    
    return html.Div([
        html.Div([
            html.Span(label, className="attr-group__label-text"),
            Badge("要対応", "amber") if needs_attention else None,
        ], className="attr-group__label"),
        html.Div(pills, className="attr-pills"),
    ], className="attr-group")


def HistoryItem(event):
    """履歴アイテム"""
    return html.Div([
        html.Div(className="history-item__marker"),
        html.Div([
            html.Div([
                html.Span(event["at"]),
                html.Span(" — "),
                html.Span(event["event"], className="history-item__event"),
                html.Span(f" — by {event['by']}", className="history-item__by"),
            ], className="history-item__header"),
            html.Div(event["note"], className="history-item__note"),
        ], className="history-item__content"),
    ], className="history-item")


# ========================================
# Page Sections
# ========================================

def FilterSection():
    """フィルタセクション"""
    return dmc.Paper(withBorder=True, p="md", mb="md", radius="md", children=[
        dmc.Text("フィルタ", weight=600, size="sm", mb="sm"),
        dmc.Group([
            dmc.Select(id="filter-table", label="source_table", data=[{"value": "all", "label": "すべて"}, {"value": "tbl_a", "label": "tbl_a"}, {"value": "tbl_b", "label": "tbl_b"}], value="all", size="sm", style={"width": "160px"}),
            dmc.Select(id="filter-status", label="状態", data=[{"value": "all", "label": "すべて"}, {"value": "要承認", "label": "要承認"}, {"value": "保留", "label": "保留"}], value="all", size="sm", style={"width": "140px"}),
            dmc.Checkbox(id="filter-exclude-pending", label="撤回申請中を除外", checked=True, size="sm", style={"marginTop": "24px"}),
        ]),
    ])


def ListSection():
    """一覧セクション"""
    return html.Div([
        html.Div([
            dmc.Text("レビュー一覧（最新）", weight=600, size="sm"),
            dmc.Text(id="cluster-count", size="xs", color="dimmed"),
        ], className="section-card__header"),
        html.Table([
            html.Thead(html.Tr([
                html.Th("cluster_id"),
                html.Th("representative（masked）"),
                html.Th("last_seen"),
                html.Th("状態"),
            ])),
            html.Tbody(id="cluster-table-body"),
        ], className="data-table"),
    ], className="section-card")


def ClusterRow(row, selected_id):
    """一覧の行"""
    rep = row["representative"]
    is_selected = row["cluster_id"] == selected_id
    row_class = "data-table__row data-table__row--selected" if is_selected else "data-table__row"
    
    return html.Tr([
        html.Td(row["cluster_id"], className="data-table__cell--mono"),
        html.Td([html.Div(rep["name"]), html.Div(rep["phone"], className="text-muted"), html.Div(rep["email"], className="text-muted")]),
        html.Td(row["last_seen"]),
        html.Td(Badge(row["status"])),
    ], id={"type": "cluster-row", "cluster_id": row["cluster_id"]}, className=row_class)


def DetailPanel(cluster_id):
    """詳細パネル"""
    if not cluster_id or cluster_id not in DETAILS:
        return dmc.Paper(withBorder=True, radius="md", p="lg", children=[dmc.Text("左の一覧からクラスタを選択してください", color="dimmed", size="sm")])
    
    d = DETAILS[cluster_id]
    diff = d["diff"]
    winner = d["rep_candidates"][0]
    
    # 確認サマリを生成
    checks, warnings = analyze_cluster(d)
    
    return html.Div([
        # 確認サマリ（NEW）
        CheckSummary(checks, warnings),
        
        # 差分バナー
        dmc.Paper(withBorder=True, radius="md", p="sm", mb="md", children=[
            html.Div([
                html.Div([
                    html.Span("前回承認との差分", className="diff-banner__label"),
                    Badge(f"+{diff['added']} 追加", "blue"),
                    Badge(f"-{diff['removed']} 削除", "red"),
                    Badge("代表 変更あり" if diff["rep_changed"] else "代表 変更なし", "red" if diff["rep_changed"] else "gray"),
                    html.Span(f"前回承認: {diff['last_approved_at']}", className="diff-banner__meta"),
                ], className="diff-banner__content"),
                dmc.Button("差分の詳細", id="btn-open-diff", variant="subtle", color="blue", size="xs"),
            ], className="diff-banner"),
        ]),
        
        # 1) 代表セクション
        SectionCard(
            "1) 代表（便宜値・自動選定）",
            title_extra=dmc.Button("代表とは？", id="btn-open-help", variant="subtle", color="gray", size="xs"),
            right=dmc.Button("候補を比較", id="btn-open-compare", variant="subtle", color="blue", size="xs") if len(d["rep_candidates"]) > 1 else None,
            children=html.Div([
                html.Div([
                    html.Div("キー（複合）", className="preview-block__label"),
                    KeyChips(winner["pk"]),
                    PreviewBlock("最小プレビュー", [winner["preview"]["name"], winner["preview"]["phone"], winner["preview"]["email"]]),
                ], className="rep-info__main"),
                html.Div([
                    Badge(winner["tag"], "blue"),
                    html.Div(f"理由: {winner['reasons']}", className="rep-info__reason"),
                    html.Div(f"score: {winner['score']}", className="rep-info__score"),
                ], className="rep-info__side"),
            ], className="rep-info"),
        ),
        
        # 2) 構成員セクション
        SectionCard(
            "2) 構成員",
            right=dmc.Text(f"{len(d['members'])}件", size="xs", color="dimmed"),
            children=[MemberCard(m, i) for i, m in enumerate(d["members"])],
        ),
        
        # 3) 属性セクション
        SectionCard(
            "3) 属性 代表候補",
            right=dmc.Button("属性を編集", variant="outline", color="gray", size="xs"),
            children=[
                AttrGroup("氏名", d["attrs"].get("name", [])),
                AttrGroup("電話（E.164）", d["attrs"].get("phone", [])),
                AttrGroup("メール", d["attrs"].get("email", [])),
                AttrGroup("住所", d["attrs"].get("address", [])),
            ],
        ),
        
        # 履歴セクション
        dmc.Accordion([
            dmc.AccordionItem(value="history", children=[
                dmc.AccordionControl("履歴（スナップショット／イベント）"),
                dmc.AccordionPanel([HistoryItem(e) for e in d["history"]]),
            ]),
        ], variant="separated", radius="md"),
    ])


def Modals():
    """モーダル群"""
    return html.Div([
        # 用語ヘルプ
        dmc.Modal(id="modal-help", title="用語ヘルプ：代表（便宜値）", size="lg", children=[
            dmc.Text("代表（便宜値）は、画面表示や外部連携のために一時的に採用する単一値です。", size="sm", mb="sm"),
            dmc.Text("実体の真実は、候補値の集合とその証跡で管理します。代表は再計算や統合により変更され得ます。", size="sm", color="dimmed"),
        ]),
        
        # 差分詳細
        dmc.Modal(id="modal-diff", title="前回承認との差分 詳細", size="xl", children=[html.Div(id="modal-diff-content")]),
        
        # 候補比較
        dmc.Drawer(id="drawer-compare", title="代表候補を比較", position="right", size="70%", children=[html.Div(id="drawer-compare-content")]),
        
        # cannot登録
        dmc.Modal(id="modal-cannot", title="結合禁止（cannot）登録", size="lg", children=[
            dmc.TextInput(id="cannot-left", label="対象(左) レコードキー", disabled=True, mb="sm"),
            dmc.TextInput(id="cannot-right", label="対象(右)", placeholder="例: C-0099 または customer_id=999", mb="sm"),
            dmc.Select(id="cannot-reason", label="理由", data=[{"value": "生年月日矛盾", "label": "生年月日矛盾"}, {"value": "個人・法人不整合", "label": "個人・法人不整合"}, {"value": "共有値のみ一致", "label": "共有値のみ一致"}, {"value": "その他", "label": "その他"}], value="共有値のみ一致", mb="md"),
            dmc.Group(position="right", children=[dmc.Button("キャンセル", id="cannot-cancel", variant="outline"), dmc.Button("登録", id="cannot-submit", color="blue")]),
        ]),
        
        # 撤回申請
        dmc.Modal(id="modal-retract", title="cannot 撤回申請", size="lg", children=[
            dmc.Text(id="retract-target", mb="sm"),
            dmc.Select(id="retract-reason", label="理由", data=[{"value": "共有値一致のみで誤除外", "label": "共有値一致のみで誤除外"}, {"value": "外部マスタ差異の解消", "label": "外部マスタ差異の解消"}, {"value": "その他", "label": "その他"}], value="共有値一致のみで誤除外", mb="sm"),
            dmc.Textarea(id="retract-note", label="補足", placeholder="根拠や参照チケット等", minRows=3, mb="md"),
            dmc.Group(position="right", children=[dmc.Button("キャンセル", id="retract-cancel", variant="outline"), dmc.Button("申請を送信", id="retract-submit", color="blue")]),
        ]),
    ])


def ApprovalBar():
    """承認バー"""
    return html.Div([
        html.Div([
            html.Span("対象: "),
            html.Span("未選択", id="approval-bar-cluster-id", className="approval-bar__cluster-id"),
        ], className="approval-bar__info"),
        html.Div([
            dmc.Button("承認", id="btn-approve", color="blue", size="sm", disabled=True),
            dmc.Button("保留", id="btn-hold", variant="outline", size="sm", disabled=True),
            dmc.Button("差戻し", id="btn-reject", variant="outline", size="sm", disabled=True),
        ], className="approval-bar__actions"),
    ], className="approval-bar")


def DiffContent(cluster_id):
    """差分詳細モーダルの内容"""
    if not cluster_id or cluster_id not in DETAILS:
        return dmc.Text("データがありません", color="dimmed")
    
    diff = DETAILS[cluster_id]["diff"]
    
    return dmc.Grid([
        dmc.Col([
            dmc.Paper(withBorder=True, p="md", radius="md", children=[
                dmc.Text("追加されたメンバ", weight=600, size="sm", mb="sm"),
                html.Ul([html.Li([html.Span(" ".join(m["pk"]), className="text-mono text-sm"), html.Span(f"（{m['reason']}）", className="text-muted ml-sm")]) for m in diff.get("added_members", [])]) if diff.get("added_members") else dmc.Text("—", color="dimmed"),
            ]),
        ], span=6),
        dmc.Col([
            dmc.Paper(withBorder=True, p="md", radius="md", children=[
                dmc.Text("削除されたメンバ", weight=600, size="sm", mb="sm"),
                html.Ul([html.Li([html.Span(" ".join(m["pk"]), className="text-mono text-sm"), html.Span(f"（{m['reason']}）", className="text-muted ml-sm")]) for m in diff.get("removed_members", [])]) if diff.get("removed_members") else dmc.Text("—", color="dimmed"),
            ]),
        ], span=6),
    ])


def CompareContent(cluster_id):
    """候補比較ドロワーの内容"""
    if not cluster_id or cluster_id not in DETAILS:
        return dmc.Text("データがありません", color="dimmed")
    
    candidates = DETAILS[cluster_id]["rep_candidates"]
    
    rows = [html.Tr([
        html.Td(Badge(c["tag"], "blue" if i == 0 else "gray")),
        html.Td(f"{c['score']}"),
        html.Td(KeyChips(c["pk"])),
        html.Td(c["preview"]["name"]),
        html.Td(c["preview"]["phone"]),
        html.Td(c["preview"]["email"]),
        html.Td(c["reasons"]),
        html.Td(dmc.Button("代表に採用", variant="outline", size="xs")),
    ]) for i, c in enumerate(candidates)]
    
    return html.Div([
        dmc.Text(f"候補数: {len(candidates)}", size="xs", color="dimmed", mb="md"),
        html.Table([
            html.Thead(html.Tr([html.Th(h) for h in ["種別", "score", "キー", "氏名", "電話", "メール", "理由", ""]])),
            html.Tbody(rows),
        ], className="data-table"),
    ])


# ========================================
# Layout
# ========================================

layout = html.Div([
    # Stores
    dcc.Store(id="selected-cluster-id"),
    dcc.Store(id="cannot-target-pk"),
    dcc.Store(id="retract-target-pk"),
    
    # Modals
    Modals(),
    
    # Page Title
    html.Div([
        html.H3("名寄せ 第1段階 承認UI", className="page-title__main"),
        html.Div("最新Run固定・軽量版", className="page-title__sub"),
    ], className="page-title"),
    
    # Two Pane Layout
    html.Div([
        html.Div([FilterSection(), ListSection()], className="two-pane__left"),
        html.Div(html.Div(id="detail-panel"), className="two-pane__right"),
    ], className="two-pane"),
    
    # Approval Bar
    ApprovalBar(),
    
    # Toast
    html.Div(id="toast-container"),
])


# ========================================
# Callbacks
# ========================================

@callback(Output("cluster-table-body", "children"), Output("cluster-count", "children"), Input("filter-table", "value"), Input("filter-status", "value"), Input("filter-exclude-pending", "checked"), Input("selected-cluster-id", "data"))
def update_list(ft, fs, ep, sel):
    filtered = [r for r in CLUSTERS if (ft == "all" or r["source_table"] == ft) and (fs == "all" or r["status"] == fs)]
    return [ClusterRow(r, sel) for r in filtered], f"件数: {len(filtered)}"


@callback(Output("selected-cluster-id", "data"), Input({"type": "cluster-row", "cluster_id": ALL}, "n_clicks"), State("selected-cluster-id", "data"), prevent_initial_call=True)
def select_row(_, cur):
    return ctx.triggered_id["cluster_id"] if ctx.triggered_id else cur


@callback(Output("detail-panel", "children"), Input("selected-cluster-id", "data"))
def update_detail(sel):
    return DetailPanel(sel)


@callback(Output("approval-bar-cluster-id", "children"), Output("btn-approve", "disabled"), Output("btn-hold", "disabled"), Output("btn-reject", "disabled"), Input("selected-cluster-id", "data"))
def update_approval_bar(sel):
    return (sel, False, False, False) if sel else ("未選択", True, True, True)


@callback(Output("toast-container", "children"), Output("selected-cluster-id", "data", allow_duplicate=True), Input("btn-approve", "n_clicks"), Input("btn-hold", "n_clicks"), Input("btn-reject", "n_clicks"), State("selected-cluster-id", "data"), prevent_initial_call=True)
def handle_action(a, h, r, sel):
    if not sel:
        return None, None
    action = {"btn-approve": "承認", "btn-hold": "保留", "btn-reject": "差戻し"}.get(ctx.triggered_id, "")
    if not action:
        return None, sel
    return html.Div([html.Span(f"{action}しました（{sel}）", className="toast__message"), html.Span("5秒以内なら取り消せます", className="toast__hint")], className="toast"), None


@callback(Output("modal-help", "opened"), Input("btn-open-help", "n_clicks"), State("modal-help", "opened"), prevent_initial_call=True)
def toggle_help(n, o):
    return not o if n else o


@callback(Output("modal-diff", "opened"), Output("modal-diff-content", "children"), Input("btn-open-diff", "n_clicks"), State("modal-diff", "opened"), State("selected-cluster-id", "data"), prevent_initial_call=True)
def toggle_diff(n, o, sel):
    return (not o, DiffContent(sel)) if n else (o, no_update)


@callback(Output("drawer-compare", "opened"), Output("drawer-compare-content", "children"), Input("btn-open-compare", "n_clicks"), State("drawer-compare", "opened"), State("selected-cluster-id", "data"), prevent_initial_call=True)
def toggle_compare(n, o, sel):
    return (not o, CompareContent(sel)) if n else (o, no_update)


@callback(Output("modal-cannot", "opened"), Output("cannot-left", "value"), Output("cannot-target-pk", "data"), Input({"type": "btn-cannot", "index": ALL, "pk": ALL}, "n_clicks"), Input("cannot-cancel", "n_clicks"), Input("cannot-submit", "n_clicks"), State("modal-cannot", "opened"), prevent_initial_call=True)
def handle_cannot(btn_clicks, cancel, submit, o):
    t = ctx.triggered_id
    if t in ("cannot-cancel", "cannot-submit"):
        return False, "", None
    if isinstance(t, dict) and t.get("type") == "btn-cannot":
        if any(c for c in btn_clicks if c):
            return True, f"レコード: {t['pk']}", t["pk"]
    return o, no_update, no_update


@callback(Output("modal-retract", "opened"), Output("retract-target", "children"), Output("retract-target-pk", "data"), Input({"type": "btn-retract", "index": ALL, "pk": ALL}, "n_clicks"), Input("retract-cancel", "n_clicks"), Input("retract-submit", "n_clicks"), State("modal-retract", "opened"), prevent_initial_call=True)
def handle_retract(btn_clicks, cancel, submit, o):
    t = ctx.triggered_id
    if t in ("retract-cancel", "retract-submit"):
        return False, "", None
    if isinstance(t, dict) and t.get("type") == "btn-retract":
        if any(c for c in btn_clicks if c):
            return True, f"対象: {t['pk']}", t["pk"]
    return o, no_update, no_update