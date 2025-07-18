import streamlit as st

def main():
    st.set_page_config(page_title="Real Economy Simulator", layout="centered")
    st.title("📊 Real Economy Simulator")
    st.markdown("Use the sliders to simulate basic economic parameters:")

    # Sliders
    interest_rate = st.slider("Interest Rate (%)", 0.0, 15.0, 2.5)
    inflation_rate = st.slider("Inflation Rate (%)", 0.0, 10.0, 3.0)
    gdp_growth = st.slider("GDP Growth Rate (%)", -5.0, 10.0, 2.0)

    # New Economic Inputs
    st.subheader("🔧 Economic Parameters")
    min_wage = st.slider("Federal Minimum Wage ($/hr)", 7.25, 25.0, 15.0, 0.25)
    housing_cost = st.slider("Avg Monthly Housing Cost ($)", 500, 3000, 1200, 50)
    tax_rate = st.slider("Tax Rate (%)", 0.0, 40.0, 15.0, 0.5)

    # Basic Yearly Income Calculation (Full-time: 40hrs/week * 52 weeks)
    annual_income = min_wage * 40 * 52
    annual_tax_paid = annual_income * (tax_rate / 100)
    net_income = annual_income - annual_tax_paid
    annual_housing_cost = housing_cost * 12
    disposable_income = net_income - annual_housing_cost

    # Show new values
    st.metric("Net Annual Income", f"${net_income:,.2f}")
    st.metric("Annual Housing Cost", f"${annual_housing_cost:,.2f}")
    st.metric("Disposable Income After Housing", f"${disposable_income:,.2f}")

    # Simple calculation
    unemployment = round(max(0.5, 8 - gdp_growth + interest_rate / 2 + inflation_rate / 4), 2)

    from streamlit_elements import elements, html

    # Basic CSS for visual simulation
    css = """
    <style>
    .simulation-container {
        width: 100%;
        height: 300px;
        position: relative;
        background-color: #1e1e1e;
        border: 1px solid #444;
        border-radius: 8px;
        overflow: hidden;
        margin-top: 2rem;
    }
    .person {
        width: 40px;
        height: 40px;
        background-color: #4CAF50;
        position: absolute;
        bottom: 10px;
        border-radius: 8px;
        animation: movePerson 5s infinite alternate ease-in-out;
    }
    .coin {
        width: 20px;
        height: 20px;
        background-color: gold;
        border-radius: 50%;
        position: absolute;
        bottom: 60px;
        animation: moveCoin 2s infinite alternate ease-in-out;
    }

    @keyframes movePerson {
        0% { left: 10%; }
        100% { left: 70%; }
    }

    @keyframes moveCoin {
        0% { left: 15%; }
        100% { left: 75%; }
    }
    </style>
    """

    with elements("visual_simulation"):
        html(f"""
        {css}
        <div class="simulation-container">
            <div class="person" style="animation-delay: 0s;"></div>
            <div class="coin" style="animation-delay: 0.5s;"></div>
        </div>
        """)

    # Output
    st.metric("Estimated Unemployment Rate", f"{unemployment} %")

if __name__ == "__main__":
    main()
