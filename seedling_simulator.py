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
st.markdown("An interactive model by Environment Africa for project in rural Zimbabwe.")

# --- SIDEBAR FOR USER INPUTS ---
st.sidebar.header("Simulation Parameters")

# 1. Production and Costing Inputs
st.sidebar.subheader("1. Production & Costs (defaults updated)")

# NOTE: these defaults were set per your request:
# - Greenhouse/shed default cost = 300
# - Irrigation default cost = 200
# - Tools & planting materials renamed to "Agric inputs" default = 200
# - Monthly labour default = 150
# - Seed cost default = 100
# - Growing medium default = 100
greenhouse_cost = st.sidebar.slider(
    "Greenhouse / Shed Cost ($)",
    min_value=0,
    max_value=5000,
    value=300,
    step=50,
    help="One-off cost for greenhouse / shed (default 300).",
)

irrigation_cost = st.sidebar.slider(
    "Irrigation System Cost ($)",
    min_value=0,
    max_value=3000,
    value=200,
    step=25,
    help="One-off irrigation system cost (default 200).",
)

agric_inputs_cost = st.sidebar.slider(
    "Agric Inputs (tools & planting materials) Cost ($)",
    min_value=0,
    max_value=3000,
    value=200,
    step=25,
    help="Cost for tools and planting materials (renamed to Agric Inputs) (default 200).",
)

labor_cost_per_month = st.sidebar.slider(
    "Monthly Labour Cost ($)",
    min_value=0,
    max_value=2000,
    value=150,
    step=10,
    help="Total monthly labour cost (default 150).",
)

seed_cost_per_cycle = st.sidebar.slider(
    "Seed Cost per Cycle ($)",
    min_value=0,
    max_value=2000,
    value=100,
    step=10,
    help="Seeds cost per production cycle (default 100).",
)

medium_cost_per_cycle = st.sidebar.slider(
    "Growing Medium Cost per Cycle ($)",
    min_value=0,
    max_value=2000,
    value=100,
    step=10,
    help="Growing medium cost per production cycle (default 100).",
)

# 2. Production Yield Inputs
st.sidebar.subheader("2. Production Yield")

# User requested trays can start from default 50 (we interpret this as number_of_trays default)
num_trays = st.sidebar.number_input(
    "Number of Seedling Trays",
    min_value=50,   # user requested starting default 50
    max_value=20000,
    value=50,
    step=1,
    help="Total number of trays used per cycle (default 50).",
)

# Optional: allow user to set cells per tray (kept as assumption; can be adjusted)
cells_per_tray = st.sidebar.number_input(
    "Cells per Tray (seedlings per tray)",
    min_value=4,
    max_value=500,
    value=200,
    step=1,
    help="Number of seedling cells per tray (default 200).",
)

success_rate = st.sidebar.slider(
    "Seedling Success Rate (%)",
    min_value=10,
    max_value=100,
    value=85,
    step=1,
) / 100.0

# 3. Market and Sales Inputs
st.sidebar.subheader("3. Market & Sales")
avg_price_veg = st.sidebar.slider(
    "Avg. Vegetable Seedling Price ($)",
    min_value=0.01,
    max_value=5.00,
    value=0.05,
    step=0.01,
    format="%.2f",
)
avg_price_tree = st.sidebar.slider(
    "Avg. Tree Seedling Price ($)",
    min_value=0.01,
    max_value=10.00,
    value=0.15,
    step=0.01,
    format="%.2f",
)
veg_percentage = st.sidebar.slider(
    "Percentage of Veggie Seedlings (%)",
    min_value=0,
    max_value=100,
    value=70,
    step=1,
) / 100.0

# 4. Cycle assumptions
st.sidebar.subheader("4. Cycle assumptions")
months_per_cycle = st.sidebar.selectbox(
    "Months per production cycle",
    options=[1, 2, 3, 4, 6],
    index=2,
    help="How many months a production cycle runs (default 3).",
)

cycles_per_year = int(12 / months_per_cycle)

