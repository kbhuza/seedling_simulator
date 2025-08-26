import streamlit as st
import pandas as pd
import plotly.express as px

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Zimbabwe Seedling Nursery Simulator",
    page_icon="🌱",
    layout="wide",
)

st.title("🌱 Commercial Seedling Nursery Simulation")
st.markdown("An interactive model by Environment Africa for a project in rural Zimbabwe.")

# --- SIDEBAR FOR USER INPUTS ---
st.sidebar.header("Simulation Parameters")

# --- Constants for Production Cycles ---
VEG_CYCLES_PER_YEAR = 4
TREE_CYCLES_PER_YEAR = 1

# 1. Shared Initial & Monthly Costs
st.sidebar.subheader("1. Shared Initial & Monthly Costs")
greenhouse_cost = st.sidebar.slider(
    "Greenhouse / Shed Cost ($)",
    min_value=0,
    max_value=5000,
    value=300,
    step=50,
    help="One-off cost for a shared greenhouse / shed.",
)
irrigation_cost = st.sidebar.slider(
    "Irrigation System Cost ($)",
    min_value=0,
    max_value=3000,
    value=200,
    step=25,
    help="One-off cost for a shared irrigation system.",
)
agric_inputs_cost = st.sidebar.slider(
    "Agric Inputs (tools, etc.) Cost ($)",
    min_value=0,
    max_value=3000,
    value=200,
    step=25,
    help="One-off cost for shared tools and other agricultural inputs.",
)
labor_cost_per_month = st.sidebar.slider(
    "Monthly Labour Cost ($)",
    min_value=0,
    max_value=2000,
    value=150,
    step=10,
    help="Total monthly labour cost for the entire nursery.",
)

# 2. Production Yield & Success Rate
st.sidebar.subheader("2. Production Yield & Success")
initial_veg_seedlings_per_cycle = st.sidebar.number_input(
    "Initial Vegetable Seedlings (per cycle)",
    min_value=1000,
    max_value=50000,
    value=10000,
    step=100,
    help=f"Number of vegetable seedlings planted each cycle ({VEG_CYCLES_PER_YEAR} cycles/year).",
)
successful_tree_seedlings_target = st.sidebar.number_input(
    "Target Successful Tree Seedlings (per year)",
    min_value=500,
    max_value=20000,
    value=2950,
    step=50,
    help=f"The target number of sellable tree seedlings to produce each year ({TREE_CYCLES_PER_YEAR} cycle/year).",
)
success_rate = st.sidebar.slider(
    "Seedling Success Rate (%)",
    min_value=10,
    max_value=100,
    value=85,
    step=1,
    help="The percentage of seedlings that are expected to grow successfully and be sellable.",
) / 100.0

# 3. Costs & Pricing per Seedling Type
st.sidebar.subheader("3. Costs & Pricing")
# Vegetable Costs & Price
st.sidebar.markdown("---")
st.sidebar.markdown("**Vegetable Seedlings**")
avg_price_veg = st.sidebar.slider(
    "Avg. Price per Vegetable Seedling ($)",
    min_value=0.01,
    max_value=1.00,
    value=0.15,
    step=0.01,
    format="%.2f",
)
seed_cost_veg_cycle = st.sidebar.slider(
    "Seed Cost (per veg cycle)",
    min_value=0,
    max_value=2000,
    value=100,
    step=10,
    help="Cost of vegetable seeds for one cycle.",
)
medium_cost_veg_cycle = st.sidebar.slider(
    "Growing Medium Cost (per veg cycle)",
    min_value=0,
    max_value=2000,
    value=100,
    step=10,
    help="Cost of growing medium for one vegetable cycle.",
)
# Tree Costs & Price
st.sidebar.markdown("---")
st.sidebar.markdown("**Tree Seedlings**")
avg_price_tree = st.sidebar.slider(
    "Avg. Price per Tree Seedling ($)",
    min_value=0.50,
    max_value=10.00,
    value=4.50,
    step=0.05,
    format="%.2f",
)
seed_cost_tree_cycle = st.sidebar.slider(
    "Seed Cost (per tree cycle)",
    min_value=0,
    max_value=2000,
    value=150, # Assuming slightly higher cost for tree seeds
    step=10,
    help="Cost of tree seeds for the single annual cycle.",
)
medium_cost_tree_cycle = st.sidebar.slider(
    "Growing Medium Cost (per tree cycle)",
    min_value=0,
    max_value=2000,
    value=150, # Assuming slightly higher cost for tree medium
    step=10,
    help="Cost of growing medium for the single annual tree cycle.",
)
st.sidebar.markdown("---")


