import streamlit as st
from io import BytesIO
import base64
from streamlit_ace import st_ace
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from datetime import datetime


def create_download_link_pdf(pdf_data, download_filename):
    b64 = base64.b64encode(pdf_data).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="{download_filename}">Download PDF</a>'
    return href


class Version:
    def __init__(self, name, version_number, description=""):
        self.name = name
        self.version_number = version_number
        self.description = description
        self.creation_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.status = "Active"
        self.notes = []
        self.code_snippets = []
        self.issues = []


# Initialize session states and set the initial parent-child relationship
if 'codebases' not in st.session_state:
    st.session_state.codebases = {}

    # Predefined initial file
    initial_version = Version(name="app1.py", version_number="1.0")
    st.session_state.codebases["app1.py"] = initial_version

# Sidebar for codebase management
with st.sidebar:
    st.header("Codebase Management")

    # File name input with extension
    new_file_name = st.text_input("File Name (with extension, e.g., appxx.py):")

    if st.button("Add New File"):
        if new_file_name:
            if new_file_name not in st.session_state.codebases:
                # Create new version object with default version number
                new_version = Version(name=new_file_name, version_number="1.0")

                # Add to codebases
                st.session_state.codebases[new_file_name] = new_version

                st.success(f"Added file: {new_file_name} (Version 1.0)")
            else:
                st.error("File already exists!")
        else:
            st.error("Please enter a file name!")

# Main content area
if st.session_state.codebases:
    selected_file = st.selectbox(
        "Select File to Work With",
        list(st.session_state.codebases.keys())
    )

    version_obj = st.session_state.codebases[selected_file]

    st.title(f"File: {selected_file}")
    st.subheader(f"Version: {version_obj.version_number}")

    # Display file information
    st.header("File Details")
    st.write(f"Created: {version_obj.creation_date}")
    st.write(f"Status: {version_obj.status}")

    # Status update
    status_options = ["Active", "Deprecated", "Issues Found"]
    new_status = st.selectbox("File Status", status_options, index=status_options.index(version_obj.status))
    if new_status != version_obj.status:
        version_obj.status = new_status
        st.success(f"Updated status to: {new_status}")

    # Testing notes
    st.header("Testing Documentation")
    regression_notes = st.text_area("Regression Testing Notes:")
    if st.button("Save Testing Notes"):
        version_obj.notes.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "content": regression_notes
        })
        st.success("Saved testing notes")

    # Issue tracking
    st.header("Issue Tracking")
    issue_description = st.text_area("Issue Description:")
    issue_severity = st.selectbox("Issue Severity", ["Low", "Medium", "High", "Critical"])
    if st.button("Add Issue"):
        version_obj.issues.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "description": issue_description,
            "severity": issue_severity,
            "status": "Open"
        })
        st.success("Added issue")

    # Code editor
    st.header("Code Editor")
    code = st_ace(
        language="python",
        theme="monokai",
        key=f"ace-editor-{selected_file}",
        value=version_obj.code_snippets[-1]["code"] if version_obj.code_snippets else ""
    )
    if st.button("Save Code"):
        version_obj.code_snippets.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "code": code
        })
        st.success("Saved code")

    # Display saved information
    if version_obj.notes or version_obj.issues or version_obj.code_snippets:
        st.header("History")

        # Display testing notes
        if version_obj.notes:
            st.subheader("Testing Notes")
            for note in version_obj.notes:
                st.text(f"[{note['timestamp']}]")
                st.markdown(note['content'])
                st.markdown("---")

        # Display issues
        if version_obj.issues:
            st.subheader("Issues")
            for issue in version_obj.issues:
                st.markdown(f"**Severity:** {issue['severity']}")
                st.markdown(f"**Reported:** {issue['timestamp']}")
                st.markdown(f"**Description:** {issue['description']}")
                st.markdown("---")

        # Display code history
        if version_obj.code_snippets:
            st.subheader("Code History")
            for snippet in version_obj.code_snippets:
                st.text(f"[{snippet['timestamp']}]")
                st.code(snippet['code'], language="python")
                st.markdown("---")

    # Generate PDF
    if st.button("Generate PDF Report"):
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, leftMargin=36, rightMargin=36)
        styles = getSampleStyleSheet()
        pdf_elements = []

        # File and version information
        pdf_elements.append(Paragraph(f"File: {selected_file}", styles['Title']))
        pdf_elements.append(Paragraph(f"Version: {version_obj.version_number}", styles['Heading1']))

        # File details
        pdf_elements.append(Paragraph("File Details", styles['Heading2']))
        file_data = [
            ["Created", version_obj.creation_date],
            ["Status", version_obj.status]
        ]
        file_table = Table(file_data)
        file_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        pdf_elements.append(file_table)
        pdf_elements.append(Spacer(1, 20))

        # Add other sections (notes, issues, code) as before...
        if version_obj.notes:
            pdf_elements.append(Paragraph("Testing Notes", styles['Heading2']))
            for note in version_obj.notes:
                pdf_elements.append(Paragraph(f"[{note['timestamp']}]", styles['Normal']))
                pdf_elements.append(Paragraph(note['content'], styles['Normal']))
                pdf_elements.append(Spacer(1, 10))

        if version_obj.issues:
            pdf_elements.append(Paragraph("Issues", styles['Heading2']))
            for issue in version_obj.issues:
                pdf_elements.append(Paragraph(f"Severity: {issue['severity']}", styles['Normal']))
                pdf_elements.append(Paragraph(f"Reported: {issue['timestamp']}", styles['Normal']))
                pdf_elements.append(Paragraph(f"Description: {issue['description']}", styles['Normal']))
                pdf_elements.append(Spacer(1, 10))

        if version_obj.code_snippets:
            pdf_elements.append(Paragraph("Code History", styles['Heading2']))
            code_style = ParagraphStyle(
                name='CodeStyle',
                fontName='Courier',
                fontSize=8,
                leftIndent=10,
                rightIndent=10,
                leading=8,
                wordWrap='CJK'
            )
            for snippet in version_obj.code_snippets:
                pdf_elements.append(Paragraph(f"[{snippet['timestamp']}]", styles['Normal']))
                pdf_elements.append(Preformatted(snippet['code'], code_style, maxLineLength=65))
                pdf_elements.append(Spacer(1, 10))

        # Build the PDF
        doc.build(pdf_elements)
        pdf_buffer.seek(0)
        pdf_data = pdf_buffer.read()

        # Create download link
        st.markdown(
            create_download_link_pdf(pdf_data, f"{selected_file}_v{version_obj.version_number}_report.pdf"),
            unsafe_allow_html=True
        )
