import streamlit as st
from groq import Groq
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm
import io

st.set_page_config(
    page_title="AI Email Generator",
    page_icon="📧",
    layout="centered"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    .stApp { 
        background: linear-gradient(135deg, #0f1117 0%, #1a1a2e 50%, #16213e 100%);
        font-family: 'Inter', sans-serif;
    }
    h1 { 
        background: linear-gradient(90deg, #00d4ff, #7b2ff7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-size: 2.5em !important;
        font-weight: 700 !important;
    }
    p { color: #888; text-align: center; }
    .email-box {
        background: linear-gradient(135deg, #1e1e2e, #2a2a3e);
        border-radius: 20px;
        padding: 35px;
        border: 1px solid rgba(0, 212, 255, 0.2);
        margin: 10px 0;
        animation: fadeIn 0.5s ease;
    }
    .subject-box {
        background: linear-gradient(135deg, #2e1e2e, #3e2a3e);
        border-radius: 12px;
        padding: 15px 20px;
        border-left: 4px solid #7b2ff7;
        margin-bottom: 16px;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .stButton button {
        border-radius: 12px !important;
        font-weight: 600 !important;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>📧 AI Email Generator</h1>", unsafe_allow_html=True)
st.markdown("<p style='font-size:16px'>Generate professional emails instantly with AI</p>", unsafe_allow_html=True)
st.divider()

api_key = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=api_key)

def generate_pdf(email_content, email_type, tone):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                           rightMargin=20*mm, leftMargin=20*mm,
                           topMargin=20*mm, bottomMargin=20*mm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Heading1'],
                                fontSize=18, textColor=colors.HexColor('#00d4ff'),
                                spaceAfter=10)
    body_style = ParagraphStyle('Body', parent=styles['Normal'],
                               fontSize=11, spaceAfter=6, leading=16)
    story = []
    story.append(Paragraph(f"Email: {email_type} — {tone}", title_style))
    story.append(Spacer(1, 6*mm))
    for line in email_content.split('\n'):
        if line.strip():
            story.append(Paragraph(line.strip(), body_style))
            story.append(Spacer(1, 2*mm))
    doc.build(story)
    buffer.seek(0)
    return buffer

col1, col2 = st.columns(2)
with col1:
    email_type = st.selectbox("Email Type:", [
        "Professional Email",
        "Cold Outreach",
        "Follow Up",
        "Apology Email",
        "Thank You Email",
        "Job Application",
        "Internship Request",
        "Complaint Email",
        "Introduction Email"
    ])
with col2:
    tone = st.selectbox("Tone:", [
        "Formal",
        "Friendly",
        "Persuasive",
        "Urgent",
        "Humble",
        "Confident"
    ])

col3, col4 = st.columns(2)
with col3:
    sender_name = st.text_input("Your Name:", placeholder="Rohit Savan")
with col4:
    recipient = st.text_input("Recipient:", placeholder="HR Manager / Professor / Client")

context = st.text_area(
    "What is this email about?",
    height=120,
    placeholder="e.g. I want to apply for an AI internship at a startup. I have 8 deployed AI projects and want to introduce myself..."
)

if st.button("✉️ Generate Email", use_container_width=True):
    if context:
        with st.spinner("Writing your email..."):
            prompt = f"""Write a {tone.lower()} {email_type.lower()} with the following details:

Sender: {sender_name if sender_name else "the sender"}
Recipient: {recipient if recipient else "the recipient"}
Context: {context}

Instructions:
- Write a complete professional email
- Include Subject line at the top
- Include proper greeting
- Clear and concise body
- Professional closing
- Make it {tone.lower()} in tone
- Make it specific to the context provided
- Format: Start with "Subject: ..." then the full email"""

            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": f"You are an expert email writer. Write professional, effective {tone.lower()} emails that get results."},
                    {"role": "user", "content": prompt}
                ],
                stream=True
            )

            st.markdown("### ✉️ Your Email")
            email_placeholder = st.empty()
            full_email = ""

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_email += chunk.choices[0].delta.content
                    email_placeholder.markdown(f"""
                    <div class="email-box">
                        <pre style="color:#cdd6f4; font-size:14px; white-space:pre-wrap; font-family:'Inter',sans-serif; line-height:1.8">{full_email}▌</pre>
                    </div>
                    """, unsafe_allow_html=True)

            email_placeholder.markdown(f"""
            <div class="email-box">
                <pre style="color:#cdd6f4; font-size:14px; white-space:pre-wrap; font-family:'Inter',sans-serif; line-height:1.8">{full_email}</pre>
            </div>
            """, unsafe_allow_html=True)

            st.session_state.email = full_email
            st.session_state.email_type = email_type
            st.session_state.tone = tone

        st.divider()

        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="📥 Download as PDF",
                data=generate_pdf(full_email, email_type, tone),
                file_name=f"email_{email_type.replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        with col2:
            st.download_button(
                label="📋 Download as Text",
                data=full_email,
                file_name=f"email_{email_type.replace(' ', '_')}.txt",
                mime="text/plain",
                use_container_width=True
            )
    else:
        st.warning("Please describe what the email is about!")

st.markdown("<p style='margin-top:20px'>Built by Rohit • Powered by Groq + Llama 3</p>", unsafe_allow_html=True)