# --- CORE SIMULATION LOGIC (Calculations) ---

# 1. Initial Setup Costs (Shared)
production_cost = greenhouse_cost + irrigation_cost + agric_inputs_cost

# 2. Vegetable Seedling Calculations
successful_veg_per_cycle = initial_veg_seedlings_per_cycle * success_rate
annual_successful_veg = successful_veg_per_cycle * VEG_CYCLES_PER_YEAR
annual_revenue_veg = annual_successful_veg * avg_price_veg
opex_per_veg_cycle = seed_cost_veg_cycle + medium_cost_veg_cycle
annual_opex_veg = opex_per_veg_cycle * VEG_CYCLES_PER_YEAR

# 3. Tree Seedling Calculations
# Work backward to find the initial number of tree seedlings needed
initial_tree_seedlings_per_year = successful_tree_seedlings_target / success_rate if success_rate > 0 else 0
annual_revenue_tree = successful_tree_seedlings_target * avg_price_tree
opex_per_tree_cycle = seed_cost_tree_cycle + medium_cost_tree_cycle
annual_opex_tree = opex_per_tree_cycle * TREE_CYCLES_PER_YEAR

# 4. Combined Annual Financials
total_annual_revenue = annual_revenue_veg + annual_revenue_tree
# Total OPEX = veg costs + tree costs + full year of labor
total_annual_opex = annual_opex_veg + annual_opex_tree + (labor_cost_per_month * 12)
total_annual_profit = total_annual_revenue - total_annual_opex
roi_years = (production_cost / total_annual_profit) if total_annual_profit > 0 else float("inf")

# --- MAIN DASHBOARD DISPLAY ---
st.header("Combined Annual Financial Dashboard")
col1, col2, col3, col4 = st.columns(4)

col1.metric("Initial Setup Cost", f"${production_cost:,.0f}", help="One-time setup costs (greenhouse, irrigation, tools). This is shared across both operations.")
col2.metric("Total Annual OPEX", f"${total_annual_opex:,.0f}", help="Total recurring costs per year, including all seedling inputs and labor.")
col3.metric("Projected Annual Revenue", f"${total_annual_revenue:,.0f}", help="Combined projected revenue from both vegetable and tree seedlings in one year.")
col4.metric("Projected Annual Profit", f"${total_annual_profit:,.0f}", help="Combined projected profit per year after all costs.")

# Row 2: Charts and Visuals
st.header("Visual Projections")
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Profitability Over Time (5 years)")
    profit_data = {
        'Year': list(range(1, 6)),
        'Cumulative Profit ($)': [total_annual_profit * i for i in range(1, 6)]
    }
    profit_df = pd.DataFrame(profit_data)
    fig_profit = px.line(
        profit_df,
        x='Year',
        y='Cumulative Profit ($)',
        title="5-Year Cumulative Profit Projection",
        markers=True
    )
    fig_profit.add_hline(y=production_cost, line_dash="dot", annotation_text="Initial Setup Cost", annotation_position="bottom right")
    st.plotly_chart(fig_profit, use_container_width=True)

