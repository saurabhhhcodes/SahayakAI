from fpdf import FPDF
import textwrap

class EducationalPDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 15)
        self.cell(0, 10, 'Sahayak.AI - Lesson Plan', border=False, align='C')
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

def create_pdf(title: str, content: str, filename: str):
    pdf = EducationalPDF()
    pdf.add_page()
    
    # Title
    pdf.set_font("Helvetica", "B", 16)
    pdf.multi_cell(0, 10, title, align='L')
    pdf.ln(5)
    
    # Content
    # Simplified Markdown parsing (removing ** for bold)
    pdf.set_font("Helvetica", size=12)
    
    # Very basic cleanup of markdown for PDF
    clean_content = content.replace('**', '').replace('###', '')
    
    # Handle utf-8 characters robustly
    try:
        # FPDF standard fonts only support Latin-1.
        # We replace unsupported chars to prevent crash.
        clean_content = clean_content.encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 7, clean_content)
    except Exception as e:
        print(f"PDF Generation Encoding Error: {e}")
        pdf.multi_cell(0, 7, "Error: Content contains unsupported characters for PDF generation. Please view in web interface.")
    
    pdf.output(filename)
    return filename
