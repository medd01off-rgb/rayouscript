import base64
from decimal import Decimal
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Rayou Systems | Verification Engine",
    page_icon=None,
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Custom Styling for Luxury & Diplomatic Aesthetic
st.markdown(
    """
    <style>
    /* Main Page Background & Typography */
    .stApp {
        background-color: #0b1325;
        color: #e6edf3;
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    }
    
    /* Header Card */
    .header-container {
        text-align: center;
        padding: 35px 25px;
        background: linear-gradient(145deg, #0d1b34 0%, #162a4a 100%);
        border: 1px solid #c5a059;
        border-radius: 4px;
        margin-bottom: 35px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
    }
    
    .brand-title {
        font-family: 'Georgia', 'Times New Roman', serif;
        font-size: 30px;
        font-weight: 700;
        letter-spacing: 4px;
        color: #c5a059;
        text-transform: uppercase;
        margin: 0;
    }
    
    .brand-subtitle {
        font-size: 12px;
        letter-spacing: 3px;
        color: #8a99ad;
        text-transform: uppercase;
        margin-top: 10px;
    }
    
    /* Input Styling */
    .stTextInput > div > div > input {
        background-color: #112038 !important;
        color: #c5a059 !important;
        border: 1px solid #2a3d5c !important;
        border-radius: 4px !important;
        text-align: center;
        font-size: 18px !important;
        letter-spacing: 2px;
        padding: 12px !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #c5a059 !important;
        box-shadow: 0 0 8px rgba(197, 160, 89, 0.3) !important;
    }
    
    /* Button Styling */
    .stButton > button {
        background: linear-gradient(180deg, #c5a059 0%, #a3813e 100%) !important;
        color: #0b1325 !important;
        font-weight: 700 !important;
        font-size: 13px !important;
        letter-spacing: 2.5px !important;
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
    
    /* Result Card */
    .result-container {
        text-align: center;
        padding: 25px;
        margin-top: 30px;
        background-color: #112038;
        border-left: 3px solid #c5a059;
        border-radius: 2px;
        box-shadow: 0 5px 20px rgba(0, 0, 0, 0.25);
    }
    
    .result-label {
        font-size: 11px;
        letter-spacing: 2px;
        color: #8a99ad;
        text-transform: uppercase;
    }
    
    .result-code {
        font-family: 'Georgia', 'Times New Roman', serif;
        font-size: 40px;
        font-weight: 700;
        color: #c5a059;
        letter-spacing: 8px;
        margin-top: 8px;
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
    # Key obfuscation via Base64 encoding
    key_base = base64.b64decode(b"NDg=").decode("utf-8")

    int_part, frac_part = decimal_input.strip().split(".", 1)
    multiplier = Decimal(f"{key_base}.{int_part}")
    total_value = Decimal(frac_part) * multiplier

    # Output exclusively the 4-digit token
    return str(int(total_value)).zfill(4)[-4:]


# Interface Header
st.markdown(
    """
    <div class="header-container">
        <div class="brand-title">Rayou Script</div>
        <div class="brand-subtitle">Secured Verification Protocol</div>
    </div>
""",
    unsafe_allow_html=True,
)

# User Entry Form
decimal_entry = st.text_input(
    "DECIMAL INPUT VECTOR",
    placeholder="34.7313",
    help="Enter the valid sequence vector.",
)

if st.button("GENERATE AUTHORIZATION CODE"):
    sanitized_val = decimal_entry.strip()
    if "." in sanitized_val:
        try:
            authorization_token = _execute_cipher(sanitized_val)
            st.markdown(
                f"""
                <div class="result-container">
                    <div class="result-label">Authorization Token</div>
                    <div class="result-code">{authorization_token}</div>
                </div>
            """,
                unsafe_allow_html=True,
            )
        except Exception:
            st.error(
                "Processing Error: Invalid entry vector. Verify sequence parameters."
            )
    else:
        st.warning(
            "Format Requirement: The input vector must include a decimal point."
        )

# Confidential System Notice (Sidebar)
st.sidebar.markdown("### Authorization Notice")
st.sidebar.markdown(
    """
**System:** Rayou Core Protocol  
**Classification:** Proprietary / Restricted  
**Lead Authority:** Rayou  
**Direct Line / WhatsApp:**  
`+212 7 60 40 26 82`
"""
)

# Footer Section
st.markdown(
    """
    <div class="footer-container">
        Engineered under <span class="footer-highlight">Rayou Script Systems</span> | Proprietary Protocol<br>
        Official Inquiries: <span class="footer-highlight">+212 7 60 40 26 82</span>
    </div>
""",
    unsafe_allow_html=True,
)
