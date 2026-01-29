import streamlit as st
import requests
import time
import random
import json
import os

# File to persist watchlist
WATCHLIST_FILE = os.path.join(os.path.dirname(__file__), "watchlist.json")

def load_watchlist():
    try:
        if os.path.exists(WATCHLIST_FILE):
            with open(WATCHLIST_FILE, "r") as f:
                return json.load(f)
    except:
        pass
    return {}

def save_watchlist(watchlist):
    try:
        with open(WATCHLIST_FILE, "w") as f:
            json.dump(watchlist, f)
    except:
        pass

# Initialize all session state at once
if "watchlist" not in st.session_state:
    st.session_state.watchlist = load_watchlist()
if "acknowledged_alerts" not in st.session_state:
    st.session_state.acknowledged_alerts = set()
if "editing_threshold" not in st.session_state:
    st.session_state.editing_threshold = None
if "rate_limit_until" not in st.session_state:
    st.session_state.rate_limit_until = 0
if "prices_cache" not in st.session_state:
    st.session_state.prices_cache = {}
if "prices_cache_time" not in st.session_state:
    st.session_state.prices_cache_time = 0

# Check rate limit status
def is_rate_limited():
    return st.session_state.rate_limit_until > 0

def set_rate_limit():
    st.session_state.rate_limit_until = time.time()

def clear_rate_limit():
    st.session_state.rate_limit_until = 0

def check_api_available():
    """Check if CoinGecko API is available again"""
    try:
        response = requests.get(
            "https://api.coingecko.com/api/v3/ping",
            timeout=5
        )
        return response.status_code == 200
    except:
        return False

