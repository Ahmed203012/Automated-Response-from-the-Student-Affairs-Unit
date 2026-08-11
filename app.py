import streamlit as st
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

st.set_page_config(page_title="وحدة شؤون الطلاب - كلية الرؤية", layout="centered")

st.title("🎓 المساعد الأكاديمي الذكي - وحدة شؤون الطلاب")

# Read Secrets
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", "")
SMTP_EMAIL = st.secrets.get("SMTP_EMAIL", "")
SMTP_PASSWORD = st.secrets.get("SMTP_PASSWORD", "")

# Initialize Session States
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "otp_code" not in st.session_state:
    st.session_state.otp_code = None
if "user_email" not in st.session_state:
    st.session_state.user_email = ""

def send_otp_email(to_email, otp):
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_EMAIL
        msg['To'] = to_email
        msg['Subject'] = "رمز التحقق الخاصة بك - وحدة شؤون الطلاب"
        body = f"مرحباً بك،\n\nرمز التحقق الخاص بك للوصول إلى النظام هو: {otp}\n\nشكراً لك."
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.sendmail(SMTP_EMAIL, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"حدث خطأ أثناء إرسال البريد: {e}")
        return False

# --- Step 1: Authentication ---
if not st.session_state.authenticated:
    st.subheader("🔒 تسجيل الدخول للطلبة")
    st.info("أدخل بريدك الجامعي ليصلك رمز التحقق OTP.")
    
    email_input = st.text_input("البريد الإلكتروني الجامعي:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("إرسال رمز التحقق"):
            if email_input:
                otp = str(random.randint(100000, 999999))
                st.session_state.otp_code = otp
                st.session_state.user_email = email_input
                if send_otp_email(email_input, otp):
                    st.success("تم إرسال رمز التحقق!")
            else:
                st.warning("يرجى إدخال البريد الإلكتروني.")
                
    if st.session_state.otp_code:
        st.markdown("---")
        otp_input = st.text_input("أدخل رمز التحقق (OTP) المكون من 6 أرقام:")
        if st.button("تأكيد الرمز والدخول"):
            if otp_input.strip() == st.session_state.otp_code:
                st.session_state.authenticated = True
                st.success("تم التحقق بنجاح!")
                st.rerun()
            else:
                st.error("رمز التحقق غير صحيح.")

# --- Step 2: Main Application ---
else:
    st.success(f"مرحباً بك: {st.session_state.user_email}")
    st.markdown("---")
    
    @st.cache_resource
    def load_vector_store():
        files = [
            "نتائج ودرجات الاختبارات في كلية الرؤية بالرياض.pdf",
            "ضوابط قبول الأعذار الطلابية في كلية الرؤية بالرياض.pdf"
        ]
        documents = []
        for file in files:
            try:
                loader = PyPDFLoader(file)
                documents.extend(loader.load())
            except Exception as e:
                pass
                
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        splits = text_splitter.split_documents(documents)
        
        embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
        vectorstore = FAISS.from_documents(splits, embeddings)
        return vectorstore

    if not OPENAI_API_KEY:
        st.error("يرجى إدخال OPENAI_API_KEY في إعدادات Secrets لمتابعة الاستفسارات.")
    else:
        try:
            vectorstore = load_vector_store()
            retriever = vectorstore.as_retriever()
            llm = ChatOpenAI(model="gpt-4o-mini", openai_api_key=OPENAI_API_KEY, temperature=0)
            
            system_prompt = (
                "أنت مساعد أكاديمي لشؤون الطلاب بكلية الرؤية بالرياض. أجب على استفسارات الطلاب بوضوح ودقة بناءً على النص المرفق فقط.\n\n"
                "السياق:\n{context}"
            )
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", "{input}"),
            ])
            
            question_answer_chain = create_stuff_documents_chain(llm, prompt)
            rag_chain = create_retrieval_chain(retriever, question_answer_chain)
            
            user_query = st.text_input("اكتب استفسارك حول الاختبارات والأعذار الأكاديمية:")
            if user_query:
                with st.spinner("جاري الإجابة..."):
                    response = rag_chain.invoke({"input": user_query})
                    st.write("### الإجابة:")
                    st.write(response["answer"])
        except Exception as e:
            st.error(f"حدث خطأ أثناء تحميل البيانات: {e}")
