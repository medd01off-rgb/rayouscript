import base64
import datetime
from decimal import Decimal
import urllib.parse
import streamlit as st
import streamlit.components.v1 as components
from upstash_redis import Redis

# Page Configuration
st.set_page_config(
    page_title="Rayou Systems | Verification Engine",
    page_icon=None,
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Connect to Upstash Redis Database using provided credentials
UPSTASH_URL = "https://enabling-dane-155670.upstash.io"
UPSTASH_TOKEN = (
    "gQAAAAAAAmAWAAIgcDI5Yzc5ZjZlZTEzZWE0ZWVmYjc3OWM1ZWMyYTQyYWQyMw"
)

redis = Redis(url=UPSTASH_URL, token=UPSTASH_TOKEN)

MAX_DAILY_LIMIT = 5
today_date_str = str(datetime.date.today())


# Get Client IP Address from Streamlit context
def get_client_ip() -> str:
    try:
        if hasattr(st, "context") and hasattr(st.context, "headers"):
            headers = st.context.headers
            if "X-Forwarded-For" in headers:
                return headers["X-Forwarded-For"].split(",")[0].strip()
            if "x-forwarded-for" in headers:
                return headers["x-forwarded-for"].split(",")[0].strip()
    except Exception:
        pass
    return "default_user_ip"


client_ip = get_client_ip()
redis_key = f"usage:{today_date_str}:{client_ip}"


# Helper functions to query and increment IP execution counters in Upstash Redis
def get_ip_usage(key: str) -> int:
    try:
        val = redis.get(key)
        if val is not None:
            return int(val)
    except Exception:
        pass
    return st.session_state.get("fallback_usage", 0)


def increment_ip_usage(key: str) -> int:
    try:
        new_val = redis.incr(key)
        return int(new_val)
    except Exception:
        pass
    st.session_state["fallback_usage"] = (
        st.session_state.get("fallback_usage", 0) + 1
    )
    return st.session_state["fallback_usage"]


# Read current usage count directly from Upstash Redis
current_usage = get_ip_usage(redis_key)

# GitHub Dark Theme Palette & Typography (Jost + Cairo)
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&family=Jost:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"], .stApp, *, input, button, select, textarea {
        font-family: 'Jost', 'Cairo', sans-serif !important;
    }

    /* GitHub Dark Canvas Background */
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }

    /* Header Container Style */
    .header-container {
        position: relative;
        text-align: center;
        padding: 35px 20px 25px 20px;
        background-color: #161b22;
        border: 1px solid #c5a059;
        border-radius: 8px;
        margin-top: 15px;
        margin-bottom: 25px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }

    /* WhatsApp Gold Badge attached to Top-Right Corner */
    .header-wa-badge {
        position: absolute;
        top: -18px;
        right: -18px;
        width: 44px;
        height: 44px;
        background-color: #c5a059;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
        z-index: 100;
        text-decoration: none;
        transition: transform 0.2s ease-in-out;
    }

    .header-wa-badge:hover {
        transform: scale(1.1);
    }

    .brand-title {
        font-size: 32px;
        font-weight: 700;
        letter-spacing: 4px;
        color: #c5a059;
        text-transform: uppercase;
        margin: 0;
    }

    .brand-subtitle-en {
        font-size: 14px;
        letter-spacing: 1.5px;
        color: #8b949e;
        margin-top: 10px;
    }

    .brand-subtitle-ar {
        font-size: 14px;
        color: #8b949e;
        margin-top: 4px;
    }

    /* Centered Input Label */
    .input-label-centered {
        text-align: center;
        font-size: 13px;
        font-weight: 600;
        letter-spacing: 2px;
        color: #8b949e;
        margin-bottom: 8px;
        text-transform: uppercase;
    }

    /* Input Field Styling */
    .stTextInput > div > div > input {
        background-color: #0d1117 !important;
        color: #c5a059 !important;
        border: 1px solid #30363d !important;
        border-radius: 6px !important;
        text-align: center;
        font-size: 18px !important;
        letter-spacing: 2.5px;
        padding: 10px 14px !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: #c5a059 !important;
        box-shadow: 0 0 0 3px rgba(197, 160, 89, 0.2) !important;
    }

    /* Primary Execution Button */
    .stButton > button {
        background: linear-gradient(180deg, #c5a059 0%, #a3813e 100%) !important;
        color: #0d1117 !important;
        font-weight: 700 !important;
        font-size: 13px !important;
        letter-spacing: 2px !important;
        text-transform: uppercase !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 12px 24px !important;
        width: 100%;
        transition: all 0.2s ease-in-out;
        margin-top: 8px;
    }

    .stButton > button:hover {
        background: linear-gradient(180deg, #d4af37 0%, #b59247 100%) !important;
        box-shadow: 0 4px 12px rgba(197, 160, 89, 0.3) !important;
        color: #0d1117 !important;
    }

    /* Output Result Box */
    .result-container {
        text-align: center;
        padding: 22px;
        margin-top: 22px;
        background-color: #161b22;
        border: 1px solid #30363d;
        border-left: 4px solid #c5a059;
        border-right: 4px solid #c5a059;
        border-radius: 6px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }

    .result-label {
        font-size: 12px;
        letter-spacing: 1.5px;
        color: #8b949e;
        text-transform: uppercase;
    }

    .result-code {
        font-size: 40px;
        font-weight: 700;
        color: #c5a059;
        letter-spacing: 6px;
        margin-top: 4px;
    }

    /* Daily Execution Counter Display */
    .usage-tracker {
        text-align: center;
        font-size: 12px;
        letter-spacing: 1px;
        color: #8b949e;
        margin-bottom: 16px;
        line-height: 1.6;
    }

    /* Limit Threshold Exceeded Notice */
    .limit-container {
        text-align: center;
        padding: 30px 20px;
        margin-top: 22px;
        background-color: #161b22;
        border: 1px solid #30363d;
        border-top: 3px solid #f85149;
        border-radius: 6px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }

    .limit-title-en {
        font-size: 16px;
        font-weight: 700;
        color: #f85149;
        letter-spacing: 1.5px;
        text-transform: uppercase;
    }

    .limit-title-ar {
        font-size: 15px;
        font-weight: 600;
        color: #f85149;
        margin-top: 4px;
        margin-bottom: 15px;
    }

    .limit-desc {
        font-size: 13px;
        color: #8b949e;
        margin-bottom: 22px;
        line-height: 1.7;
    }

    .wa-link-button {
        display: inline-block;
        background: linear-gradient(180deg, #c5a059 0%, #a3813e 100%);
        color: #0d1117 !important;
        text-decoration: none;
        font-weight: 700;
        font-size: 13px;
        letter-spacing: 1.5px;
        padding: 10px 24px;
        border-radius: 6px;
        line-height: 1.5;
        transition: all 0.2s ease-in-out;
    }

    .wa-link-button:hover {
        background: linear-gradient(180deg, #d4af37 0%, #b59247 100%);
        box-shadow: 0 4px 12px rgba(197, 160, 89, 0.3);
    }

    /* Footer Section (English Only) */
    .footer-container {
        margin-top: 50px;
        padding-top: 20px;
        border-top: 1px solid #21262d;
        text-align: center;
        font-size: 12px;
        color: #8b949e;
        letter-spacing: 1px;
        line-height: 1.8;
    }

    .footer-highlight {
        color: #c5a059;
        font-weight: 600;
    }
    </style>
""",
    unsafe_allow_html=True,
)


# Obfuscated Core Cipher Protocol
def _execute_cipher(decimal_input: str) -> str:
    key_base = base64.b64decode(b"NDg=").decode("utf-8")
    int_part, frac_part = decimal_input.strip().split(".", 1)
    multiplier = Decimal(f"{key_base}.{int_part}")
    total_value = Decimal(frac_part) * multiplier
    return str(int(total_value)).zfill(4)[-4:]


# Interface Header
st.markdown(
    """
    <div class="header-container">
        <a href="https://wa.me/212760402682" target="_blank" class="header-wa-badge" title="WhatsApp Contact">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="#161b22">
                <path d="M12 2C6.48 2 2 6.48 2 12c0 1.82.49 3.53 1.35 5L2 22l5.12-1.32C8.51 21.52 10.2 22 12 22c5.52 0 10-4.48 10-10S17.52 2 12 2zm0 18c-1.57 0-3.04-.42-4.32-1.16l-.31-.18-3.21.83.84-3.13-.2-.32C4.04 14.95 3.6 13.51 3.6 12c0-4.63 3.77-8.4 8.4-8.4s8.4 3.77 8.4 8.4-3.77 8.4-8.4-8.4zm4.61-6.28c-.25-.13-1.49-.74-1.72-.82-.23-.08-.4-.13-.57.13-.17.25-.66.82-.81.99-.15.17-.3.19-.55.06-.25-.13-1.07-.39-2.04-1.25-.76-.67-1.27-1.5-1.42-1.75-.15-.25-.02-.39.11-.51.11-.11.25-.29.38-.44.13-.15.17-.25.25-.42.08-.17.04-.32-.02-.44-.06-.13-.57-1.37-.78-1.87-.2-.49-.41-.42-.57-.43h-.49c-.17 0-.44.06-.67.31-.23.25-.88.86-.88 2.1 0 1.24.9 2.44 1.03 2.61.13.17 1.77 2.71 4.29 3.8.6.26 1.07.41 1.44.53.6.19 1.15.16 1.59.1.48-.07 1.49-.61 1.7-.19.21-.58.21-.98.15-1.05-.06-.07-.23-.13-.48-.26z"/>
            </svg>
        </a>
        <div class="brand-title">RAYOU SCRIPT</div>
        <div class="brand-subtitle-en">Secured Verification Protocol</div>
        <div class="brand-subtitle-ar">بروتوكول التحقق المشفر</div>
    </div>
""",
    unsafe_allow_html=True,
)

remaining_executions = MAX_DAILY_LIMIT - current_usage

if remaining_executions > 0:
    st.markdown(
        f"""
        <div class="usage-tracker">
            <div>Daily Executions Remaining: <b>{remaining_executions}/{MAX_DAILY_LIMIT}</b></div>
            <div>المحاولات المتبقية اليوم: <b>{remaining_executions}/{MAX_DAILY_LIMIT}</b></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="input-label-centered">DECIMAL INPUT VECTOR</div>',
        unsafe_allow_html=True,
    )

    decimal_entry = st.text_input(
        "",
        placeholder="34.7313",
        help="Enter the decimal sequence | أدخل التسلسل العشري",
        label_visibility="collapsed",
    )

    if st.button(
        "GENERATE AUTHORIZATION CODE | توليد كود التفعيل",
        use_container_width=True,
    ):
        sanitized_val = decimal_entry.strip()
        if "." in sanitized_val:
            try:
                authorization_token = _execute_cipher(sanitized_val)

                # Increment IP count directly in Upstash Redis database
                increment_ip_usage(redis_key)

                st.session_state["generated_token"] = authorization_token
            except Exception:
                st.error(
                    "Processing Error: Invalid entry vector | خطأ في المعالجة: يرجى التأكد من إدخال رقم عشري صحيح."
                )
        else:
            st.warning(
                "Format Requirement: The input must include a decimal point | صيغة غير صحيحة: يجب أن يحتوي الرقم على فاصلة."
            )

    # Display Generated Authorization Code
    if "generated_token" in st.session_state:
        token_val = st.session_state["generated_token"]
        st.markdown(
            f"""
            <div class="result-container">
                <div class="result-label">Authorization Token | كود التفعيل الخاص بك</div>
                <div class="result-code">{token_val}</div>
            </div>
        """,
            unsafe_allow_html=True,
        )

        copy_component_html = f"""
        <div style="text-align: center; margin-top: 14px;">
            <button id="copyBtn" onclick="copyToClipboard()" style="
                background: transparent;
                color: #c5a059;
                border: 1px solid #c5a059;
                padding: 10px 22px;
                font-family: 'Jost', 'Cairo', sans-serif;
                font-size: 12px;
                font-weight: 600;
                letter-spacing: 1.5px;
                border-radius: 6px;
                cursor: pointer;
                transition: all 0.2s ease-in-out;
            ">COPY AUTHORIZATION CODE | نسخ كود التفعيل</button>
        </div>
        <script>
        function copyToClipboard() {{
            navigator.clipboard.writeText('{token_val}');
            var button = document.getElementById('copyBtn');
            button.innerText = 'COPIED TO CLIPBOARD | تم النسخ بنجاح';
            button.style.background = '#c5a059';
            button.style.color = '#0d1117';
            setTimeout(function() {{
                button.innerText = 'COPY AUTHORIZATION CODE | نسخ كود التفعيل';
                button.style.background = 'transparent';
                button.style.color = '#c5a059';
            }}, 2000);
        }}
        </script>
        """
        components.html(copy_component_html, height=60)

else:
    wa_msg_text = (
        "Hello Rayou Script, I would like to subscribe for unlimited access.\n"
        "مرحباً رايو سكريبت، أود الاشتراك للحصول على وصول غير محدود."
    )
    encoded_wa_msg = urllib.parse.quote(wa_msg_text)
    whatsapp_subscription_url = (
        f"https://wa.me/212760402682?text={encoded_wa_msg}"
    )

    st.markdown(
        f"""
        <div class="limit-container">
            <div class="limit-title-en">Script Execution Limit Reached</div>
            <div class="limit-title-ar">تم الوصول للحد الأقصى اليومي</div>
            <div class="limit-desc">
                The maximum limit of {MAX_DAILY_LIMIT} daily executions has been reached.<br>
                For unlimited operational access, please contact administration to activate your subscription.<br><br>
                تم الوصول إلى الحد الأقصى لعدد عمليات الإعدام اليومية وهو {MAX_DAILY_LIMIT} عمليات.<br>
                للحصول على استخدام غير محدود، يرجى التواصل مع الإدارة لتفعيل الاشتراك الكامل.
            </div>
            <a href="{whatsapp_subscription_url}" target="_blank" class="wa-link-button">
                Subscribe via WhatsApp<br>
                <span style="font-size: 12px; font-weight: 600; letter-spacing: 0;">الاشتراك عبر الواتساب</span>
            </a>
        </div>
    """,
        unsafe_allow_html=True,
    )

# Confidential System Notice (Sidebar)
st.sidebar.markdown("### Authorization Notice")
st.sidebar.markdown(
    """
**System:** Rayou Core Protocol  
**Classification:** Proprietary & Restricted  
**Developer:** Rayou  
**Direct WhatsApp:**  
`+212 7 60 40 26 82`
"""
)

# Footer Section (English Only)
st.markdown(
    """
    <div class="footer-container">
        Engineered under <span class="footer-highlight">Rayou Script Systems</span> | All Rights Reserved<br>
        Official Inquiries: <span class="footer-highlight">+212 7 60 40 26 82</span>
    </div>
""",
    unsafe_allow_html=True,
)
v>Daily Executions Remaining: <b>{remaining_executions}/{MAX_DAILY_LIMIT}</b></div>
            <div>المحاولات المتبقية اليوم: <b>{remaining_executions}/{MAX_DAILY_LIMIT}</b></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="input-label-centered">DECIMAL INPUT VECTOR</div>',
        unsafe_allow_html=True,
    )

    decimal_entry = st.text_input(
        "",
        placeholder="34.7313",
        help="Enter the decimal sequence | أدخل التسلسل العشري",
        label_visibility="collapsed",
    )

    if st.button(
        "GENERATE AUTHORIZATION CODE | توليد كود التفعيل",
        use_container_width=True,
    ):
        sanitized_val = decimal_entry.strip()
        if "." in sanitized_val:
            try:
                authorization_token = _execute_cipher(sanitized_val)

                # Increment IP count on global server memory
                new_usage = increment_ip_usage(client_ip, today_date_str)

                # Store generated token in session state so it NEVER disappears
                st.session_state["generated_token"] = authorization_token
            except Exception:
                st.error(
                    "Processing Error: Invalid entry vector | خطأ في المعالجة: يرجى التأكد من إدخال رقم عشري صحيح."
                )
        else:
            st.warning(
                "Format Requirement: The input must include a decimal point | صيغة غير صحيحة: يجب أن يحتوي الرقم على فاصلة."
            )

    # Persistent Display of Generated Code
    if "generated_token" in st.session_state:
        token_val = st.session_state["generated_token"]
        st.markdown(
            f"""
            <div class="result-container">
                <div class="result-label">Authorization Token | كود التفعيل الخاص بك</div>
                <div class="result-code">{token_val}</div>
            </div>
        """,
            unsafe_allow_html=True,
        )

        copy_component_html = f"""
        <div style="text-align: center; margin-top: 14px;">
            <button id="copyBtn" onclick="copyToClipboard()" style="
                background: transparent;
                color: #c5a059;
                border: 1px solid #c5a059;
                padding: 10px 22px;
                font-family: 'Jost', 'Cairo', sans-serif;
                font-size: 12px;
                font-weight: 600;
                letter-spacing: 1.5px;
                border-radius: 6px;
                cursor: pointer;
                transition: all 0.2s ease-in-out;
            ">COPY AUTHORIZATION CODE | نسخ كود التفعيل</button>
        </div>
        <script>
        function copyToClipboard() {{
            navigator.clipboard.writeText('{token_val}');
            var button = document.getElementById('copyBtn');
            button.innerText = 'COPIED TO CLIPBOARD | تم النسخ بنجاح';
            button.style.background = '#c5a059';
            button.style.color = '#0d1117';
            setTimeout(function() {{
                button.innerText = 'COPY AUTHORIZATION CODE | نسخ كود التفعيل';
                button.style.background = 'transparent';
                button.style.color = '#c5a059';
            }}, 2000);
        }}
        </script>
        """
        components.html(copy_component_html, height=60)

else:
    wa_msg_text = (
        "Hello Rayou Script, I would like to subscribe for unlimited access.\n"
        "مرحباً رايو سكريبت، أود الاشتراك للحصول على وصول غير محدود."
    )
    encoded_wa_msg = urllib.parse.quote(wa_msg_text)
    whatsapp_subscription_url = (
        f"https://wa.me/212760402682?text={encoded_wa_msg}"
    )

    st.markdown(
        f"""
        <div class="limit-container">
            <div class="limit-title-en">Script Execution Limit Reached</div>
            <div class="limit-title-ar">تم الوصول للحد الأقصى اليومي</div>
            <div class="limit-desc">
                The maximum limit of {MAX_DAILY_LIMIT} daily executions has been reached.<br>
                For unlimited operational access, please contact administration to activate your subscription.<br><br>
                تم الوصول إلى الحد الأقصى لعدد عمليات الإعدام اليومية وهو {MAX_DAILY_LIMIT} عمليات.<br>
                للحصول على استخدام غير محدود، يرجى التواصل مع الإدارة لتفعيل الاشتراك الكامل.
            </div>
            <a href="{whatsapp_subscription_url}" target="_blank" class="wa-link-button">
                Subscribe via WhatsApp<br>
                <span style="font-size: 12px; font-weight: 600; letter-spacing: 0;">الاشتراك عبر الواتساب</span>
            </a>
        </div>
    """,
        unsafe_allow_html=True,
    )

# Confidential System Notice (Sidebar)
st.sidebar.markdown("### Authorization Notice")
st.sidebar.markdown(
    """
**System:** Rayou Core Protocol  
**Classification:** Proprietary & Restricted  
**Developer:** Rayou  
**Direct WhatsApp:**  
`+212 7 60 40 26 82`
"""
)

# Footer Section (English Only)
st.markdown(
    """
    <div class="footer-container">
        Engineered under <span class="footer-highlight">Rayou Script Systems</span> | All Rights Reserved<br>
        Official Inquiries: <span class="footer-highlight">+212 7 60 40 26 82</span>
    </div>
""",
    unsafe_allow_html=True,
)
