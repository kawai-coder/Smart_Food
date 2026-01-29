from __future__ import annotations

import pandas as pd
import streamlit as st

from lib import api

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

st.title("📊 冰箱全局概览")
st.write("快速了解库存健康度、临期风险与最近操作。")

summary = api.dashboard_summary()
metrics = st.columns(3)
metrics[0].metric("即将过期批次数", summary.get("kpi_expiring", 0))
metrics[1].metric("在库批次数", summary.get("kpi_batches", 0))
metrics[2].metric("今日可做菜数", summary.get("kpi_recipes", 0))

st.markdown("### 即将过期 Top N")
expiring = api.list_expiring(days=3)["batches"]
if expiring:
    df = pd.DataFrame(expiring)
    df = df[["item_name_snapshot", "quantity", "unit", "expire_date", "days_left", "location"]]
    df.rename(
        columns={
            "item_name_snapshot": "食材",
            "quantity": "数量",
            "unit": "单位",
            "expire_date": "到期日",
            "days_left": "剩余天数",
            "location": "位置",
        },
        inplace=True,
    )
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.success("暂无临期批次，库存很健康！")

st.markdown("### 最近事件流")
events = api.list_events(limit=10)["events"]
if events:
    ev_df = pd.DataFrame(events)
    ev_df = ev_df[["event_type", "batch_id", "delta_quantity", "note", "created_at"]]
    ev_df.rename(
        columns={
            "event_type": "事件",
            "batch_id": "批次",
            "delta_quantity": "数量变化",
            "note": "备注",
            "created_at": "时间",
        },
        inplace=True,
    )
    st.dataframe(ev_df, use_container_width=True, hide_index=True)
else:
    st.info("还没有事件记录，先去上传识别一些食材吧。")

st.markdown("### 快捷入口")
cols = st.columns(2)
with cols[0]:
    st.page_link("pages/3_📷_上传入库.py", label="📷 上传入库", icon="📷")
with cols[1]:
    st.page_link("pages/4_🍽️_菜单.py", label="🍽️ 菜单生成", icon="🍽️")
