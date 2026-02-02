from __future__ import annotations

import json
import math

import pandas as pd
import streamlit as st
from streamlit import components

from lib import api


def render_live_bubbles(expiring_data: list[dict]) -> None:
    st.markdown("### 🥗 食材生命体征 (Live)")
    if not expiring_data:
        st.success("暂无临期批次，库存很健康！")
        return

    nodes = []
    for entry in expiring_data[:30]:
        days_left = entry.get("days_left")
        days_left = int(days_left) if isinstance(days_left, (int, float)) else 0
        quantity = entry.get("quantity")
        quantity = float(quantity) if isinstance(quantity, (int, float)) else 1.0
        radius = max(26, min(60, 26 + math.sqrt(max(quantity, 0)) * 10))
        life = max(0, min(100, int(days_left * 10)))
        nodes.append(
            {
                "id": entry.get("batch_id") or f"batch_{len(nodes)}",
                "name": entry.get("item_name_snapshot") or "未知食材",
                "days_left": days_left,
                "quantity": quantity,
                "unit": entry.get("unit") or "unit",
                "expire_date": entry.get("expire_date") or "未知",
                "r": radius,
                "life": life,
            }
        )

    nodes_json = json.dumps(nodes, ensure_ascii=False)
    html = f"""
    <div id="bubble-wrap">
      <div class="tip" id="bubble-tip"></div>
      <div class="drawer" id="bubble-drawer">
        <div class="drawer-title">批次详情</div>
        <div class="drawer-body" id="drawer-body"></div>
        <div class="drawer-actions">
          <button id="copy-name">📋 复制食材名</button>
          <button id="flag-batch">⭐ 设为优先消耗</button>
          <button id="close-drawer">✅ 关闭</button>
        </div>
      </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/d3@7"></script>
    <script>
      const nodes = {nodes_json};
      const wrap = document.getElementById("bubble-wrap");
      const tip = document.getElementById("bubble-tip");
      const drawer = document.getElementById("bubble-drawer");
      const drawerBody = document.getElementById("drawer-body");
      const copyBtn = document.getElementById("copy-name");
      const flagBtn = document.getElementById("flag-batch");
      const closeBtn = document.getElementById("close-drawer");
      let selectedId = null;

      const width = wrap.clientWidth;
      const height = wrap.clientHeight;
      const svg = d3.select(wrap)
        .append("svg")
        .attr("width", width)
        .attr("height", height);

      const nodeGroup = svg.append("g");

      const colorForLife = (life) => `hsl(${120 * (life / 100)}, 65%, 45%)`;

      const simulation = d3.forceSimulation(nodes)
        .force("center", d3.forceCenter(width / 2, height / 2))
        .force("x", d3.forceX(width / 2).strength(0.02))
        .force("y", d3.forceY(height / 2).strength(0.02))
        .force("collide", d3.forceCollide().radius(d => d.r + 6).iterations(2));

      const drag = d3.drag()
        .on("start", (event, d) => {{
          simulation.alphaTarget(0.25).restart();
          d.fx = d.x;
          d.fy = d.y;
        }})
        .on("drag", (event, d) => {{
          d.fx = event.x;
          d.fy = event.y;
        }})
        .on("end", (event, d) => {{
          simulation.alphaTarget(0);
          d.fx = null;
          d.fy = null;
        }});

      const bubble = nodeGroup.selectAll("g")
        .data(nodes)
        .enter()
        .append("g")
        .attr("class", "bubble")
        .call(drag)
        .on("mousemove", (event, d) => {{
          tip.style.opacity = 1;
          tip.style.transform = "translateY(0)";
          tip.style.left = (event.offsetX + 12) + "px";
          tip.style.top = (event.offsetY + 12) + "px";
          tip.innerHTML = `<strong>${{d.name}}</strong><br/>生命值 ${{d.life}}% · 剩余 ${{d.days_left}} 天`;
        }})
        .on("mouseleave", () => {{
          tip.style.opacity = 0;
          tip.style.transform = "translateY(6px)";
        }})
        .on("click", (event, d) => {{
          selectedId = d.id;
          nodeGroup.selectAll("circle")
            .attr("data-selected", n => n.id === selectedId ? "true" : "false");
          drawer.classList.add("show");
          drawerBody.innerHTML = `
            <div><strong>${{d.name}}</strong></div>
            <div>生命值：${{d.life}}%</div>
            <div>剩余天数：${{d.days_left}} 天</div>
            <div>数量：${{d.quantity}} ${{d.unit}}</div>
            <div>到期日：${{d.expire_date}}</div>
          `;
          copyBtn.onclick = () => {{
            navigator.clipboard.writeText(d.name);
          }};
          flagBtn.onclick = () => {{
            alert("MVP：已标记（后续可接 API）");
          }};
        }});

      bubble.append("circle")
        .attr("r", d => d.r)
        .attr("fill", d => colorForLife(d.life))
        .attr("stroke", d => d3.color(colorForLife(d.life)).darker(0.8))
        .attr("stroke-width", 2);

      bubble.append("text")
        .attr("class", "label")
        .attr("text-anchor", "middle")
        .attr("dy", "-0.2em")
        .text(d => d.name.length > 6 ? d.name.slice(0, 6) + "…" : d.name);

      bubble.append("text")
        .attr("class", "sub-label")
        .attr("text-anchor", "middle")
        .attr("dy", "1.2em")
        .text(d => `生命值 ${{d.life}}%`);

      closeBtn.onclick = () => {{
        drawer.classList.remove("show");
      }};

      simulation.on("tick", () => {{
        bubble.attr("transform", d => {{
          d.x = Math.max(d.r + 6, Math.min(width - d.r - 6, d.x));
          d.y = Math.max(d.r + 6, Math.min(height - d.r - 6, d.y));
          return `translate(${{d.x}},${{d.y}})`;
        }});
      }});
    </script>
    <style>
      #bubble-wrap {{
        position: relative;
        width: 100%;
        height: 360px;
        background: #f8f9fa;
        border-radius: 15px;
        overflow: hidden;
        box-shadow: inset 0 0 0 1px rgba(15, 23, 42, 0.06);
      }}
      #bubble-wrap svg {{
        width: 100%;
        height: 100%;
      }}
      .bubble {{
        cursor: grab;
        transition: transform 0.15s ease;
      }}
      .bubble:hover {{
        transform: scale(1.06);
      }}
      circle[data-selected="true"] {{
        stroke-width: 4;
        filter: drop-shadow(0 0 10px rgba(15, 23, 42, 0.2));
      }}
      .label {{
        font-size: 12px;
        fill: #ffffff;
        font-weight: 600;
        pointer-events: none;
      }}
      .sub-label {{
        font-size: 11px;
        fill: rgba(255, 255, 255, 0.85);
        pointer-events: none;
      }}
      .tip {{
        position: absolute;
        padding: 8px 10px;
        border-radius: 8px;
        background: rgba(15, 23, 42, 0.92);
        color: #fff;
        font-size: 12px;
        box-shadow: 0 6px 16px rgba(15, 23, 42, 0.25);
        opacity: 0;
        transform: translateY(6px);
        transition: opacity 0.15s ease, transform 0.15s ease;
        pointer-events: none;
        z-index: 3;
      }}
      .drawer {{
        position: absolute;
        top: 14px;
        right: 14px;
        width: 260px;
        background: #fff;
        border-radius: 14px;
        padding: 14px;
        box-shadow: 0 12px 28px rgba(15, 23, 42, 0.15);
        opacity: 0;
        transform: translateY(-8px);
        transition: opacity 0.2s ease, transform 0.2s ease;
        z-index: 4;
      }}
      .drawer.show {{
        opacity: 1;
        transform: translateY(0);
      }}
      .drawer-title {{
        font-weight: 700;
        margin-bottom: 8px;
        color: #0f172a;
      }}
      .drawer-body {{
        font-size: 12px;
        color: #475569;
        line-height: 1.6;
      }}
      .drawer-actions {{
        margin-top: 12px;
        display: flex;
        flex-direction: column;
        gap: 8px;
      }}
      .drawer-actions button {{
        border: none;
        padding: 8px 10px;
        border-radius: 10px;
        background: #f1f5f9;
        cursor: pointer;
        font-size: 12px;
        color: #0f172a;
      }}
      .drawer-actions button:hover {{
        background: #e2e8f0;
      }}
    </style>
    """
    components.v1.html(html, height=380)

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

expiring_live = api.list_expiring(days=10)["batches"]
render_live_bubbles(expiring_live)

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
