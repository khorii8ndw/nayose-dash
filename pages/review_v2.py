"""
レビュー（タスクキュー型）- v2
縦1カラム: 代表レコード → その他のレコード（縦スクロール）
統合値は非表示、アクションバーから編集
"""

import dash
from dash import html, dcc, callback, Input, Output, State, ctx, ALL, no_update
import dash_mantine_components as dmc

dash.register_page(__name__, path="/review-v2")


# ========================================
# Data (Mock)
# ========================================

REVIEW_QUEUE = ["C-0001", "C-0003"]

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
            {"pk": ["customer_id=1001", "system=A"], "preview": {"name": "佐々木 太郎", "phone": "+81-90-1234-5678", "email": "sasaki@example.com"}, "matches": {"name": True, "phone": True, "email": True, "address": False}, "last_seen": "2025/11/12 14:22", "constraint": None, "is_rep": True},
            {"pk": ["customer_id=1002", "system=A"], "preview": {"name": "佐々木 太郎", "phone": "+81-90-1234-5678", "email": "x_sasaki@example.com"}, "matches": {"name": True, "phone": True, "email": False, "address": True}, "last_seen": "2025/11/10 10:05", "constraint": {"reason": "共有値のみ一致"}, "is_rep": False},
            {"pk": ["customer_id=1003", "system=X"], "preview": {"name": "佐々木 太郎", "phone": "+81-90-1111-2222", "email": "sasaki3@example.com"}, "matches": {"name": True, "phone": False, "email": False, "address": True}, "last_seen": "2025/11/14 09:00", "constraint": None, "is_rep": False, "is_new": True},
        ],
        "attrs": {
            "name": [{"id": "name1", "label": "佐々木 太郎", "seen": 4, "recency": 0.9, "trust": 0.8, "shared": False}, {"id": "name2", "label": "ササキ タロウ", "seen": 2, "recency": 0.7, "trust": 0.6, "shared": False}],
            "phone": [{"id": "phone1", "label": "+81-90-1234-5678", "seen": 3, "recency": 0.8, "trust": 0.8, "shared": False}, {"id": "phone2", "label": "+81-80-9999-8888", "seen": 5, "recency": 0.4, "trust": 0.7, "shared": True}],
            "email": [{"id": "email1", "label": "sasaki@example.com", "seen": 3, "recency": 0.9, "trust": 0.8, "shared": False}],
            "address": [{"id": "addr1", "label": "東京都千代田区千代田1-1", "seen": 2, "recency": 0.8, "trust": 0.7, "shared": False}],
        },
        "merged_values": {"name": "佐々木 太郎", "phone": "+81-90-1234-5678", "email": "sasaki@example.com", "address": "東京都千代田区千代田1-1"},
    },
    "C-0003": {
        "cluster_id": "C-0003",
        "diff": {"added": 2, "removed": 0, "rep_changed": False, "last_approved_at": "2025/11/11 15:30",
                 "added_members": [{"pk": ["customer_id=3002", "system=C"], "reason": "氏名一致"}, {"pk": ["customer_id=3003", "system=A"], "reason": "住所一致"}], "removed_members": []},
        "rep_candidates": [
            {"pk": ["customer_id=3001", "system=A"], "tag": "自動選定", "reasons": "出所信頼度", "preview": {"name": "田中 一郎", "phone": "+81-90-5555-6666", "email": "tanaka@example.com"}, "score": 0.95},
        ],
        "members": [
            {"pk": ["customer_id=3001", "system=A"], "preview": {"name": "田中 一郎", "phone": "+81-90-5555-6666", "email": "tanaka@example.com"}, "matches": {"name": True, "phone": True, "email": True, "address": True}, "last_seen": "2025/11/13 18:20", "constraint": None, "is_rep": True},
            {"pk": ["customer_id=3002", "system=C"], "preview": {"name": "田中 一郎", "phone": "+81-80-7777-8888", "email": "tanaka2@example.com"}, "matches": {"name": True, "phone": False, "email": False, "address": True}, "last_seen": "2025/11/12 12:00", "constraint": None, "is_rep": False, "is_new": True},
            {"pk": ["customer_id=3003", "system=A"], "preview": {"name": "タナカイチロウ", "phone": "+81-90-5555-6666", "email": "ichiro@example.com"}, "matches": {"name": False, "phone": True, "email": False, "address": True}, "last_seen": "2025/11/14 10:00", "constraint": None, "is_rep": False, "is_new": True},
        ],
        "attrs": {
            "name": [{"id": "name1", "label": "田中 一郎", "seen": 6, "recency": 0.9, "trust": 0.85, "shared": False}],
            "phone": [{"id": "phone1", "label": "+81-90-5555-6666", "seen": 4, "recency": 0.9, "trust": 0.8, "shared": False}, {"id": "phone2", "label": "+81-80-7777-8888", "seen": 2, "recency": 0.7, "trust": 0.6, "shared": True}],
            "email": [{"id": "email1", "label": "tanaka@example.com", "seen": 4, "recency": 0.9, "trust": 0.8, "shared": False}],
            "address": [{"id": "addr1", "label": "神奈川県横浜市中区本町1-1", "seen": 5, "recency": 0.85, "trust": 0.8, "shared": False}],
        },
        "merged_values": {"name": "田中 一郎", "phone": "+81-90-5555-6666", "email": "tanaka@example.com", "address": "神奈川県横浜市中区本町1-1"},
    },
}


