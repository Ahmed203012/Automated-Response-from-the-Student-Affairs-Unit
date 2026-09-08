import os, re, streamlit as st

# 1. تهيئة إعدادات الصفحة
st.set_page_config(page_title="كليات الرؤية", layout="centered")

# 2. إخفاء كافة عناصر منصة Streamlit والأزرار والشريط السفلي عبر CSS - نسخة محسنة لإخفاء ما يظهر للطالب
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');

/* التنسيق العام والاتجاه من اليمين للشمال */
html, body, [data-testid="stAppViewContainer"] { direction: rtl!important; text-align: right!important; background:#fff!important; }
* { font-family: 'Tajawal', sans-serif!important; direction: rtl!important; text-align: right!important; }
div[data-testid="stImage"] { display:flex!important; justify-content:center!important; }

/* تنسيق زر البحث والأجوبة */
div[data-testid="stButton"] > button { 
    background:#c5a880!important; 
    color:white!important; 
    border-radius:14px!important; 
    width:100%!important; 
    font-weight:bold!important; 
    font-size:17px!important; 
    padding:12px!important; 
}
.answer-box { background:#eaf7f0; padding:22px; border-radius:12px; border:1px solid #c3e6cb; font-size:18px; line-height:2; }
.disclaimer-box { background:#fef9e7; padding:16px; border-radius:12px; border:1px solid #f5d78e; margin-top:18px; font-size:14px; }

/* --- إخفاء نهائي لكل أشرطة وأزرار Streamlit --- */
#MainMenu, header, footer { visibility:hidden!important; display:none!important; }
div[data-testid="stHeader"], div[data-testid="stToolbar"], div[data-testid="stDecoration"] { display:none!important; }
div[data-testid="stStatusWidget"], div[data-testid="InputInstructions"] { display:none!important; }
.stAppDeployButton, .stAppFooter { display:none!important; }

/* --- إخفاء الشريط السفلي الجديد اللي فيه 88 والتاج - هذا هو اللي كان ظاهر في جوالك --- */
div[data-testid="stBottom"], div[data-testid="stBottomBlockContainer"], section[data-testid="stBottom"] { display:none!important; }
div[class*="viewerBadge"], div[class*="stViewerBadge"], .viewerBadge_container__1A52n, .viewerBadge_link__1S137 { display:none!important; }
[data-testid="manage-app-button"], div[data-testid="stActionButton"], div[class*="stAppViewer"] { display:none!important; }
button[title="View app source"], button[class*="viewerBadge"], a[href*="streamlit.io"] { display:none!important; }
iframe[title="streamlit_app"] { display:none!important; }
</style>
""", unsafe_allow_html=True)
