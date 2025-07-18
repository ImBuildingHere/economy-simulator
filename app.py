import streamlit as st
from animation_component import render_animation

# Set wide layout
st.set_page_config(layout="wide")

st.title("💸 Real Economy Simulator")
st.caption("Adjust parameters to simulate a simple economic model.")
st.markdown("---")

# --- Control Bar ---
col1, col2, col3 = st.columns(3)
with col1:
    inflation = st.slider("Inflation Rate (%)", 0.0, 10.0, 2.0, 0.1)
with col2:
    gdp_growth = st.slider("GDP Growth Rate (%)", -5.0, 10.0, 2.0, 0.1)
with col3:
    min_wage = st.slider("Minimum Wage ($/hr)", 7.25, 25.0, 15.0, 0.25)

monthly_housing = st.slider("Monthly Housing Cost ($)", 500, 3000, 1200, 50)
tax_rate = st.slider("Tax Rate (%)", 0.0, 40.0, 15.0, 0.5)

# --- Economic Logic ---
def calculate_income(min_wage, tax_rate):
    gross_income = min_wage * 40 * 52
    return gross_income * (1 - tax_rate / 100)

def calculate_housing_cost(monthly_cost):
    return monthly_cost * 12

def calculate_unemployment_rate(inflation, gdp_growth):
    base = 5.0
    inflation_impact = (inflation - 2.0) * 0.5
    gdp_impact = (2.0 - gdp_growth) * 0.7
    return max(0.0, base + inflation_impact + gdp_impact)

net_income = calculate_income(min_wage, tax_rate)
housing_cost = calculate_housing_cost(monthly_housing)
disposable_income = net_income - housing_cost
unemployment = calculate_unemployment_rate(inflation, gdp_growth)

# --- Results ---
st.markdown("### 📊 Simulation Results")
m1, m2, m3 = st.columns(3)
m1.metric("Net Annual Income", f"${net_income:,.2f}")
m2.metric("Annual Housing Cost", f"${housing_cost:,.2f}")
m3.metric("Disposable Income", f"${disposable_income:,.2f}")

st.markdown(f"### 📉 Estimated Unemployment Rate: **{unemployment:.1f}%**")

# --- Animation Component ---
render_animation(
    min_wage=min_wage,
    tax_rate=tax_rate,
    inflation=inflation,
    gdp_growth=gdp_growth,
    unemployment=unemployment,
    disposable_income=disposable_income
)
