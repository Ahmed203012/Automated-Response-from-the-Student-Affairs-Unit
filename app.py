import streamlit as st

# كود CSS شامِل لإخفاء جميع عناصر Streamlit الخارجية
hide_st_style = """
    <style>
    /* إخفاء الهيدر والشريط العلوي بالكامل */
    header {visibility: hidden !important; height: 0px !important;}
    [data-testid="stHeader"] {display: none !important;}
    [data-testid="stToolbar"] {display: none !important;}
    
    /* إخفاء زر Viewer Badge وزر GitHub */
    [data-testid="stDecoration"] {display: none !important;}
    .viewerBadge_container__1QSob {display: none !important;}
    #GithubIcon {visibility: hidden !important;}
    
    /* إخفاء التذييل والقائمة الرئيسية */
    footer {visibility: hidden !important; height: 0px !important;}
    #MainMenu {visibility: hidden !important;}
    
    /* ضبط المساحة العلوية للتطبيق بعد إخفاء الهيدر */
    .main .block-container {
        padding-top: 1rem !important;
    }
    </style>
"""

st.markdown(hide_st_style, unsafe_allow_html=True)
