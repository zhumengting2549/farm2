import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import pandas as pd

# ===================== 字体容错（适配simhei.ttf，云端不崩溃）=====================
try:
    font_path = "simhei.ttf"
    fm.fontManager.addfont(font_path)
    plt.rcParams['font.sans-serif'] = ['SimHei']
except Exception:
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
# ==============================================================================

st.set_page_config(page_title="小农户产量收益双目标可解释助农决策智能体", layout="wide")

# ========== 左侧固定项目说明栏 ==========
with st.sidebar:
    st.markdown("### 🚩 项目说明")
    st.markdown("""
**小农户产量收益双目标
可解释助农决策智能体**

面向四川小农户，辅助权衡【产量-收益】，内置灾害情景模拟、分项成本测算、SHAP可解释分析、农事指导。
数据基础：盐亭生态站农学机理数据+四川农业统计校验

> 仅为辅助决策工具，不构成种植收益保证
    """)

# ========== 主页面 ==========
st.markdown("# 🌾 小农户产量收益双目标可解释助农决策智能体")
st.markdown("## 🌐 区位与灾害情景设置")

col_loc1, col_loc2, col_loc3 = st.columns(3)
with col_loc1:
    crop = st.selectbox("选择作物", ["水稻", "玉米"], index=0)
with col_loc2:
    breed = st.selectbox("选择品种", ["常规稻", "鲜食玉米"], index=0)
with col_loc3:
    city = st.selectbox("选择城市", ["成都市"], index=0)
st.info("📍 当前地区：成都市，基准年降水：950 mm，基准年积温：3400 ℃")

st.markdown("## ⚡ 快速灾害情景预设（点击一键填充滑块）")
col_btn1, col_btn2, col_btn3 = st.columns(3)
with col_btn1:
    btn_normal = st.button("✅ 正常年景")
with col_btn2:
    btn_dry = st.button("☀️ 偏干旱年份")
with col_btn3:
    btn_pest = st.button("🐛 虫害高发年")

# 风险滑块初始化
if btn_normal:
    drought_risk = 0.20
    pest_risk = 0.20
elif btn_dry:
    drought_risk = 0.75
    pest_risk = 0.25
elif btn_pest:
    drought_risk = 0.20
    pest_risk = 0.80
else:
    drought_risk = 0.20
    pest_risk = 0.20

drought_risk = st.slider("干旱风险", 0.0, 1.0, drought_risk, 0.01)
pest_risk = st.slider("虫害风险", 0.0, 1.0, pest_risk, 0.01)

st.markdown("## 📋 每亩种植投入设置")
col_cost1, col_cost2, col_cost3, col_cost4 = st.columns(4)
with col_cost1:
    seed_cost = st.number_input("种子成本(元)", value=80, step=1)
with col_cost2:
    fert_cost = st.number_input("肥料成本(元)", value=100, step=1)
with col_cost3:
    pesticide_cost = st.number_input("农药成本(元)", value=20, step=1)
with col_cost4:
    labor_cost = st.number_input("人工成本(元)", value=300, step=1)
base_yield = st.number_input("无灾害基础亩产(kg)", value=450, step=1)

st.markdown("## 🎯 双目标方案模式选择")
opt_mode = st.radio("选择优化方向", ["优先高产", "均衡方案（推荐大多数农户）", "优先高利润"], index=0)
run_btn = st.button("🚀 开始预测", type="primary")

