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
if "users" not in st.session_state:
    st.session_state.users = {"admin": "coke123"}  # Default credentials

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "current_user" not in st.session_state:
    st.session_state.current_user = ""

if "products" not in st.session_state:
    st.session_state.products = {
        "Coca-Cola 300ml Glass": {"case_price": 450.0, "bottles_per_case": 24},
        "Sprite 300ml Glass": {"case_price": 440.0, "bottles_per_case": 24},
        "Thums Up 300ml Glass": {"case_price": 450.0, "bottles_per_case": 24},
        "Minute Maid Orange 1L": {"case_price": 720.0, "bottles_per_case": 12},
        "Kinley Soda 600ml": {"case_price": 300.0, "bottles_per_case": 24}
    }

if "customers" not in st.session_state:
    st.session_state.customers = [
        {"id": 1, "name": "Rajesh Kumar", "shop": "Kumar General Store", "phone": "9876543210", "address": "Market Road, City"},
        {"id": 2, "name": "Amit Sharma", "shop": "Sharma Cold Drinks", "phone": "9123456789", "address": "Station Street, City"}
    ]

if "orders" not in st.session_state:
    st.session_state.orders = []

if "cart" not in st.session_state:
    st.session_state.cart = []

# ----------------- AUTHENTICATION FLOW -----------------
def login_signup_page():
    st.title("🥤 Coca-Cola Distributor Portal")
    st.write("Please sign in or create an account to access the distribution ERP system.")
    
    auth_tab1, auth_tab2 = st.tabs(["🔑 Sign In", "📝 Sign Up"])

    with auth_tab1:
        st.subheader("Sign In to Your Account")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit_login = st.form_submit_button("Sign In")

            if submit_login:
                if username in st.session_state.users and st.session_state.users[username] == password:
                    st.session_state.authenticated = True
                    st.session_state.current_user = username
                    st.success("Successfully logged in!")
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

    with auth_tab2:
        st.subheader("Create a New Account")
        with st.form("signup_form"):
            new_user = st.text_input("Choose Username")
            new_pass = st.text_input("Choose Password", type="password")
            confirm_pass = st.text_input("Confirm Password", type="password")
            submit_signup = st.form_submit_button("Sign Up")

            if submit_signup:
                if not new_user or not new_pass:
                    st.error("Username and password cannot be empty.")
                elif new_user in st.session_state.users:
                    st.error("Username already exists. Please sign in.")
                elif new_pass != confirm_pass:
                    st.error("Passwords do not match.")
                else:
                    st.session_state.users[new_user] = new_pass
                    st.success("Account created successfully! You can now sign in.")

# Run authentication check
if not st.session_state.authenticated:
    login_signup_page()
