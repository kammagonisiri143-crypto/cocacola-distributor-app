import streamlit as st
import pandas as pd

st.set_page_config(page_title="Coca-Cola Distributor Pricing Calculator", page_icon="🥤", layout="centered")

# Custom styling for Coca-Cola branding aesthetic
st.markdown("""
    <style>
    .main {
        background-color: #f9f9f9;
    }
    .stButton>button {
        background-color: #F40009;
        color: white;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🥤 Coca-Cola Distributor Order & Rate Calculator")
st.write("Instant volume-based pricing calculator for retail and wholesale orders.")

# Product Catalog with base prices per case (₹)
products = {
    "Coca-Cola 300ml Glass (24 bottles)": 450.0,
    "Sprite 300ml Glass (24 bottles)": 440.0,
    "Thums Up 300ml Glass (24 bottles)": 450.0,
    "Minute Maid Orange 1L (12 bottles)": 720.0,
    "Kinley Soda 600ml (24 bottles)": 300.0
}

col1, col2 = st.columns(2)

with col1:
    selected_product = st.selectbox("Select Product", list(products.keys()))
    base_price = products[selected_product]
    st.info(f"Base Rate (1 Case): ₹{base_price:.2f}")

with col2:
    cases = st.number_input("Enter Number of Cases", min_value=1, max_value=10000, value=1, step=1)

# Tiered Pricing Logic
def calculate_rate(cases, base_price):
    if cases >= 100:
        discount = 0.10  # 10% discount for 100+ cases
        tier_name = "Bulk Tier (100+ Cases - 10% Off)"
    elif cases >= 50:
        discount = 0.07  # 7% discount for 50-99 cases
        tier_name = "Wholesale Tier (50-99 Cases - 7% Off)"
    elif cases >= 10:
        discount = 0.04  # 4% discount for 10-49 cases
        tier_name = "Dealer Tier (10-49 Cases - 4% Off)"
    else:
        discount = 0.0   # Standard retail rate for 1-9 cases
        tier_name = "Standard Tier (1-9 Cases)"
    
    discounted_rate = base_price * (1 - discount)
    total_amount = discounted_rate * cases
    return discounted_rate, total_amount, tier_name, discount * 100

unit_rate, total_amount, tier_name, discount_pct = calculate_rate(cases, base_price)

st.markdown("---")
st.subheader("📊 Order Summary")

m1, m2, m3 = st.columns(3)
m1.metric("Applied Tier", tier_name)
m2.metric("Rate Per Case", f"₹{unit_rate:.2f}", delta=f"-{discount_pct}%" if discount_pct > 0 else None)
m3.metric("Total Order Value", f"₹{total_amount:,.2f}")

# Quick Reference Table for Volume Discount Tiers
with st.expander("View Volume Discount Tiers for Selected Product"):
    tier_data = {
        "Quantity Range": ["1 - 9 Cases", "10 - 49 Cases", "50 - 99 Cases", "100+ Cases"],
        "Discount": ["0% (Base Price)", "4%", "7%", "10%"],
        "Effective Rate per Case": [
            f"₹{base_price:.2f}", 
            f"₹{base_price * 0.96:.2f}", 
            f"₹{base_price * 0.93:.2f}", 
            f"₹{base_price * 0.90:.2f}"
        ]
    }
    st.table(pd.DataFrame(tier_data))
