from __future__ import annotations

import pandas as pd
import streamlit as st

from lib import api

st.set_page_config(page_title="库存", page_icon="📦", layout="wide")

st.title("📦 库存管理")
st.write("筛选、编辑、消耗或丢弃库存批次，所有操作都会记录事件。")

filters_col, action_col = st.columns([2, 1])
with filters_col:
    location = st.selectbox("位置", options=["", "fridge", "freezer", "pantry"], index=0)
    status = st.selectbox("状态", options=["", "in_stock", "consumed", "discarded"], index=0)
    keyword = st.text_input("搜索关键词")

filters = {"location": location or None, "status": status or None, "keyword": keyword or None}
response = api.list_batches(filters)
batches = response["batches"]

if batches:
    df = pd.DataFrame(batches)
    display_df = df[[
        "batch_id",
        "item_name_snapshot",
        "quantity",
        "unit",
        "expire_date",
        "location",
        "status",
        "source_type",
    ]]
    display_df.rename(
        columns={
            "batch_id": "批次",
            "item_name_snapshot": "食材",
            "quantity": "数量",
            "unit": "单位",
            "expire_date": "到期日",
            "location": "位置",
            "status": "状态",
            "source_type": "来源",
        },
        inplace=True,
    )

    st.markdown("### 批次列表（可编辑）")
    edited = st.data_editor(
        display_df,
        use_container_width=True,
        num_rows="dynamic",
        disabled=["批次", "食材", "单位", "状态", "来源"],
    )

    if st.button("保存编辑", type="primary"):
        for _, row in edited.iterrows():
            original = df[df["batch_id"] == row["批次"]].iloc[0]
            patch = {}
            if row["数量"] != original["quantity"]:
                patch["quantity"] = float(row["数量"])
            if row["到期日"] != original["expire_date"]:
                patch["expire_date"] = row["到期日"]
            if row["位置"] != original["location"]:
                patch["location"] = row["位置"]
            if patch:
                api.update_batch(original["batch_id"], patch)
        st.success("已保存批次更新")

    st.markdown("### 批次操作")
    batch_ids = [b["batch_id"] for b in batches]
    selected_batch = st.selectbox("选择批次", batch_ids)
    col1, col2 = st.columns(2)
    with col1:
        consume_qty = st.number_input("消耗数量", min_value=0.0, step=0.5)
        if st.button("确认消耗"):
            api.consume_batch(selected_batch, consume_qty, note="手动消耗")
            st.success("已记录消耗事件")
    with col2:
        discard_qty = st.number_input("丢弃数量", min_value=0.0, step=0.5)
        discard_reason = st.text_input("丢弃原因")
        if st.button("确认丢弃"):
            api.discard_batch(selected_batch, discard_qty, reason=discard_reason)
            st.success("已记录丢弃事件")

    st.markdown("### 事件历史")
    events = api.list_batch_events(selected_batch)["events"]
    if events:
        ev_df = pd.DataFrame(events)
        ev_df = ev_df[["event_type", "delta_quantity", "note", "created_at"]]
        ev_df.rename(
            columns={
                "event_type": "事件",
                "delta_quantity": "数量变化",
                "note": "备注",
                "created_at": "时间",
            },
            inplace=True,
        )
        st.dataframe(ev_df, use_container_width=True, hide_index=True)
    else:
        st.info("该批次暂无事件记录。")
else:
    st.info("没有找到匹配的批次，先去上传识别或调整筛选条件。")
