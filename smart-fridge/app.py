from __future__ import annotations

import streamlit as st

from db.seed import seed
from lib import db

st.set_page_config(page_title="Smart Fridge Demo", page_icon="🧊", layout="wide")

db.init_db()
if db.count_rows("items") == 0:
    seed()

st.title("🧊 Smart Fridge 智能冰箱 Demo")
st.write(
    "欢迎体验一镜到底的智能冰箱 MVP：从上传图片识别食材，到入库管理，再到菜单生成与购物清单。"
)

st.markdown("### 快速开始")
st.page_link("pages/3_📷_上传入库.py", label="📷 上传入库", icon="📷")
st.page_link("pages/2_📦_库存.py", label="📦 库存管理", icon="📦")
st.page_link("pages/4_🍽️_菜单.py", label="🍽️ 菜单生成", icon="🍽️")
st.page_link("pages/5_🧾_购物清单.py", label="🧾 购物清单", icon="🧾")

st.info("提示：即使没有图片，也可以使用上传页中的“生成随机示例检测结果”按钮进行演示。")
