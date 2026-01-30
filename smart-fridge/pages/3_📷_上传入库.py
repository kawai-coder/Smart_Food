from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from lib import api

st.set_page_config(page_title="上传入库", page_icon="📷", layout="wide")

st.title("📷 上传照片入库")
st.write("上传冰箱照片或使用示例检测结果，确认后批次自动入库。")

if "last_image_id" not in st.session_state:
    st.session_state.last_image_id = None
if "last_detections" not in st.session_state:
    st.session_state.last_detections = []

col1, col2 = st.columns([2, 1])
with col1:
    uploaded = st.file_uploader("上传冰箱照片", type=["png", "jpg", "jpeg"])
with col2:
    demo_dir = Path(__file__).resolve().parents[1] / "assets" / "demo_images"
    demo_images = list(demo_dir.glob("*.*")) if demo_dir.exists() else []
    use_demo = st.button("使用示例图片")
    if use_demo and demo_images:
        demo_path = demo_images[0]
        st.image(str(demo_path), caption="示例图片", use_column_width=True)
        image_id = f"demo_{demo_path.stem}"
        result = api.detect(image_id, provider="mock")
        st.session_state.last_image_id = image_id
        st.session_state.last_detections = result["detections"]
        st.success("已使用示例图片生成检测结果")
    elif use_demo and not demo_images:
        st.warning("未找到示例图片，可直接上传或使用随机检测结果。")

    if st.button("生成随机示例检测结果"):
        image_id = "demo_random"
        result = api.detect(image_id, provider="mock")
        st.session_state.last_image_id = image_id
        st.session_state.last_detections = result["detections"]
        st.success("已生成示例检测结果")

if uploaded:
    upload_result = api.upload_image(uploaded)
    st.session_state.last_image_id = upload_result["image_id"]
    st.image(uploaded, caption="已上传图片", use_column_width=True)
    if st.button("开始识别", type="primary"):
        result = api.detect(st.session_state.last_image_id, provider="mock")
        st.session_state.last_detections = result["detections"]

if st.session_state.last_detections:
    st.markdown("### 识别结果（可编辑）")
    det_df = pd.DataFrame(st.session_state.last_detections)
    display_df = det_df[[
        "item_id",
        "item_name",
        "quantity",
        "unit",
        "suggest_expire_date",
        "location",
    ]]
    display_df.rename(
        columns={
            "item_id": "item_id",
            "item_name": "食材",
            "quantity": "数量",
            "unit": "单位",
            "suggest_expire_date": "到期日",
            "location": "位置",
        },
        inplace=True,
    )
    edited_df = st.data_editor(display_df, use_container_width=True, num_rows="dynamic")

    if st.button("确认入库", type="primary"):
        batches = []
        for _, row in edited_df.iterrows():
            batches.append(
                {
                    "item_id": row.get("item_id"),
                    "item_name": row.get("食材"),
                    "quantity": row.get("数量"),
                    "unit": row.get("单位"),
                    "expire_date": row.get("到期日"),
                    "location": row.get("位置"),
                }
            )
        api.bulk_create_batches(
            source={"type": "image", "image_id": st.session_state.last_image_id},
            batches=batches,
        )
        st.success("已成功入库！可以前往库存页查看。")
        st.page_link("pages/2_📦_库存.py", label="前往库存", icon="📦")
else:
    st.info("上传图片后点击“开始识别”，或使用示例检测结果进行演示。")
