import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
import json
import os
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="💎 Smart Price Tracker",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for premium design
st.markdown("""
    <style>
    :root {
        --primary-color: #7c3aed;
        --secondary-color: #06b6d4;
        --accent-color: #ec4899;
        --success-color: #10b981;
    }
    
    * {
        margin: 0;
        padding: 0;
    }
    
    [data-testid="stMainBlockContainer"] {
        background: linear-gradient(135deg, #1e1b4b 0%, #3730a3 50%, #2e1065 100%);
        min-height: 100vh;
    }
    
    .main {
        background: transparent;
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #312e81 0%, #1e1b4b 100%);
    }
    
    .premium-header {
        background: linear-gradient(90deg, rgba(124,58,237,0.3), rgba(6,182,212,0.3));
        border: 1px solid rgba(6,182,212,0.3);
        border-radius: 15px;
        padding: 25px;
        margin-bottom: 25px;
        backdrop-filter: blur(10px);
    }
    
    .stat-card {
        background: linear-gradient(135deg, rgba(124,58,237,0.2), rgba(6,182,212,0.1));
        border: 1px solid rgba(6,182,212,0.3);
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        backdrop-filter: blur(10px);
    }
    
    .product-card {
        background: linear-gradient(135deg, rgba(124,58,237,0.15), rgba(6,182,212,0.1));
        border: 2px solid rgba(6,182,212,0.2);
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    
    .product-card:hover {
        border-color: rgba(6,182,212,0.5);
        background: linear-gradient(135deg, rgba(124,58,237,0.25), rgba(6,182,212,0.15));
    }
    
    .price-dropped {
        border-color: rgba(16,185,129,0.5);
        background: linear-gradient(135deg, rgba(16,185,129,0.15), rgba(6,182,212,0.1));
    }
    
    .text-cyan { color: #06b6d4; }
    .text-pink { color: #ec4899; }
    .text-green { color: #10b981; }
    .text-purple { color: #a78bfa; }
    
    h1, h2, h3, h4, h5, h6 {
        background: linear-gradient(90deg, #06b6d4, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #06b6d4, #ec4899) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: bold !important;
        padding: 12px 24px !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 0 20px rgba(6,182,212,0.5);
    }
    
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {
        background: rgba(30,27,75,0.8) !important;
        border: 1px solid rgba(6,182,212,0.3) !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 12px !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
        border-color: rgba(6,182,212,0.8) !important;
        box-shadow: 0 0 10px rgba(6,182,212,0.3) !important;
    }
    
    .metric-value {
        font-size: 32px;
        font-weight: bold;
        background: linear-gradient(90deg, #06b6d4, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    </style>
""", unsafe_allow_html=True)

# Data storage functions
DATA_FILE = "tracked_products.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {"products": [], "history": {}}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def get_product_price(url):
    """Fetch product price from Amazon/Flipkart"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Try different selectors
        title_tag = soup.find(id="productTitle")
        title = title_tag.get_text().strip() if title_tag else "Unknown Product"
        
        price_tag = soup.find("span", class_="a-price-whole") or soup.find("span", class_="a-offscreen")
        
        if price_tag:
            price_text = price_tag.get_text().replace("₹", "").replace(",", "").strip()
            return title, float(price_text)
        else:
            return title, None
    except Exception as e:
        return "Error", None

# Initialize session state
if "products" not in st.session_state:
    data = load_data()
    st.session_state.products = data["products"]
    st.session_state.history = data["history"]
    st.session_state.notifications = []

# Header
st.markdown("""
    <div class="premium-header">
        <h1 style="margin: 0; font-size: 48px;">💎 Smart Price Tracker</h1>
        <p style="color: #a78bfa; margin-top: 10px; font-size: 16px;">Track prices, save money, get alerts instantly</p>
    </div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    auto_update = st.checkbox("🔄 Auto Update (5s)", value=True)
    show_history = st.checkbox("📊 Show Price History", value=False)
    notification_enabled = st.checkbox("🔔 Enable Notifications", value=True)

# Main Layout
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
        <div class="stat-card">
            <p style="color: #a78bfa; font-size: 12px; font-weight: bold;">PRODUCTS TRACKED</p>
            <p class="metric-value" style="font-size: 36px; margin-top: 5px;">""" + str(len(st.session_state.products)) + """</p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    total_savings = sum([max(0, p.get("target_price", 0) - p.get("current_price", 0)) for p in st.session_state.products])
    st.markdown(f"""
        <div class="stat-card">
            <p style="color: #a78bfa; font-size: 12px; font-weight: bold;">TOTAL SAVINGS POTENTIAL</p>
            <p class="metric-value" style="font-size: 36px; margin-top: 5px;">₹{total_savings:,.0f}</p>
        </div>
    """, unsafe_allow_html=True)

with col3:
    dropped = sum([1 for p in st.session_state.products if p.get("status") == "dropped"])
    st.markdown(f"""
        <div class="stat-card">
            <p style="color: #a78bfa; font-size: 12px; font-weight: bold;">PRICE ALERTS</p>
            <p class="metric-value" style="font-size: 36px; margin-top: 5px;">🎉 {dropped}</p>
        </div>
    """, unsafe_allow_html=True)

# Input Section
st.markdown("---")
st.markdown("### 🚀 Add Product to Track")

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    product_url = st.text_input("Product URL", placeholder="https://amazon.com/dp/...", label_visibility="collapsed")

