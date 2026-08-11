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

st.set_page_config(page_title="وحدة شؤون الطلاب - الاستفسارات الأكاديمية", layout="wide")

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
    st.subheader("🔒 التحقق من الهوية (البريد الجامعي)")
    email_input = st.text_input("أدخل بريدك الإلكتروني:")
    
    if st.button("إرسال رمز التحقق (OTP)"):
        if email_input:
            otp = str(random.randint(100000, 999999))
            st.session_state.otp_code = otp
            st.session_state.user_email = email_input
            if send_otp_email(email_input, otp):
                st.success("تم إرسال رمز التحقق إلى بريدك الإلكتروني بنجاح!")
        else:
            st.warning("يرجى إدخال البريد الإلكتروني أولاً.")
            
    if st.session_state.otp_code:
        otp_input = st.text_input("أدخل رمز التحقق (OTP):")
        if st.button("تأكيد الرمز"):
            if otp_input.strip() == st.session_state.otp_code:
                st.session_state.authenticated = True
                st.success("تم التحقق بنجاح!")
                st.rerun()
            else:
                st.error("رمز التحقق غير صحيح، حاول مرة أخرى.")

# --- Step 2: Main Application ---
else:
    st.success(f"تم تسجيل الدخول بنجاح بصفتك: {st.session_state.user_email}")
    st.markdown("---")
    st.subheader("💬 اسأل عن نتائج الاختبارات أو ضوابط قبول الأعذار")
    
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
                st.warning(f"تعذر تحميل الملف {file}: {e}")
                
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        splits = text_splitter.split_documents(documents)
        
        embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
        vectorstore = FAISS.from_documents(splits, embeddings)
        return vectorstore

    if not OPENAI_API_KEY:
        st.error("يرجى ضبط OPENAI_API_KEY في Secrets أولاً.")
    else:
        with st.spinner("جاري تحميل اللوائح والبيانات..."):
            try:
                vectorstore = load_vector_store()
                retriever = vectorstore.as_retriever()
                
                llm = ChatOpenAI(model="gpt-4o-mini", openai_api_key=OPENAI_API_KEY, temperature=0)
                
                system_prompt = (
                    "أنت مساعد أكاديمي لالرد على استفسارات الطلاب في وحدة شؤون الطلاب بـ كلية الرؤية بالرياض.\n"
                    "استخدم سياق المعلومات المرفق فقط للإجابة على الأسئلة بأسلوب مهني وواضح ودقيق.\n"
                    "إذا لم تجد الإجابة في النص المرفق، أبلغ الطالب بالتواصل مباشرة مع وحدة شؤون الطلاب.\n\n"
                    "السياق:\n{context}"
                )
                prompt = ChatPromptTemplate.from_messages([
                    ("system", system_prompt),
                    ("human", "{input}"),
                ])
                
                question_answer_chain = create_stuff_documents_chain(llm, prompt)
                rag_chain = create_retrieval_chain(retriever, question_answer_chain)
                
                user_query = st.text_input("اكتب استفسارك هنا:")
                if user_query:
                    with st.spinner("جاري البحث عن الإجابة..."):
                        response = rag_chain.invoke({"input": user_query})
                        st.write("### الإجابة:")
                        st.write(response["answer"])
            except Exception as e:
                st.error(f"حدث خطأ أثناء معالجة الطلب: {e}")
