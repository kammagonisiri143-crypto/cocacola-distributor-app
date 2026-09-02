import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Coca-Cola Distributor ERP", page_icon="🥤", layout="wide")

# Custom styling for Coca-Cola aesthetic
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { background-color: #F40009; color: white; font-weight: bold; border-radius: 4px; }
    .stButton>button:hover { background-color: #d10007; color: white; }
    </style>
""", unsafe_allow_html=True)

# ----------------- SESSION STATE INITIALIZATION -----------------
if "products" not in st.session_state:
    st.session_state.products = {
        "Coca-Cola 300ml Glass (24 bottles)": 450.0,
        "Sprite 300ml Glass (24 bottles)": 440.0,
        "Thums Up 300ml Glass (24 bottles)": 450.0,
        "Minute Maid Orange 1L (12 bottles)": 720.0,
        "Kinley Soda 600ml (24 bottles)": 300.0
    }

if "customers" not in st.session_state:
    st.session_state.customers = [
        {"id": 1, "name": "Rajesh Kumar", "shop": "Kumar General Store", "phone": "9876543210", "address": "Market Road, City"},
        {"id": 2, "name": "Amit Sharma", "shop": "Sharma Cold Drinks", "phone": "9123456789", "address": "Station Street, City"}
    ]

if "orders" not in st.session_state:
    st.session_state.orders = []

# ----------------- NAVIGATION -----------------
st.sidebar.title("🥤 Coke Distributor ERP")
menu = st.sidebar.radio("Navigation", ["Dashboard & Calculator", "Product Management", "Customer Management", "Orders & Invoicing"])

# ----------------- 1. DASHBOARD & CALCULATOR -----------------
if menu == "Dashboard & Calculator":
    st.title("🥤 Quick Rate & Order Estimator")
    st.write("Calculate instant volume-based pricing for active retail and wholesale orders.")

    col1, col2 = st.columns(2)
    products = st.session_state.products

    with col1:
        selected_product = st.selectbox("Select Product", list(products.keys()))
        base_price = products[selected_product]
        st.info(f"Base Rate (1 Case): ₹{base_price:.2f}")

    with col2:
        cases = st.number_input("Enter Number of Cases", min_value=1, max_value=10000, value=1, step=1)

    def calculate_rate(cases, base_price):
        if cases >= 100:
            discount = 0.10
            tier_name = "Bulk Tier (100+ Cases - 10% Off)"
        elif cases >= 50:
            discount = 0.07
            tier_name = "Wholesale Tier (50-99 Cases - 7% Off)"
        elif cases >= 10:
            discount = 0.04
            tier_name = "Dealer Tier (10-49 Cases - 4% Off)"
        else:
            discount = 0.0
            tier_name = "Standard Tier (1-9 Cases)"
        
        discounted_rate = base_price * (1 - discount)
        total_amount = discounted_rate * cases
        return discounted_rate, total_amount, tier_name, discount * 100

    unit_rate, total_amount, tier_name, discount_pct = calculate_rate(cases, base_price)

    st.markdown("---")
    m1, m2, m3 = st.columns(3)
    m1.metric("Applied Tier", tier_name)
    m2.metric("Rate Per Case", f"₹{unit_rate:.2f}", delta=f"-{discount_pct}%" if discount_pct > 0 else None)
    m3.metric("Total Order Value", f"₹{total_amount:,.2f}")

# ----------------- 2. PRODUCT MANAGEMENT -----------------
elif menu == "Product Management":
    st.title("📦 Product & Pricing Management")
    st.write("Add new Coca-Cola items or update current wholesale rates per case.")

    tab1, tab2 = st.tabs(["Update / Edit Existing Products", "Add New Product"])

    with tab1:
        st.subheader("Edit Current Product Rates")
        for prod, price in list(st.session_state.products.items()):
            col_a, col_b, col_c = st.columns([3, 2, 1])
            with col_a:
                st.write(f"**{prod}**")
            with col_b:
                new_price = st.number_input(f"Rate for {prod}", value=float(price), key=f"price_{prod}", label_visibility="collapsed")
            with col_c:
                if st.button("Update", key=f"btn_{prod}"):
                    st.session_state.products[prod] = new_price
                    st.success(f"Updated!")
            st.divider()

    with tab2:
        st.subheader("Add a New Product SKU")
        with st.form("new_product_form"):
            new_name = st.text_input("Product Name & Packaging Description (e.g., Fanta 300ml Glass)")
            new_price = st.number_input("Base Rate per Case (₹)", min_value=1.0, value=400.0)
            submit_product = st.form_submit_button("Add Product")
            
            if submit_product:
                if new_name and new_name not in st.session_state.products:
                    st.session_state.products[new_name] = new_price
                    st.success(f"Successfully added {new_name}!")
                    st.rerun()
                else:
                    st.error("Product name cannot be empty or already exists.")

# ----------------- 3. CUSTOMER MANAGEMENT -----------------
elif menu == "Customer Management":
    st.title("👥 Customer Directory & Ledger")
    
    tab_list, tab_add = st.tabs(["View / Search / Edit Customers", "Add New Customer"])

    with tab_list:
        search_query = st.text_input("🔍 Search customer by name, shop name, or phone number", "").lower()
        
        filtered_customers = [
            c for c in st.session_state.customers 
            if search_query in c["name"].lower() or search_query in c["shop"].lower() or search_query in c["phone"]
        ]

        if not filtered_customers:
            st.info("No customers found.")
        else:
            for cust in filtered_customers:
                with st.expander(f"🏪 {cust['shop']} — {cust['name']} ({cust['phone']})"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Contact Person:** {cust['name']}")
                        st.write(f"**Phone:** {cust['phone']}")
                        st.write(f"**Address:** {cust['address']}")
                    with col2:
                        # Compute customer history metrics
                        cust_orders = [o for o in st.session_state.orders if o['customer_id'] == cust['id']]
                        total_spent = sum([o['total_amount'] for o in cust_orders])
                        st.metric("Total Orders Placed", len(cust_orders))
                        st.metric("Total Amount Purchased", f"₹{total_spent:,.2f}")

                    # Edit & Delete options
                    with st.form(f"edit_cust_{cust['id']}"):
                        st.write("### Edit Details")
                        e_name = st.text_input("Customer Name", value=cust['name'], key=f"ename_{cust['id']}")
                        e_shop = st.text_input("Shop Name", value=cust['shop'], key=f"eshop_{cust['id']}")
                        e_phone = st.text_input("Phone Number", value=cust['phone'], key=f"ephone_{cust['id']}")
                        e_addr = st.text_area("Address", value=cust['address'], key=f"eaddr_{cust['id']}")
                        
                        col_sub1, col_sub2 = st.columns(2)
                        with col_sub1:
                            if st.form_submit_button("Save Changes"):
                                cust['name'] = e_name
                                cust['shop'] = e_shop
                                cust['phone'] = e_phone
                                cust['address'] = e_addr
                                st.success("Customer details updated successfully!")
                                st.rerun()
                        with col_sub2:
                            if st.form_submit_button("Delete Customer", type="primary"):
                                st.session_state.customers = [c for c in st.session_state.customers if c['id'] != cust['id']]
                                st.warning("Customer deleted.")
                                st.rerun()

                    # Order History Table
                    if cust_orders:
                        st.write("#### Order History")
                        df_history = pd.DataFrame(cust_orders)[['order_id', 'date', 'total_cases', 'total_amount', 'payment_status']]
                        st.dataframe(df_history, use_container_width=True)

    with tab_add:
        st.subheader("Register a New Retailer / Outlet")
        with st.form("add_customer_form"):
            c_name = st.text_input("Customer Full Name")
            c_shop = st.text_input("Shop Name")
            c_phone = st.text_input("Phone Number")
            c_addr = st.text_area("Shop Address")
            
            submitted = st.form_submit_button("Save Customer")
            if submitted:
                if c_name and c_shop and c_phone:
                    new_id = max([c['id'] for c in st.session_state.customers], default=0) + 1
                    st.session_state.customers.append({
                        "id": new_id, "name": c_name, "shop": c_shop, "phone": c_phone, "address": c_addr
                    })
                    st.success(f"Customer {c_shop} added successfully!")
                    st.rerun()
                else:
                    st.error("Please fill in Name, Shop Name, and Phone Number.")

# ----------------- 4. ORDERS & INVOICING -----------------
elif menu == "Orders & Invoicing":
    st.title("📝 Orders & Professional Invoicing")

    tab_create, tab_view = st.tabs(["Create New Order", "View Orders & Invoices"])

    with tab_create:
        if not st.session_state.customers:
            st.warning("Please add at least one customer under Customer Management before making an order.")
        else:
            st.subheader("Generate New Order")
            with st.form("create_order_form"):
                # Customer selection
                cust_options = {f"{c['shop']} ({c['name']})": c['id'] for c in st.session_state.customers}
                selected_cust_label = st.selectbox("Select Customer", list(cust_options.keys()))
                customer_id = cust_options[selected_cust_label]

                # Product line item selection
                st.write("#### Order Items")
                products = st.session_state.products
                selected_product = st.selectbox("Select Product SKU", list(products.keys()))
                cases = st.number_input("Quantity (Cases)", min_value=1, value=1)
                payment_status = st.selectbox("Payment Status", ["Paid", "Pending", "Partial"])

                submit_order = st.form_submit_button("Create Order & Calculate")

                if submit_order:
                    base_price = products[selected_product]
                    # Apply automatic tiered calculation logic
                    if cases >= 100:
                        discount_pct = 10.0
                    elif cases >= 50:
                        discount_pct = 7.0
                    elif cases >= 10:
                        discount_pct = 4.0
                    else:
                        discount_pct = 0.0

                    rate_per_case = base_price * (1 - (discount_pct / 100))
                    total_amount = rate_per_case * cases

                    order_id = f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    
                    new_order = {
                        "order_id": order_id,
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "customer_id": customer_id,
                        "product": selected_product,
                        "cases": cases,
                        "base_price": base_price,
                        "discount_pct": discount_pct,
                        "rate_per_case": rate_per_case,
                        "total_amount": total_amount,
                        "payment_status": payment_status
                    }
                    st.session_state.orders.insert(0, new_order)
                    st.success(f"Order created successfully! Order ID: {order_id}")

    with tab_view:
        st.subheader("All Orders Ledger")
        if not st.session_state.orders:
            st.info("No orders created yet.")
        else:
            for ord in st.session_state.orders:
                cust_info = next((c for c in st.session_state.customers if c['id'] == ord['customer_id']), {"name": "Unknown", "shop": "Unknown", "phone": "", "address": ""})
                
                with st.expander(f"Order #{ord['order_id']} | {cust_info['shop']} | ₹{ord['total_amount']:,.2f} | Status: {ord['payment_status']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Date:** {ord['date']}")
                        st.write(f"**Customer:** {cust_info['name']} ({cust_info['shop']})")
                        st.write(f"**Phone:** {cust_info['phone']}")
                    with col2:
                        st.write(f"**Product:** {ord['product']}")
                        st.write(f"**Total Cases:** {ord['cases']}")
                        st.write(f"**Payment Status:** {ord['payment_status']}")

                    # Invoice Generator Preview Window
                    if st.button(f"Generate Invoice for #{ord['order_id']}", key=f"inv_btn_{ord['order_id']}"):
                        st.markdown("---")
                        invoice_html = f"""
                        <div style="border: 2px solid #F40009; padding: 25px; border-radius: 8px; font-family: Arial, sans-serif; background-color: #ffffff; color: #000000;">
                            <h2 style="color: #F40009; text-align: center; margin-bottom: 0;">COCA-COLA AUTHORIZED DISTRIBUTOR</h2>
                            <p style="text-align: center; font-size: 13px; color: #555;">Wholesale & Retail Beverage Distribution Invoice</p>
                            <hr style="border: 1px solid #ddd;">
                            
                            <table style="width: 100%; margin-bottom: 20px;">
                                <tr>
                                    <td>
                                        <strong>Invoice Number:</strong> {ord['order_id']}<br>
                                        <strong>Date:</strong> {ord['date']}<br>
                                        <strong>Payment Status:</strong> <span style="color: {'green' if ord['payment_status']=='Paid' else 'orange'}; font-weight: bold;">{ord['payment_status']}</span>
                                    </td>
                                    <td style="text-align: right;">
                                        <strong>Bill To:</strong><br>
                                        {cust_info['shop']}<br>
                                        Attn: {cust_info['name']}<br>
                                        Phone: {cust_info['phone']}<br>
                                        Address: {cust_info['address']}
                                    </td>
                                </tr>
                            </table>

                            <table border="1" style="width: 100%; border-collapse: collapse; text-align: center; font-size: 14px;">
                                <tr style="background-color: #F40009; color: white;">
                                    <th style="padding: 8px;">Product Description</th>
                                    <th style="padding: 8px;">Cases / Qty</th>
                                    <th style="padding: 8px;">Base Rate (₹)</th>
                                    <th style="padding: 8px;">Discount (%)</th>
                                    <th style="padding: 8px;">Effective Rate (₹)</th>
                                    <th style="padding: 8px;">Total (₹)</th>
                                </tr>
                                <tr>
                                    <td style="padding: 8px; text-align: left;">{ord['product']}</td>
                                    <td style="padding: 8px;">{ord['cases']}</td>
                                    <td style="padding: 8px;">₹{ord['base_price']:.2f}</td>
                                    <td style="padding: 8px;">{ord['discount_pct']}%</td>
                                    <td style="padding: 8px;">₹{ord['rate_per_case']:.2f}</td>
                                    <td style="padding: 8px;">₹{ord['total_amount']:,.2f}</td>
                                </tr>
                            </table>
                            
                            <h3 style="text-align: right; margin-top: 15px; color: #333;">Grand Total: ₹{ord['total_amount']:,.2f}</h3>
                            <p style="text-align: center; font-size: 12px; margin-top: 30px; color: #777;">Thank you for your business! Refresh stock regularly.</p>
                        </div>
                        """
                        st.markdown(invoice_html, unsafe_allow_html=True)
                        
                        # Print/Download triggers
                        st.markdown("""
                            <script>
                            function printDiv() {
                                window.print();
                            }
                            </script>
                        """, unsafe_allow_html=True)
                        
                        col_p1, col_p2 = st.columns(2)
                        with col_p1:
                            if st.button("🖨️ Print Invoice", key=f"print_{ord['order_id']}"):
                                st.write("ℹ️ *Tip: Use your browser's print dialog (Ctrl+P / Cmd+P) to print or save as PDF.*")
                        with col_p2:
                            st.download_button(
                                label="📥 Download Invoice HTML",
                                data=invoice_html,
                                file_name=f"Invoice_{ord['order_id']}.html",
                                mime="text/html",
                                key=f"dl_{ord['order_id']}"
                            )