# Cached API functions
@st.cache_data(ttl=600, show_spinner=False)
def search_coin(query):
    try:
        response = requests.get(
            f"https://api.coingecko.com/api/v3/search?query={query}",
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        return {"error": response.status_code, "message": response.text}
    except:
        return {"error": 0, "message": "Connection error"}

@st.cache_data(ttl=120, show_spinner=False)
def get_price(coin_id):
    try:
        response = requests.get(
            f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd&include_24hr_change=true",
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        return {"error": response.status_code, "message": response.text}
    except:
        return {"error": 0, "message": "Connection error"}

def fetch_watchlist_prices():
    """Fetch prices for watchlist with session caching"""
    if not st.session_state.watchlist:
        return {}

    # Check session cache (2 min)
    if (st.session_state.prices_cache and
        time.time() - st.session_state.prices_cache_time < 120):
        return st.session_state.prices_cache

    coin_ids = list(st.session_state.watchlist.keys())
    ids_str = ",".join(coin_ids)

    try:
        response = requests.get(
            f"https://api.coingecko.com/api/v3/simple/price?ids={ids_str}&vs_currencies=usd&include_24hr_change=true",
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            st.session_state.prices_cache = data
            st.session_state.prices_cache_time = time.time()
            return data
    except:
        pass

    return st.session_state.prices_cache

@st.cache_data(ttl=3600, show_spinner=False)
def get_all_coins():
    """Fetch top 50 coins for random selection"""
    try:
        response = requests.get(
            "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=50&page=1",
            timeout=10
        )
        if response.status_code == 200:
            return [c["id"] for c in response.json() if c.get("market_cap")]
    except:
        pass
    return ["bitcoin", "ethereum", "solana", "dogecoin", "cardano", "ripple", "litecoin"]

@st.cache_data(ttl=180, show_spinner=False)
def get_vibe_check(coin_name, price, change_24h, personality, _api_key):
    prompt = f"""The price of {coin_name} is ${price:,.2f} and it has moved {change_24h:.2f}% in 24 hours.

Give me:
1. A vibe rating from 1-10 (1 = doom, 10 = moon)
2. A 2-sentence summary of the vibe in the style of {personality}.

Format exactly like:
RATING: [number]
VIBE: [your 2 sentences]"""

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {_api_key}", "Content-Type": "application/json"},
            json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "max_tokens": 200},
            timeout=15
        )

        if response.status_code == 200:
            content = response.json()["choices"][0]["message"]["content"]
            rating = 5
            vibe = content
            for line in content.strip().split("\n"):
                if line.startswith("RATING:"):
                    try:
                        rating = int(line.replace("RATING:", "").strip().split()[0])
                    except:
                        pass
                elif line.startswith("VIBE:"):
                    vibe = line.replace("VIBE:", "").strip()
            return {"success": True, "message": vibe, "rating": rating}
        return {"success": False, "message": f"Error {response.status_code}", "rating": 0}
    except:
        return {"success": False, "message": "Connection error", "rating": 0}

def get_rating_emoji(rating):
    return {1: "💀", 2: "😱", 3: "😰", 4: "😟", 5: "😐", 6: "🙂", 7: "😊", 8: "😄", 9: "🚀", 10: "🌙"}.get(rating, "😐")

# Fetch watchlist prices once
watched_prices = fetch_watchlist_prices()

# Check for alerts
has_alerts = False
alerting_coins = []
for coin_id, coin_info in st.session_state.watchlist.items():
    if coin_id in watched_prices:
        change = watched_prices[coin_id].get("usd_24h_change", 0)
        if change and abs(change) >= coin_info['threshold']:
            alerting_coins.append(coin_id)
            if coin_id not in st.session_state.acknowledged_alerts:
                has_alerts = True

# Mark alerts as seen
if has_alerts:
    st.session_state.acknowledged_alerts.update(alerting_coins)
st.session_state.acknowledged_alerts &= set(alerting_coins)

# Page config
st.set_page_config(
    page_title="Crypto Vibe Check",
    page_icon="🪙",
    initial_sidebar_state="expanded" if has_alerts else "collapsed"
)

# Modern UI Styling
st.markdown("""
<style>
/* Modern dark theme */
.stApp {
    background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
}

/* Title styling */
h1 {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 800 !important;
    text-align: center;
    padding: 10px 0;
}

/* Subheaders */
h2, h3 {
    color: #a78bfa !important;
}

/* Input styling */
div[data-testid="stTextInput"] input {
    background: linear-gradient(145deg, #1e1e2e, #2a2a3e) !important;
    border: 1px solid #4c4c6d !important;
    border-radius: 12px !important;
    color: #e0e0e0 !important;
    padding: 12px 16px !important;
    font-size: 16px !important;
    transition: all 0.3s ease !important;
}

div[data-testid="stTextInput"] input:focus {
    border-color: #667eea !important;
    box-shadow: 0 0 20px rgba(102, 126, 234, 0.3) !important;
}

/* Button styling */
.stButton > button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    border: none !important;
    border-radius: 12px !important;
    color: white !important;
    font-weight: 600 !important;
    padding: 10px 20px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6) !important;
}

/* Selectbox styling */
div[data-testid="stSelectbox"] > div > div {
    background: linear-gradient(145deg, #1e1e2e, #2a2a3e) !important;
    border: 1px solid #4c4c6d !important;
    border-radius: 12px !important;
}

/* Metric cards */
div[data-testid="stMetric"] {
    background: linear-gradient(145deg, #1e1e2e, #252536) !important;
    border: 1px solid #3d3d5c !important;
    border-radius: 16px !important;
    padding: 20px !important;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3) !important;
}

div[data-testid="stMetric"] label {
    color: #a0a0b0 !important;
}

div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    color: #ffffff !important;
    font-weight: 700 !important;
}

/* Warning/Alert boxes */
div[data-testid="stAlert"] {
    border-radius: 12px !important;
    border: none !important;
}

/* Sidebar styling */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%) !important;
}

section[data-testid="stSidebar"] .stButton > button {
    background: linear-gradient(135deg, #4c4c6d 0%, #3d3d5c 100%) !important;
    box-shadow: none !important;
    padding: 5px 10px !important;
    font-size: 14px !important;
}

/* Divider */
hr {
    border-color: #3d3d5c !important;
}

/* Slider */
div[data-testid="stSlider"] > div > div > div {
    background: #667eea !important;
}

/* Success message */
div.stSuccess {
    background: linear-gradient(135deg, #1a472a 0%, #2d5a3d 100%) !important;
    border-radius: 12px !important;
}

/* Info boxes in sidebar */
div[data-testid="stAlert"] {
    background: linear-gradient(145deg, #1e1e2e, #252536) !important;
}
</style>
""", unsafe_allow_html=True)

st.title("✨ Crypto Vibe Check")

api_key = st.secrets.get("GROQ_API_KEY", "")

# === SIDEBAR ===
st.sidebar.header("Price Alerts")

if st.session_state.watchlist:
    st.sidebar.subheader("Your Watchlist")

    for coin_id, coin_info in list(st.session_state.watchlist.items()):
        change = watched_prices.get(coin_id, {}).get("usd_24h_change", 0) or 0
        is_alerting = abs(change) >= coin_info['threshold'] if change else False
        is_acknowledged = coin_id in st.session_state.acknowledged_alerts

        col1, col2, col3 = st.sidebar.columns([3, 1, 1])

        with col1:
            if is_alerting and not is_acknowledged:
                color = "🟢" if change > 0 else "🔴"
                st.error(f"{color} **{coin_info['symbol']}**: {change:+.2f}%")
            elif is_alerting or st.session_state.editing_threshold == coin_id:
                new_threshold = st.slider(
                    coin_info['symbol'], 1, 50, coin_info['threshold'],
                    key=f"thresh_{coin_id}"
                )
                if new_threshold != coin_info['threshold']:
                    st.session_state.watchlist[coin_id]['threshold'] = new_threshold
                    save_watchlist(st.session_state.watchlist)
            else:
                color = "🟢" if change > 0 else "🔴" if change < 0 else "⚪"
                st.info(f"{color} **{coin_info['symbol']}**: {change:+.2f}%")

        with col2:
            if is_alerting and not is_acknowledged:
                if st.button("✏️", key=f"ack_{coin_id}"):
                    st.session_state.acknowledged_alerts.add(coin_id)
                    st.rerun()
            elif is_alerting:
                if st.button("✓", key=f"done_{coin_id}"):
                    st.session_state.acknowledged_alerts.discard(coin_id)
                    st.rerun()
            elif st.session_state.editing_threshold == coin_id:
                if st.button("✓", key=f"save_{coin_id}"):
                    st.session_state.editing_threshold = None
                    st.rerun()
            else:
                if st.button("⚙️", key=f"edit_{coin_id}"):
                    st.session_state.editing_threshold = coin_id
                    st.rerun()

        with col3:
            if st.button("❌", key=f"del_{coin_id}"):
                del st.session_state.watchlist[coin_id]
                save_watchlist(st.session_state.watchlist)
                st.rerun()

    # Show main alerts
    for coin_id in alerting_coins:
        if coin_id in st.session_state.watchlist:
            info = st.session_state.watchlist[coin_id]
            change = watched_prices.get(coin_id, {}).get("usd_24h_change", 0)
            if change:
                direction = "up" if change > 0 else "down"
                st.warning(f"🚨 **{info['name']}** is {direction} {change:.2f}% in 24h!")
else:
    st.sidebar.info("No coins in watchlist. Search for a coin and add it!")

st.sidebar.divider()

# === MAIN ===
personalities = [
    "A Surfer Dude", "A Grumpy Old Man", "A Wall Street Banker", "A Gen Z Influencer",
    "A Pirate Captain", "Donald Trump", "Donald Duck", "Yoda from Star Wars",
    "Shakespeare", "A Dramatic Soap Opera Narrator", "Gordon Ramsay",
    "A Conspiracy Theorist", "Bob Ross", "Kratos from God of War", "Atreus from God of War"
]
personality = st.selectbox("Choose a vibe personality:", personalities)

# Prison bars CSS overlay for rate limited state
if is_rate_limited():
    st.markdown("""
    <style>
    /* Block all interaction on input container */
    div[data-testid="stTextInput"] {
        position: relative !important;
    }
    /* Invisible blocking overlay */
    div[data-testid="stTextInput"]::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        z-index: 9999;
        cursor: not-allowed;
    }
    /* Prison bars overlay */
    div[data-testid="stTextInput"] > div:last-child {
        position: relative;
    }
    div[data-testid="stTextInput"] > div:last-child::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background:
            repeating-linear-gradient(
                90deg,
                transparent 0px,
                transparent 14px,
                #1a1a2e 14px,
                #2a2a3e 15px,
                #3a3a4e 16px,
                #2a2a3e 17px,
                #1a1a2e 18px,
                transparent 18px
            );
        pointer-events: none;
        z-index: 999;
        border-radius: 12px;
    }
    /* Metallic shine effect */
    div[data-testid="stTextInput"] > div:last-child::after {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background:
            repeating-linear-gradient(
                90deg,
                transparent 0px,
                transparent 14px,
                rgba(100,100,120,0.8) 15px,
                rgba(60,60,80,0.9) 16px,
                rgba(40,40,60,0.95) 17px,
                transparent 18px
            );
        pointer-events: none;
        z-index: 1000;
        border-radius: 12px;
    }
    /* Locked input styling */
    div[data-testid="stTextInput"] input {
        background: linear-gradient(145deg, #0a0a14, #12121e) !important;
        cursor: not-allowed !important;
        color: #2a2a3e !important;
        border: 2px solid #1a1a2e !important;
        box-shadow: inset 0 0 30px rgba(0,0,0,0.9) !important;
        -webkit-user-select: none !important;
        -moz-user-select: none !important;
        -ms-user-select: none !important;
        user-select: none !important;
    }
    div[data-testid="stTextInput"] label {
        color: #3a3a4e !important;
    }
    /* Disabled button */
    button[disabled] {
        opacity: 0.2 !important;
        pointer-events: none !important;
        filter: grayscale(100%) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Search input
col_input, col_random = st.columns([4, 1])
with col_input:
    symbol = st.text_input(
        "Search any cryptocurrency:",
        placeholder="BTC, ETH, dogecoin, shiba-inu, pepe...",
        disabled=is_rate_limited()
    )
with col_random:
    st.write("")
    st.write("")
    if st.button("🎲 Random", disabled=is_rate_limited()):
        coins = get_all_coins()
        st.session_state.selected_coin = random.choice(coins)
        st.rerun()

# Rate limit warning (shown below the text box)
if is_rate_limited():
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #2d1f3d 0%, #1a1a2e 100%);
        border: 1px solid #4c3a6d;
        border-radius: 12px;
        padding: 16px 20px;
        margin: 10px 0;
        display: flex;
        align-items: center;
        gap: 12px;
    ">
        <span style="font-size: 24px;">🔒</span>
        <div>
            <div style="color: #d4a5ff; font-weight: 600; margin-bottom: 4px;">Search limit reached</div>
            <div style="color: #a0a0b0; font-size: 14px;">The search bar has been temporarily imprisoned for excessive curiosity. Please wait while it serves its time...</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    time.sleep(3)  # Wait before checking if free
    if check_api_available():
        clear_rate_limit()
        st.rerun()
    else:
        st.rerun()  # Keep checking

# Use random coin if selected
if "selected_coin" in st.session_state and st.session_state.selected_coin:
    symbol = st.session_state.selected_coin
    del st.session_state.selected_coin

# Search and display
if symbol and not is_rate_limited():
    search_data = search_coin(symbol.lower().strip())

    if "error" in search_data:
        if search_data['error'] == 429:
            set_rate_limit()
            st.rerun()
        else:
            st.error(f"Search error: {search_data.get('message', 'Unknown error')}")
    elif search_data.get("coins"):
        coin = search_data["coins"][0]
        coin_id, coin_name, coin_symbol = coin["id"], coin["name"], coin["symbol"].upper()

        price_data = get_price(coin_id)

        if "error" in price_data:
            if price_data['error'] == 429:
                set_rate_limit()
                st.rerun()
            else:
                st.error(f"Price error: {price_data.get('message', 'Unknown error')}")
        elif coin_id in price_data:
            data = price_data[coin_id]
            price, change_24h = data["usd"], data["usd_24h_change"]

            # Header
            col_title, col_watch = st.columns([4, 1])
            with col_title:
                st.subheader(f"{coin_name} ({coin_symbol})")
            with col_watch:
                if coin_id not in st.session_state.watchlist:
                    if st.button("➕ Watch"):
                        st.session_state.watchlist[coin_id] = {
                            "name": coin_name, "symbol": coin_symbol, "threshold": 10
                        }
                        save_watchlist(st.session_state.watchlist)
                        st.rerun()
                else:
                    st.success("✓ Watching")

            # Metrics
            col1, col2 = st.columns(2)
            col1.metric("Price (USD)", f"${price:,.2f}")
            col2.metric("24h Change", f"{change_24h:.2f}%", delta=f"{change_24h:.2f}%")

            # Vibe check
            if api_key:
                with st.spinner("Getting the vibe..."):
                    result = get_vibe_check(coin_name, price, change_24h, personality, api_key)

                if result["success"]:
                    st.markdown("<br>", unsafe_allow_html=True)

                    # Vibe card
                    rating = result['rating']
                    emoji = get_rating_emoji(rating)

                    # Color based on rating
                    if rating <= 3:
                        vibe_color = "#ff6b6b"
                        vibe_bg = "linear-gradient(135deg, #2d1f1f 0%, #1a1a2e 100%)"
                    elif rating <= 6:
                        vibe_color = "#ffd93d"
                        vibe_bg = "linear-gradient(135deg, #2d2a1f 0%, #1a1a2e 100%)"
                    else:
                        vibe_color = "#6bcb77"
                        vibe_bg = "linear-gradient(135deg, #1f2d1f 0%, #1a1a2e 100%)"

                    st.markdown(f"""
                    <div style="
                        background: {vibe_bg};
                        border: 1px solid #3d3d5c;
                        border-radius: 16px;
                        padding: 24px;
                        margin: 10px 0;
                    ">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                            <span style="color: #a78bfa; font-size: 20px; font-weight: 600;">The Vibe</span>
                            <div style="
                                background: linear-gradient(135deg, #1e1e2e, #2a2a3e);
                                border-radius: 12px;
                                padding: 8px 16px;
                                display: flex;
                                align-items: center;
                                gap: 8px;
                            ">
                                <span style="font-size: 28px;">{emoji}</span>
                                <span style="color: {vibe_color}; font-size: 24px; font-weight: 700;">{rating}/10</span>
                            </div>
                        </div>
                        <p style="color: #e0e0e0; font-size: 16px; line-height: 1.6; margin: 0;">{result["message"]}</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error(f"Vibe error: {result['message']}")
            else:
                st.error("Add GROQ_API_KEY to .streamlit/secrets.toml")
        else:
            st.error(f"No price data for {coin_name}")
    else:
        st.warning(f"Couldn't find '{symbol}'. Try a different search term.")