with col2:
    st.subheader("Annual Revenue Mix")
    revenue_mix_data = {
        'Seedling Type': ['Vegetable', 'Tree'],
        'Revenue ($)': [annual_revenue_veg, annual_revenue_tree]
    }
    revenue_df = pd.DataFrame(revenue_mix_data)
    fig_pie = px.pie(
        revenue_df,
        names='Seedling Type',
        values='Revenue ($)',
        hole=0.4,
        color_discrete_map={'Vegetable': '#2ca02c', 'Tree': '#8c564b'}
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# --- DETAILED PRODUCTION TABLES ---
st.header("Detailed Production Numbers")

# Table 1: Vegetable Seedlings
st.subheader(f"Vegetable Seedlings ({VEG_CYCLES_PER_YEAR} Cycles per Year)")
veg_df = pd.DataFrame({
    "Metric": [
        "Initial seedlings planted per cycle",
        f"Successful seedlings per cycle (at {success_rate:.0%})",
        "Total successful seedlings per year",
        "OPEX per cycle (seeds & medium)",
        "Annual OPEX (seeds & medium)",
        "Projected Annual Revenue"
    ],
    "Value": [
        f"{initial_veg_seedlings_per_cycle:,.0f}",
        f"{successful_veg_per_cycle:,.0f}",
        f"{annual_successful_veg:,.0f}",
        f"${opex_per_veg_cycle:,.2f}",
        f"${annual_opex_veg:,.2f}",
        f"${annual_revenue_veg:,.2f}"
    ]
})
st.table(veg_df)

# Table 2: Tree Seedlings
st.subheader(f"Tree Seedlings ({TREE_CYCLES_PER_YEAR} Cycle per Year)")
tree_df = pd.DataFrame({
    "Metric": [
        "Target successful seedlings per year",
        f"Initial seedlings to plant (at {success_rate:.0%})",
        "OPEX per year (seeds & medium)",
        "Projected Annual Revenue"
    ],
    "Value": [
        f"{successful_tree_seedlings_target:,.0f}",
        f"{initial_tree_seedlings_per_year:,.0f}",
        f"${annual_opex_tree:,.2f}",
        f"${annual_revenue_tree:,.2f}"
    ]
})
st.table(tree_df)

# Add a summary of shared costs and final profit
st.subheader("Annual Financial Summary")
summary_df = pd.DataFrame({
    "Metric": [
        "Total Annual Revenue (Veg + Tree)",
        "Total Annual OPEX (Veg + Tree + Labor)",
        "--> Annual Labor Cost",
        "Projected Annual Profit",
        "Initial Setup Cost (One-time)",
        "Return on Investment (ROI)"
    ],
    "Value": [
        f"${total_annual_revenue:,.2f}",
        f"${total_annual_opex:,.2f}",
        f"--> ${(labor_cost_per_month*12):,.2f}",
        f"${total_annual_profit:,.2f}",
        f"${production_cost:,.2f}",
        f"{roi_years:.1f} years" if roi_years != float("inf") else "No positive profit"
    ]
})
st.table(summary_df)


# --- RISKS SECTION ---
st.header("Risks & Mitigation")
st.subheader("Interactive Risk Simulation")

col1, col2 = st.columns(2)
with col1:
    risk_factor = st.select_slider(
        "Simulate a risk event:",
        options=['No Risk', 'Drought (-20% sales)', 'Pest Outbreak (-15% yield)'],
        value='No Risk'
    )
    # Apply risk to calculations
    adjusted_revenue = total_annual_revenue
    risk_info = "No major risk applied."
    if 'Drought' in risk_factor:
        adjusted_revenue *= 0.80
        risk_info = "Drought simulated: -20% sales (revenue reduction)."
    if 'Pest' in risk_factor:
        # Pest reduces yield for both seedling types
        adj_successful_veg = successful_veg_per_cycle * 0.85
        adj_successful_tree = successful_tree_seedlings_target * 0.85
        adj_rev_veg = (adj_successful_veg * VEG_CYCLES_PER_YEAR) * avg_price_veg
        adj_rev_tree = adj_successful_tree * avg_price_tree
        adjusted_revenue = adj_rev_veg + adj_rev_tree
        risk_info = "Pest outbreak simulated: -15% yield (fewer sellable seedlings)."

    adjusted_annual_profit = adjusted_revenue - total_annual_opex
    st.warning(f"**Scenario:** {risk_info}")

with col2:
    # Protect against division by zero for the % change display
    if total_annual_profit != 0:
        pct_change = ((adjusted_annual_profit - total_annual_profit) / abs(total_annual_profit)) * 100
    else:
        pct_change = 0.0
    st.metric("Adjusted Annual Profit", f"${adjusted_annual_profit:,.0f}", f"{pct_change:.1f}% vs. Base")
    st.info("**Mitigation Strategy:** Promote drought-tolerant varieties, water-conserving irrigation, and Integrated Pest Management (IPM).")


# --- NEW SUSTAINABILITY SECTION ---
st.header("Project Sustainability Strategy")
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("1. Institutional Strengthening")
    st.markdown("""
    - **Community Ownership:** Transfer management to local farmer groups, schools, or cooperatives.
    - **Leadership Training:** Equip local leaders with skills in nursery management, record keeping, and decision-making.
    - **Local Policies:** Work with local authorities to integrate the project into agricultural development plans.
    """)

    st.subheader("4. Partnerships and Networking")
    st.markdown("""
    - **Linkages with Agro-dealers:** Partner with seed suppliers and agro-shops to secure reliable seed supply.
    - **Schools and Community Groups:** Engage schools and youth clubs to expand participation.
    - **Market Linkages:** Connect seedling producers with local markets and commercial farmers.
    """)

with col2:
    st.subheader("2. Financial Sustainability")
    st.markdown("""
    - **Cost Recovery Model:** Farmers pay a small fee for seedlings, ensuring revenue covers production costs.
    - **Microfinance/Cooperatives:** Facilitate access to small loans for farmer groups or groups managing nurseries.
    - **Savings Groups:** Encourage farmer groups to form savings and credit schemes for reinvestment.
    """)

    st.subheader("5. Environmental and Social Sustainability")
    st.markdown("""
    - **Eco-friendly Practices:** Promote organic fertilizers and water-efficient irrigation.
    - **Diversity of Crops:** Encourage a mix of vegetable varieties to reduce the risk of pests and diseases.
    - **Youth Engagement:** Involve young people through school and youth clubs to ensure continuity.
    """)

with col3:
    st.subheader("3. Capacity Building")
    st.markdown("""
    - **Skills Transfer:** Train farmers and youth in seedling production, pest and disease management, and business skills.
    - **Demonstration Plots:** Establish learning sites for continuous training and innovation.
    """)

    st.subheader("6. Monitoring and Evaluation")
    st.markdown("""
    - **Community Monitoring Committees:** Form groups to track seedling production, sales, and challenges.
    - **Annual Reviews:** Hold farmer-led evaluations to assess project operations.
    - **Knowledge Sharing:** Use field days, WhatsApp groups, and workshops to share best practices.
    """)


# --- PROJECT VISION & FOOTER ---
st.header("Project Vision")
col1, col2 = st.columns(2)
col1.image("https://i.imgur.com/gqyRU81.jpeg", caption="High-quality vegetable seedlings ready for local farmers.", use_column_width=True)
col2.image("https://i.imgur.com/2a99hpD.jpeg", caption="Tree seedlings to support afforestation and community orchards.", use_column_width=True)

st.markdown(
    """
---
**Notes & How to Use the Model**
- **Shared Costs:** Initial setup costs (greenhouse, irrigation, tools) and monthly labor are treated as shared overhead for the entire nursery.
- **Production Cycles:** The model assumes fixed cycles: 4 per year for vegetables and 1 per year for trees.
- **Inputs:** All parameters can be adjusted in the sidebar on the left to simulate different scenarios.
"""
)