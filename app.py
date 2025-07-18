import streamlit as st


def main():
    st.set_page_config(page_title="Real Economy Simulator", layout="centered")

    st.title("📊 Real Economy Simulator")

    st.markdown("Use the sliders to simulate basic economic parameters:")

    # Sliders
    interest_rate = st.slider("Interest Rate (%)", 0.0, 15.0, 2.5)
    inflation_rate = st.slider("Inflation Rate (%)", 0.0, 10.0, 3.0)
    gdp_growth = st.slider("GDP Growth Rate (%)", -5.0, 10.0, 2.0)

    # Simple calculation
    unemployment = round(
        max(0.5, 8 - gdp_growth + interest_rate / 2 + inflation_rate / 4), 2
    )

    # Output
    st.metric("Estimated Unemployment Rate", f"{unemployment} %")


if __name__ == "__main__":
    main()