# --- CORE SIMULATION LOGIC (Calculations) ---
# 1. Production cost (replaces 'investment' or 'capex' from previous version)
# Interpretation: production_cost combines greenhouse, irrigation, and agric inputs (tools + planting materials).
# If you prefer to treat some as recurring, move them into opex below.
production_cost = greenhouse_cost + irrigation_cost + agric_inputs_cost

# 2. Operating expenses per cycle (OPEX)
# We treat labour as monthly and multiply by months_per_cycle to get labour per cycle.
# Seed and growing medium are per-cycle costs as before.
opex_per_cycle = (labor_cost_per_month * months_per_cycle) + seed_cost_per_cycle + medium_cost_per_cycle

# 3. Yield Calculation
total_potential_seedlings = num_trays * cells_per_tray  # trays * cells per tray
projected_yield = total_potential_seedlings * success_rate

# 4. Revenue Calculation
num_veg_seedlings = projected_yield * veg_percentage
num_tree_seedlings = projected_yield * (1 - veg_percentage)
revenue_per_cycle = (num_veg_seedlings * avg_price_veg) + (num_tree_seedlings * avg_price_tree)

# 5. Profitability Calculation
profit_per_cycle = revenue_per_cycle - opex_per_cycle
profit_per_year = profit_per_cycle * cycles_per_year
roi_years = (production_cost / profit_per_year) if profit_per_year > 0 else float("inf")

# --- MAIN DASHBOARD DISPLAY ---
st.header("Financial Dashboard")
col1, col2, col3, col4 = st.columns(4)

# showing production cost instead of "Initial CAPEX"
col1.metric("Production Cost (setup)", f"${production_cost:,.0f}", help="One-time production/setup costs (greenhouse, irrigation, agric inputs).")
col2.metric("OPEX per Cycle", f"${opex_per_cycle:,.0f}", help=f"Recurring costs each cycle ({months_per_cycle} months per cycle).")
col3.metric("Projected Revenue / Cycle", f"${revenue_per_cycle:,.0f}")
col4.metric("Projected Profit / Year", f"${profit_per_year:,.0f}", delta_color="inverse")

st.markdown(
    f"""
**Assumptions summary:** {num_trays:,} trays × {cells_per_tray:,} cells/tray = {total_potential_seedlings:,} potential seedlings; \
success rate = {success_rate*100:.0f}%; cycles/year = {cycles_per_year}.
"""
)

# Row 2: Charts and Visuals
st.header("Visual Projections")
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Profitability Over Time (5 years)")
    profit_data = {
        'Year': [1, 2, 3, 4, 5],
        # cumulative profit each year (simple model: same annual profit each year)
        'Cumulative Profit ($)': [profit_per_year * i for i in range(1, 6)]
    }
    profit_df = pd.DataFrame(profit_data)
    fig_profit = px.line(
        profit_df,
        x='Year',
        y='Cumulative Profit ($)',
        title="5-Year Cumulative Profit Projection",
        markers=True
    )
    # Add a line for the initial production cost
    fig_profit.add_hline(y=production_cost, line_dash="dot", annotation_text="Production Cost (setup)", annotation_position="bottom right")
    st.plotly_chart(fig_profit, use_container_width=True)