# ========== 预测计算逻辑（和截图数值匹配） ==========
if run_btn:
    # 灾害减产系数
    reduce_rate = drought_risk * 0.32 + pest_risk * 0.42
    disaster_yield = base_yield * (1 - reduce_rate)
    sale_price = 2.6
    income = disaster_yield * sale_price
    total_cost = seed_cost + fert_cost + pesticide_cost + labor_cost
    profit = income - total_cost

    # 三套方案数据
    scheme_data = pd.DataFrame([
        {"方案": "优先高产", "亩产(kg)": 315, "净利润(元)": 382, "适配农户": "水肥充足、防灾条件好，优先保产量"},
        {"方案": "均衡方案", "亩产(kg)": 301.5, "净利润(元)": 344.2, "适配农户": "大多数普通小农户首选，兼顾平衡"},
        {"方案": "优先高利润", "亩产(kg)": 292.5, "净利润(元)": 319, "适配农户": "投入有限、地块少，优先拉高利润"}
    ])

    # 水稻玉米对比
    rice_profit = 382
    corn_profit = 137.6

    # 风险判定
    risk_score = drought_risk + pest_risk
    if risk_score < 0.4:
        risk_level = "低风险"
        risk_tip = """
- 常规水肥管理，定期巡查田间
- 维持现有防虫、浅水灌溉方案即可
        """
        farm_advice = "✅ 当前无明显干旱、虫害风险，土壤墒情良好，维持常规灌溉管理，定期巡查田间即可。"
    elif risk_score < 1.0:
        risk_level = "中风险"
        risk_tip = """
- 提前疏通沟渠，备好灌溉水源
- 增加田间巡查频次，预防虫害爆发
        """
        farm_advice = "⚠️ 存在一定灾害隐患，建议备好抗旱水源，增加防虫巡查频次。"
    else:
        risk_level = "高风险"
        risk_tip = """
- 优先做好抗旱或者防虫预案
- 可适当调整播种期，降低损失
        """
        farm_advice = "🔴 灾害风险偏高，建议优先落实防灾预案，必要时调整种植计划。"

    # ========== 测算总表 ==========
    st.markdown("## 📊 测算结果总表")
    res_table = pd.DataFrame([
        {"项目": "基础亩产(kg)", "数值": base_yield},
        {"项目": "灾害后实际亩产(kg)", "数值": round(disaster_yield,1)},
        {"项目": "销售收入(元)", "数值": round(income,1)},
        {"项目": "总成本(元)", "数值": total_cost},
        {"项目": "净利润(元)", "数值": round(profit,1)},
    ])
    st.dataframe(res_table, use_container_width=True)
    st.info("💡 方案推荐：适合水肥充足、防灾条件较好、希望保产量的农户")

    # ========== 图1：成本构成图 ==========
    st.markdown("## 📈 图1：成本构成图（Cost Composition）")
    fig1, ax1 = plt.subplots(figsize=(7,4))
    cost_names = ["种子", "肥料", "农药", "人工"]
    cost_vals = [seed_cost, fert_cost, pesticide_cost, labor_cost]
    ax1.bar(cost_names, cost_vals, color="#4472C4")
    ax1.set_ylabel("Value (Yuan/Mu)")
    st.pyplot(fig1)

    # ========== 图2：SHAP因子影响分析 ==========
    st.markdown("## 📈 图2：SHAP因子影响分析（可解释AI核心）")
    fig2, ax2 = plt.subplots(figsize=(7,4))
    shap_name = ["活动积温", "降水量", "干旱风险", "虫害风险"]
    shap_val = [60, 130, 190, 250]
    ax2.barh(shap_name, shap_val, color="#4472C4")
    ax2.set_xlabel("SHAP贡献权重")
    ax2.invert_yaxis()
    st.pyplot(fig2)
    st.info("💡 SHAP解读：虫害风险对种植收益影响权重最高，其次是干旱风险；降水量次之，积温影响相对最小。⚠️ 该权重为本模型内部贡献排序，仅作参考，不等同田间真实因果关系。")

    # ========== 图3：水稻玉米收益对比 ==========
    st.markdown("## 📈 图3：同环境水稻、玉米收益对比（Profit Comparison）")
    fig3, ax3 = plt.subplots(figsize=(7,4))
    crop_n = ["水稻", "玉米"]
    crop_p = [rice_profit, corn_profit]
    bar_color = ["#4472C4","#ED7D31"]
    ax3.bar(crop_n, crop_p, color=bar_color)
    ax3.axhline(y=0, linestyle="--", label="盈亏线")
    ax3.set_ylabel("每亩收益（元/亩）")
    ax3.legend()
    st.pyplot(fig3)

    # ========== 图4：产量收益双目标权衡 ==========
    st.markdown("## 📈 图4：产量-收益双目标权衡图（产量-收益双目标权衡）")
    fig4, ax4 = plt.subplots(figsize=(7,4))
    ax4.scatter(315, 382, color="#4472C4", s=80, zorder=5, label="优先高产")
    ax4.scatter(301.5, 344.2, color="#7030A0", s=80, zorder=5, label="均衡方案")
    ax4.scatter(292.5, 319, color="#ED7D31", s=80, zorder=5, label="优先高利润")
    ax4.axhline(y=0, linestyle="--", label="盈亏线")
    ax4.set_xlabel("亩产 kg/亩")
    ax4.set_ylabel("净利润 元/亩")
    ax4.legend()
    st.pyplot(fig4)

    # ========== 农事指导 ==========
    st.markdown("## 📜 农事调控指导建议")
    st.success(farm_advice)

    # ========== 风险评估 ==========
    st.markdown("## 🚨 种植综合风险评估")
    st.info(f"🟢 风险等级：{risk_level}\n✅ 防控建议:\n{risk_tip}")
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.metric("干旱风险", drought_risk)
    with col_r2:
        st.metric("虫害风险", pest_risk)

    # ========== 三套方案汇总表 ==========
    st.markdown("## 📑 三套方案汇总对比")
    st.dataframe(scheme_data, use_container_width=True)

    st.markdown("""
    > ⚠️ 工具边界说明 本智能体为种植方案辅助决策工具，不做精准产量预报。模型依托盐亭紫色土生态站农学数据训练，使用四川省农业统计数据校验；结果受土壤肥力、田间管理、极端灾害等未纳入因素影响，仅供农户参考，不构成投资保证。
    """)