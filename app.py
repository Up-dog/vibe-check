import streamlit as st
import requests
import time
import random
import json
import os
from datetime import datetime, timedelta
import pandas as pd
import plotly.graph_objects as go

# File paths
WATCHLIST_FILE = os.path.join(os.path.dirname(__file__), "watchlist.json")
SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "settings.json")

# Translations
TRANSLATIONS = {
    "en": {
        "title": "Crypto Vibe Check",
        "search_placeholder": "BTC, ETH, Dogecoin, Solana...",
        "search_label": "Search any cryptocurrency:",
        "random_btn": "Random",
        "watch_btn": "Watch",
        "watching": "Watching",
        "personality_label": "Choose a vibe personality or type your own:",
        "personality_placeholder": "e.g., A wise monk, Tony Stark, Your grandma...",
        "price_label": "Price (USD)",
        "change_label": "24h Change",
        "the_vibe": "The Vibe",
        "getting_vibe": "Getting the vibe...",
        "price_alerts": "Price Alerts",
        "your_watchlist": "Your Watchlist",
        "no_watchlist": "No coins in watchlist. Search for a coin and add it!",
        "search_limit": "Search limit reached",
        "search_limit_msg": "The search bar has been temporarily imprisoned for excessive curiosity. Please wait while it serves its time...",
        "alert_title": "Price Alert!",
        "alert_threshold_hit": "has hit your alert threshold!",
        "current_change": "Current 24h Change",
        "your_threshold": "Your Threshold",
        "price_history": "Price History (7 Days)",
        "dismiss": "Dismiss",
        "language_title": "Welcome! Select Your Language",
        "language_subtitle": "Choose your preferred language to continue",
        "continue_btn": "Continue",
        "not_found": "Couldn't find '{symbol}'. Try a different search term.",
        "up": "up",
        "down": "down",
        "trending": "Trending Now",
        "market_overview": "Market Overview",
        "total_market_cap": "Total Market Cap",
        "btc_dominance": "BTC Dominance",
        "active_coins": "Active Cryptocurrencies",
        "top_coins": "Top Coins",
        "quick_pick": "Quick Pick"
    },
    "es": {
        "title": "Crypto Vibe Check",
        "search_placeholder": "BTC, ETH, Dogecoin, Solana...",
        "search_label": "Buscar criptomoneda:",
        "random_btn": "Aleatorio",
        "watch_btn": "Seguir",
        "watching": "Siguiendo",
        "personality_label": "Elige una personalidad o escribe la tuya:",
        "personality_placeholder": "ej., Un monje sabio, Tony Stark, Tu abuela...",
        "price_label": "Precio (USD)",
        "change_label": "Cambio 24h",
        "the_vibe": "La Vibra",
        "getting_vibe": "Obteniendo la vibra...",
        "price_alerts": "Alertas de Precio",
        "your_watchlist": "Tu Lista",
        "no_watchlist": "No hay monedas en la lista. Busca una moneda y agrégala!",
        "search_limit": "Límite de búsqueda alcanzado",
        "search_limit_msg": "La barra de búsqueda ha sido encarcelada temporalmente por curiosidad excesiva. Espera mientras cumple su condena...",
        "trending": "Tendencias",
        "market_overview": "Resumen del Mercado",
        "total_market_cap": "Cap. de Mercado Total",
        "btc_dominance": "Dominancia BTC",
        "active_coins": "Criptomonedas Activas",
        "top_coins": "Top Monedas",
        "quick_pick": "Selección Rápida",
        "alert_title": "¡Alerta de Precio!",
        "alert_threshold_hit": "ha alcanzado tu umbral de alerta!",
        "current_change": "Cambio Actual 24h",
        "your_threshold": "Tu Umbral",
        "price_history": "Historial de Precio (7 Días)",
        "dismiss": "Cerrar",
        "language_title": "¡Bienvenido! Selecciona Tu Idioma",
        "language_subtitle": "Elige tu idioma preferido para continuar",
        "continue_btn": "Continuar",
        "not_found": "No se encontró '{symbol}'. Intenta con otro término.",
        "up": "subió",
        "down": "bajó"
    },
    "fr": {
        "title": "Crypto Vibe Check",
        "search_placeholder": "BTC, ETH, Dogecoin, Solana...",
        "search_label": "Rechercher une crypto:",
        "random_btn": "Aléatoire",
        "watch_btn": "Suivre",
        "watching": "Suivi",
        "personality_label": "Choisissez une personnalité ou écrivez la vôtre:",
        "personality_placeholder": "ex., Un moine sage, Tony Stark, Ta grand-mère...",
        "price_label": "Prix (USD)",
        "change_label": "Variation 24h",
        "the_vibe": "L'Ambiance",
        "getting_vibe": "Analyse en cours...",
        "price_alerts": "Alertes de Prix",
        "your_watchlist": "Votre Liste",
        "no_watchlist": "Aucune crypto dans la liste. Cherchez une crypto et ajoutez-la!",
        "search_limit": "Limite de recherche atteinte",
        "search_limit_msg": "La barre de recherche a été temporairement emprisonnée pour curiosité excessive. Veuillez patienter...",
        "alert_title": "Alerte de Prix!",
        "alert_threshold_hit": "a atteint votre seuil d'alerte!",
        "current_change": "Variation Actuelle 24h",
        "your_threshold": "Votre Seuil",
        "price_history": "Historique des Prix (7 Jours)",
        "dismiss": "Fermer",
        "language_title": "Bienvenue! Sélectionnez Votre Langue",
        "language_subtitle": "Choisissez votre langue préférée pour continuer",
        "continue_btn": "Continuer",
        "not_found": "'{symbol}' introuvable. Essayez un autre terme.",
        "up": "en hausse",
        "down": "en baisse",
        "trending": "Tendances",
        "market_overview": "Aperçu du Marché",
        "total_market_cap": "Cap. Marché Totale",
        "btc_dominance": "Dominance BTC",
        "active_coins": "Cryptos Actives",
        "top_coins": "Top Cryptos",
        "quick_pick": "Sélection Rapide"
    },
    "de": {
        "title": "Crypto Vibe Check",
        "search_placeholder": "BTC, ETH, Dogecoin, Solana...",
        "search_label": "Kryptowährung suchen:",
        "random_btn": "Zufällig",
        "watch_btn": "Folgen",
        "watching": "Folge",
        "personality_label": "Wähle eine Persönlichkeit oder schreibe deine eigene:",
        "personality_placeholder": "z.B., Ein weiser Mönch, Tony Stark, Deine Oma...",
        "price_label": "Preis (USD)",
        "change_label": "24h Änderung",
        "the_vibe": "Die Stimmung",
        "getting_vibe": "Stimmung wird ermittelt...",
        "price_alerts": "Preisalarme",
        "your_watchlist": "Deine Liste",
        "no_watchlist": "Keine Coins in der Liste. Suche nach einem Coin und füge ihn hinzu!",
        "search_limit": "Suchlimit erreicht",
        "search_limit_msg": "Die Suchleiste wurde vorübergehend wegen übermäßiger Neugier eingesperrt. Bitte warten...",
        "alert_title": "Preisalarm!",
        "alert_threshold_hit": "hat deinen Alarmschwellenwert erreicht!",
        "current_change": "Aktuelle 24h Änderung",
        "your_threshold": "Dein Schwellenwert",
        "price_history": "Preisverlauf (7 Tage)",
        "dismiss": "Schließen",
        "language_title": "Willkommen! Wähle Deine Sprache",
        "language_subtitle": "Wähle deine bevorzugte Sprache zum Fortfahren",
        "continue_btn": "Weiter",
        "not_found": "'{symbol}' nicht gefunden. Versuche einen anderen Begriff.",
        "up": "gestiegen",
        "down": "gefallen",
        "trending": "Im Trend",
        "market_overview": "Marktübersicht",
        "total_market_cap": "Gesamte Marktkapitalisierung",
        "btc_dominance": "BTC Dominanz",
        "active_coins": "Aktive Kryptos",
        "top_coins": "Top Coins",
        "quick_pick": "Schnellauswahl"
    },
    "ja": {
        "title": "Crypto Vibe Check",
        "search_placeholder": "BTC, ETH, Dogecoin, Solana...",
        "search_label": "暗号通貨を検索:",
        "random_btn": "ランダム",
        "watch_btn": "追加",
        "watching": "追跡中",
        "personality_label": "パーソナリティを選択または入力:",
        "personality_placeholder": "例: 賢い僧侶、トニー・スターク、おばあちゃん...",
        "price_label": "価格 (USD)",
        "change_label": "24時間変動",
        "the_vibe": "バイブ",
        "getting_vibe": "バイブを取得中...",
        "price_alerts": "価格アラート",
        "your_watchlist": "ウォッチリスト",
        "no_watchlist": "リストにコインがありません。コインを検索して追加してください！",
        "search_limit": "検索制限に達しました",
        "search_limit_msg": "検索バーは過度の好奇心のため一時的に投獄されました。しばらくお待ちください...",
        "alert_title": "価格アラート！",
        "alert_threshold_hit": "がアラートしきい値に達しました！",
        "current_change": "現在の24時間変動",
        "your_threshold": "しきい値",
        "price_history": "価格履歴（7日間）",
        "dismiss": "閉じる",
        "language_title": "ようこそ！言語を選択してください",
        "language_subtitle": "続行するには、ご希望の言語を選択してください",
        "continue_btn": "続ける",
        "not_found": "'{symbol}'が見つかりませんでした。別の用語をお試しください。",
        "up": "上昇",
        "down": "下落",
        "trending": "トレンド",
        "market_overview": "市場概要",
        "total_market_cap": "時価総額",
        "btc_dominance": "BTC支配率",
        "active_coins": "アクティブな暗号通貨",
        "top_coins": "トップコイン",
        "quick_pick": "クイックピック"
    },
    "zh": {
        "title": "Crypto Vibe Check",
        "search_placeholder": "BTC, ETH, Dogecoin, Solana...",
        "search_label": "搜索加密货币:",
        "random_btn": "随机",
        "watch_btn": "关注",
        "watching": "已关注",
        "personality_label": "选择或输入个性:",
        "personality_placeholder": "例如: 智慧的僧侣、托尼·史塔克、你的奶奶...",
        "price_label": "价格 (USD)",
        "change_label": "24小时变化",
        "the_vibe": "氛围",
        "getting_vibe": "获取氛围中...",
        "price_alerts": "价格提醒",
        "your_watchlist": "关注列表",
        "no_watchlist": "列表中没有币种。搜索并添加一个币种！",
        "search_limit": "达到搜索限制",
        "search_limit_msg": "搜索栏因过度好奇而被暂时监禁。请稍候...",
        "alert_title": "价格提醒！",
        "alert_threshold_hit": "已达到您的提醒阈值！",
        "current_change": "当前24小时变化",
        "your_threshold": "您的阈值",
        "price_history": "价格历史（7天）",
        "dismiss": "关闭",
        "language_title": "欢迎！选择您的语言",
        "language_subtitle": "选择您的首选语言以继续",
        "continue_btn": "继续",
        "not_found": "找不到'{symbol}'。请尝试其他搜索词。",
        "up": "上涨",
        "down": "下跌",
        "trending": "热门趋势",
        "market_overview": "市场概览",
        "total_market_cap": "总市值",
        "btc_dominance": "BTC主导地位",
        "active_coins": "活跃加密货币",
        "top_coins": "热门币种",
        "quick_pick": "快速选择"
    }
}

