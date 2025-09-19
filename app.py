import streamlit as st
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListItem, ListFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.enums import TA_CENTER
from openai import OpenAI
from io import BytesIO
import re

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="Automation Idea Generator", page_icon="⚡", layout="centered")


st.title("⚡ Automation Idea Generator")
st.write("Generate automation ideas based on your input. Get tailored workflows and tool suggestions for your business.")


industry = st.text_input("What industry are you in?", placeholder="e.g., E-commerce, Healthcare, Finance")
team_size = st.selectbox("What is your team size?", ["1-10", "11-50", "51-200", "201-500", "500+"])
pain_points = st.text_area("What are your main pain points?", placeholder="e.g., Customer support, Inventory management, Data analysis")

if st.button("Generate Ideas"):
    with st.spinner("Generating ideas..."):
        prompt = f"""
        You are a world-class AI Automation Consultant hired to advise a business.

        Business Context:
        - Industry: {industry}
        - Team size: {team_size}
        - Current pain points: {pain_points}

        Your task:
        Generate exactly 3 automation workflows tailored to this business.

        For EACH workflow, include:
        1. **Title / Goal** — short, powerful headline (e.g., "Automated Lead Qualification with AI")
        2. **Why It Matters** — 1–2 sentences explaining the impact
        3. **Step-by-Step Implementation** — 3–5 clear, numbered steps that the business can follow
        4. **AI Tools / Apps** — 2–3 relevant tools (mention specific categories or sample tools, not generic fluff)
        5. **Estimated ROI** — show either hours saved per week OR cost reduction (estimate based on team size and task)

        Requirements:
        - Keep output concise, clear, and formatted with markdown (use headings, bullet points, bold where relevant).
        - Prioritize high-impact automations that save time, cut costs, and improve scalability.
        - Focus on realistic solutions that a small business team of {team_size} can implement without heavy technical expertise.
        - Avoid generic advice like "use AI to save time." Be specific and tactical.
        - Tone should be practical and business-friendly, not academic.

        Deliver the output as a professional mini-report ready for a business owner to act on immediately.
        """
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an AI automation expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )

        # Display output
        report_text = response.choices[0].message.content
        st.markdown(report_text)

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer)
        styles = getSampleStyleSheet()
        story = []

        current_list = []

        for line in report_text.split('\n'):
            line = line.strip()
            if line.startswith("### "):
                story.append(Paragraph(line[4:], styles["Heading3"]))
                story.append(Spacer(1, 6))
            elif line.startswith("## "):
                story.append(Paragraph(line[3:], styles["Heading2"]))
                story.append(Spacer(1, 8))
            elif line.startswith("# "):
                story.append(Paragraph(line[2:], styles["Heading1"]))
                story.append(Spacer(1, 12))
            elif line.startswith("- "):
                current_list.append(ListItem(Paragraph(line[2:], styles["Normal"])))
            elif line == "" and current_list:
                story.append(ListFlowable(current_list))
                story.append(Spacer(1, 6))
                current_list = []
            else:
                # convert **bold** to <b>bold</b>
                line = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", line)
                story.append(Paragraph(line, styles["Normal"]))
                story.append(Spacer(1, 6))

        if current_list:
            story.append(ListFlowable(current_list))

        doc.build(story)
        buffer.seek(0)

        st.download_button(
            label="📥 Download Report as PDF",
            data=buffer,
            file_name="automation_ideas_report.pdf",
            mime="application/pdf"
        )


