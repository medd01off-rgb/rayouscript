import base64
import datetime
from decimal import Decimal
import urllib.parse
import streamlit as st
import streamlit.components.v1 as components

# Page Configuration
st.set_page_config(
    page_title="Rayou Systems | Verification Engine",
    page_icon=None,
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Session State Initialization for Daily Usage Limit Tracking (Max 5 per day)
today_date = datetime.date.today()
if (
    "usage_date" not in st.session_state
    or st.session_state["usage_date"] != today_date
):
    st.session_state["usage_date"] = today_date
    st.session_state["usage_count"] = 0

MAX_DAILY_LIMIT = 5

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

    /* Header Container (GitHub Card Style with Gold Accent & Top-Right Logo) */
    .header-container {
        position: relative;
        text-align: center;
        padding: 30px 20px;
        background-color: #161b22;
        border: 1px solid #30363d;
        border-top: 3px solid #c5a059;
        border-radius: 6px;
        margin-bottom: 25px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }

    .header-wa-icon {
        position: absolute;
        top: 14px;
        right: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        text-decoration: none;
        transition: transform 0.2s ease-in-out;
    }

    .header-wa-icon:hover {
        transform: scale(1.1);
    }

    .brand-title {
        font-size: 28px;
        font-weight: 700;
        letter-spacing: 3px;
        color: #c5a059;
        text-transform: uppercase;
        margin: 0;
    }

    .brand-subtitle {
        font-size: 13px;
        letter-spacing: 1.5px;
        color: #8b949e;
        margin-top: 6px;
    }

    /* Input Field Styling (GitHub Dark Input) */
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
        margin-bottom: 12px;
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


# Interface Header with Gold WhatsApp Icon Cutout at Top-Right
st.markdown(
    """
    <div class="header-container">
        <a href="https://wa.me/212760402682" target="_blank" class="header-wa-icon" title="WhatsApp Contact">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="12" r="12" fill="#c5a059"/>
                <path fill-rule="evenodd" clip-rule="evenodd" d="M12 3.5C7.306 3.5 3.5 7.306 3.5 12C3.5 13.688 3.993 15.26 4.843 16.582L3.8 20.4L7.712 19.375C8.988 20.147 10.45 20.5 12 20.5C16.694 20.5 20.5 16.694 20.5 12C20.5 7.306 16.694 3.5 12 3.5ZM9.08 8.182C8.941 8.182 8.718 8.234 8.528 8.442C8.337 8.65 7.8 9.153 7.8 10.177C7.8 11.201 8.546 12.19 8.65 12.329C8.754 12.468 10.12 14.576 12.215 15.48C13.957 16.232 14.312 16.082 14.694 16.047C15.076 16.012 15.908 15.556 16.082 15.07C16.255 14.584 16.255 14.167 16.203 14.08C16.151 13.993 16.012 13.941 15.804 13.837C15.595 13.733 14.57 13.229 14.379 13.16C14.188 13.09 14.049 13.056 13.91 13.264C13.771 13.472 13.372 13.941 13.25 14.08C13.129 14.219 13.007 14.236 12.799 14.132C12.59 14.028 11.918 13.808 11.121 13.098C10.499 12.544 10.079 11.86 9.958 11.651C9.836 11.443 9.945 11.33 10.05 11.226C10.144 11.133 10.258 10.984 10.362 10.862C10.466 10.74 10.5 10.653 10.57 10.515C10.639 10.376 10.605 10.255 10.553 10.151C10.501 10.047 10.084 9.04 9.911 8.623C9.742 8.217 9.57 8.24 9.444 8.234C9.323 8.228 9.184 8.182 9.08 8.182Z" fill="#161b22"/>
            </svg>
        </a>
        <div class="brand-title">Rayou Script</div>
        <div class="brand-subtitle">Secured Verification Protocol | بروتوكول التحقق المشفر</div>
    </div>
""",
    unsafe_allow_html=True,
)

# Execution Counter Check
remaining_executions = MAX_DAILY_LIMIT - st.session_state["usage_count"]

if remaining_executions > 0:
    st.markdown(
        f'<div class="usage-tracker">Daily Executions Remaining: <b>{remaining_executions}/{MAX_DAILY_LIMIT}</b> | المحاولات المتبقية اليوم: <b>{remaining_executions}/{MAX_DAILY_LIMIT}</b></div>',
        unsafe_allow_html=True,
    )

    decimal_entry = st.text_input(
        "DECIMAL INPUT VECTOR | أدخل الرقم العشري",
        placeholder="34.7313",
        help="Enter the decimal sequence | أدخل التسلسل العشري",
    )

    if st.button(
        "GENERATE AUTHORIZATION CODE | توليد كود التفعيل",
        use_container_width=True,
    ):
        sanitized_val = decimal_entry.strip()
        if "." in sanitized_val:
            try:
                authorization_token = _execute_cipher(sanitized_val)
                st.session_state["usage_count"] += 1

                # Display Generated Authorization Code
                st.markdown(
                    f"""
                    <div class="result-container">
                        <div class="result-label">Authorization Token | كود التفعيل الخاص بك</div>
                        <div class="result-code">{authorization_token}</div>
                    </div>
                """,
                    unsafe_allow_html=True,
                )

                # Dedicated Clipboard Copy Button Component
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
                    navigator.clipboard.writeText('{authorization_token}');
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

            except Exception:
                st.error(
                    "Processing Error: Invalid entry vector | خطأ في المعالجة: يرجى التأكد من إدخال رقم عشري صحيح."
                )
        else:
            st.warning(
                "Format Requirement: The input must include a decimal point | صيغة غير صحيحة: يجب أن يحتوي الرقم على فاصلة."
            )
else:
    # Display Threshold Exceeded Card with Dual-Language Pre-filled WhatsApp Message
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