# ========================================
# UI Components
# ========================================

def Badge(label, color="gray"):
    return html.Span(label, className=f"badge badge--{color}")


def KeyChips(keys):
    return html.Div([html.Span(k, className="key-chip") for k in keys], className="key-chips")


# ========================================
# Header & Change Summary
# ========================================

def QueueHeader(index, total):
    remaining = total - index
    if remaining <= 0:
        return html.Div([
            html.Span("レビュー完了", className="queue-header__title"),
        ], className="queue-header")
    
    return html.Div([
        html.Span("名寄せレビュー", className="queue-header__title"),
        html.Span(f"残り {remaining}件", className="queue-header__count"),
    ], className="queue-header")


def ChangeSummaryBar(cluster_id):
    """変更サマリバー"""
    if not cluster_id or cluster_id not in DETAILS:
        return None
    
    detail = DETAILS[cluster_id]
    diff = detail["diff"]
    added = diff.get("added", 0)
    removed = diff.get("removed", 0)
    last_date = diff.get("last_approved_at", "")
    
    if added == 0 and removed == 0:
        return None
    
    parts = []
    if added > 0:
        parts.append(f"{added}件のレコードが追加されました")
    if removed > 0:
        parts.append(f"{removed}件のレコードが削除されました")
    
    message = "、".join(parts)
    
    return html.Div([
        html.Div([
            html.Span(message, className="change-summary__message"),
            html.Span(f"（{last_date}）", className="change-summary__date"),
        ], className="change-summary__content"),
        dmc.Button("詳細", id="btn-change-detail", variant="subtle", color="blue", size="sm", compact=True),
    ], className="change-summary")


# ========================================
# Record Cards
# ========================================

