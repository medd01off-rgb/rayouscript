import streamlit as st
from decimal import Decimal

# إعداد واجهة الموقع
st.set_page_config(page_title="Code Calculator", page_icon="🔢")
st.title("Code Generator")
st.write("Enter a decimal number to generate your 4-digit code.")

# مدخل البيانات
num_input = st.text_input("Enter Decimal Number", placeholder="34.7313")

if st.button("Calculate Code"):
    num_str = num_input.strip()
    if "." in num_str:
        try:
            int_part, frac_part = num_str.split(".", 1)
            
            # العمليات الحسابية بواسطة Decimal
            multiplier = Decimal(f"48.{int_part}")
            frac_val = Decimal(frac_part)
            total = frac_val * multiplier
            code = str(int(total)).zfill(4)[-4:]
            
            # عرض النتيجة
            st.success(f"Your Code: **{code}**")
            st.info(f"Full Calculation: {frac_val} × {multiplier} = {total}")
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.warning("Please enter a valid decimal number containing a dot (e.g., 34.7313).")