else:
    # ----------------- MAIN ERP APPLICATION -----------------
    st.sidebar.title("🥤 Coke Distributor ERP")
    st.sidebar.write(f"Welcome, **{st.session_state.current_user}**!")
    
    if st.sidebar.button("🚪 Sign Out"):
        st.session_state.authenticated = False
        st.session_state.current_user = ""
        st.rerun()

    menu = st.sidebar.radio("Navigation", ["Dashboard & Calculator", "Product Management", "Customer Management", "Orders & Invoicing"])

    # ----------------- 1. DASHBOARD & CALCULATOR -----------------
    if menu == "Dashboard & Calculator":
        st.title("🥤 Quick Rate & Order Estimator")
        st.write("Calculate instant volume-based pricing per case and per single bottle.")

        col1, col2 = st.columns(2)
        products = st.session_state.products

        with col1:
            selected_product = st.selectbox("Select Product", list(products.keys()))
            prod_info = products[selected_product]
            base_case_price = prod_info["case_price"]
            bottles_per_case = prod_info["bottles_per_case"]
            base_bottle_price = base_case_price / bottles_per_case

            st.info(f"📦 Base Case Rate ({bottles_per_case} bottles): ₹{base_case_price:.2f}")
            st.info(f"🍾 Base Single Bottle Rate: ₹{base_bottle_price:.2f}")

        with col2:
            cases = st.number_input("Enter Number of Cases", min_value=1, max_value=10000, value=1, step=1)
            total_bottles = cases * bottles_per_case
            st.write(f"Total Bottles in Order: **{total_bottles} bottles**")

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
            
            discounted_case_rate = base_price * (1 - discount)
            total_amount = discounted_case_rate * cases
            return discounted_case_rate, total_amount, tier_name, discount * 100

        unit_case_rate, total_amount, tier_name, discount_pct = calculate_rate(cases, base_case_price)
        unit_bottle_rate = unit_case_rate / bottles_per_case

        st.markdown("---")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Applied Tier", tier_name)
        m2.metric("Effective Rate / Case", f"₹{unit_case_rate:.2f}", delta=f"-{discount_pct}%" if discount_pct > 0 else None)
        m3.metric("Effective Rate / Bottle", f"₹{unit_bottle_rate:.2f}")
        m4.metric("Total Order Value", f"₹{total_amount:,.2f}")

    # ----------------- 2. PRODUCT MANAGEMENT -----------------
    elif menu == "Product Management":
        st.title("📦 Product & Pricing Management")
        st.write("Manage product SKUs, adjust case prices, or update individual bottle prices dynamically.")

        tab1, tab2 = st.tabs(["Update / Edit Existing Products", "Add New Product"])

        with tab1:
            st.subheader("Edit Current Product Prices & Packaging")
            for prod, info in list(st.session_state.products.items()):
                with st.container():
                    col_a, col_b, col_c, col_d = st.columns([3, 2, 2, 1])
                    with col_a:
                        st.write(f"**{prod}**")
                        st.caption(f"Standard Pack: {info['bottles_per_case']} bottles/case")
                    with col_b:
                        new_case_price = st.number_input(f"Case Price (₹) - {prod}", value=float(info['case_price']), key=f"case_p_{prod}")
                    with col_c:
                        new_bottle_price = st.number_input(f"Bottle Price (₹) - {prod}", value=float(info['case_price'] / info['bottles_per_case']), key=f"bot_p_{prod}", format="%.2f")
                    with col_d:
                        st.write("")
                        st.write("")
                        if st.button("Save", key=f"btn_{prod}"):
                            if new_case_price != info['case_price']:
                                st.session_state.products[prod]['case_price'] = new_case_price
                            elif new_bottle_price != (info['case_price'] / info['bottles_per_case']):
                                st.session_state.products[prod]['case_price'] = new_bottle_price * info['bottles_per_case']
                            st.success(f"Updated {prod}!")
                            st.rerun()
                    st.divider()

        with tab2:
            st.subheader("Add a New Product SKU")
            with st.form("new_product_form"):
                new_name = st.text_input("Product Name & Variant (e.g., Fanta 300ml Glass)")
                col_f1, col_f2 = st.columns(2)
                with col_f1:
                    new_bottles = st.number_input("Bottles per Case", min_value=1, value=24)
                with col_f2:
                    new_price = st.number_input("Base Case Rate (₹)", min_value=1.0, value=400.0)
                
                submit_product = st.form_submit_button("Add Product")
                
                if submit_product:
                    if new_name and new_name not in st.session_state.products:
                        st.session_state.products[new_name] = {
                            "case_price": new_price,
                            "bottles_per_case": int(new_bottles)
                        }
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
                            cust_orders = [o for o in st.session_state.orders if o['customer_id'] == cust['id']]
                            total_spent = sum([o['total_amount'] for o in cust_orders])
                            st.metric("Total Orders Placed", len(cust_orders))
                            st.metric("Total Amount Purchased", f"₹{total_spent:,.2f}")

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
                                    st.success("Customer updated successfully!")
                                    st.rerun()
                            with col_sub2:
                                if st.form_submit_button("Delete Customer", type="primary"):
                                    st.session_state.customers = [c for c in st.session_state.customers if c['id'] != cust['id']]
                                    st.warning("Customer deleted.")
                                    st.rerun()

                        if cust_orders:
                            st.write("#### Order History")
                            history_summary = []
                            for ord in cust_orders:
                                history_summary.append({
                                    "Order ID": ord['order_id'],
                                    "Date": ord['date'],
                                    "Total Cases": sum(item['cases'] for item in ord['items']),
                                    "Amount (₹)": f"₹{ord['total_amount']:,.2f}",
                                    "Status": ord['payment_status']
                                })
                            st.dataframe(pd.DataFrame(history_summary), use_container_width=True)

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
        st.title("📝 Multi-SKU Orders & Professional Invoicing")

        tab_create, tab_view = st.tabs(["Create Multi-SKU Order", "View Orders & Invoices"])

        with tab_create:
            if not st.session_state.customers:
                st.warning("Please add at least one customer under Customer Management first.")
            else:
                st.subheader("Build Order Cart (Multiple SKUs)")
                
                cust_options = {f"{c['shop']} ({c['name']})": c['id'] for c in st.session_state.customers}
                selected_cust_label = st.selectbox("Select Customer", list(cust_options.keys()))
                customer_id = cust_options[selected_cust_label]

                products = st.session_state.products

                with st.form("add_to_cart_form"):
                    st.write("#### Add Product Line Item")
                    col_i1, col_i2 = st.columns(2)
                    with col_i1:
                        sel_product = st.selectbox("Select SKU", list(products.keys()))
                    with col_i2:
                        cases = st.number_input("Quantity (Cases)", min_value=1, value=1)
                    
                    add_to_cart_btn = st.form_submit_button("Add to Order Cart")
                    if add_to_cart_btn:
                        p_info = products[sel_product]
                        base_price = p_info["case_price"]
                        bottles_per_case = p_info["bottles_per_case"]

                        if cases >= 100:
                            disc = 10.0
                        elif cases >= 50:
                            disc = 7.0
                        elif cases >= 10:
                            disc = 4.0
                        else:
                            disc = 0.0

                        rate_per_case = base_price * (1 - (disc / 100))
                        rate_per_bottle = rate_per_case / bottles_per_case
                        total_item_amount = rate_per_case * cases

                        cart_item = {
                            "product": sel_product,
                            "cases": cases,
                            "bottles_per_case": bottles_per_case,
                            "total_bottles": cases * bottles_per_case,
                            "base_price": base_price,
                            "discount_pct": disc,
                            "rate_per_case": rate_per_case,
                            "rate_per_bottle": rate_per_bottle,
                            "total_amount": total_item_amount
                        }
                        st.session_state.cart.append(cart_item)
                        st.success(f"Added {cases} case(s) of {sel_product} to cart!")

                if st.session_state.cart:
                    st.write("#### Current Cart Items")
                    cart_df = pd.DataFrame(st.session_state.cart)[['product', 'cases', 'total_bottles', 'rate_per_case', 'discount_pct', 'total_amount']]
                    cart_df.columns = ["Product SKU", "Cases", "Total Bottles", "Rate/Case (₹)", "Discount (%)", "Total (₹)"]
                    st.dataframe(cart_df, use_container_width=True)

                    grand_total = sum([item['total_amount'] for item in st.session_state.cart])
                    total_cases_all = sum([item['cases'] for item in st.session_state.cart])
                    st.write(f"### Total Cases: {total_cases_all} | Grand Total: ₹{grand_total:,.2f}")

                    payment_status = st.selectbox("Payment Status", ["Paid", "Pending", "Partial"])

                    col_c1, col_c2 = st.columns(2)
                    with col_c1:
                        if st.button("✅ Confirm & Finalize Order"):
                            order_id = f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                            new_order = {
                                "order_id": order_id,
                                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                "customer_id": customer_id,
                                "items": list(st.session_state.cart),
                                "total_cases": total_cases_all,
                                "total_amount": grand_total,
                                "payment_status": payment_status
                            }
                            st.session_state.orders.insert(0, new_order)
                            st.session_state.cart = []
                            st.success(f"Order #{order_id} successfully created!")
                            st.rerun()
                    with col_c2:
                        if st.button("🗑️ Clear Cart"):
                            st.session_state.cart = []
                            st.rerun()
                else:
                    st.info("Cart is empty. Add products above to build an order.")

        with tab_view:
            st.subheader("All Orders Ledger & Invoices")
            if not st.session_state.orders:
                st.info("No orders created yet.")
            else:
                for ord in st.session_state.orders:
                    cust_info = next((c for c in st.session_state.customers if c['id'] == ord['customer_id']), {"name": "Unknown", "shop": "Unknown", "phone": "", "address": ""})
                    
                    with st.expander(f"Order #{ord['order_id']} | {cust_info['shop']} | Cases: {ord['total_cases']} | ₹{ord['total_amount']:,.2f} | Status: {ord['payment_status']}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Date:** {ord['date']}")
                            st.write(f"**Customer:** {cust_info['name']} ({cust_info['shop']})")
                            st.write(f"**Phone:** {cust_info['phone']}")
                        with col2:
                            st.write(f"**Payment Status:** {ord['payment_status']}")
                            st.write(f"**Total Items/SKUs:** {len(ord['items'])}")

                        if st.button(f"Generate Invoice for #{ord['order_id']}", key=f"inv_btn_{ord['order_id']}"):
                            st.markdown("---")
                            
                            items_html = ""
                            for item in ord['items']:
                                items_html += f"""
                                <tr>
                                    <td style="padding: 8px; text-align: left;">{item['product']}</td>
                                    <td style="padding: 8px;">{item['cases']}</td>
                                    <td style="padding: 8px;">{item['total_bottles']}</td>
                                    <td style="padding: 8px;">₹{item['base_price']:.2f}</td>
                                    <td style="padding: 8px;">{item['discount_pct']}%</td>
                                    <td style="padding: 8px;">₹{item['rate_per_case']:.2f}</td>
                                    <td style="padding: 8px;">₹{item['rate_per_bottle']:.2f}</td>
                                    <td style="padding: 8px;">₹{item['total_amount']:,.2f}</td>
                                </tr>
                                """

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

                                <table border="1" style="width: 100%; border-collapse: collapse; text-align: center; font-size: 13px;">
                                    <tr style="background-color: #F40009; color: white;">
                                        <th style="padding: 8px;">Product Description</th>
                                        <th style="padding: 8px;">Cases</th>
                                        <th style="padding: 8px;">Total Bottles</th>
                                        <th style="padding: 8px;">Base Case (₹)</th>
                                        <th style="padding: 8px;">Discount</th>
                                        <th style="padding: 8px;">Rate/Case (₹)</th>
                                        <th style="padding: 8px;">Rate/Bottle (₹)</th>
                                        <th style="padding: 8px;">Total (₹)</th>
                                    </tr>
                                    {items_html}
                                </table>
                                
                                <h3 style="text-align: right; margin-top: 15px; color: #333;">Grand Total: ₹{ord['total_amount']:,.2f}</h3>
                                <p style="text-align: center; font-size: 12px; margin-top: 30px; color: #777;">Thank you for your business! Refresh stock regularly.</p>
                            </div>
                            """
                            st.markdown(invoice_html, unsafe_allow_html=True)
                            
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