LANGUAGE_OPTIONS = {
    "en": "English",
    "es": "Español",
    "fr": "Français",
    "de": "Deutsch",
    "ja": "日本語",
    "zh": "中文"
}

# Top 50 coins with correct CoinGecko IDs
TOP_50_COINS = [
    "bitcoin", "ethereum", "tether", "xrp", "bnb", "solana", "usdc", "dogecoin",
    "cardano", "tron", "avalanche-2", "chainlink", "shiba-inu", "polkadot",
    "bitcoin-cash", "sui", "stellar", "hedera-hashgraph", "toncoin", "litecoin",
    "uniswap", "hyperliquid", "pepe", "near", "dai", "ethena-usde", "internet-computer",
    "aptos", "aave", "crypto-com-chain", "polygon-ecosystem-token", "render-token",
    "ethereum-classic", "monero", "vechain", "mantle", "bittensor", "filecoin",
    "arbitrum", "okb", "cosmos", "fetch-ai", "injective-protocol", "kaspa",
    "theta-token", "optimism", "immutable-x", "bonk", "fantom", "algorand"
]

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

def load_settings():
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
    except:
        pass
    return {}

def save_settings(settings):
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f)
    except:
        pass

def t(key):
    """Get translation for current language"""
    lang = st.session_state.get("language", "en")
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, key)

