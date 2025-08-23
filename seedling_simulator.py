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
st.markdown("An interactive model by Takunda for project in rural Zimbabwe.")

# --- SIDEBAR FOR USER INPUTS ---
st.sidebar.header("Simulation Parameters")

# 1. Production and Costing Inputs
st.sidebar.subheader("1. Investment & Costs")
greenhouse_cost = st.sidebar.slider("Greenhouse/Tunnel Cost ($)", 1000, 10000, 3000)
irrigation_cost = st.sidebar.slider("Irrigation System Cost ($)", 500, 5000, 2500)
tools_cost = st.sidebar.slider("Tools & Equipment Cost ($)", 500, 5000, 2000)
labor_cost_per_month = st.sidebar.slider("Total Monthly Labor Cost ($)", 200, 2000, 750) # Simplified for the slider
seed_cost_per_cycle = st.sidebar.slider("Seed Cost per Cycle ($)", 200, 3000, 1000)
medium_cost_per_cycle = st.sidebar.slider("Growing Medium Cost per Cycle ($)", 200, 2000, 800)

# 2. Production Yield Inputs
st.sidebar.subheader("2. Production Yield")
num_trays = st.sidebar.number_input("Number of Seedling Trays", 5000, 20000, 10000)
success_rate = st.sidebar.slider("Seedling Success Rate (%)", 50, 100, 85) / 100.0

# 3. Market and Sales Inputs
st.sidebar.subheader("3. Market & Sales")
avg_price_veg = st.sidebar.slider("Avg. Vegetable Seedling Price ($)", 0.01, 0.20, 0.05, 0.01)
avg_price_tree = st.sidebar.slider("Avg. Tree Seedling Price ($)", 0.05, 0.50, 0.15, 0.01)
veg_percentage = st.sidebar.slider("Percentage of Veggie Seedlings (%)", 0, 100, 70) / 100.0

# --- CORE SIMULATION LOGIC (Calculations) ---

# 1. Costing Calculation
capex = greenhouse_cost + irrigation_cost + tools_cost
opex_per_cycle = (labor_cost_per_month * 3) + seed_cost_per_cycle + medium_cost_per_cycle

# 2. Yield Calculation
total_potential_seedlings = num_trays * 200 # Assuming 200 cells per tray
projected_yield = total_potential_seedlings * success_rate

# 3. Revenue Calculation
num_veg_seedlings = projected_yield * veg_percentage
num_tree_seedlings = projected_yield * (1 - veg_percentage)
revenue_per_cycle = (num_veg_seedlings * avg_price_veg) + (num_tree_seedlings * avg_price_tree)

# 4. Profitability Calculation
profit_per_cycle = revenue_per_cycle - opex_per_cycle
profit_per_year = profit_per_cycle * 4 # Assuming 4 cycles per year
roi_years = capex / profit_per_year if profit_per_year > 0 else float('inf')

# --- MAIN DASHBOARD DISPLAY ---

# Row 1: Key Metrics
st.header("Financial Dashboard")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Initial CAPEX", f"${capex:,.0f}", help="One-time setup costs")
col2.metric("OPEX per Cycle", f"${opex_per_cycle:,.0f}", help="Recurring costs every 3 months")
col3.metric("Projected Revenue/Cycle", f"${revenue_per_cycle:,.0f}")
col4.metric("Projected Profit/Year", f"${profit_per_year:,.0f}", delta_color="inverse")


# Row 2: Charts and Visuals
st.header("Visual Projections")
col1, col2 = st.columns([2, 1])

with col1:
    # Profitability Chart
    st.subheader("Profitability Over Time")
    profit_data = {
        'Year': [1, 2, 3, 4, 5],
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
    # Add a line for the initial investment
    fig_profit.add_hline(y=capex, line_dash="dot", annotation_text="Initial Investment (CAPEX)", annotation_position="bottom right")
    st.plotly_chart(fig_profit, use_container_width=True)


with col2:
    # Revenue Breakdown Chart
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
        color_discrete_map={'Vegetable':'#2ca02c', 'Tree':'#8c564b'}
    )
    st.plotly_chart(fig_pie, use_container_width=True)


# Row 3: Risks and Sustainability
st.header("5. Risks & Sustainability")
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
    risk_info = ""
    if 'Drought' in risk_factor:
        adjusted_revenue *= 0.80
        risk_info = "Droughts can reduce farmer purchasing power, lowering sales."
    if 'Pest' in risk_factor:
        adjusted_yield = projected_yield * 0.85
        adjusted_revenue = (adjusted_yield * veg_percentage * avg_price_veg) + \
                           (adjusted_yield * (1 - veg_percentage) * avg_price_tree)
        risk_info = "A severe pest attack can reduce the number of sellable seedlings."

    adjusted_profit = (adjusted_revenue - opex_per_cycle) * 4
    st.warning(f"**Scenario:** {risk_info}")


with col2:
    st.metric("Adjusted Annual Profit", f"${adjusted_profit:,.0f}", f"{((adjusted_profit - profit_per_year) / profit_per_year) * 100 if profit_per_year else 0:.1f}% vs. No Risk")
    st.info(f"**Mitigation Strategy:** Our model promotes drought-tolerant varieties and uses Integrated Pest Management (IPM) to minimize these risks.")

# Add some visual appeal
st.header("Project Vision")
st.image("http://googleusercontent.com/image_collection/image_retrieval/12460295809072866260_0", caption="A vision for our commercial nursery in rural Zimbabwe.", use_column_width=True)

col1, col2 = st.columns(2)
col1.image("http://googleusercontent.com/image_collection/image_retrieval/8150812869663407436_0", caption="High-quality vegetable seedlings ready for local farmers.", use_column_width=True)
col2.image("http://googleusercontent.com/image_collection/image_retrieval/5002659753976204598_0", caption="Tree seedlings to support afforestation and community orchards.", use_column_width=True)