def RecordCard(member, index, is_rep=False, show_compare=False, candidate_count=0):
    """レコードカード（代表・その他共通）"""
    is_new = member.get("is_new", False)
    has_constraint = member.get("constraint") is not None
    pk_str = " ".join(member["pk"])
    
    # カードのクラス
    card_classes = ["record-card"]
    if is_rep:
        card_classes.append("record-card--representative")
    if is_new:
        card_classes.append("record-card--new")
    if has_constraint:
        card_classes.append("record-card--constrained")
    
    # ステータスバッジ
    status_badges = []
    if is_rep:
        status_badges.append(Badge("★ 代表", "blue"))
    if is_new:
        status_badges.append(Badge("NEW", "green"))
    if has_constraint:
        status_badges.append(Badge(f"cannot: {member['constraint']['reason']}", "red"))
    
    # 一致バッジ
    match_badges = []
    if not is_rep:
        for key, label in [("name", "氏名"), ("phone", "電話"), ("email", "メール"), ("address", "住所")]:
            if member["matches"].get(key):
                match_badges.append(Badge(f"{label}一致", "blue"))
    
    # アクションボタン
    action_btns = []
    if is_rep and show_compare and candidate_count > 1:
        action_btns.append(
            dmc.Button("候補を比較", id="btn-open-compare-v2", variant="subtle", color="blue", size="sm", compact=True)
        )
    elif has_constraint:
        action_btns.append(
            dmc.Button("撤回申請", id={"type": "btn-retract", "index": index, "pk": pk_str}, variant="outline", color="gray", size="sm")
        )
    elif not is_rep:
        action_btns.append(
            dmc.Button("🚫 cannot", id={"type": "btn-cannot", "index": index, "pk": pk_str}, variant="outline", color="red", size="sm")
        )
    
    return html.Div([
        # ヘッダー行（バッジ + アクション）
        html.Div([
            html.Div(status_badges, className="record-card__badges"),
            html.Div(action_btns, className="record-card__actions") if action_btns else None,
        ], className="record-card__header"),
        
        # メイン情報（名前 / 電話 / メール）
        html.Div([
            html.Span(member["preview"]["name"], className="record-card__name"),
            html.Span(member["preview"]["phone"], className="record-card__phone"),
            html.Span(member["preview"]["email"], className="record-card__email"),
        ], className="record-card__main"),
        
        # 一致バッジ（代表以外）
        html.Div(match_badges, className="record-card__matches") if match_badges else None,
        
        # フッター行（日時 + キー）
        html.Div([
            html.Span(f"last_seen: {member['last_seen']}", className="record-card__date"),
            KeyChips(member["pk"]),
        ], className="record-card__footer"),
    ], className=" ".join(card_classes))


# ========================================
# Main Task Content
# ========================================

def TaskContent(cluster_id):
    """タスク内容（縦1カラム）"""
    if not cluster_id:
        return html.Div([
            html.Div("🎉", className="empty-state__icon"),
            html.Div("すべてのレビューが完了しました", className="empty-state__title"),
            html.Div("新しいタスクが届くまでお待ちください", className="empty-state__sub"),
        ], className="empty-state")
    
    if cluster_id not in DETAILS:
        return html.Div("データがありません", className="text-muted")
    
    detail = DETAILS[cluster_id]
    members = detail["members"]
    candidate_count = len(detail["rep_candidates"])
    
    # 代表レコード
    rep_member = next((m for m in members if m.get("is_rep")), members[0])
    
    # その他のレコード（新規を先頭、constraint適用中を末尾）
    other_members = [m for m in members if not m.get("is_rep")]
    other_members.sort(key=lambda m: (
        0 if m.get("is_new") else 1,
        1 if m.get("constraint") else 0,
    ))
    
    cards = []
    
    # 代表レコード
    cards.append(RecordCard(rep_member, -1, is_rep=True, show_compare=True, candidate_count=candidate_count))
    
    # その他のレコード
    for i, m in enumerate(other_members):
        cards.append(RecordCard(m, i))
    
    return html.Div(cards, className="record-list")


# ========================================
# Action Bar
# ========================================

def ActionBar(cluster_id):
    """アクションバー（Tertiary → Secondary → Primary の順）"""
    if not cluster_id:
        return None
    
    return html.Div([
        html.Div([
            # Tertiary: 統合値編集
            dmc.Button("統合値を編集...", id="btn-open-merged-edit", variant="subtle", color="gray", size="md"),
            # Secondary: スキップ
            dmc.Button("スキップ", id="btn-skip", variant="outline", size="md"),
            # Primary: 確定
            dmc.Button("確定", id="btn-confirm", color="blue", size="md"),
        ], className="action-bar__buttons"),
    ], className="action-bar")


# ========================================
# Modals
# ========================================

