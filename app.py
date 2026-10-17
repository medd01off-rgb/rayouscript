import base64
import datetime
from decimal import Decimal
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

# Global Typography (Jost for Latin & Cairo for Arabic) & Luxury Dark Aesthetics
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&family=Jost:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"], .stApp, *, input, button, select, textarea {
        font-family: 'Jost', 'Cairo', sans-serif !important;
    }

    .stApp {
        background-color: #0b1325;
        color: #e6edf3;
    }

    /* Header Container */
    .header-container {
        text-align: center;
        padding: 35px 25px;
        background: linear-gradient(145deg, #0d1b34 0%, #162a4a 100%);
        border: 1px solid #c5a059;
        border-radius: 4px;
        margin-bottom: 25px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
    }

    .brand-title {
        font-size: 32px;
        font-weight: 700;
        letter-spacing: 3px;
        color: #c5a059;
        text-transform: uppercase;
        margin: 0;
    }

    .brand-subtitle {
        font-size: 13px;
        letter-spacing: 2px;
        color: #8a99ad;
        margin-top: 8px;
    }

    /* Input Field Styling */
    .stTextInput > div > div > input {
        background-color: #112038 !important;
        color: #c5a059 !important;
        border: 1px solid #2a3d5c !important;
        border-radius: 4px !important;
        text-align: center;
        font-size: 20px !important;
        letter-spacing: 3px;
        padding: 12px !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: #c5a059 !important;
        box-shadow: 0 0 8px rgba(197, 160, 89, 0.3) !important;
    }

    /* Primary Execution Button */
    .stButton > button {
        background: linear-gradient(180deg, #c5a059 0%, #a3813e 100%) !important;
        color: #0b1325 !important;
        font-weight: 700 !important;
        font-size: 13px !important;
        letter-spacing: 2px !important;
        text-transform: uppercase !important;
        border: none !important;
        border-radius: 4px !important;
        padding: 14px 28px !important;
        width: 100%;
        transition: all 0.3s ease;
        margin-top: 10px;
    }

    .stButton > button:hover {
        background: linear-gradient(180deg, #d4af37 0%, #b59247 100%) !important;
        box-shadow: 0 4px 15px rgba(197, 160, 89, 0.4) !important;
        color: #0b1325 !important;
    }

    /* Output Result Box */
    .result-container {
        text-align: center;
        padding: 25px;
        margin-top: 25px;
        background-color: #112038;
        border-left: 3px solid #c5a059;
        border-right: 3px solid #c5a059;
        border-radius: 2px;
        box-shadow: 0 5px 20px rgba(0, 0, 0, 0.25);
    }

    .result-label {
        font-size: 12px;
        letter-spacing: 2px;
        color: #8a99ad;
        text-transform: uppercase;
    }

    .result-code {
        font-size: 44px;
        font-weight: 700;
        color: #c5a059;
        letter-spacing: 8px;
        margin-top: 5px;
    }

    /* Daily Execution Counter Display */
    .usage-tracker {
        text-align: center;
        font-size: 12px;
        letter-spacing: 1.5px;
        color: #8a99ad;
        margin-bottom: 12px;
    }

    /* Limit Threshold Exceeded Notice */
    .limit-container {
        text-align: center;
        padding: 35px 25px;
        margin-top: 25px;
        background-color: #111d33;
        border: 1px solid #7a2b3a;
        border-radius: 4px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
    }

    .limit-title {
        font-size: 16px;
        font-weight: 700;
        color: #e57373;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 12px;
    }

    .limit-desc {
        font-size: 13px;
        color: #a3b1c6;
        margin-bottom: 25px;
        line-height: 1.8;
    }

    .wa-link-button {
        display: inline-block;
        background: linear-gradient(180deg, #c5a059 0%, #a3813e 100%);
        color: #0b1325 !important;
        text-decoration: none;
        font-weight: 700;
        font-size: 13px;
        letter-spacing: 2px;
        padding: 14px 28px;
        border-radius: 4px;
        transition: all 0.3s ease;
    }

    .wa-link-button:hover {
        background: linear-gradient(180deg, #d4af37 0%, #b59247 100%);
        box-shadow: 0 4px 15px rgba(197, 160, 89, 0.4);
    }

    /* Footer Section */
    .footer-container {
        margin-top: 60px;
        padding-top: 25px;
        border-top: 1px solid #1a2d4a;
        text-align: center;
        font-size: 12px;
        color: #728197;
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
                        <div class="result-label">Authorization Token | كود التفعيل الخـاص بك</div>
                        <div class="result-code">{authorization_token}</div>
                    </div>
                """,
                    unsafe_allow_html=True,
                )

                # Dedicated Clipboard Copy Button Component
                copy_component_html = f"""
                <div style="text-align: center; margin-top: 15px;">
                    <button id="copyBtn" onclick="copyToClipboard()" style="
                        background: transparent;
                        color: #c5a059;
                        border: 1px solid #c5a059;
                        padding: 11px 26px;
                        font-family: 'Jost', 'Cairo', sans-serif;
                        font-size: 12px;
                        font-weight: 600;
                        letter-spacing: 1.5px;
                        border-radius: 4px;
                        cursor: pointer;
                        transition: all 0.3s ease;
                    ">COPY AUTHORIZATION CODE | نسخ كود التفعيل</button>
                </div>
                <script>
                function copyToClipboard() {{
                    navigator.clipboard.writeText('{authorization_token}');
                    var button = document.getElementById('copyBtn');
                    button.innerText = 'COPIED TO CLIPBOARD | تم النسخ بنجاح';
                    button.style.background = '#c5a059';
                    button.style.color = '#0b1325';
                    setTimeout(function() {{
                        button.innerText = 'COPY AUTHORIZATION CODE | نسخ كود التفعيل';
                        button.style.background = 'transparent';
                        button.style.color = '#c5a059';
                    }}, 2000);
                }}
                </script>
                """
                components.html(copy_component_html, height=65)

            except Exception:
                st.error(
                    "Processing Error: Invalid entry vector | خطأ في المعالجة: يرجى التأكد من إدخال رقم عشري صحيح."
                )
        else:
            st.warning(
                "Format Requirement: The input must include a decimal point | صيغة غير صحيحة: يجب أن يحتوي الرقم على فاصلة."
            )
else:
    # Display Threshold Exceeded Card
    whatsapp_subscription_url = "https://wa.me/212760402682?text=Hello%20Rayou%20Script%2C%20I%20would%20like%20to%20subscribe%20for%20unlimited%20access."
    st.markdown(
        f"""
        <div class="limit-container">
            <div class="limit-title">Script Execution Limit Reached | تم الوصول للحد الأقصى اليومي</div>
            <div class="limit-desc">
                The maximum limit of {MAX_DAILY_LIMIT} daily executions has been reached.<br>
                For unlimited operational access, please contact administration to activate your subscription.<br><br>
                لقد وصلت للحد الأقصى المسموح به <b>({MAX_DAILY_LIMIT} محاولات يومياً)</b>.<br>
                للحصول على استخدام غير محدود، يرجى التواصل مع الإدارة لتفعيل الاشتراك الكامل.
            </div>
            <a href="{whatsapp_subscription_url}" target="_blank" class="wa-link-button">Subscribe via WhatsApp | الاشتراك عبر الواتساب</a>
        </div>
    """,
        unsafe_allow_html=True,
    )

# Confidential System Notice (Sidebar)
st.sidebar.markdown("### Authorization Notice | معلومات النظام")
st.sidebar.markdown(
    """
**System / النظام:** Rayou Core Protocol  
**Classification / التصنيف:** Proprietary & Restricted  
**Developer / المطور:** Rayou  
**Direct WhatsApp / التواصل المباشر:**  
`+212 7 60 40 26 82`
"""
)

# Footer Section
st.markdown(
    """
    <div class="footer-container">
        Engineered under <span class="footer-highlight">Rayou Script Systems</span> | جميع الحقوق محفوظة لـ سكريبت رايو<br>
        Official Inquiries / للاستفسارات الرسمية: <span class="footer-highlight">+212 7 60 40 26 82</span>
    </div>
""",
    unsafe_allow_html=True,
)