# Initialize session state
if "watchlist" not in st.session_state:
    st.session_state.watchlist = load_watchlist()
if "settings" not in st.session_state:
    st.session_state.settings = load_settings()
if "language" not in st.session_state:
    st.session_state.language = st.session_state.settings.get("language", None)
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
if "popup_alerts" not in st.session_state:
    st.session_state.popup_alerts = []
if "dismissed_popups" not in st.session_state:
    st.session_state.dismissed_popups = set()
if "first_load" not in st.session_state:
    st.session_state.first_load = True

# Rate limit functions
def is_rate_limited():
    return st.session_state.rate_limit_until > 0

def set_rate_limit():
    st.session_state.rate_limit_until = time.time()

def clear_rate_limit():
    st.session_state.rate_limit_until = 0

def check_api_available():
    try:
        response = requests.get("https://api.coingecko.com/api/v3/ping", timeout=5)
        return response.status_code == 200
    except:
        return False

# Cached API functions
@st.cache_data(ttl=600, show_spinner=False)
def search_coin(query):
    try:
        response = requests.get(f"https://api.coingecko.com/api/v3/search?query={query}", timeout=10)
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

@st.cache_data(ttl=300, show_spinner=False)
def get_coin_chart(coin_id, days=7):
    """Get price history for chart"""
    try:
        response = requests.get(
            f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days={days}",
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            prices = data.get("prices", [])
            return [(datetime.fromtimestamp(p[0]/1000), p[1]) for p in prices]
        return []
    except:
        return []

@st.cache_data(ttl=300, show_spinner=False)
def get_trending_coins():
    """Get trending coins from CoinGecko"""
    try:
        response = requests.get(
            "https://api.coingecko.com/api/v3/search/trending",
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("coins", [])[:7]
        return []
    except:
        return []

@st.cache_data(ttl=300, show_spinner=False)
def get_global_market_data():
    """Get global crypto market data"""
    try:
        response = requests.get(
            "https://api.coingecko.com/api/v3/global",
            timeout=10
        )
        if response.status_code == 200:
            return response.json().get("data", {})
        return {}
    except:
        return {}

@st.cache_data(ttl=120, show_spinner=False)
def get_top_coins_data():
    """Get top 6 coins with price data for homepage"""
    try:
        response = requests.get(
            "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=6&page=1&sparkline=false",
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

def fetch_watchlist_prices():
    if not st.session_state.watchlist:
        return {}

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

@st.cache_data(ttl=180, show_spinner=False)
def get_vibe_check(coin_name, price, change_24h, personality, _api_key, language):
    lang_instruction = ""
    if language != "en":
        lang_names = {"es": "Spanish", "fr": "French", "de": "German", "ja": "Japanese", "zh": "Chinese"}
        lang_instruction = f"\n\nIMPORTANT: Write your response in {lang_names.get(language, 'English')}."

    # Handle default personality differently
    if personality == "Default (Just the facts)":
        style_instruction = "Give a straightforward, factual 2-sentence summary of the market sentiment."
    else:
        style_instruction = f"Give a 2-sentence summary of the vibe in the style of {personality}."

    prompt = f"""The price of {coin_name} is ${price:,.2f} and it has moved {change_24h:.2f}% in 24 hours.

Give me:
1. A vibe rating from 1-10 (1 = doom, 10 = moon)
2. {style_instruction}

Format exactly like:
RATING: [number]
VIBE: [your 2 sentences]{lang_instruction}"""

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {_api_key}", "Content-Type": "application/json"},
            json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "max_tokens": 300},
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

# Page config - must be first Streamlit command
st.set_page_config(
    page_title="Crypto Vibe Check",
    page_icon="🪙",
    initial_sidebar_state="collapsed"
)

# Check if language is set - show language selector first
if st.session_state.language is None:
    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #0a0a0f 0%, #1a0a2e 50%, #0f1a2e 100%);
    }
    * {
        -webkit-user-select: none !important;
        -moz-user-select: none !important;
        -ms-user-select: none !important;
        user-select: none !important;
    }
    .language-card {
        background: linear-gradient(145deg, #1a1a2e, #252540);
        border: 2px solid #3d3d6d;
        border-radius: 20px;
        padding: 40px;
        text-align: center;
        max-width: 500px;
        margin: 100px auto;
        box-shadow: 0 20px 60px rgba(0, 255, 255, 0.1), 0 0 40px rgba(255, 0, 255, 0.1);
    }
    .language-title {
        font-size: 28px;
        font-weight: 700;
        background: linear-gradient(90deg, #00ffff, #ff00ff, #00ffff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
    }
    .language-subtitle {
        color: #8080a0;
        font-size: 16px;
        margin-bottom: 30px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="language-card">
        <div class="language-title">Welcome! Select Your Language</div>
        <div class="language-subtitle">Choose your preferred language to continue</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        selected_lang = st.selectbox(
            "Language",
            options=list(LANGUAGE_OPTIONS.keys()),
            format_func=lambda x: LANGUAGE_OPTIONS[x],
            label_visibility="collapsed"
        )

        if st.button("Continue →"):
            st.session_state.language = selected_lang
            st.session_state.settings["language"] = selected_lang
            save_settings(st.session_state.settings)
            st.rerun()

    st.stop()

# Fetch watchlist prices
watched_prices = fetch_watchlist_prices()

# Check for alerts and prepare popups on first load
if st.session_state.first_load:
    for coin_id, coin_info in st.session_state.watchlist.items():
        if coin_id in watched_prices:
            change = watched_prices[coin_id].get("usd_24h_change", 0)
            if change and abs(change) >= coin_info['threshold']:
                if coin_id not in st.session_state.dismissed_popups:
                    st.session_state.popup_alerts.append({
                        "coin_id": coin_id,
                        "name": coin_info["name"],
                        "symbol": coin_info["symbol"],
                        "change": change,
                        "threshold": coin_info["threshold"],
                        "price": watched_prices[coin_id].get("usd", 0)
                    })
    st.session_state.first_load = False

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

if has_alerts:
    st.session_state.acknowledged_alerts.update(alerting_coins)
st.session_state.acknowledged_alerts &= set(alerting_coins)

# Cyberpunk Neon Theme CSS
st.markdown("""
<style>
/* Global no-select */
* {
    -webkit-user-select: none !important;
    -moz-user-select: none !important;
    -ms-user-select: none !important;
    user-select: none !important;
}

/* Cyberpunk dark theme */
.stApp {
    background: linear-gradient(135deg, #0a0a0f 0%, #1a0a2e 50%, #0f1a2e 100%);
}

/* Animated background glow */
.stApp::before {
    content: "";
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background:
        radial-gradient(ellipse at 20% 20%, rgba(0, 255, 255, 0.03) 0%, transparent 50%),
        radial-gradient(ellipse at 80% 80%, rgba(255, 0, 255, 0.03) 0%, transparent 50%);
    pointer-events: none;
    z-index: 0;
}

/* Title styling - Neon glow */
h1 {
    background: linear-gradient(90deg, #00ffff 0%, #ff00ff 50%, #00ffff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 800 !important;
    text-align: center;
    padding: 10px 0;
    animation: neonPulse 2s ease-in-out infinite alternate;
}

@keyframes neonPulse {
    from { filter: brightness(1); }
    to { filter: brightness(1.2); }
}

/* Subheaders */
h2, h3, h4 {
    color: #00ffff !important;
    text-shadow: 0 0 10px rgba(0, 255, 255, 0.3);
}

/* Input styling - Neon border */
div[data-testid="stTextInput"] input {
    background: rgba(10, 10, 20, 0.8) !important;
    border: 1px solid #00ffff !important;
    border-radius: 12px !important;
    color: #e0e0e0 !important;
    padding: 12px 16px !important;
    font-size: 16px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 0 10px rgba(0, 255, 255, 0.2), inset 0 0 10px rgba(0, 0, 0, 0.5) !important;
}

div[data-testid="stTextInput"] input:focus {
    border-color: #ff00ff !important;
    box-shadow: 0 0 20px rgba(255, 0, 255, 0.4), inset 0 0 10px rgba(0, 0, 0, 0.5) !important;
}

/* Button styling - Neon gradient */
.stButton > button {
    background: linear-gradient(135deg, #00ffff 0%, #ff00ff 100%) !important;
    border: none !important;
    border-radius: 12px !important;
    color: #0a0a0f !important;
    font-weight: 700 !important;
    padding: 10px 20px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 20px rgba(0, 255, 255, 0.3), 0 4px 20px rgba(255, 0, 255, 0.3) !important;
}

.stButton > button:hover {
    transform: translateY(-2px) scale(1.02) !important;
    box-shadow: 0 6px 30px rgba(0, 255, 255, 0.5), 0 6px 30px rgba(255, 0, 255, 0.5) !important;
}

/* Selectbox styling */
div[data-testid="stSelectbox"] > div > div {
    background: rgba(10, 10, 20, 0.8) !important;
    border: 1px solid #3d3d6d !important;
    border-radius: 12px !important;
}

/* Metric cards - Glassmorphism */
div[data-testid="stMetric"] {
    background: rgba(20, 20, 40, 0.6) !important;
    border: 1px solid rgba(0, 255, 255, 0.3) !important;
    border-radius: 16px !important;
    padding: 20px !important;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3), inset 0 0 20px rgba(0, 255, 255, 0.05) !important;
    backdrop-filter: blur(10px) !important;
}

div[data-testid="stMetric"] label {
    color: #00ffff !important;
}

div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    color: #ffffff !important;
    font-weight: 700 !important;
    text-shadow: 0 0 10px rgba(255, 255, 255, 0.3);
}

/* Alert boxes */
div[data-testid="stAlert"] {
    border-radius: 12px !important;
    border: 1px solid rgba(255, 0, 255, 0.3) !important;
    background: rgba(20, 10, 30, 0.8) !important;
}

/* Sidebar styling */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a0a15 0%, #1a0a2e 100%) !important;
    border-right: 1px solid rgba(0, 255, 255, 0.2) !important;
}

section[data-testid="stSidebar"] .stButton > button {
    background: linear-gradient(135deg, #2a2a4d 0%, #1a1a3d 100%) !important;
    border: 1px solid rgba(0, 255, 255, 0.3) !important;
    box-shadow: none !important;
    padding: 5px 10px !important;
    font-size: 14px !important;
    color: #00ffff !important;
}

/* Divider */
hr {
    border-color: rgba(0, 255, 255, 0.2) !important;
}

/* Slider */
div[data-testid="stSlider"] > div > div > div {
    background: linear-gradient(90deg, #00ffff, #ff00ff) !important;
}

/* Labels */
label {
    color: #8080a0 !important;
}

/* Links */
a {
    color: #00ffff !important;
    text-decoration: none !important;
}
a:hover {
    color: #ff00ff !important;
}

/* Line chart */
.stLineChart {
    background: rgba(10, 10, 20, 0.5) !important;
    border-radius: 12px !important;
}
</style>
""", unsafe_allow_html=True)

# Show alert popups
if st.session_state.popup_alerts:
    alert = st.session_state.popup_alerts[0]
    coin_id = alert["coin_id"]

    change_color = "#00ff88" if alert["change"] > 0 else "#ff0066"
    change_symbol = "+" if alert["change"] > 0 else ""

    # Alert container
    st.markdown("---")

    # Header with dismiss button
    col_title, col_close = st.columns([6, 1])
    with col_title:
        st.markdown(f"## 🚨 {t('alert_title')}")
    with col_close:
        if st.button("✕", key=f"dismiss_{coin_id}", help=t("dismiss")):
            st.session_state.popup_alerts.pop(0)
            st.session_state.dismissed_popups.add(coin_id)
            st.rerun()

    # Coin name with CoinGecko link
    st.markdown(f"### {alert['name']} ({alert['symbol']})")
    st.caption(f"{alert['name']} {t('alert_threshold_hit')}")

    # CoinGecko link
    st.markdown(f"🔗 [View on CoinGecko](https://www.coingecko.com/en/coins/{coin_id})")

    # Stats in columns
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            t("current_change"),
            f"{change_symbol}{alert['change']:.2f}%",
            delta=f"{change_symbol}{alert['change']:.2f}%"
        )
    with col2:
        st.metric(t("your_threshold"), f"±{alert['threshold']}%")
    with col3:
        st.metric(t("price_label"), f"${alert['price']:,.2f}")

    # AI Vibe Summary
    api_key = st.secrets.get("GROQ_API_KEY", "")
    if api_key:
        st.markdown(f"#### {t('the_vibe')}")
        with st.spinner(t("getting_vibe")):
            vibe_result = get_vibe_check(
                alert['name'],
                alert['price'],
                alert['change'],
                "A Financial News Anchor",
                api_key,
                st.session_state.language
            )

        if vibe_result["success"]:
            rating = vibe_result['rating']
            emoji = get_rating_emoji(rating)

            if rating <= 3:
                vibe_color = "#ff0066"
            elif rating <= 6:
                vibe_color = "#ffff00"
            else:
                vibe_color = "#00ff88"

            col_emoji, col_msg = st.columns([1, 5])
            with col_emoji:
                st.markdown(f"<div style='font-size: 48px; text-align: center;'>{emoji}</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='text-align: center; color: {vibe_color}; font-weight: bold;'>{rating}/10</div>", unsafe_allow_html=True)
            with col_msg:
                st.info(vibe_result["message"])

    # Interactive Chart
    st.markdown(f"#### {t('price_history')}")

    # Load data for chart (365 days for zoom out capability)
    chart_data = get_coin_chart(coin_id, 365)
    if chart_data:
        df = pd.DataFrame(chart_data, columns=["Date", "Price"])

        # Calculate initial range (last 7 days)
        now = datetime.now()
        seven_days_ago = now - timedelta(days=7)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["Date"],
            y=df["Price"],
            mode='lines',
            name='Price',
            line=dict(color='#00ffff', width=2),
            fill='tozeroy',
            fillcolor='rgba(0, 255, 255, 0.1)'
        ))

        fig.update_layout(
            plot_bgcolor='#0a0a14',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#ffffff',
            xaxis=dict(
                gridcolor='#1a1a2e',
                range=[seven_days_ago, now],
                rangeslider=dict(visible=True, thickness=0.1),
                rangeselector=dict(
                    buttons=[
                        dict(count=7, label="7D", step="day", stepmode="backward"),
                        dict(count=30, label="30D", step="day", stepmode="backward"),
                        dict(count=90, label="90D", step="day", stepmode="backward"),
                        dict(count=1, label="1Y", step="year", stepmode="backward"),
                        dict(step="all", label="ALL")
                    ],
                    bgcolor='#1a1a2e',
                    activecolor='#ff00ff',
                    font=dict(color='#fff', size=11),
                    x=0,
                    y=1.15
                )
            ),
            yaxis=dict(gridcolor='#1a1a2e', tickprefix='$'),
            margin=dict(l=50, r=20, t=60, b=20),
            height=350,
            hovermode='x unified'
        )

        st.plotly_chart(fig, key=f"popup_chart_{coin_id}")
    else:
        st.info("📊 Chart data unavailable")

    # Quick Actions
    st.markdown("#### Quick Actions")
    col_search, col_remove, col_dismiss = st.columns(3)

    with col_search:
        if st.button("🔍 Search This Coin", key=f"search_{coin_id}"):
            st.session_state.selected_coin = coin_id
            st.session_state.popup_alerts.pop(0)
            st.session_state.dismissed_popups.add(coin_id)
            st.rerun()

    with col_remove:
        if st.button("🗑️ Remove from Watchlist", key=f"remove_{coin_id}"):
            if coin_id in st.session_state.watchlist:
                del st.session_state.watchlist[coin_id]
                save_watchlist(st.session_state.watchlist)
            st.session_state.popup_alerts.pop(0)
            st.session_state.dismissed_popups.add(coin_id)
            st.rerun()

    with col_dismiss:
        if st.button(f"✕ {t('dismiss')}", key=f"dismiss_bottom_{coin_id}"):
            st.session_state.popup_alerts.pop(0)
            st.session_state.dismissed_popups.add(coin_id)
            st.rerun()

    st.stop()

st.title(f"✨ {t('title')}")

api_key = st.secrets.get("GROQ_API_KEY", "")

# === SIDEBAR ===
st.sidebar.header(t("price_alerts"))

if st.session_state.watchlist:
    st.sidebar.subheader(t("your_watchlist"))

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

    for coin_id in alerting_coins:
        if coin_id in st.session_state.watchlist:
            info = st.session_state.watchlist[coin_id]
            change = watched_prices.get(coin_id, {}).get("usd_24h_change", 0)
            if change:
                direction = t("up") if change > 0 else t("down")
                st.warning(f"🚨 **{info['name']}** {direction} {abs(change):.2f}%!")
else:
    st.sidebar.info(t("no_watchlist"))

st.sidebar.divider()

# === MAIN ===
preset_personalities = [
    "Default (Just the facts)",
    "A Surfer Dude", "A Grumpy Old Man", "A Wall Street Banker", "A Gen Z Influencer",
    "A Pirate Captain", "Donald Trump", "Donald Duck", "Yoda from Star Wars",
    "Shakespeare", "A Dramatic Soap Opera Narrator", "Gordon Ramsay",
    "A Conspiracy Theorist", "Bob Ross", "Kratos from God of War", "Atreus from God of War",
    "✏️ Custom..."
]

selected_personality = st.selectbox(t("personality_label"), preset_personalities)

if selected_personality == "✏️ Custom...":
    personality = st.text_input(
        "Enter your custom personality:",
        placeholder=t("personality_placeholder")
    )
    if not personality:
        personality = "Default (Just the facts)"
else:
    personality = selected_personality

# Prison bars CSS overlay for rate limited state
if is_rate_limited():
    st.markdown("""
    <style>
    div[data-testid="stTextInput"]:first-of-type + div + div div[data-testid="stTextInput"] {
        position: relative !important;
    }
    div[data-testid="stTextInput"]:first-of-type + div + div div[data-testid="stTextInput"]::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        z-index: 9999;
        cursor: not-allowed;
    }
    div[data-testid="stTextInput"]:first-of-type + div + div div[data-testid="stTextInput"] > div:last-child::before {
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
                #0a0a15 14px,
                #1a1a30 15px,
                #2a2a45 16px,
                #1a1a30 17px,
                #0a0a15 18px,
                transparent 18px
            );
        pointer-events: none;
        z-index: 999;
        border-radius: 12px;
    }
    div[data-testid="stTextInput"]:first-of-type + div + div div[data-testid="stTextInput"] > div:last-child::after {
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
                rgba(0, 255, 255, 0.3) 15px,
                rgba(255, 0, 255, 0.2) 16px,
                rgba(0, 255, 255, 0.1) 17px,
                transparent 18px
            );
        pointer-events: none;
        z-index: 1000;
        border-radius: 12px;
    }
    div[data-testid="stTextInput"]:first-of-type + div + div div[data-testid="stTextInput"] input {
        background: rgba(5, 5, 10, 0.9) !important;
        cursor: not-allowed !important;
        color: #1a1a30 !important;
        border: 2px solid #1a0a2e !important;
        box-shadow: inset 0 0 30px rgba(0,0,0,0.9) !important;
    }
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
        t("search_label"),
        placeholder=t("search_placeholder"),
        disabled=is_rate_limited(),
        key="search_input"
    )
with col_random:
    st.write("")
    st.write("")
    if st.button(f"🎲 {t('random_btn')}", disabled=is_rate_limited()):
        st.session_state.selected_coin = random.choice(TOP_50_COINS)
        st.rerun()

# Rate limit warning
if is_rate_limited():
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #2d0a3d 0%, #1a0a2e 100%);
        border: 1px solid #ff00ff;
        border-radius: 12px;
        padding: 16px 20px;
        margin: 10px 0;
        display: flex;
        align-items: center;
        gap: 12px;
        box-shadow: 0 0 20px rgba(255, 0, 255, 0.2);
    ">
        <span style="font-size: 24px;">🔒</span>
        <div>
            <div style="color: #ff00ff; font-weight: 600; margin-bottom: 4px;">{t("search_limit")}</div>
            <div style="color: #a0a0b0; font-size: 14px;">{t("search_limit_msg")}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    time.sleep(3)
    if check_api_available():
        clear_rate_limit()
        st.rerun()
    else:
        st.rerun()

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

            col_title, col_watch = st.columns([4, 1])
            with col_title:
                st.subheader(f"{coin_name} ({coin_symbol})")
            with col_watch:
                if coin_id not in st.session_state.watchlist:
                    if st.button(f"➕ {t('watch_btn')}"):
                        st.session_state.watchlist[coin_id] = {
                            "name": coin_name, "symbol": coin_symbol, "threshold": 10
                        }
                        save_watchlist(st.session_state.watchlist)
                        st.rerun()
                else:
                    st.success(f"✓ {t('watching')}")

            col1, col2 = st.columns(2)
            col1.metric(t("price_label"), f"${price:,.2f}")
            col2.metric(t("change_label"), f"{change_24h:.2f}%", delta=f"{change_24h:.2f}%")

            if api_key:
                with st.spinner(t("getting_vibe")):
                    result = get_vibe_check(coin_name, price, change_24h, personality, api_key, st.session_state.language)

                if result["success"]:
                    st.markdown("<br>", unsafe_allow_html=True)

                    rating = result['rating']
                    emoji = get_rating_emoji(rating)

                    if rating <= 3:
                        vibe_color = "#ff0066"
                        vibe_glow = "rgba(255, 0, 102, 0.3)"
                        vibe_bg = "linear-gradient(135deg, #2d0a1a 0%, #1a0a2e 100%)"
                    elif rating <= 6:
                        vibe_color = "#ffff00"
                        vibe_glow = "rgba(255, 255, 0, 0.3)"
                        vibe_bg = "linear-gradient(135deg, #2d2d0a 0%, #1a0a2e 100%)"
                    else:
                        vibe_color = "#00ff88"
                        vibe_glow = "rgba(0, 255, 136, 0.3)"
                        vibe_bg = "linear-gradient(135deg, #0a2d1a 0%, #1a0a2e 100%)"

                    st.markdown(f"""
                    <div style="
                        background: {vibe_bg};
                        border: 1px solid {vibe_color};
                        border-radius: 16px;
                        padding: 24px;
                        margin: 10px 0;
                        box-shadow: 0 0 30px {vibe_glow};
                    ">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                            <span style="color: #00ffff; font-size: 20px; font-weight: 600; text-shadow: 0 0 10px rgba(0, 255, 255, 0.5);">{t("the_vibe")}</span>
                            <div style="
                                background: rgba(10, 10, 20, 0.8);
                                border: 1px solid {vibe_color};
                                border-radius: 12px;
                                padding: 8px 16px;
                                display: flex;
                                align-items: center;
                                gap: 8px;
                                box-shadow: 0 0 15px {vibe_glow};
                            ">
                                <span style="font-size: 28px;">{emoji}</span>
                                <span style="color: {vibe_color}; font-size: 24px; font-weight: 700; text-shadow: 0 0 10px {vibe_glow};">{rating}/10</span>
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
        st.warning(t("not_found").format(symbol=symbol))

# Home page content when no search
elif not is_rate_limited():
    # Floating coins animation
    st.markdown("""
    <style>
    @keyframes float {
        0%, 100% { transform: translateY(0) rotate(0deg); opacity: 0.6; }
        50% { transform: translateY(-20px) rotate(10deg); opacity: 1; }
    }
    @keyframes floatSlow {
        0%, 100% { transform: translateY(0) rotate(0deg); opacity: 0.4; }
        50% { transform: translateY(-30px) rotate(-10deg); opacity: 0.8; }
    }
    @keyframes floatFast {
        0%, 100% { transform: translateY(0) rotate(5deg); opacity: 0.5; }
        50% { transform: translateY(-15px) rotate(-5deg); opacity: 0.9; }
    }
    .floating-coins {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        pointer-events: none;
        z-index: 0;
        overflow: hidden;
    }
    .coin {
        position: absolute;
        font-size: 24px;
        opacity: 0.5;
    }
    .coin:nth-child(1) { top: 15%; left: 10%; animation: float 4s ease-in-out infinite; }
    .coin:nth-child(2) { top: 25%; right: 15%; animation: floatSlow 5s ease-in-out infinite 0.5s; }
    .coin:nth-child(3) { top: 45%; left: 5%; animation: floatFast 3s ease-in-out infinite 1s; }
    .coin:nth-child(4) { top: 60%; right: 8%; animation: float 4.5s ease-in-out infinite 1.5s; }
    .coin:nth-child(5) { top: 75%; left: 12%; animation: floatSlow 5.5s ease-in-out infinite 0.3s; }
    .coin:nth-child(6) { top: 35%; right: 5%; animation: floatFast 3.5s ease-in-out infinite 0.8s; }
    .coin:nth-child(7) { top: 85%; right: 20%; animation: float 4s ease-in-out infinite 1.2s; }
    .coin:nth-child(8) { top: 10%; left: 25%; animation: floatSlow 6s ease-in-out infinite 0.7s; }
    .coin:nth-child(9) { top: 55%; left: 20%; animation: floatFast 3.2s ease-in-out infinite 1.8s; }
    .coin:nth-child(10) { top: 70%; right: 25%; animation: float 4.8s ease-in-out infinite 0.4s; }
    </style>
    <div class="floating-coins">
        <span class="coin">🪙</span>
        <span class="coin">💰</span>
        <span class="coin">₿</span>
        <span class="coin">🪙</span>
        <span class="coin">💎</span>
        <span class="coin">🚀</span>
        <span class="coin">💰</span>
        <span class="coin">₿</span>
        <span class="coin">🪙</span>
        <span class="coin">💎</span>
    </div>
    """, unsafe_allow_html=True)

    # Trending row
    st.markdown(f"#### 🔥 {t('trending')}")
    trending = get_trending_coins()
    if trending:
        cols = st.columns(7)
        for i, item in enumerate(trending[:7]):
            coin = item.get("item", {})
            with cols[i]:
                if st.button(
                    coin.get('symbol', '').upper(),
                    key=f"trend_{coin.get('id')}",
                    help=f"#{coin.get('market_cap_rank', '?')} {coin.get('name', '')}"
                ):
                    st.session_state.selected_coin = coin.get('id')
                    st.rerun()