def MergedEditContent(cluster_id):
    """統合値編集モーダルの内容"""
    if not cluster_id or cluster_id not in DETAILS:
        return dmc.Text("データがありません", color="dimmed")
    
    detail = DETAILS[cluster_id]
    attrs = detail["attrs"]
    
    attr_labels = {"name": "氏名", "phone": "電話", "email": "メール", "address": "住所"}
    
    sections = []
    for attr_key, items in attrs.items():
        label = attr_labels.get(attr_key, attr_key)
        
        options = []
        for item in items:
            option_label = item["label"]
            if item.get("shared"):
                option_label += " （共有値）"
            option_label += f" — 観測:{item['seen']}回 信頼度:{item['trust']}"
            options.append({"value": item["id"], "label": option_label})
        
        sections.append(
            html.Div([
                html.Div(label, className="merged-edit__label"),
                dmc.RadioGroup(
                    id={"type": "merged-edit-radio", "attr": attr_key},
                    children=[dmc.Radio(label=opt["label"], value=opt["value"]) for opt in options],
                    value=items[0]["id"] if items else None,
                    size="sm",
                ),
            ], className="merged-edit__group")
        )
    
    return html.Div(sections, className="merged-edit__content")


def DiffContent(cluster_id):
    """差分詳細モーダルの内容"""
    if not cluster_id or cluster_id not in DETAILS:
        return dmc.Text("データがありません", color="dimmed")
    
    diff = DETAILS[cluster_id]["diff"]
    
    return dmc.Grid([
        dmc.Col([
            dmc.Paper(withBorder=True, p="md", radius="md", children=[
                dmc.Text("追加されたメンバ", weight=600, size="sm", mb="sm"),
                html.Ul([
                    html.Li([
                        html.Span(" ".join(m["pk"]), className="text-mono"),
                        html.Span(f"（{m['reason']}）", className="text-muted"),
                    ]) for m in diff.get("added_members", [])
                ]) if diff.get("added_members") else dmc.Text("—", color="dimmed"),
            ]),
        ], span=6),
        dmc.Col([
            dmc.Paper(withBorder=True, p="md", radius="md", children=[
                dmc.Text("削除されたメンバ", weight=600, size="sm", mb="sm"),
                html.Ul([
                    html.Li([
                        html.Span(" ".join(m["pk"]), className="text-mono"),
                        html.Span(f"（{m['reason']}）", className="text-muted"),
                    ]) for m in diff.get("removed_members", [])
                ]) if diff.get("removed_members") else dmc.Text("—", color="dimmed"),
            ]),
        ], span=6),
    ])


def CompareContent(cluster_id):
    """候補比較ドロワーの内容"""
    if not cluster_id or cluster_id not in DETAILS:
        return dmc.Text("データがありません", color="dimmed")
    
    candidates = DETAILS[cluster_id]["rep_candidates"]
    
    cards = []
    for i, c in enumerate(candidates):
        cards.append(
            html.Div([
                html.Div([
                    Badge(c["tag"], "blue" if i == 0 else "gray"),
                    html.Span(f"score: {c['score']}", className="compare-card__score"),
                ], className="compare-card__header"),
                html.Div([
                    html.Span(c["preview"]["name"], className="compare-card__name"),
                    html.Span(c["preview"]["phone"]),
                    html.Span(c["preview"]["email"]),
                ], className="compare-card__preview"),
                html.Div([
                    KeyChips(c["pk"]),
                ], className="compare-card__keys"),
                html.Div(f"理由: {c['reasons']}", className="compare-card__reason"),
                html.Div([
                    dmc.Button("代表に採用", variant="outline", size="sm"),
                ], className="compare-card__action"),
            ], className="compare-card")
        )
    
    return html.Div([
        dmc.Text(f"候補数: {len(candidates)}", size="sm", color="dimmed", mb="md"),
        html.Div(cards, className="compare-cards"),
    ])


