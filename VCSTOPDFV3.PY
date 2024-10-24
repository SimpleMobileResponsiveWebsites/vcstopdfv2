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

class FileInput:
    def __init__(self, input_type, content, timestamp=None):
        self.input_type = input_type
        self.content = content
        self.timestamp = timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class Version:
    def __init__(self, name, version_number, description=""):
        self.name = name
        self.version_number = version_number
        self.description = description
        self.creation_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.status = "ACTIVE"
        self.inputs = []  # List to store all inputs for this file
        self.categories = {
            "requirements": [],
            "documentation": [],
            "dependencies": [],
            "test_cases": [],
            "notes": []
        }

# Initialize session state
if 'codebases' not in st.session_state:
    st.session_state.codebases = {}

# Sidebar for file management
with st.sidebar:
    st.header("File Management")
    
    new_file_name = st.text_input("File Name (with extension):")
    file_description = st.text_area("File Description:", height=100)
    
    if st.button("Add New File"):
        if new_file_name:
            file_version_key = f"{new_file_name}_v1.0"
            
            if file_version_key not in st.session_state.codebases:
                new_version = Version(name=new_file_name, version_number="1.0", description=file_description)
                st.session_state.codebases[file_version_key] = new_version
                st.success(f"Added file: {new_file_name}")
            else:
                st.error("File already exists!")
        else:
            st.error("Please enter a file name!")

# Main content area
if st.session_state.codebases:
    selected_file_version = st.selectbox(
        "Select File to Work With",
        [""] + list(st.session_state.codebases.keys()),
        index=0
    )

    if selected_file_version:
        version_obj = st.session_state.codebases[selected_file_version]
        
        st.title(f"File: {version_obj.name}")
        st.subheader(f"Description: {version_obj.description}")
        
        # Input type selection
        input_type = st.selectbox(
            "Select Input Type",
            ["Requirements", "Documentation", "Dependencies", "Test Cases", "Notes"]
        )
        
        # Input form
        with st.form(key=f"input_form_{selected_file_version}"):
            st.subheader(f"Add {input_type}")
            
            if input_type == "Requirements":
                requirement_name = st.text_input("Requirement Name:")
                priority = st.selectbox("Priority", ["High", "Medium", "Low"])
                description = st.text_area("Requirement Description:")
                content = {
                    "name": requirement_name,
                    "priority": priority,
                    "description": description
                }
            
            elif input_type == "Dependencies":
                dep_name = st.text_input("Dependency Name:")
                version = st.text_input("Version:")
                purpose = st.text_area("Purpose:")
                content = {
                    "name": dep_name,
                    "version": version,
                    "purpose": purpose
                }
            
            elif input_type == "Test Cases":
                test_name = st.text_input("Test Name:")
                test_type = st.selectbox("Test Type", ["Unit", "Integration", "System", "Acceptance"])
                test_description = st.text_area("Test Description:")
                expected_result = st.text_area("Expected Result:")
                content = {
                    "name": test_name,
                    "type": test_type,
                    "description": test_description,
                    "expected_result": expected_result
                }
            
            else:  # Documentation and Notes
                title = st.text_input("Title:")
                details = st.text_area("Details:")
                content = {
                    "title": title,
                    "details": details
                }
            
            submit_button = st.form_submit_button("Save Input")
            
            if submit_button:
                new_input = FileInput(input_type.lower(), content)
                version_obj.inputs.append(new_input)
                version_obj.categories[input_type.lower().replace(" ", "_")].append(new_input)
                st.success(f"Saved {input_type} input")
        
        # Display all inputs
        st.header("File History")
        
        for category in version_obj.categories:
            if version_obj.categories[category]:
                st.subheader(category.replace("_", " ").title())
                for input_item in version_obj.categories[category]:
                    with st.expander(f"{input_item.timestamp}"):
                        for key, value in input_item.content.items():
                            st.write(f"**{key.replace('_', ' ').title()}:** {value}")
        
        # Generate PDF
        if st.button("Generate PDF Report"):
            pdf_buffer = BytesIO()
            doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, leftMargin=36, rightMargin=36)
            styles = getSampleStyleSheet()
            pdf_elements = []
            
            # File information
            pdf_elements.append(Paragraph(f"File: {version_obj.name}", styles['Title']))
            pdf_elements.append(Paragraph(f"Description: {version_obj.description}", styles['Normal']))
            pdf_elements.append(Spacer(1, 20))
            
            # Add all categories
            for category in version_obj.categories:
                if version_obj.categories[category]:
                    pdf_elements.append(Paragraph(category.replace("_", " ").title(), styles['Heading1']))
                    
                    for input_item in version_obj.categories[category]:
                        pdf_elements.append(Paragraph(f"Timestamp: {input_item.timestamp}", styles['Heading2']))
                        
                        data = [[key.replace('_', ' ').title(), str(value)] 
                               for key, value in input_item.content.items()]
                        
                        table = Table(data)
                        table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                            ('FONTSIZE', (0, 0), (-1, -1), 10),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black)
                        ]))
                        
                        pdf_elements.append(table)
                        pdf_elements.append(Spacer(1, 20))
            
            # Build PDF
            doc.build(pdf_elements)
            pdf_buffer.seek(0)
            pdf_data = pdf_buffer.read()
            
            # Create download link
            st.markdown(
                create_download_link_pdf(pdf_data, f"{version_obj.name}_report.pdf"),
                unsafe_allow_html=True
            )
