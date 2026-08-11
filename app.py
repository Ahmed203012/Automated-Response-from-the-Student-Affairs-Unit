import streamlit as st
import re
import pandas as pd
from datetime import datetime

# ==========================================
# 1. إعدادات الصفحة والتصميم
# ==========================================
st.set_page_config(
    page_title="نظام استفسارات الطلاب",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="expanded"
)

# تخصيص الاتجاه والواجهة لدعم اللغة العربية (RTL)
st.markdown("""
    <style>
    .main {
        direction: rtl;
        text-align: right;
    }
    div[data-baseweb="select"] {
        direction: rtl;
    }
    .stButton>button {
        width: 100%;
        background-color: #0056b3;
        color: white;
        border-radius: 8px;
        height: 3em;
        font-size: 16px;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. دوال التحقق والتحقق من البيانات
# ==========================================
def validate_email(email):
    """التحقق من صحة صيغة البريد الإلكتروني"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def save_inquiry(student_id, name, email, category, message):
    """حفظ الاستفسار في القائمة المحلية أو قاعدة البيانات"""
    new_data = {
        "تاريخ الطلب": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "الرقم الجامعي": student_id,
        "اسم الطالب": name,
        "البريد الإلكتروني": email,
        "نوع الاستفسار": category,
        "نص الاستفسار": message,
        "الحالة": "قيد المراجعة"
    }
    if "inquiries_db" not in st.session_state:
        st.session_state["inquiries_db"] = []
    st.session_state["inquiries_db"].append(new_data)

# ==========================================
# 3. الهيكل الرئيسي للتطبيق
# ==========================================
def main():
    st.title("🎓 بوابة استفسارات الطلاب الأكاديمية")
    st.write("أهلاً بك! يمكنك تقديم استفسارك أو طلبك الأكاديمي من خلال النموذج أدناه.")
    st.divider()

    # القائمة الجانبية (Sidebar)
    st.sidebar.title("لوحة التحكم")
    page = st.sidebar.radio("اختر الوجهة:", ["تقديم استفسار جديد", "متابعة حالة طلب"])

    if page == "تقديم استفسار جديد":
        st.subheader("📝 نموذج تقديم طلب / استفسار")
        
        with st.form("student_inquiry_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                student_name = st.text_input("اسم الطالب الثلاثي *")
            with col2:
                student_id = st.text_input("الرقم الجامعي / الأكاديمي *")

            student_email = st.text_input("البريد الإلكتروني *")
            
            inquiry_type = st.selectbox(
                "تصنيف الاستفسار *",
                [
                    "استفسار عن الشؤون الأكاديمية والجدول",
                    "طلب إعادة تصحيح / مراجعة اختبار",
                    "استفسار عن السجل الأكاديمي والدرجات",
                    "تقديم أعذار غياب",
                    "عام / أخرى"
                ]
            )

            inquiry_text = st.text_area("تفاصيل الاستفسار أو الطلب *", height=150)
            
            submit_button = st.form_submit_button("إرسال الطلب")

        if submit_button:
            # التحقق من إدخال جميع الحقول المطلوبة
            if not student_name or not student_id or not student_email or not inquiry_text:
                st.error("⚠️ يرجى ملء كافة الحقول المطلوبة قبل الإرسال.")
            elif not validate_email(student_email):
                st.error("❌ البريد الإلكتروني غير صحيح، يرجى إدخال بريد إلكتروني فعال.")
            else:
                # حفظ الطلب
                save_inquiry(student_id, student_name, student_email, inquiry_type, inquiry_text)
                st.success("✅ تم إرسال استفسارك بنجاح! سيتم التواصل معك عبر البريد الإلكتروني المدخل.")
                st.balloons()

    elif page == "متابعة حالة طلب":
        st.subheader("🔍 الاستعلام عن حالة الطلب")
        search_id = st.text_input("أدخل الرقم الجامعي لمتابعة طلباتك:")
        
        if st.button("بحث"):
            if "inquiries_db" in st.session_state and st.session_state["inquiries_db"]:
                user_requests = [req for req in st.session_state["inquiries_db"] if req["الرقم الجامعي"] == search_id]
                if user_requests:
                    df = pd.DataFrame(user_requests)
                    st.dataframe(df, use_container_state_dict=True)
                else:
                    st.warning("لم يتم العثور على أي طلبات مرتبطة بهذا الرقم الجامعي.")
            else:
                st.info("لا توجد طلبات مسجلة في النظام حالياً.")

if __name__ == "__main__":
    main()