def Modals():
    """モーダル群"""
    return html.Div([
        # 差分詳細
        dmc.Modal(id="modal-diff-v2", title="前回承認との差分", size="lg", children=[
            html.Div(id="modal-diff-content-v2"),
        ]),
        
        # 候補比較
        dmc.Drawer(id="drawer-compare-v2", title="代表候補を比較", position="right", size="lg", children=[
            html.Div(id="drawer-compare-content-v2"),
        ]),
        
        # 統合値編集
        dmc.Modal(id="modal-merged-edit", title="統合値を編集", size="lg", children=[
            html.Div(id="modal-merged-edit-content"),
            dmc.Group([
                dmc.Button("キャンセル", id="merged-edit-cancel", variant="outline"),
                dmc.Button("適用", id="merged-edit-apply", color="blue"),
            ], position="right", mt="lg"),
        ]),
        
        # cannot登録
        dmc.Modal(id="modal-cannot-v2", title="結合禁止（cannot）登録", size="md", children=[
            dmc.TextInput(id="cannot-left-v2", label="対象レコード", disabled=True, mb="sm"),
            dmc.TextInput(id="cannot-right-v2", label="結合禁止先", placeholder="例: C-0099 または customer_id=999", mb="sm"),
            dmc.Select(id="cannot-reason-v2", label="理由", data=[
                {"value": "生年月日矛盾", "label": "生年月日矛盾"},
                {"value": "個人・法人不整合", "label": "個人・法人不整合"},
                {"value": "共有値のみ一致", "label": "共有値のみ一致"},
                {"value": "その他", "label": "その他"},
            ], value="共有値のみ一致", mb="md"),
            dmc.Group([
                dmc.Button("キャンセル", id="cannot-cancel-v2", variant="outline"),
                dmc.Button("登録", id="cannot-submit-v2", color="blue"),
            ], position="right"),
        ]),
        
        # 撤回申請
        dmc.Modal(id="modal-retract-v2", title="cannot 撤回申請", size="md", children=[
            dmc.Text(id="retract-target-v2", mb="sm"),
            dmc.Select(id="retract-reason-v2", label="理由", data=[
                {"value": "共有値一致のみで誤除外", "label": "共有値一致のみで誤除外"},
                {"value": "外部マスタ差異の解消", "label": "外部マスタ差異の解消"},
                {"value": "その他", "label": "その他"},
            ], value="共有値一致のみで誤除外", mb="sm"),
            dmc.Textarea(id="retract-note-v2", label="補足", placeholder="根拠や参照チケット等", minRows=3, mb="md"),
            dmc.Group([
                dmc.Button("キャンセル", id="retract-cancel-v2", variant="outline"),
                dmc.Button("申請を送信", id="retract-submit-v2", color="blue"),
            ], position="right"),
        ]),
    ])


# ========================================
# Layout
# ========================================

layout = html.Div([
    # Stores
    dcc.Store(id="queue-index", data=0),
    dcc.Store(id="queue-items", data=REVIEW_QUEUE),
    dcc.Store(id="cannot-target-pk-v2"),
    dcc.Store(id="retract-target-pk-v2"),
    
    # Modals
    Modals(),
    
    # Main Layout
    html.Div([
        html.Div(id="queue-header-container"),
        html.Div(id="change-summary-container"),
        html.Div(id="task-content-container", className="task-container"),
        html.Div(id="action-bar-container"),
    ], className="queue-layout"),
    
    # Toast
    html.Div(id="toast-container-v2"),
])


# ========================================
# Callbacks
# ========================================

@callback(
    Output("queue-header-container", "children"),
    Output("change-summary-container", "children"),
    Output("task-content-container", "children"),
    Output("action-bar-container", "children"),
    Input("queue-index", "data"),
    State("queue-items", "data"),
)
def update_view(index, queue):
    total = len(queue)
    cluster_id = queue[index] if index < total else None
    
    return (
        QueueHeader(index, total),
        ChangeSummaryBar(cluster_id),
        TaskContent(cluster_id),
        ActionBar(cluster_id),
    )