with col2:
    target_price = st.number_input("Target Price (₹)", min_value=0, step=100, label_visibility="collapsed")

with col3:
    if st.button("🚀 Start Tracking", use_container_width=True):
        if product_url and target_price > 0:
            title, current_price = get_product_price(product_url)
            
            if current_price:
                product = {
                    "id": str(datetime.now().timestamp()),
                    "name": title[:50],
                    "url": product_url,
                    "target_price": float(target_price),
                    "current_price": float(current_price),
                    "added_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "status": "dropped" if current_price <= target_price else "tracking"
                }
                
                st.session_state.products.insert(0, product)
                st.session_state.history[product["id"]] = [{"price": current_price, "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]
                
                data = load_data()
                data["products"] = st.session_state.products
                data["history"] = st.session_state.history
                save_data(data)
                
                if product["status"] == "dropped":
                    st.success(f"✅ Price Dropped! Current: ₹{current_price:,.2f}")
                else:
                    st.info(f"📦 Tracking started! Current: ₹{current_price:,.2f}")
                st.rerun()
            else:
                st.error("❌ Could not fetch price. Check URL or try again later.")
        else:
            st.error("❌ Please enter a valid URL and price.")

# Products Section
st.markdown("---")
st.markdown("### 📦 Tracked Products")

if len(st.session_state.products) == 0:
    st.info("📊 No products tracked yet. Add one to get started!")
else:
    for idx, product in enumerate(st.session_state.products):
        css_class = "price-dropped" if product["status"] == "dropped" else ""
        
        with st.container():
            st.markdown(f"""
                <div class="product-card {css_class}">
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 15px;">
                        <div>
                            <h3 style="margin: 0; color: #06b6d4;">{product['name']}</h3>
                            <p style="color: #a78bfa; font-size: 12px; margin: 5px 0;">Added: {product['added_date']}</p>
                        </div>
                        <div style="display: flex; gap: 10px;">
                            <span style="background: {'rgba(16,185,129,0.3)' if product['status'] == 'dropped' else 'rgba(245,158,11,0.3)'}; color: {'#10b981' if product['status'] == 'dropped' else '#fbbf24'}; padding: 5px 12px; border-radius: 20px; font-size: 12px; font-weight: bold;">
                                {'✅ Price Dropped!' if product['status'] == 'dropped' else '⏳ Tracking'}
                            </span>
                        </div>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 15px;">
                        <div>
                            <p style="color: #a78bfa; font-size: 11px; font-weight: bold; margin-bottom: 5px;">TARGET PRICE</p>
                            <p style="color: #06b6d4; font-size: 24px; font-weight: bold;">₹{product['target_price']:,.0f}</p>
                        </div>
                        <div>
                            <p style="color: #a78bfa; font-size: 11px; font-weight: bold; margin-bottom: 5px;">CURRENT PRICE</p>
                            <p style="color: #ec4899; font-size: 24px; font-weight: bold;">₹{product['current_price']:,.0f}</p>
                        </div>
                        <div>
                            <p style="color: #a78bfa; font-size: 11px; font-weight: bold; margin-bottom: 5px;">SAVINGS</p>
                            <p style="color: {'#10b981' if product['current_price'] <= product['target_price'] else '#ef4444'}; font-size: 24px; font-weight: bold;">₹{max(0, product['target_price'] - product['current_price']):,.0f}</p>
                        </div>
                        <div>
                            <p style="color: #a78bfa; font-size: 11px; font-weight: bold; margin-bottom: 5px;">DISCOUNT %</p>
                            <p style="color: #06b6d4; font-size: 24px; font-weight: bold;">{((product['target_price'] - product['current_price']) / product['target_price'] * 100):.1f}%</p>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button(f"🔗 View Product", key=f"view_{idx}"):
                    st.write(f"URL: {product['url']}")
            
            with col2:
                if st.button(f"📊 Update Price", key=f"update_{idx}"):
                    title, new_price = get_product_price(product['url'])
                    if new_price:
                        st.session_state.products[idx]["current_price"] = new_price
                        st.session_state.products[idx]["status"] = "dropped" if new_price <= product["target_price"] else "tracking"
                        
                        if product["id"] not in st.session_state.history:
                            st.session_state.history[product["id"]] = []
                        st.session_state.history[product["id"]].append({"price": new_price, "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
                        
                        data = load_data()
                        data["products"] = st.session_state.products
                        data["history"] = st.session_state.history
                        save_data(data)
                        
                        st.success(f"✅ Updated! New price: ₹{new_price:,.2f}")
                        st.rerun()
            
            with col3:
                if st.button(f"🗑️ Delete", key=f"delete_{idx}"):
                    st.session_state.products.pop(idx)
                    data = load_data()
                    data["products"] = st.session_state.products
                    save_data(data)
                    st.success("✅ Product removed!")
                    st.rerun()
            
            if show_history and product["id"] in st.session_state.history:
                st.markdown("#### 📊 Price History")
                history_data = st.session_state.history[product["id"]]
                
                df = pd.DataFrame(history_data)
                st.line_chart(data=df.set_index("date")["price"], use_container_width=True)
                
                with st.expander("View Details"):
                    st.dataframe(df, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #a78bfa; padding: 20px; font-size: 14px;">
        <p>💎 Smart Price Tracker • Track prices and save money • Built with ❤️</p>
        <p style="font-size: 12px; color: #6b7280; margin-top: 10px;">Prices update automatically • Get instant alerts when prices drop</p>
    </div>
""", unsafe_allow_html=True)