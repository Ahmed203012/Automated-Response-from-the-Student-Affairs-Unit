import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import streamlit as st

# ==========================================
# 1. إعدادات الصفحة
# ==========================================
st.set_page_config(
    page_title="بوابة التحقق - كليات رؤية", page_icon="🎓", layout="centered"
)


# ==========================================
# 2. الدوال المساعدة (Utility Functions)
# ==========================================
def is_allowed_domain(email: str) -> bool:
    """التحقق الحصري من أن البريد ينتهي بـ @vision.edu.sa"""
    email = email.strip().lower()
    return email.endswith("@vision.edu.sa")


def generate_otp() -> str:
    """توليد رمز تحقق عشوائي من 6 أرقام"""
    return str(random.randint(100000, 999999))


def send_otp_email(receiver_email: str, otp_code: str) -> bool:
    """دالة إرسال البريد الإلكتروني عبر خدمة SMTP"""
    # أضف بيانات بريد الإرسال الخاص بالنظام هنا أو من secrets
    sender_email = st.secrets.get("EMAIL_USER", "your_system_email@gmail.com")
    sender_password = st.secrets.get("EMAIL_PASSWORD", "your_app_password")

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = "رمز التحقق الخاص بك - بوابة الكلية"

    body = f"""
    مرحباً بك،
    
    رمز التحقق الخاص بك للدخول إلى البوابة هو: {otp_code}
    
    هذا الرمز صالح للاستخدام الحالي فقط. يرجى عدم مشاركته مع أي شخص.
    """
    msg.attach(MIMEText(body, "plain", "utf-8"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"حدث خطأ أثناء إرسال البريد: {e}")
        return False


# ==========================================
# 3. إدارة جلسة المستخدم (Session State)
# ==========================================
if "otp_sent" not in st.session_state:
    st.session_state.otp_sent = False
if "generated_otp" not in st.session_state:
    st.session_state.generated_otp = None
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False


# ==========================================
# 4. واجهة التطبيق (UI Logic)
# ==========================================
st.title("🎓 بوابة خدمات الطلبة ومنسوبي الكلية")
st.write("يرجى إدخال البريد الجامعي الرسمي لتلقي رمز التحقق.")

st.divider()

# الصفحة بعد الدخول بنجاح
if st.session_state.authenticated:
    st.success(
        f"تم تسجيل الدخول بنجاح! مرحباً بك: {st.session_state.user_email}"
    )

    # محتوى النظام أو الاستعلامات يوضع هنا
    st.subheader("الخدمات المتاحة")
    st.info("يمكنك الآن الوصول إلى نظام الاستفسارات والخدمات الرقمية.")

    if st.button("تسجيل الخروج"):
        st.session_state.clear()
        st.rerun()

# صفحة الطلب والتحقق من الرمز
else:
    # الخطوة 1: أدخل الإيميل وأرسل الرمز
    email_input = st.text_input(
        "البريد الإلكتروني الجامعي:",
        value=st.session_state.user_email,
        placeholder="example@vision.edu.sa",
    )

    if st.button("إرسال رمز التحقق"):
        if not email_input:
            st.warning("الرجاء أدخل البريد الإلكتروني أولاً.")

        # شرط الحظر الصارم لأي امتداد آخر
        elif not is_allowed_domain(email_input):
            st.error(
                "❌ عذراً! النظام يقبل البريد الجامعي الرسمي فقط الذي ينتهي بـ (@vision.edu.sa)."
            )
            st.session_state.otp_sent = False

        else:
            # إذا كان البريد صحيحاً ويحمل الامتداد المطلوب
            otp = generate_otp()
            if send_otp_email(email_input, otp):
                st.session_state.otp_sent = True
                st.session_state.generated_otp = otp
                st.session_state.user_email = email_input
                st.success(f"تم إرسال رمز التحقق بنجاح إلى: {email_input}")
            else:
                st.error(
                    "فشل في إرسال الرمز، يرجى التأكد من الإعدادات والمحاولة لاحقاً."
                )

    # الخطوة 2: حقل أدخل الرمز (يظهر فقط إذا تم إرسال الرمز بنجاح)
    if st.session_state.otp_sent:
        st.divider()
        st.subheader("تأكيد الرمز")
        user_otp = st.text_input("أدخل رمز التحقق المكون من 6 أرقام:")

        if st.button("تأكيد الدخول"):
            if user_otp == st.session_state.generated_otp:
                st.session_state.authenticated = True
                st.success("تم التحقق بنجاح!")
                st.rerun()
            else:
                st.error("رمز التحقق غير صحيح، حاول مرة أخرى.")