@callback(
    Output("queue-index", "data"),
    Output("toast-container-v2", "children"),
    Input("btn-confirm", "n_clicks"),
    Input("btn-skip", "n_clicks"),
    State("queue-index", "data"),
    State("queue-items", "data"),
    prevent_initial_call=True,
)
def handle_action(confirm_clicks, skip_clicks, current_index, queue):
    if not ctx.triggered_id:
        return current_index, None
    
    action = "確定" if ctx.triggered_id == "btn-confirm" else "スキップ"
    cluster_id = queue[current_index] if current_index < len(queue) else None
    
    next_index = current_index + 1
    
    toast = html.Div([
        html.Span(f"{action}しました（{cluster_id}）"),
    ], className="toast") if cluster_id else None
    
    return next_index, toast


@callback(
    Output("modal-diff-v2", "opened"),
    Output("modal-diff-content-v2", "children"),
    Input("btn-change-detail", "n_clicks"),
    State("modal-diff-v2", "opened"),
    State("queue-index", "data"),
    State("queue-items", "data"),
    prevent_initial_call=True,
)
def toggle_diff(n, opened, idx, queue):
    cluster_id = queue[idx] if idx < len(queue) else None
    return (not opened, DiffContent(cluster_id)) if n else (opened, no_update)


@callback(
    Output("drawer-compare-v2", "opened"),
    Output("drawer-compare-content-v2", "children"),
    Input("btn-open-compare-v2", "n_clicks"),
    State("drawer-compare-v2", "opened"),
    State("queue-index", "data"),
    State("queue-items", "data"),
    prevent_initial_call=True,
)
def toggle_compare(n, opened, idx, queue):
    cluster_id = queue[idx] if idx < len(queue) else None
    return (not opened, CompareContent(cluster_id)) if n else (opened, no_update)


@callback(
    Output("modal-merged-edit", "opened"),
    Output("modal-merged-edit-content", "children"),
    Input("btn-open-merged-edit", "n_clicks"),
    Input("merged-edit-cancel", "n_clicks"),
    Input("merged-edit-apply", "n_clicks"),
    State("modal-merged-edit", "opened"),
    State("queue-index", "data"),
    State("queue-items", "data"),
    prevent_initial_call=True,
)
def toggle_merged_edit(open_clicks, cancel_clicks, apply_clicks, opened, idx, queue):
    t = ctx.triggered_id
    if t in ("merged-edit-cancel", "merged-edit-apply"):
        return False, no_update
    if t == "btn-open-merged-edit":
        cluster_id = queue[idx] if idx < len(queue) else None
        return True, MergedEditContent(cluster_id)
    return opened, no_update


@callback(
    Output("modal-cannot-v2", "opened"),
    Output("cannot-left-v2", "value"),
    Output("cannot-target-pk-v2", "data"),
    Input({"type": "btn-cannot", "index": ALL, "pk": ALL}, "n_clicks"),
    Input("cannot-cancel-v2", "n_clicks"),
    Input("cannot-submit-v2", "n_clicks"),
    State("modal-cannot-v2", "opened"),
    prevent_initial_call=True,
)
def handle_cannot(btn_clicks, cancel, submit, opened):
    t = ctx.triggered_id
    if t in ("cannot-cancel-v2", "cannot-submit-v2"):
        return False, "", None
    if isinstance(t, dict) and t.get("type") == "btn-cannot":
        if any(c for c in btn_clicks if c):
            return True, t["pk"], t["pk"]
    return opened, no_update, no_update


@callback(
    Output("modal-retract-v2", "opened"),
    Output("retract-target-v2", "children"),
    Output("retract-target-pk-v2", "data"),
    Input({"type": "btn-retract", "index": ALL, "pk": ALL}, "n_clicks"),
    Input("retract-cancel-v2", "n_clicks"),
    Input("retract-submit-v2", "n_clicks"),
    State("modal-retract-v2", "opened"),
    prevent_initial_call=True,
)
def handle_retract(btn_clicks, cancel, submit, opened):
    t = ctx.triggered_id
    if t in ("retract-cancel-v2", "retract-submit-v2"):
        return False, "", None
    if isinstance(t, dict) and t.get("type") == "btn-retract":
        if any(c for c in btn_clicks if c):
            return True, f"対象: {t['pk']}", t["pk"]
    return opened, no_update, no_update