with col2:
    st.subheader("Revenue Mix per Cycle")
    revenue_mix_data = {
        'Seedling Type': ['Vegetable', 'Tree'],
        'Revenue ($)': [num_veg_seedlings * avg_price_veg, num_tree_seedlings * avg_price_tree]
    }
    revenue_df = pd.DataFrame(revenue_mix_data)
    fig_pie = px.pie(
        revenue_df,
        names='Seedling Type',
        values='Revenue ($)',
        hole=0.4,
        # color_discrete_map retained from previous code for clarity
        color_discrete_map={'Vegetable':'#2ca02c', 'Tree':'#8c564b'}
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# Row 3: Risks and Sustainability
st.header("Risks & Sustainability")
st.subheader("Interactive Risk Simulation")

col1, col2 = st.columns(2)
with col1:
    risk_factor = st.select_slider(
        "Simulate a risk event:",
        options=['No Risk', 'Drought (-20% sales)', 'Pest Outbreak (-15% yield)'],
        value='No Risk'
    )
    # Apply risk to calculations
    adjusted_revenue = revenue_per_cycle
    adjusted_yield = projected_yield
    risk_info = "No major risk applied."
    if 'Drought' in risk_factor:
        # drought reduces sales (i.e., fewer customers buy seedlings) — apply to revenue directly
        adjusted_revenue *= 0.80
        risk_info = "Drought simulated: -20% sales (revenue reduction)."
    if 'Pest' in risk_factor:
        # pest reduces yield (fewer seedlings to sell)
        adjusted_yield = projected_yield * 0.85
        adjusted_revenue = (adjusted_yield * veg_percentage * avg_price_veg) + \
                           (adjusted_yield * (1 - veg_percentage) * avg_price_tree)
        risk_info = "Pest outbreak simulated: -15% yield (fewer sellable seedlings)."

    adjusted_profit_annual = (adjusted_revenue - opex_per_cycle) * cycles_per_year
    st.warning(f"**Scenario:** {risk_info}")

with col2:
    # Protect against division by zero for the % change display
    if profit_per_year != 0:
        pct_change = ((adjusted_profit_annual - profit_per_year) / abs(profit_per_year)) * 100
    else:
        pct_change = 0.0
    st.metric("Adjusted Annual Profit", f"${adjusted_profit_annual:,.0f}", f"{pct_change:.1f}% vs. Base")
    st.info("**Mitigation Strategy:** Promote drought-tolerant varieties, water-conserving irrigation, and Integrated Pest Management (IPM).")

# Quick table of key numbers
st.header("Key Production Numbers")
key_df = pd.DataFrame({
    "Metric": [
        "Total potential seedlings (trays × cells)",
        "Projected sellable seedlings (after success rate)",
        "Vegetable seedlings",
        "Tree seedlings",
        "Revenue per cycle",
        "OPEX per cycle",
        "Profit per cycle",
        "Production cost (setup)",
        "ROI (years, approx.)"
    ],
    "Value": [
        f"{total_potential_seedlings:,}",
        f"{projected_yield:,.0f}",
        f"{num_veg_seedlings:,.0f}",
        f"{num_tree_seedlings:,.0f}",
        f"${revenue_per_cycle:,.2f}",
        f"${opex_per_cycle:,.2f}",
        f"${profit_per_cycle:,.2f}",
        f"${production_cost:,.2f}",
        f"{roi_years:.1f}" if roi_years != float("inf") else "∞ (no positive annual profit)"
    ]
})
# Display as a neat table
st.table(key_df)

# Add some visual appeal (retain example images; replace URLs if you have local assets)
st.header("Project Vision")
st.image("http://googleusercontent.com/image_collection/image_retrieval/12460295809072866260_0", caption="A vision for our commercial nursery in rural Zimbabwe.", use_column_width=True)

col1, col2 = st.columns(2)
col1.image("http://googleusercontent.com/image_collection/image_retrieval/8150812869663407436_0", caption="High-quality vegetable seedlings ready for local farmers.", use_column_width=True)
col2.image("http://googleusercontent.com/image_collection/image_retrieval/5002659753976204598_0", caption="Tree seedlings to support afforestation and community orchards.", use_column_width=True)

# Footer / Notes
st.markdown(
    """
**Notes & how to adjust the model**
- `production_cost` currently aggregates greenhouse, irrigation, and agric inputs as a setup cost.  
  If you prefer to treat certain items (e.g., tools) as CAPEX and planting materials as recurring OPEX, move them from `production_cost` into `opex_per_cycle`.
- `months_per_cycle` determines cycles per year (12 / months_per_cycle). Change it to model faster/slower production systems.
- `cells_per_tray` remains adjustable; default is 200 cells/tray but you can reduce it if your trays are smaller.
"""
)
