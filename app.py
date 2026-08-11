import streamlit as st
import random
import smtplib
from email.mime.text import MIMEText
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

# --- إعدادات الصفحة ---
st.set_page_config(page_title="المساعد الأكاديمي للطلاب - كلية الرؤية", page_icon="🎓", layout="centered")

st.title("🎓 المساعد الأكاديمي للطلاب - كلية الرؤية")
st.caption("مساعد ذكي للإجابة على الاستفسارات الأكاديمية استناداً إلى لوائح الكلية")

# --- إدارة الجلسة ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "otp_sent" not in st.session_state:
    st.session_state.otp_sent = False
if "generated_otp" not in st.session_state:
    st.session_state.generated_otp = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- دالة إرسال رمز التحقق OTP ---
def send_otp_email(user_email, otp_code):
    sender_email = st.secrets.get("SMTP_EMAIL", "")
    sender_password = st.secrets.get("SMTP_PASSWORD", "")
    
    msg = MIMEText(f"رمز التحقق الخاص بك للدخول إلى المساعد الأكاديمي هو: {otp_code}")
    msg['Subject'] = 'رمز التحقق - المساعد الأكاديمي'
    msg['From'] = sender_email
    msg['To'] = user_email

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, user_email, msg.as_string())
        return True
    except Exception as e:
        st.error(f"حدث خطأ أثناء إرسال البريد: {e}")
        return False

# --- شاشة التحقق ---
if not st.session_state.authenticated:
    st.subheader("🔐 تسجيل الدخول للطلبة")
    st.info("يرجى إدخال بريدك الجامعي الرسمي للتحقق من الهوية.")

    email_input = st.text_input("البريد الإلكتروني الجامعي", placeholder="student@vision.edu.sa")

    if not st.session_state.otp_sent:
        if st.button("إرسال رمز التحقق"):
            if email_input.endswith("@vision.edu.sa") or email_input.endswith(".edu.sa"):
                otp = str(random.randint(100000, 999999))
                st.session_state.generated_otp = otp
                if send_otp_email(email_input, otp):
                    st.session_state.otp_sent = True
                    st.success("تم إرسال رمز التحقق إلى بريدك الإلكتروني!")
                    st.rerun()
            else:
                st.error("عذراً، هذا التطبيق مخصص لطلبة الكلية فقط (@vision.edu.sa).")
    else:
        otp_input = st.text_input("أدخل رمز التحقق (OTP)")
        if st.button("تأكيد الرمز والدخول"):
            if otp_input == st.session_state.generated_otp:
                st.session_state.authenticated = True
                st.success("تم التحقق بنجاح!")
                st.rerun()
            else:
                st.error("رمز التحقق غير صحيح، حاول مرة أخرى.")
    st.stop()

# --- تحميل اللوائح ---
@st.cache_resource
def load_knowledge_base():
    loader = PyPDFDirectoryLoader(".")
    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)
    vectorstore = FAISS.from_documents(splits, OpenAIEmbeddings(api_key=st.secrets["OPENAI_API_KEY"]))
    return vectorstore.as_retriever()

try:
    retriever = load_knowledge_base()
except Exception as e:
    st.warning("جاري إعداد قاعدة البيانات...")
    retriever = None

# --- واجهة المحادثة ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("اكتب سؤالك الأكاديمي هنا..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if retriever:
            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=st.secrets["OPENAI_API_KEY"])
            system_prompt = (
                "أنت مساعد أكاديمي لكلية الرؤية بالرياض. أجب على استفسارات الطلاب باللغة العربية بناءً على اللوائح المرفقة فقط.\n"
                "إذا لم تجد الإجابة في اللوائح، وضح للطالب التواصل مع شؤون الطلاب.\n\n"
                "اللوائح المتاحة:\n{context}"
            )
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", "{input}"),
            ])
            question_answer_chain = create_stuff_documents_chain(llm, prompt_template)
            rag_chain = create_retrieval_chain(retriever, question_answer_chain)
            response = rag_chain.invoke({"input": prompt})
            bot_reply = response["answer"]
        else:
            bot_reply = "عذراً، قاعدة معرفة اللوائح غير متصلة حالياً."

        st.markdown(bot_reply)
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
