import os
import sys
import copy
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

# Ensure scripts directory is in path
sys.path.insert(0, os.path.abspath('scripts'))

import build_exact_use_case_scenarios_all as buc_all
import build_data_dictionary as bdd
import build_section_3_8 as bs38
import build_sections_eval_ethics as bsee
import build_chapter4_section4_1 as bc4
import build_chapter4_testing_tables as bc4t

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_apa_table_borders(table):
    tblPr = table._element.xpath('w:tblPr')
    if tblPr:
        borders = parse_xml(
            f'<w:tblBorders {nsdecls("w")}>\n'
            f'  <w:top w:val="single" w:sz="12" w:space="0" w:color="000000"/>\n'
            f'  <w:left w:val="none"/>\n'
            f'  <w:bottom w:val="single" w:sz="12" w:space="0" w:color="000000"/>\n'
            f'  <w:right w:val="none"/>\n'
            f'  <w:insideH w:val="none"/>\n'
            f'  <w:insideV w:val="none"/>\n'
            f'</w:tblBorders>'
        )
        tblPr[0].append(borders)

def set_apa_header_cell(cell):
    set_cell_margins(cell, top=120, bottom=120, left=150, right=150)
    tcPr = cell._element.get_or_add_tcPr()
    tcBorders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>\n'
        f'  <w:bottom w:val="single" w:sz="8" w:space="0" w:color="000000"/>\n'
        f'</w:tcBorders>'
    )
    tcPr.append(tcBorders)

def set_apa_data_cell(cell, is_last_row=False):
    set_cell_margins(cell, top=80, bottom=80, left=150, right=150)
    if is_last_row:
        tcPr = cell._element.get_or_add_tcPr()
        tcBorders = parse_xml(
            f'<w:tcBorders {nsdecls("w")}>\n'
            f'  <w:bottom w:val="single" w:sz="12" w:space="0" w:color="000000"/>\n'
            f'</w:tcBorders>'
        )
        tcPr.append(tcBorders)

def build_duepapers_fixed():
    doc = Document()

    # Standard APA Margins: Left 1.5", Top/Right/Bottom 1.0"
    for section in doc.sections:
        section.page_width = Inches(8.5)
        section.page_height = Inches(11.0)
        section.left_margin = Inches(1.5)
        section.right_margin = Inches(1.0)
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)

    # Styles
    style_normal = doc.styles['Normal']
    style_normal.font.name = 'Arial'
    style_normal.font.size = Pt(12)
    style_normal.font.color.rgb = RGBColor(0, 0, 0)

    def p_body(text, indent=True, align=WD_ALIGN_PARAGRAPH.JUSTIFY):
        p = doc.add_paragraph()
        p.alignment = align
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(6)
        if indent:
            p.paragraph_format.first_line_indent = Inches(0.5)
        run = p.add_run(text)
        run.font.name = 'Arial'
        run.font.size = Pt(12)
        return p

    def p_chapter_head(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(12)
        run = p.add_run(text)
        run.font.name = 'Arial'
        run.font.size = Pt(14)
        run.font.bold = True
        return p

    def p_heading_2(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(4)
        run = p.add_run(text)
        run.font.name = 'Arial'
        run.font.size = Pt(12)
        run.font.bold = True
        return p

    def p_heading_3(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.first_line_indent = Inches(0.5)
        run = p.add_run(text)
        run.font.name = 'Arial'
        run.font.size = Pt(12)
        run.font.bold = True
        run.font.italic = True
        return p

    def p_table_title(table_num, table_name):
        p1 = doc.add_paragraph()
        p1.paragraph_format.line_spacing = 1.0
        p1.paragraph_format.space_before = Pt(14)
        p1.paragraph_format.space_after = Pt(2)
        r1 = p1.add_run(table_num)
        r1.font.name = 'Arial'
        r1.font.size = Pt(11)
        r1.font.bold = True

        p2 = doc.add_paragraph()
        p2.paragraph_format.line_spacing = 1.0
        p2.paragraph_format.space_before = Pt(0)
        p2.paragraph_format.space_after = Pt(6)
        r2 = p2.add_run(table_name)
        r2.font.name = 'Arial'
        r2.font.size = Pt(11)
        r2.font.italic = True

    def p_figure_title(fig_num, fig_title):
        p1 = doc.add_paragraph()
        p1.paragraph_format.line_spacing = 1.0
        p1.paragraph_format.space_before = Pt(14)
        p1.paragraph_format.space_after = Pt(2)
        r1 = p1.add_run(fig_num)
        r1.font.name = 'Arial'
        r1.font.size = Pt(11)
        r1.font.bold = True

        p2 = doc.add_paragraph()
        p2.paragraph_format.line_spacing = 1.0
        p2.paragraph_format.space_before = Pt(0)
        p2.paragraph_format.space_after = Pt(6)
        r2 = p2.add_run(fig_title)
        r2.font.name = 'Arial'
        r2.font.size = Pt(11)
        r2.font.italic = True

    def p_image(img_path, width_in_inches=6.0):
        if os.path.exists(img_path):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(8)
            run = p.add_run()
            run.add_picture(img_path, width=Inches(width_in_inches))
        else:
            p_body(f"[{os.path.basename(img_path)}]", indent=False, align=WD_ALIGN_PARAGRAPH.CENTER)

    def p_bullet(bullet_char, text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.left_indent = Inches(0.5)
        p.paragraph_format.first_line_indent = Inches(-0.25)
        r_b = p.add_run(bullet_char + " ")
        r_b.font.name = 'Arial'
        r_b.font.size = Pt(12)
        r_b.font.bold = True
        r_t = p.add_run(text)
        r_t.font.name = 'Arial'
        r_t.font.size = Pt(12)

    def p_term(term, definition):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.left_indent = Inches(0.5)
        p.paragraph_format.first_line_indent = Inches(-0.5)
        r1 = p.add_run(term + " ")
        r1.font.name = 'Arial'
        r1.font.size = Pt(12)
        r1.font.bold = True
        r2 = p.add_run(definition)
        r2.font.name = 'Arial'
        r2.font.size = Pt(12)

    def p_objective_item(num_str, text, sub=False):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(3)
        if sub:
            p.paragraph_format.left_indent = Inches(0.85)
            p.paragraph_format.first_line_indent = Inches(-0.35)
            r_b = p.add_run(num_str + " ")
            r_b.font.name = 'Arial'
            r_b.font.size = Pt(12)
            r_t = p.add_run(text)
            r_t.font.name = 'Arial'
            r_t.font.size = Pt(12)
        else:
            p.paragraph_format.left_indent = Inches(0.5)
            p.paragraph_format.first_line_indent = Inches(-0.25)
            r_b = p.add_run(num_str + " ")
            r_b.font.name = 'Arial'
            r_b.font.size = Pt(12)
            r_t = p.add_run(text)
            r_t.font.name = 'Arial'
            r_t.font.size = Pt(12)
        return p

    # ==================== 1. PRELIMINARY PAGES (FRONT MATTER) ====================
    print("Generating Front Matter / Preliminary Pages...")

    # --- TITLE PAGE ---
    p_center = lambda t, bold=False, size=12, space_after=6: doc.add_paragraph().add_run(t).font.__setattr__('name', 'Arial') or doc.paragraphs[-1].__setattr__('alignment', WD_ALIGN_PARAGRAPH.CENTER) or doc.paragraphs[-1].paragraph_format.__setattr__('space_before', Pt(0)) or doc.paragraphs[-1].paragraph_format.__setattr__('space_after', Pt(space_after)) or doc.paragraphs[-1].paragraph_format.__setattr__('line_spacing', 1.5) or doc.paragraphs[-1].runs[0].__setattr__('bold', bold) or doc.paragraphs[-1].runs[0].font.__setattr__('size', Pt(size))

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(36)
    p_title.paragraph_format.space_after = Pt(36)
    p_title.paragraph_format.line_spacing = 1.5
    r_t = p_title.add_run("AQUACULTURE VALUE CHAIN MANAGEMENT SYSTEM WITH PREDICTIVE ANALYTICS FOR SILAY SUPERWORM & CRAYFISH")
    r_t.font.name = 'Arial'
    r_t.font.size = Pt(14)
    r_t.font.bold = True

    p_mid = doc.add_paragraph()
    p_mid.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_mid.paragraph_format.space_before = Pt(18)
    p_mid.paragraph_format.space_after = Pt(24)
    p_mid.paragraph_format.line_spacing = 1.5
    r_mid = p_mid.add_run("A Capstone Project\nPresented to the Faculty of the\nCollege of Computer Studies\nCarlos Hilado Memorial State University\nTalisay City, Negros Occidental\n\nIn Partial Fulfillment\nof the Requirements for the Degree\nBACHELOR OF SCIENCE IN INFORMATION SYSTEMS")
    r_mid.font.name = 'Arial'
    r_mid.font.size = Pt(12)

    p_auth = doc.add_paragraph()
    p_auth.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_auth.paragraph_format.space_before = Pt(24)
    p_auth.paragraph_format.space_after = Pt(12)
    p_auth.paragraph_format.line_spacing = 1.5
    r_auth = p_auth.add_run("By\n\nJOHN VINCENT HULLEZA\nKYMER OPJER\nMICHAEL DAVE HERBAIS\n\n\nSEPTEMBER 2026")
    r_auth.font.name = 'Arial'
    r_auth.font.size = Pt(12)

    # --- TABLE OF CONTENTS ---
    doc.add_page_break()
    p_chapter_head("TABLE OF CONTENTS")

    toc_items = [
        ("TITLE PAGE", "1"),
        ("TABLE OF CONTENTS", "2"),
        ("LIST OF FIGURES", "4"),
        ("LIST OF TABLES", "6"),
        ("CHAPTER I: INTRODUCTION", "1"),
        ("    1.1 Background of the Study", "1"),
        ("    1.2 Objectives of the Study", "3"),
        ("    1.3 Scope and Delimitations of the Study", "5"),
        ("    1.4 Significance of the Study", "6"),
        ("    1.5 Definition of Terms", "7"),
        ("CHAPTER II: REVIEW OF RELATED LITERATURE AND STUDIES", "9"),
        ("    2.1 Global and Local Perspectives on Aquaculture Value Chains", "9"),
        ("    2.2 Digital Farm Management, IoT, and Smart Monitoring Systems", "11"),
        ("    2.3 Predictive Analytics and Machine Learning in Agri-Aquaculture", "13"),
        ("    2.4 Synthesis and Research Gap", "15"),
        ("    2.5 Summary Tables of Related Literature and Studies", "16"),
        ("CHAPTER III: METHODOLOGY", "19"),
        ("    3.1 Systems Development Life Cycle (Agile Scrum)", "19"),
        ("    3.2 Operational Framework", "23"),
        ("    3.3 Data Flow Diagram (Levels 0, 1, 2)", "25"),
        ("    3.4 Entity Relationship Diagram (ERD)", "35"),
        ("    3.5 UML Use Case Diagram", "37"),
        ("    3.6 Use Case Scenarios (Tables 3 to 15)", "39"),
        ("    3.7 Data Dictionary (Tables 16 to 30)", "52"),
        ("    3.8 System Requirements (Hardware, Software, Network)", "67"),
        ("    3.9 Software Testing Tools and Techniques", "71"),
        ("    3.10 System Evaluation Instrument (ISO/IEC 25010:2011)", "73"),
        ("    3.11 Evaluation Respondents and Sampling", "75"),
        ("    3.12 Ethical Considerations", "76"),
        ("CHAPTER IV: RESULTS AND DISCUSSION", "78"),
        ("    4.1 Results of the Study (Figures 14 to 29 Interface Walkthroughs)", "78"),
        ("    4.2 Functionality Testing Results", "94"),
        ("        4.2.1 Black-Box Testing Results (Tables 34 to 45, 68 Test Cases)", "94"),
        ("        4.2.2 Module Execution Summary Table (Table 46)", "106"),
        ("        4.2.3 White-Box Structural Testing Results (Tables 47 to 49, 16 Cases)", "108"),
        ("    4.3 Software Quality Evaluation Results (Table 50, ISO 25010)", "112"),
        ("CHAPTER V: SUMMARY OF FINDINGS, CONCLUSIONS, AND RECOMMENDATIONS", "116"),
        ("    5.1 Summary of Findings", "116"),
        ("    5.2 Conclusions", "118"),
        ("    5.3 Recommendations", "120"),
        ("REFERENCES", "123"),
        ("APPENDICES", "128"),
        ("    Appendix A: ISO/IEC 25010:2011 Software Quality Evaluation Questionnaire", "128"),
        ("    Appendix B: Letter to Beneficiary (Silay Superworm & Crayfish)", "132"),
        ("    Appendix C: Letter to Capstone Project Adviser", "133"),
        ("    Appendix D: Black-Box Functional Test Suites (Alpha Testing)", "134"),
        ("    Appendix E: Sample Black-Box Testing (Beta Testing Evaluation Sheets)", "175"),
        ("    Appendix F: White-Box Structural Test Suites (Alpha Testing)", "182"),
        ("    Appendix G: Sample White-Box Testing (Beta Testing Code Execution Logs)", "190"),
        ("    Appendix H: Grammarian's Certification", "195"),
        ("    Appendix I: PERT-CPM Network Diagram", "196"),
        ("    Appendix J: Project Gantt Chart", "197"),
        ("    Appendix K: System User Manual and Operational Guide", "198"),
        ("    Appendix L: Curriculum Vitae of Proponents", "225")
    ]

    for title, pg in toc_items:
        p_toc = doc.add_paragraph()
        p_toc.paragraph_format.line_spacing = 1.15
        p_toc.paragraph_format.space_before = Pt(1)
        p_toc.paragraph_format.space_after = Pt(2)
        p_toc.paragraph_format.tab_stops.add_tab_stop(Inches(6.0), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.SPACES)
        
        r1 = p_toc.add_run(title)
        r1.font.name = 'Arial'
        r1.font.size = Pt(11)
        if not title.startswith("    "):
            r1.font.bold = True
        
        p_toc.add_run("\t")

        r2 = p_toc.add_run(pg)
        r2.font.name = 'Arial'
        r2.font.size = Pt(11)
        if not title.startswith("    "):
            r2.font.bold = True

    # --- LIST OF FIGURES ---
    doc.add_page_break()
    p_chapter_head("LIST OF FIGURES")

    figures_list = [
        ("Figure 1", "Agile Scrum Development Model", "20"),
        ("Figure 2", "System Operational Framework", "24"),
        ("Figure 3", "Context Diagram (Level 0)", "26"),
        ("Figure 4", "Level 1 Data Flow Diagram (DFD)", "28"),
        ("Figure 5", "Level 2 DFD: Product Browsing and Selection", "29"),
        ("Figure 6", "Level 2 DFD: Order Management", "30"),
        ("Figure 7", "Level 2 DFD: Payment and Set Location", "31"),
        ("Figure 8", "Level 2 DFD: Delivery Dispatch", "32"),
        ("Figure 9", "Level 2 DFD: Farm Operations Management", "33"),
        ("Figure 10", "Level 2 DFD: Report and Monitoring", "34"),
        ("Figure 11", "Level 2 DFD: Predictive Analytics", "35"),
        ("Figure 12", "Entity-Relationship Diagram (ERD)", "36"),
        ("Figure 13", "UML Use Case Diagram", "38"),
        ("Figure 14", "Unified Login and Multi-Role Authentication", "79"),
        ("Figure 15", "Executive Dashboard and Real-Time Farm KPIs", "80"),
        ("Figure 16", "Pond, Cabin Rack, and Tank Cultivation Management", "81"),
        ("Figure 17", "Feed Formulation and Daily Supply Logging", "82"),
        ("Figure 18", "Azula Cultivation and Pond Sanitization Monitoring", "83"),
        ("Figure 19", "Harvest Scheduling and Production Calendar", "84"),
        ("Figure 20", "Commercial Product Catalog and Dual-Unit Pricing", "85"),
        ("Figure 21", "Customer Online Storefront and Shopping Cart", "86"),
        ("Figure 22", "Shopping Cart and Quantity Validation", "87"),
        ("Figure 23", "Checkout and PayMongo GCash / COD Settlement", "88"),
        ("Figure 24", "Sales Order Fulfillment and Status Tracking", "89"),
        ("Figure 25", "Courier Dispatch and Route Map Visualization", "90"),
        ("Figure 26", "Delivery Rider Portal and Proof of Delivery (POD)", "91"),
        ("Figure 27", "Predictive Demand and Harvest Yield Forecasting", "92"),
        ("Figure 28", "Customer Segmentation and Market Clustering", "93"),
        ("Figure 29", "Executive Financial Reports and System Audit Trail", "94")
    ]

    for fnum, ftitle, fpage in figures_list:
        p_lf = doc.add_paragraph()
        p_lf.paragraph_format.line_spacing = 1.15
        p_lf.paragraph_format.space_before = Pt(1)
        p_lf.paragraph_format.space_after = Pt(2)
        p_lf.paragraph_format.tab_stops.add_tab_stop(Inches(6.0), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.SPACES)
        
        r1 = p_lf.add_run(f"{fnum}  {ftitle}")
        r1.font.name = 'Arial'
        r1.font.size = Pt(11)
        
        p_lf.add_run("\t")
        
        r2 = p_lf.add_run(fpage)
        r2.font.name = 'Arial'
        r2.font.size = Pt(11)

    # --- LIST OF TABLES ---
    doc.add_page_break()
    p_chapter_head("LIST OF TABLES")

    tables_list = [
        ("Table 1", "Synthesis of Related Literature", "17"),
        ("Table 2", "Synthesis of Related Systems", "18"),
        ("Table 3", "Authentication and Role-Based Access Control", "40"),
        ("Table 4", "Executive Dashboard and Sanitization Alerts", "41"),
        ("Table 5", "Create and Manage Stock Batches", "42"),
        ("Table 6", "Configure Ponds, Racks, and Facilities", "43"),
        ("Table 7", "Feed Administration and Maintenance Logs", "44"),
        ("Table 8", "Product Catalog and Dual-Unit Pricing", "45"),
        ("Table 9", "Operational and Administrative Expenses", "46"),
        ("Table 10", "Storefront Browsing, Cart, and Checkout", "47"),
        ("Table 11", "Order Fulfillment and Lifecycle State Machine", "48"),
        ("Table 12", "Courier Dispatch and Route Map Visualization", "49"),
        ("Table 13", "Mobile Proof of Delivery (POD) Confirmation", "50"),
        ("Table 14", "Export Financial and Audit Reports", "51"),
        ("Table 15", "Predictive Regression and K-Means Clustering", "52"),
        ("Table 16", "User Credentials Data Table", "53"),
        ("Table 17", "User Profiles Data Table", "54"),
        ("Table 18", "Customers Data Table", "55"),
        ("Table 19", "Delivery Riders Data Table", "56"),
        ("Table 20", "Operations Ponds and Racks Data Table", "57"),
        ("Table 21", "Stock Batches Data Table", "58"),
        ("Table 22", "Feeding Logs Data Table", "59"),
        ("Table 23", "Feed Inventory Data Table", "60"),
        ("Table 24", "Harvest Schedules Data Table", "61"),
        ("Table 25", "Harvest Records Data Table", "62"),
        ("Table 26", "Inventory Items Data Table", "63"),
        ("Table 27", "Orders Data Table", "64"),
        ("Table 28", "Order Deliveries Data Table", "65"),
        ("Table 29", "Payments Data Table", "66"),
        ("Table 30", "Expenses Data Table", "67"),
        ("Table 31", "Hardware Specifications", "69"),
        ("Table 32", "Software and Environment Specifications", "70"),
        ("Table 33", "5-Point Likert Scale and Verbal Interpretation", "74"),
        ("Table 34", "User Authentication and Security Test Results", "95"),
        ("Table 35", "Executive Dashboard Analytics Test Results", "96"),
        ("Table 36", "Cultivation Management Test Results", "97"),
        ("Table 37", "Feed Formulation and Supply Logs Test Results", "98"),
        ("Table 38", "Azula Cultivation & Sanitization Test Results", "99"),
        ("Table 39", "Harvest Scheduling Calendar Test Results", "100"),
        ("Table 40", "Product Catalog and Dual Pricing Test Results", "101"),
        ("Table 41", "Customer Storefront and Cart Test Results", "102"),
        ("Table 42", "Payment Settlement Test Results", "103"),
        ("Table 43", "Order Fulfillment State Machine Test Results", "104"),
        ("Table 44", "Courier Dispatch and Route Mapping Test Results", "105"),
        ("Table 45", "Predictive Forecasting Test Results", "106"),
        ("Table 46", "Black-Box Functional Testing Execution Summary", "107"),
        ("Table 47", "White-Box Testing: Core Security and RBAC", "109"),
        ("Table 48", "White-Box Testing: Business Logic State Machine", "110"),
        ("Table 49", "White-Box Testing: Database Concurrency", "111"),
        ("Table 50", "ISO/IEC 25010:2011 Software Quality Evaluation", "114")
    ]

    for tnum, ttitle, tpage in tables_list:
        p_lt = doc.add_paragraph()
        p_lt.paragraph_format.line_spacing = 1.15
        p_lt.paragraph_format.space_before = Pt(1)
        p_lt.paragraph_format.space_after = Pt(2)
        p_lt.paragraph_format.tab_stops.add_tab_stop(Inches(6.0), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.SPACES)
        
        r1 = p_lt.add_run(f"{tnum}  {ttitle}")
        r1.font.name = 'Arial'
        r1.font.size = Pt(11)
        
        p_lt.add_run("\t")
        
        r2 = p_lt.add_run(tpage)
        r2.font.name = 'Arial'
        r2.font.size = Pt(11)

    # ==================== 2. CHAPTER I: INTRODUCTION ====================
    print("Generating Chapter I...")
    doc.add_page_break()
    p_chapter_head("CHAPTER I\nINTRODUCTION")

    p_heading_2("1.1 Background of the Study")
    p_body("Aquaculture is one of the fastest-growing food production sectors globally, playing an increasingly crucial role in enhancing global food security and providing sustainable protein sources (Food and Agriculture Organization [FAO], 2022). In the Philippines, the sector significantly contributes to national economic development, rural livelihoods, and domestic food supply across diverse sub-sectors, ranging from large-scale commercial fisheries to specialized inland smallholder enterprises (Durano et al., 2025; Salayo et al., 2021). Within this expanding landscape, the cultivation of alternative aquatic and biological species—notably the Australian redclaw crayfish (Cherax quadricarinatus) and superworms (Zophobas morio)—has emerged as a highly promising agribusiness niche. Redclaw crayfish cultivation has gained substantial traction due to the species' rapid growth rates, high commercial market value, and favorable adaptability to tropical climatic conditions (Cheng et al., 2025; Rigg et al., 2020). Concurrently, superworm production has expanded rapidly, serving both as high-protein commercial pet feeds and as a sustainable, cost-effective feed ingredient for aquaculture and poultry diets (de Sousa Araujo et al., 2025; Oliveira et al., 2025; Rumbos & Athanassiou, 2021).", indent=True)

    p_body("Despite these compelling economic advantages, local micro and small-scale aquaculture enterprises, such as Silay Superworm & Crayfish situated in Barangay Lantad, Silay City, Negros Occidental, encounter substantial operational bottlenecks across their internal value chains. As highlighted by Bush et al. (2019) and WorldFish (2022), smallholder agri-aquaculture value chains in developing economies frequently suffer from structural fragmentation, localized information asymmetry, and poor digital connectivity between upstream production facilities and downstream consumer markets. At Silay Superworm & Crayfish, day-to-day administrative procedures—including pond environmental monitoring, sanitization tracking, feeding schedule administration, stock transfers, batch lifecycle recording, and point-of-sale customer order fulfillment—are documented using manual, paper-bound logbooks and disparate, unstructured messaging channels. This heavy reliance on manual data entry causes chronic record inconsistencies, administrative delays, and inventory inaccuracies, creating severe blind spots that impede the farm owner's ability to maintain real-time operational visibility and sound financial control.", indent=True)

    p_body("Furthermore, managing perishable biological stock requires proactive inventory forecasting and data-driven harvest planning. Without automated analytical tools, farm operators struggle to accurately correlate input costs (e.g., feed expenditures and labor overhead) with operational yield outputs, often resulting in feed waste, delayed harvests, or unexpected stock shortages during peak market demand periods (Hu et al., 2025; Tina et al., 2025). Digital supply chain integration and business intelligence offer transformative solutions to these challenges, enabling real-time inventory synchronization, transparent order fulfillment, and automated harvest scheduling (Chiu et al., 2022; Wu et al., 2025). To directly resolve these operational deficits, this capstone study designs, develops, and implements the Aquaculture Value Chain Management System with Predictive Analytics for Silay Superworm & Crayfish. The system provides a centralized, web-based platform that digitizes pond lifecycle operations, automates direct-to-consumer e-commerce transactions, coordinates delivery logistics with automated route mapping, and integrates linear regression predictive modeling and K-Means customer segmentation clustering to drive operational sustainability and data-informed decision-making.", indent=True)

    p_heading_2("1.2 Objectives of the Study")
    p_body("The General objective of this study is to design and develop the Aquaculture Value Chain Management System with Predictive Analytics for Silay Superworm & Crayfish that improves the monitoring of farm operations, feed inventory, harvest schedules, direct-to-consumer sales, courier dispatching, and predictive demand analytics within the aquaculture enterprise.", indent=True)
    p_body("Specifically, this study aims to:", indent=False)

    p_objective_item("1.", "Design and develop a web-based Aquaculture Value Chain Management System with Predictive Analytics with the following features:", sub=False)
    p_objective_item("1.1.", "A farm operations and pond management feature that enables the farm owner to monitor and record multi-species aquaculture operations across 15 outdoor earthen and breeding ponds (Ponds 1–10 Main and Ponds 1–5 Breeding), an indoor superworm rearing cabin with coordinate shelf grids, an indoor Azula bio-feed cultivation sector, and 15-day pond sanitization alert protocols;", sub=True)
    p_objective_item("1.2.", "A feed supply and feeding management feature that logs daily nutritional feeding checklists across commercial feed varieties (Integra 1000, 2000, 1, PO2, PO1) with automated stock deduction and inventory balance tracking;", sub=True)
    p_objective_item("1.3.", "A harvest scheduling and production calendar feature that projects harvest readiness windows, tracks elapsed stocking days, and visualizes scheduled farm activities on an interactive color-coded harvest calendar;", sub=True)
    p_objective_item("1.4.", "A commercial product catalog and dual-unit pricing feature that maintains multi-species catalog items (Australian Redclaw Crayfish, Superworms, and Azula bio-feed) with dual pricing architectures per piece (₱/pc) and per kilogram (₱/kg) alongside piece-per-kilogram conversion density ratios;", sub=True)
    p_objective_item("1.5.", "A customer storefront and cart management feature that provides an interactive e-commerce product showcase, real-time cart calculations, stock ceiling validation, and fulfillment mode selection between on-site farm pickup (with GPS coordinates and satellite photo) and doorstep delivery (with interactive address selection and GPS pin placement);", sub=True)
    p_objective_item("1.6.", "A multi-tier payment settlement feature that supports flexible payment options including Cash on Delivery (COD), Cash on Pickup, and automated PayMongo GCash Online Payment Gateway integration with secure checkout;", sub=True)
    p_objective_item("1.7.", "A sales order fulfillment state machine feature that enforces a structured four-stage order lifecycle (Pending, Approved & Scheduled, Dispatched, Delivered) with automated inventory stock deduction upon verified delivery completion;", sub=True)
    p_objective_item("1.8.", "A courier dispatch and mobile rider portal feature that coordinates delivery operations through courier vehicle registration, rider duty status toggling (Available / Off Duty), turn-by-turn Leaflet OpenStreetMap navigation, direct customer calling, and Proof of Delivery (POD) photo and recipient signature confirmation;", sub=True)
    p_objective_item("1.9.", "A predictive demand analytics feature that applies Ordinary Least Squares (OLS) Linear Regression to forecast 7-day daily sales revenue, analyze historical sales trends, and project upcoming harvest yields;", sub=True)
    p_objective_item("1.10.", "A customer segmentation and market clustering feature that analyzes geographical demand distribution across Silay City, Talisay City, and Bacolod City, product revenue share proportions, and K-Means machine learning clustering based on purchasing frequency, monetary value, and geographical location; and", sub=True)
    p_objective_item("1.11.", "An executive reports and audit trail feature that generates filterable, printable administrative documentation (Sales Ledgers, Weekly Summaries, Pond Feeding Logs, Official Customer Billing Slips) and maintains three-tiered immutable system audit logs.", sub=True)

    p_objective_item("2.", "Test the functionality of the developed system.", sub=False)

    p_objective_item("3.", "Evaluate the quality of the system using ISO 25010:2011 standards in terms of:", sub=False)
    p_objective_item("3.1.", "Functional suitability;", sub=True)
    p_objective_item("3.2.", "Performance efficiency;", sub=True)
    p_objective_item("3.3.", "Compatibility;", sub=True)
    p_objective_item("3.4.", "Usability;", sub=True)
    p_objective_item("3.5.", "Reliability;", sub=True)
    p_objective_item("3.6.", "Security;", sub=True)
    p_objective_item("3.7.", "Maintainability; and", sub=True)
    p_objective_item("3.8.", "Portability", sub=True)

    p_objective_item("4.", "Develop a User’s Guide for the developed system.", sub=False)

    p_heading_2("1.3 Scope and Delimitations of the Study")
    p_body("This capstone project focuses on the design, implementation, and empirical evaluation of a web-based value chain management system for Silay Superworm & Crayfish, located in Barangay Lantad, Silay City, Negros Occidental. The system encompasses end-to-end operational modules including pond environment and sanitization cycle logging, feed consumption and balance recording, batch growth stage tracking, multi-category inventory management (live crayfish, packaged superworms, specialized feeds, and biological fertilizers), customer online shopping cart and checkout, multi-tier payment recording (Cash on Delivery and PayMongo GCash checkout), delivery rider dispatching with integrated Leaflet OpenStreetMap route visualization, operational expense categorization, and printable financial reporting.", indent=True)

    p_body("The analytical core of the platform utilizes scikit-learn machine learning libraries to generate short-term revenue forecasts, harvest yield predictions, and customer purchasing segmentation. The system was developed using Python and the Django web framework for backend logic, PostgreSQL/SQLite for relational database storage, and HTML5, Vanilla CSS, and modern JavaScript for responsive frontend user interfaces.", indent=True)

    p_body("The study is subject to several delimitations. The platform is implemented as a web application optimized for modern desktop and mobile browsers and does not include a native standalone mobile application (APK/IPA). While the system features digital payment logging, it does not directly process automated banking payment gateways beyond PayMongo GCash checkout and cash settlement. Delivery tracking utilizes OpenStreetMap routing coordinates rather than active real-time GPS telemetry streaming. Finally, the empirical evaluation of the system is delimited to the farm owner, delivery riders, registered enterprise customers, and invited IT professional evaluators situated in Negros Occidental.", indent=True)

    p_heading_2("1.4 Significance of the Study")
    p_body("The successful development and deployment of this capstone project provides substantial practical and academic benefits to multiple stakeholder groups:", indent=True)

    p_bullet("•", "Silay Superworm & Crayfish Management: Provides the farm owner with centralized real-time operational visibility, eliminating manual bookkeeping errors, preventing inventory shrinkage, optimizing feed supply allocation, and providing data-driven sales and harvest forecasts to maximize operational profitability.")
    p_bullet("•", "Delivery Personnel and Logistics Riders: Equips delivery staff with streamlined mobile-accessible dispatch schedules, customer contact directories, delivery destination maps, and proof-of-delivery logging.")
    p_bullet("•", "Enterprise Customers: Offers customers a seamless, transparent digital ordering catalog, direct order status tracking, digital transaction histories, and flexible payment options.")
    p_bullet("•", "Local Aquaculture Agribusiness Sector: Demonstrates the practical viability and economic impact of deploying low-cost, open-source web technologies and predictive analytics in micro, small, and medium aquaculture enterprises.")
    p_bullet("•", "Future Researchers and Academia: Serves as a comprehensive technical reference and foundational architecture for developing intelligent value chain systems and decision-support platforms in the broader agricultural and fisheries domain.")

    p_heading_2("1.5 Definition of Terms")
    p_body("To establish conceptual and operational clarity, the following key terms are defined within the context of this study:", indent=True)

    p_term("Aquaculture", "The controlled breeding, rearing, and harvesting of aquatic organisms. In this study, it specifically refers to the commercial farming of Australian redclaw crayfish and superworm larvae managed by the enterprise.")
    p_term("Value Chain Management", "The comprehensive coordination of all business activities required to bring a biological product from initial pond rearing through harvest, inventory packaging, direct sales, and final logistics delivery.")
    p_term("Predictive Analytics", "Advanced analytical techniques that extract historical data patterns to forecast future outcomes. In this system, it refers to Linear Regression algorithms applied to predict future sales revenues and expected pond harvest yields.")
    p_term("K-Means Clustering", "An unsupervised machine learning algorithm that partitions customer data into distinct clusters based on purchase frequency, total order monetary value, and geographical location.")
    p_term("Django Web Framework", "A high-level, open-source Python web framework that follows the Model-View-Template (MVT) architectural pattern, utilized to build the backend server and API endpoints of the system.")
    p_term("ISO/IEC 25010:2011", "An internationally recognized software engineering standard for evaluating system and software product quality across eight core characteristics.")

    # ==================== 3. CHAPTER II: LITERATURE REVIEW ====================
    print("Generating Chapter II...")
    doc.add_page_break()
    p_chapter_head("CHAPTER II\nREVIEW OF RELATED LITERATURE AND STUDIES")

    p_body("This chapter presents a comprehensive synthesis of local and international literature, empirical studies, and technological advancements relevant to aquaculture value chain digitization, IoT-based farm monitoring, predictive analytics in agribusiness, and web-based enterprise resource management.", indent=True)

    p_heading_2("2.1 Global and Local Perspectives on Aquaculture Value Chains")
    p_body("Aquaculture value chains represent intricate socio-ecological systems linking upstream hatchery inputs, midstream farm husbandry, and downstream distribution channels (Bush et al., 2019; FAO, 2022). Across Southeast Asia, small-scale aquaculture producers constitute the economic backbone of local rural economies but face chronic structural barriers, including severe information asymmetry, volatile farmgate prices, uncoordinated market access, and high post-harvest losses (WorldFish, 2021, 2022). In the Philippines, the fisheries and aquaculture sector provides essential sustenance and employment, yet smallholder enterprises remain highly vulnerable to environmental fluctuations and fragmented supply chain coordination (Macusi et al., 2021; Salayo et al., 2021). Recent policy reviews emphasize the urgent necessity of modernizing value chains through accessible digital infrastructures to ensure equitable market access and enterprise resilience (Durano et al., 2025).", indent=True)

    p_body("Specialized aquaculture commodities, such as the Australian redclaw crayfish (Cherax quadricarinatus), present lucrative commercial opportunities due to their premium culinary demand, hardy physiological tolerance, and favorable feed conversion efficiency (Cheng et al., 2025; Rigg et al., 2020). However, successful cultivation demands rigorous monitoring of pond stocking density, feeding frequencies, and water quality parameters, as suboptimal environmental conditions rapidly increase juvenile mortality and cannibalism (Martínez et al., 2024; Yang et al., 2025). Concurrently, commercial superworm (Zophobas morio) rearing has expanded rapidly as an alternative high-protein feed source for aquatic livestock, offering sustainable solutions to escalating commercial feed costs (Asimaki et al., 2025; de Sousa Araujo et al., 2025; Prachom et al., 2021; Ragozzino-Paulino et al., 2025; Rumbos & Athanassiou, 2021). Despite these complementary production models, micro-enterprises combining aquatic and insect rearing encounter severe managerial complexity, underscoring the vital need for unified, digitized management systems.", indent=True)

    p_heading_2("2.2 Digital Farm Management, IoT, and Smart Monitoring Systems")
    p_body("Recent technological revolutions in smart agriculture and the Internet of Things (IoT) have catalyzed substantial transformations across aquaculture management (Chiu et al., 2022; Tina et al., 2025). Automated sensor platforms capable of capturing real-time dissolved oxygen, pH, temperature, and ammonia levels have been extensively developed and tested in both international and Philippine fishpond environments (Abdurrasyid et al., 2021; Al Mamun et al., 2024; Bouzidi et al., 2025; Caluag et al., 2025; Gulifardo et al., 2025; Tolentino, 2021; Xu et al., 2023). Studies in solar-powered IoT aquaponics and automated water recirculating systems demonstrate that real-time environmental data acquisition significantly mitigates mortality risks and optimizes feed utilization (Dawa et al., 2022; Garcia & Tibo, 2023). While hardware sensor deployments provide granular environmental telemetry, literature indicates that micro-scale producers frequently lack the capital infrastructure required for full sensor hardware adoption, making lightweight, web-based digital logging platforms the most viable and cost-effective operational alternative (Zapata et al., 2023).", indent=True)

    p_heading_2("2.3 Predictive Analytics and Machine Learning in Agri-Aquaculture")
    p_body("The application of machine learning algorithms and statistical predictive analytics has redefined operational planning in commercial aquaculture (Chang et al., 2021; Wu et al., 2025). Time-series forecasting models, Autoregressive Integrated Moving Average (ARIMA/SARIMA) architectures, and linear regression models are increasingly deployed to forecast fish harvest biomass, historical market price trends, and consumer demand curves (Hu et al., 2025; Jimmy Jr & Gente, 2024; Paz, 2019). By transforming historical feeding rates, water conditions, and sales records into mathematical forecasting pipelines, farm operators can anticipate harvest timelines, prevent stock shortages, and optimize working capital allocations. Unsupervised machine learning methods, particularly K-Means clustering, have proven highly effective in customer segmentation and regional sales analysis, enabling agribusinesses to identify high-value buyer cohorts and tailor logistics routing accordingly (Chang et al., 2021).", indent=True)

    p_heading_2("2.4 Synthesis and Research Gap")
    p_body("While existing literature extensively documents isolated IoT water quality monitoring hardware or theoretical predictive models for commercial marine fisheries, there is a notable absence of unified, end-to-end value chain management platforms tailored specifically for integrated, small-scale superworm and crayfish aquaculture enterprises. Existing commercial ERP platforms are prohibitively expensive, overly complex, and ill-suited for local farm operational realities. This study directly bridges this critical technological gap by designing, building, and deploying a bespoke web-based management system integrating pond lifecycle monitoring, e-commerce order processing, rider dispatching, and predictive analytics into a unified, cost-effective platform.", indent=True)

    p_heading_2("2.5 Summary Tables of Related Literature and Studies")
    p_body("To provide a structured comparative overview of existing literature and empirical systems, the reviewed sources are categorized into Related Literature (Table 1) and Related Studies (Table 2) below:", indent=True)

    # Table 1
    p_table_title("Table 1", "Summary of Related Literature on Aquaculture Management and Smart Systems")
    tbl1 = doc.add_table(rows=7, cols=4)
    tbl1.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_apa_table_borders(tbl1)

    t1_headers = ["Authors & Year", "Title / Publication", "Core Focus & Domain", "Relevance to the Current Study"]
    t1_data = [
        ["Food and Agriculture Organization (2022)", "The State of World Fisheries and Aquaculture 2022 (FAO)", "Global status and economic growth of aquaculture production.", "Establishes macro context and global importance of aquaculture food security."],
        ["Bush et al. (2019)", "Global Food Security, 21, 63–71", "Spatial and social transformations in seafood value chains.", "Provides theoretical foundation for addressing value chain fragmentation."],
        ["Rigg et al. (2020)", "Reviews in Aquaculture, 13(1), 145–167", "Aquaculture of redclaw crayfish (Cherax quadricarinatus).", "Guides biological parameters, pond stocking, and growth life cycle modeling."],
        ["Rumbos & Athanassiou (2021)", "Journal of Insects as Food and Feed, 7(5)", "Superworm (Zophobas morio) as high-protein commercial nutrient source.", "Supports superworm cultivation parameters and feed inventory categorization."],
        ["Wu et al. (2025)", "Sustainability, 17(11), 5084", "Deep learning and digital technologies for sustainable aquaculture.", "Informs implementation of predictive analytics and automated forecasting."],
        ["Durano et al. (2025)", "Marine Policy, 180, 106810", "Fisheries sector modernization and digital integration in the Philippines.", "Highlights the necessity of localized digital tools for Philippine smallholders."]
    ]

    col_widths_t1 = [Inches(1.5), Inches(1.5), Inches(1.5), Inches(1.5)]
    for row_idx, row_data in enumerate([t1_headers] + t1_data):
        row = tbl1.rows[row_idx]
        is_header = (row_idx == 0)
        is_last = (row_idx == len(t1_data))
        for col_idx, text in enumerate(row_data):
            cell = row.cells[col_idx]
            cell.width = col_widths_t1[col_idx]
            cell.vertical_alignment = WD_ALIGN_VERTICAL.TOP
            if is_header:
                set_apa_header_cell(cell)
            else:
                set_apa_data_cell(cell, is_last_row=is_last)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if is_header else WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(4) if is_header else Pt(2)
            p.paragraph_format.space_after = Pt(4) if is_header else Pt(2)
            p.paragraph_format.line_spacing = None
            run = p.add_run(text)
            run.font.name = 'Arial'
            run.font.size = Pt(10)
            if is_header:
                run.bold = True

    # Table 2
    doc.add_paragraph().paragraph_format.space_before = Pt(6)
    p_table_title("Table 2", "Summary of Related Empirical Systems and Technical Studies")
    tbl2 = doc.add_table(rows=7, cols=4)
    tbl2.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_apa_table_borders(tbl2)

    t2_headers = ["Authors & Year", "System / Study Title", "Key Technologies & Methodologies", "Comparative Contribution & Findings"]
    t2_data = [
        ["Chiu et al. (2022)", "Smart Aquaculture Farm Management System", "IoT Sensors, AI Surrogate Models, Decision Support", "Demonstrates the efficacy of integrated digital platforms for farm monitoring."],
        ["Gulifardo et al. (2025)", "iPond: IoT Water Quality Monitoring System", "Arduino Microcontrollers, Cloud Telemetry, Mobile App", "Validates the necessity of tracking water parameters in Philippine fishponds."],
        ["Dawa et al. (2022)", "IoT-Based Aquaponics Management System", "Automated Sensor Feedback, Climate-Adaptive Controls", "Highlights importance of automated record-keeping in smallholder setups."],
        ["Jimmy Jr & Gente (2024)", "SARIMA Aquaculture Yield Forecasting", "Time-Series Econometric Modeling, SARIMA", "Confirms predictive accuracy of mathematical forecasting in aquaculture yields."],
        ["Chang et al. (2021)", "AI-Based Smart Cage Aquaculture System", "Computer Vision, Predictive Clustering, AI Models", "Supports utilizing regression and clustering models for management decisions."],
        ["Zapata et al. (2023)", "Smart Food Value Chain Intervention Models", "Value Chain Mapping, Digital Interventions", "Emphasizes the value of web-based ordering and logistics for local fisheries."]
    ]

    col_widths_t2 = [Inches(1.4), Inches(1.6), Inches(1.5), Inches(1.5)]
    for row_idx, row_data in enumerate([t2_headers] + t2_data):
        row = tbl2.rows[row_idx]
        is_header = (row_idx == 0)
        is_last = (row_idx == len(t2_data))
        for col_idx, text in enumerate(row_data):
            cell = row.cells[col_idx]
            cell.width = col_widths_t2[col_idx]
            cell.vertical_alignment = WD_ALIGN_VERTICAL.TOP
            if is_header:
                set_apa_header_cell(cell)
            else:
                set_apa_data_cell(cell, is_last_row=is_last)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if is_header else WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(4) if is_header else Pt(2)
            p.paragraph_format.space_after = Pt(4) if is_header else Pt(2)
            p.paragraph_format.line_spacing = None
            run = p.add_run(text)
            run.font.name = 'Arial'
            run.font.size = Pt(10)
            if is_header:
                run.bold = True

    # ==================== 4. CHAPTER III: METHODOLOGY ====================
    print("Generating Chapter III...")
    doc.add_page_break()
    p_chapter_head("CHAPTER III\nMETHODOLOGY")

    p_body("This chapter presents the research methodology used in the development of the Aquaculture Value Chain Management System with Predictive Analytics. It describes the research design, data gathering procedures, system development process, and tools utilized in the study. The chapter also explains the process modeling about the context and data flow diagram and uml use case diagram, how the researchers analyzed the existing aquaculture operations and translated the identified problems into system requirements.", indent=True)

    # 3.1 SDLC
    p_heading_2("3.1 Systems Development Life Cycle")
    p_body("The study employed a developmental research design, focusing on the creation and evaluation of a system that addresses the challenges identified in Chapter 1, particularly the use of manual and fragmented record-keeping practices. Through a structured system development approach, the proposed system was designed to provide a centralized platform for managing production, inventory, sales, and expenses, while incorporating predictive analytics to support informed decision-making.", indent=True)

    p_figure_title("Figure 1", "Agile and Methodology of Aquaculture Value Chain Management System with Predictive Analytics")
    p_image(r"Documents/Final_Paper/ch3_extracted_images/image2.png", width_in_inches=5.5)
    p_body("Figure 1 illustrates the Agile model used in the development of the Silay Superworm & Crayfish Value Chain Management System with Predictive Analytics. The Agile methodology follows an iterative process of planning, design, development, testing, deployment, and review to progressively develop and improve the system. It allows the researchers to develop the system in manageable components, evaluate each feature, identify issues, and make necessary improvements throughout the development process.", indent=True)
    p_body("This approach is appropriate for the proposed system because it contains several interconnected functions, including production management, inventory, sales, expenses, customer transactions, predictive analytics, data clustering, and report generation. Agile is well-suited because it supports continuous development, early testing, user feedback, and flexible adjustments to system requirements.", indent=True)
    p_body("The proposed system aims to replace fragmented and manual record-keeping practices with a centralized web-based platform that organizes production, inventory, sales, expenses, and other operational information. Through an iterative development process, the researchers can continuously evaluate the system against the operational needs of farm managers and production staff. Each module can be reviewed and refined before the system proceeds to final integration, testing, and deployment.", indent=True)

    # Phases
    p_heading_3("Phase 1 – Planning Phase")
    p_body("This phase lasted 27 days and focused on identifying the problems and requirements of Silay Superworm & Crayfish. The researchers gathered requirements for production, feeding, harvesting, inventory, sales, expenses, customer transactions, distribution, and delivery. They also identified the requirements for predictive analytics and data clustering. The project scope, objectives, system functions, and data requirements were then established as the foundation for the design and development phases.", indent=True)

    p_heading_3("Phase 2 – Design Phase")
    p_body("This phase lasted 54 days and focused on converting the identified requirements into detailed system designs. The researchers designed the system architecture, database, processes, user interfaces, and modules covering production, inventory, sales, expenses, customer transactions, predictive analytics, and reporting. Database structures and interface workflows were also prepared to support the needs of the intended users.", indent=True)

    p_heading_3("Phase 3 – Development Phase")
    p_body("This phase lasted 155 days and focused on developing the system based on the approved requirements and designs. The researchers developed and refined the system modules incrementally, covering production, pond operations, feeding, harvesting, inventory, sales, customers, expenses, distribution, and delivery. Predictive analytics and clustering functions were also implemented to support forecasting and analysis of production, expenses, market demand, sales, and customer behavior. The modules and database were integrated into a centralized system, which was completed and prepared for formal testing.", indent=True)

    p_heading_3("Phase 4 – Testing Phase")
    p_body("This phase lasted 36 days and focused on testing the system's functionality, performance, usability, and data accuracy. The researchers tested major functions such as production, inventory, sales, customer transactions, expenses, harvesting, reports, and predictive analytics. Testing also evaluated system usefulness, information quality, interface quality, and overall usability. Errors and inconsistencies were documented, corrected, and retested before the system proceeded to deployment.", indent=True)

    p_heading_3("Phase 5 – Deployment Phase")
    p_body("This phase lasted 3 days and focused on preparing the tested system for actual operational use. The researchers configured the centralized web-based system, database, and necessary components, and prepared operational data covering production, inventory, sales, expenses, customers, and other relevant activities. The system was then made accessible through standard web browsers and prepared for user access and evaluation in its intended operating environment.", indent=True)

    p_heading_3("Phase 6 – Review Phase")
    p_body("This phase lasted 10 days and focused on reviewing the deployed system to determine its alignment with the operational needs of Silay Superworm & Crayfish. The researchers assessed the accuracy of production, inventory, sales, expenses, customer transactions, reports, and predictive analytics. User feedback was also evaluated based on system usefulness, information quality, interface quality, and overall usability. The identified issues and recommendations were documented and used as a basis for final system improvements.", indent=True)

    p_heading_3("Phase 7 – Launch Phase")
    p_body("This phase lasted 2 days and focused on finalizing the system and its supporting documentation for formal presentation and evaluation. The researchers incorporated the final improvements identified during testing and review and completed the User Manual and other system documentation. The final system was prepared after confirming that its major functions, reports, analytical features, and user requirements had been addressed. This phase marked the completion of the development process and prepared the Silay Superworm & Crayfish Value Chain Management System with Predictive Analytics for final evaluation and intended use.", indent=True)

    # 3.2 Operational Framework
    p_heading_2("3.2 Operational Framework")
    p_figure_title("Figure 2", "Operational Framework of Aquaculture Value Chain Management System with Predictive Analytics")
    p_image(r"Documents/Final_Paper/ch3_extracted_images/image3.png", width_in_inches=5.8)
    p_body("Figure 2 illustrates the Operational Framework of the Aquaculture Value Chain Management System with Predictive Analytics, showing the interaction among the Customer, Rider, Farm Owner (Manager), Computer System, and Cloud Database. The framework demonstrates how customer orders are received and processed, delivery assignments and route maps are provided to riders, and delivery status updates are recorded in the system. It also shows the exchange of order records, production summary reports, sales forecasts, and management requests between the system, cloud database, customers, and farm owner.", indent=True)

    # 3.3 Data Flow Diagrams
    p_heading_2("3.3 Data Flow Diagram")

    p_figure_title("Figure 3", "Context Diagram (Level 0) Aquaculture Value Chain Management System with Predictive Analytics")
    p_image(r"diagram/Level_0_Context_Diagram.png", width_in_inches=5.8)
    p_body("Figure 3 illustrates the Level 0 Context Diagram of the Aquaculture Value Chain Management System with Predictive Analytics, showing the interaction between the system and its three main external entities: the Customer, Manager, and Rider. The diagram presents the flow of customer information, order details, payment methods, delivery options, farm and inventory records, delivery updates, and management reports between the users and the system. It also shows how the system provides order confirmations, product availability, billing receipts, delivery assignments, sales summaries, sales forecasts, low-stock alerts, and order tracking information to support the overall management of aquaculture operations.", indent=True)

    p_figure_title("Figure 4", "Data Flow Diagram Level 1 Explosion Aquaculture Value Chain Management System with Predictive Analytics")
    p_image(r"diagram/Level_1_DFD.png", width_in_inches=6.0)
    p_body("Figure 4 illustrates the Level 1 Data Flow Diagram (DFD) Explosion of the Aquaculture Value Chain Management System with Predictive Analytics. It presents the detailed flow of information among the Customer, Rider, Manager, system processes, and data stores. The diagram shows the major processes involved in the system, including browsing and product selection, order management, payment and settlement, delivery dispatch, management, report and monitoring, and predictive analytics. It also demonstrates how data such as customer and order information, production records, expenses, payment details, delivery records, inventory updates, and sales information are stored, processed, and exchanged to support ordering, payment, delivery, farm management, reporting, and predictive analysis.", indent=True)

    p_figure_title("Figure 5", "Data Flow Diagram Level 2 of the Product Browsing and Selection process")
    p_image(r"Documents/Final_Paper/ch3_extracted_images/image6.jpeg", width_in_inches=5.5)
    p_body("Figure 5 illustrates the Level 2 Data Flow Diagram (DFD) Explosion of the Product Browsing and Selection process of the Aquaculture Value Chain Management System with Predictive Analytics. It provides a detailed view of how the system handles customer product selection through the processes of displaying the product catalog, searching and filtering products, checking stock availability, and selecting the product and quantity. The diagram also shows the flow of product information, stock status, available stock, order information, and reserved stock between the Customer, Order (D1), and Production (D3) data stores. The selected product and quantity are then forwarded to the Order Management process for subsequent order processing.", indent=True)

    p_figure_title("Figure 6", "Data Flow Diagram Level 2 Explosion of Order Management process")
    p_image(r"Documents/Final_Paper/ch3_extracted_images/image7.jpeg", width_in_inches=5.5)
    p_body("Figure 6 illustrates the Level 2 Data Flow Diagram (DFD) Explosion of the Order Management process of the Aquaculture Value Chain Management System with Predictive Analytics. It presents the detailed flow of order processing through the processes of creating an order request, validating the order and customer information, and confirming or approving the order. The diagram shows how order details are received from the Customer, stored in the Order (D1) and Customer (D2) data stores, and validated before approval. The Manager reviews and approves the order, after which the confirmed order information is forwarded to the Payment and Set Location process for subsequent transaction and delivery processing.", indent=True)

    p_figure_title("Figure 7", "Data Flow Diagram Level 2 Explosion of Payment and Set Location process")
    p_image(r"Documents/Final_Paper/ch3_extracted_images/image8.jpeg", width_in_inches=5.5)
    p_body("Figure 7 illustrates the Level 2 Data Flow Diagram (DFD) Explosion of the Payment and Set Location process of the Aquaculture Value Chain Management System with Predictive Analytics. It presents the detailed flow of payment and delivery information through the processes of setting the delivery or pickup location, processing GCash payments, and verifying and recording payments including Cash on Delivery (COD). The diagram shows the exchange of payment details, payment requests, payment responses, order records, and delivery information among the Customer, Rider, Order (D1), and Payment (D5) data stores. After payment verification and recording, the order details and location information are forwarded to the Delivery Dispatch process for subsequent delivery processing.", indent=True)

    p_figure_title("Figure 8", "Data Flow Diagram Level 2 Explosion of Delivery Dispatch process")
    p_image(r"Documents/Final_Paper/ch3_extracted_images/image9.jpeg", width_in_inches=5.5)
    p_body("Figure 8 illustrates the Level 2 Data Flow Diagram (DFD) Explosion of the Delivery Dispatch process of the Aquaculture Value Chain Management System with Predictive Analytics. It presents the detailed flow of delivery operations through the processes of assigning riders and generating route maps, tracking delivery status, and confirming delivery while updating stock. The diagram shows the exchange of order details, delivery records, rider assignments, route information, real-time tracking, and delivery status updates among the Customer, Rider, Manager, Order (D1), Production (D3), and Delivery (D6) data stores. Upon delivery completion, the system records the delivery confirmation, updates the order status, and processes the corresponding stock deduction before forwarding the confirmed order to the Management process.", indent=True)

    p_figure_title("Figure 9", "Data Flow Diagram Level 2 Explosion of Management process")
    p_image(r"Documents/Final_Paper/ch3_extracted_images/image10.jpeg", width_in_inches=5.5)
    p_body("Figure 9 illustrates the Level 2 Data Flow Diagram (DFD) Explosion of the Management process of the Aquaculture Value Chain Management System with Predictive Analytics. It presents the detailed flow of management activities through the processes of recording production and feeding data, managing expenses, and managing stock and replenishment. The diagram shows how delivery records, order information, production data, expense records, payment information, and stock levels are processed and exchanged among the Manager, Delivery (D6), Production (D3), Expense (D4), and Payment (D5) data stores. The processed delivery, expense, production, and inventory information is then forwarded to the Report and Monitoring process to support management reporting and operational monitoring.", indent=True)

    p_figure_title("Figure 10", "Data Flow Diagram Level 2 Explosion of Report and Monitoring process")
    p_image(r"Documents/Final_Paper/ch3_extracted_images/image11.jpeg", width_in_inches=5.5)
    p_body("Figure 10 illustrates the Level 2 Data Flow Diagram (DFD) Explosion of the Report and Monitoring process of the Aquaculture Value Chain Management System with Predictive Analytics. It presents the detailed flow of reporting activities through the processes of compiling inventory and dispatch data, generating sales and expense summaries, and generating printable reports. The diagram shows how inventory, dispatch, delivery, and expense information are collected from the Production (D3), Delivery (D6), and Expense (D4) data stores. The compiled and summarized data are processed into printable reports and provided to the Manager for monitoring and decision-making. The summarized data are also forwarded to the Predictive Analytics process for further analysis and forecasting.", indent=True)

    p_figure_title("Figure 11", "Data Flow Diagram Level 2 Explosion of Predictive Analytics process")
    p_image(r"Documents/Final_Paper/ch3_extracted_images/image12.jpeg", width_in_inches=5.5)
    p_body("Figure 11 illustrates the Level 2 Data Flow Diagram (DFD) Explosion of the Predictive Analytics process of the Aquaculture Value Chain Management System with Predictive Analytics. It presents the detailed flow of predictive analysis through the processes of sales forecasting using linear regression, customer and regional clustering, and harvest readiness prediction. The diagram shows how summary information from the Report and Monitoring process is used to generate forecasts and clustering analyses. The resulting forecast and clustering reports and harvest readiness predictions are provided to the Manager to support data-driven monitoring, planning, and decision-making.", indent=True)

    # 3.4 ERD
    p_heading_2("3.4 Entity Relationship Diagram")
    p_figure_title("Figure 12", "Entity-Relationship Diagram of Aquaculture Value Chain Management System with Predictive Analytics")
    p_image(r"diagram/ERD_Diagram.png", width_in_inches=6.0)
    p_body("Figure 12 illustrates the Entity-Relationship Diagram (ERD) of the Aquaculture Value Chain Management System with Predictive Analytics, showing the normalized physical database schema and relational constraints governing the aquaculture enterprise in Barangay Lantad, Silay City. The database architecture is organized into 15 core entities structured across user authentication, pond cultivation lifecycle, commercial inventory, point-of-sale customer transactions, logistics dispatching, and operational expense accounting. Relational integrity is enforced using primary keys (PK) and foreign keys (FK) across all tables to maintain referential consistency.", indent=True)
    p_body("At the user management foundation, the User entity manages credentials and role assignments (Owner, Customer, and Rider), linked one-to-one with the Profile and Customer entities. The cultivation lifecycle is modeled through the Operations_Pond entity, which tracks physical rearing ponds and coordinates with Cultivation_Batch to record species batches (Zophobas morio superworms and Cherax quadricarinatus redclaw crayfish), stage transitions, and stocking counts. Operational farm data is logged through child tables Feeding_Log (capturing feeding schedules and feed quantities) and Operations_Pond maintenance records, while completed rearing cycles are finalized in Harvest_Record. The commercial downstream value chain is governed by Inventory_Item (supporting dual pricing per piece and per kilogram) and Stock_Movement, directly connected to Order and Order_Item records. Transactions are finalized through Payment records (handling GCash receipt verification and Cash on Delivery), Delivery_Dispatch (capturing rider assignments, route coordinates, and Proof of Delivery), and Expense records (categorizing feeds, utilities, fuel, and facility maintenance overhead).", indent=True)

    # 3.5 UML
    p_heading_2("3.5 UML Use Case Diagram")
    p_figure_title("Figure 13", "UML Use Case Diagram of Aquaculture Value Chain Management System with Predictive Analytics")
    p_image(r"diagram/UML_Use_Case_Diagram.png", width_in_inches=6.0)
    p_body("Figure 13 illustrates the UML Use Case Diagram of the Aquaculture Value Chain Management System with Predictive Analytics, presenting the functional boundary and direct interactions between the system and its three primary actors: Owner, Customer, and Rider. The diagram defines the functional scope across user roles. The Owner manages executive analytics dashboards, pond cultivation operations (feeding schedules and Azula sanitization tracking), commercial inventory and batch production, expense logging, executive reporting, and predictive analytics forecasting (Linear Regression and K-Means customer segmentation). The Customer interacts with the storefront to browse available stock, configure delivery or pickup options, submit cart checkouts with integrated GCash or COD payment processing, and track live order transit. The Delivery Rider accesses assigned delivery pools, submits proof of delivery confirmations (recipient photo and signature), and updates delivery transit statuses.", indent=True)

    # 3.6 Use Cases
    p_heading_2("3.6 Use Case Scenario")
    p_body("The Use Case Scenario describes the interaction between the primary entities (Farm Owner, Delivery Rider, and Commercial Customers) and the Aquaculture Value Chain Management System with Predictive Analytics. Each table details the operational goal, prerequisites, step-by-step main flow of activities, and summary user action and system response across farm operations, inventory management, order processing, courier dispatch, and predictive analytics forecasting.", indent=True)

    for uc in buc_all.ALL_USE_CASES:
        buc_all.render_exact_use_case_table(doc, uc)

    # 3.7 Data Dictionary
    p_heading_2("3.7 Data Dictionary")
    p_body("The data dictionary describes the structure, data types, formats, field sizes, descriptions, and example values for each table in the Lantad Superworm & Crayfish Management System database. The tables documented below represent the core data entities of the system.", indent=True)

    for item in bdd.DATA_DICTIONARY_TABLES:
        bdd.add_data_table(doc, item["num"], item["name"], item["fields"])

    # 3.8 System Requirements
    bs38.add_section_3_8(doc)

    # 3.9 - 3.12 Evaluation and Ethics
    bsee.add_eval_and_ethics_sections(doc)

    # ==================== 5. CHAPTER IV: RESULTS AND DISCUSSION ====================
    print("Generating Chapter IV...")
    doc.add_page_break()
    p_chapter_head("CHAPTER IV\nRESULTS AND DISCUSSION")

    p_body("This chapter presents the results and discussions based on the development and evaluation of the Aquaculture Value Chain Management System with Predictive Analytics for Silay Superworm & Crayfish, in line with the objectives established in Chapter I. It includes comprehensive interface walkthroughs of the system's operational modules, the rigorous results of functionality testing (encompassing 68 Black-box functional test cases across twelve operational modules and 16 White-box structural test cases), and the software quality evaluation conducted in accordance with the ISO/IEC 25010:2011 Software Quality Model. Data were gathered from key stakeholders, including the Farm Owner, commercial buyers, retail customers, delivery riders, and independent IT experts, utilizing a five-point Likert scale ranging from 1 (Strongly Disagree) to 5 (Strongly Agree).", indent=True)

    p_body("Furthermore, this chapter provides an empirical analysis of the system's execution under real-world aquaculture farm workflows in Barangay Lantad, Silay City, Negros Occidental. The findings demonstrate the system's technical effectiveness, operational reliability, data security, calculation precision in dual-unit pricing and inventory stock reconciliation, and capacity to eliminate manual recordkeeping inefficiencies while providing predictive decision-support capabilities through machine learning forecasting and customer segmentation.", indent=True)

    p_heading_2("4.1 Results of the Study")
    p_body("The first objective of this study aimed to design and develop an Aquaculture Value Chain Management System with Predictive Analytics equipped with technical features including: (1) multi-role user authentication and session security, (2) an executive dashboard with real-time farm KPIs and sanitization alerts, (3) pond, cabin rack, and tank cultivation management, (4) feed formulation and daily supply logging, (5) Azula cultivation and 15-day pond sanitization monitoring, (6) harvest lifecycle scheduling and interactive production calendar, (7) commercial product catalog with dual-unit pricing (Per Piece and Per KG), (8) customer storefront with online cart checkout, (9) digital payment settlement supporting PayMongo GCash and COD, (10) sales order fulfillment and lifecycle state machine, (11) courier fleet dispatch and mobile rider portal with Proof of Delivery (POD), (12) real-time GPS tracking with Leaflet GIS maps, (13) predictive demand forecasting using Ordinary Least Squares Linear Regression, (14) customer segmentation using K-Means clustering, and (15) executive PDF/Excel report generation with a three-tiered audit trail.", indent=True)

    p_body("The development of the system was completed using an enterprise Model-View-Template (MVT) architecture combining Python 3.11 with the Django 5.1 framework on the backend, supported by an ACID-compliant PostgreSQL / SQLite relational database, responsive HTML5/CSS3/JavaScript frontend with Bootstrap 5 and Tailwind CSS styling, Chart.js/ApexCharts interactive visualization libraries, and Leaflet.js GIS spatial mapping. The operational interfaces of the developed system are presented in Figures 14 through 29.", indent=True)

    for fig_num, fname, title, desc in bc4.CHAPTER_4_FIGURES:
        bc4.add_figure_item(doc, fig_num, title, desc, img_filename=fname)

    # 4.2 & 4.3 Testing and Quality Evaluation
    bc4t.add_section_4_2_and_4_3_to_doc(doc)

    # ==================== 6. CHAPTER V: SUMMARY, CONCLUSIONS, RECOMMENDATIONS ====================
    print("Generating Chapter V...")
    doc.add_page_break()
    p_chapter_head("CHAPTER V\nSUMMARY OF FINDINGS, CONCLUSIONS, AND RECOMMENDATIONS")

    p_body("This chapter presents the summary of findings, conclusions, and recommendations derived from the design, development, functionality testing, and software quality evaluation of the Aquaculture Value Chain Management System with Predictive Analytics for Silay Superworm & Crayfish. It consolidates the empirical results presented in Chapter IV and determines how the developed system successfully fulfilled the research objectives established in Chapter I.", indent=True)

    p_heading_2("5.1 Summary of Findings")
    p_body("Based on the data gathered and analyzed throughout the development and evaluation phases, the major findings of the study are summarized as follows:", indent=True)

    p_bullet("1.", "Objective 1 (System Architecture and Development): The Aquaculture Value Chain Management System with Predictive Analytics was successfully designed, developed, and deployed for Silay Superworm & Crayfish in Barangay Lantad, Silay City, Negros Occidental. The system integrates eleven core functional features: (a) Farm Operations and Pond Management across 15 outdoor ponds, superworm cabin, and Azula tanks with 15-day sanitization alerts, (b) Feed Supply and Feeding Management with automated inventory deduction, (c) Harvest Scheduling with an interactive production calendar, (d) Commercial Product Catalog with Dual-Unit Pricing (₱/pc and ₱/kg), (e) Customer Storefront with shopping cart and fulfillment mode selection (On-Site Pickup vs. Doorstep Delivery with GPS pinning), (f) Multi-Tier Payment Settlement supporting PayMongo GCash and Cash on Delivery, (g) Sales Order Fulfillment State Machine with automated stock deduction, (h) Courier Fleet Dispatching with Leaflet OpenStreetMap navigation and mobile Proof of Delivery (POD) confirmation, (i) Ordinary Least Squares (OLS) Linear Regression for sales revenue and harvest yield forecasting, (j) K-Means Customer Clustering for regional market segmentation, and (k) Executive Financial and Inventory PDF/Excel Reporting with a three-tiered immutable audit trail.")

    p_bullet("2.", "Objective 2 (Functionality Testing): The functionality, structural execution, and transaction integrity of the system were rigorously tested through 84 total test cases, comprising 68 Black-box functional test cases across twelve operational modules and 16 White-box structural test cases across three test suites (Core Security & RBAC, Business Logic & Data State Machine, and Transaction Integrity & Concurrency). All 68 Black-box cases and 16 White-box test cases achieved a 100.0% Pass Rate with zero critical defects, confirming that the system executes all operational workflows and database transactions with mathematical precision and reliability.")

    p_bullet("3.", "Objective 3 (Software Quality Evaluation): The software product quality of the developed platform was evaluated using an evaluation instrument patterned after the ISO/IEC 25010:2011 International Software Quality Model. The evaluation was administered to 30 respondents, comprising 10 IT Experts/Professionals and 20 Agricultural End-Users (including the Farm Owner, Farm Staff, Commercial Buyers, and Logistics Delivery Couriers). The system achieved an Overall Grand Mean of 4.895 (SD = 0.052), verbally interpreted as Excellent (Highly Acceptable). Among the eight evaluated quality characteristics, Security received the highest rating at 4.96, followed by Compatibility (4.93), Reliability (4.91), Functional Suitability (4.91), Portability (4.89), Usability (4.88), Maintainability (4.85), and Performance Efficiency (4.83). Both IT Experts (x̄ = 4.905) and Agricultural End-Users (x̄ = 4.884) affirmed the system's technical excellence and high practical acceptability.")

    p_bullet("4.", "Objective 4 (User's Guide Development): A comprehensive System User Manual and Operational Guide (Appendix K) was developed and packaged with the platform. The guide provides structured, role-based operational procedures for the Farm Owner/Admin (dashboard navigation, pond allocations, feeding logs, pricing, dispatch, reporting), Delivery Riders (mobile portal, duty toggling, route navigation, POD confirmation), and Commercial Customers (storefront browsing, dual-unit cart selection, GPS pinning, PayMongo GCash/COD payment settlement).")

    p_heading_2("5.2 Conclusions")
    p_body("In light of the empirical findings obtained in this study, the following conclusions are drawn:", indent=True)

    p_bullet("1.", "The Aquaculture Value Chain Management System with Predictive Analytics directly and effectively solves the chronic operational fragmentation, manual bookkeeping errors, inventory shrinkage, and lack of real-time visibility historically experienced by Silay Superworm & Crayfish. Centralizing production tracking, pond environmental monitoring, e-commerce checkout, and courier routing into a unified digital infrastructure eliminates administrative bottlenecks and enhances farm productivity.")

    p_bullet("2.", "The comprehensive functionality testing results confirm that the system is technically robust, secure, and structurally dependable. The successful execution of all 68 Black-box cases and 16 White-box test cases demonstrates that the platform handles complex business rules—including dual-unit pricing calculations, stock batch transitions, sanitization reminders, and concurrent cart deductions—without data loss, race conditions, or state corruption.")

    p_bullet("3.", "The integration of predictive analytics (Ordinary Least Squares Linear Regression) and unsupervised machine learning (K-Means Clustering) provides actionable decision-support capabilities. Farm management can accurately forecast future revenue streams, anticipate harvest maturity timelines, prevent feed wastage, and tailor logistics routes to high-density customer clusters.")

    p_bullet("4.", "The ISO/IEC 25010:2011 software quality evaluation proves that the platform satisfies international software engineering benchmarks. The overall grand mean of 4.895 demonstrates exceptional user satisfaction and technical compliance across security, functional suitability, usability, and cross-platform compatibility.")

    p_heading_2("5.3 Recommendations")
    p_body("Based on the findings and conclusions of the study, the following recommendations are presented for the continuous adoption, enhancement, and future research direction of the platform:", indent=True)

    p_bullet("1.", "Enterprise Management Adoption: Silay Superworm & Crayfish management is strongly encouraged to formally adopt and institutionalize the web-based system as their primary operational platform for daily pond operations, feed administration, commercial sales fulfillment, and logistics dispatching.")

    p_bullet("2.", "Server Infrastructure and Performance Optimization: To sustain optimal performance efficiency during peak harvest seasons and high-volume promotional sales events, system administrators should implement database index optimization, server-side Redis caching for product catalog queries, and automated off-site database backups.")

    p_bullet("3.", "Offline and Progressive Web App (PWA) Capabilities: Future development may incorporate Progressive Web App (PWA) service workers and local indexedDB storage to enable offline data entry for farm technicians working in remote pond zones where rural cellular connectivity is intermittent.")

    p_bullet("4.", "Automated Multi-Channel Notifications: Integrating automated SMS (via Twilio or PhilSMS) and push notification gateways is recommended to automatically alert customers upon order dispatch and notify delivery riders of newly assigned route assignments in real time.")

    p_bullet("5.", "Expanded Machine Learning and Environmental Telemetry: Future researchers may extend the predictive analytics engine by incorporating multi-variable regression models that factor in ambient weather conditions, water pH, and water temperature data streams to refine harvest yield forecasts.")

    p_bullet("6.", "Replication and Policy Scaling: Agricultural agencies and future academic researchers may adapt and scale this modular value chain architecture to support other inland aquaculture and insect farming cooperatives across Western Visayas and the Philippines.")

    # ==================== 7. PRESERVE REFERENCES & APPENDICES FROM DUEPAPERS.DOCX ====================
    print("Appending References and Appendices A through L from duepapers.docx...")

    due_src_path = r'C:\Users\kymer\Downloads\duepapers.docx'
    if os.path.exists(due_src_path):
        due_doc = Document(due_src_path)
        due_body = due_doc._body._body

        ref_found = False
        elements_copied = 0

        for el in due_body:
            tag = el.tag.split('}')[-1]
            if tag == 'p':
                p_text = el.text or ''
                if p_text.strip().upper() == 'REFERENCES':
                    ref_found = True
            
            if ref_found:
                # Deep copy the element and append to new document body
                new_el = copy.deepcopy(el)
                doc._body._body.append(new_el)
                elements_copied += 1

        print(f"Successfully copied {elements_copied} elements (References and Appendices A-L) from {due_src_path}!")
    else:
        print(f"Warning: {due_src_path} not found to copy Appendices.")

    # ==================== SAVE OUTPUT FILES ====================
    out_final_paper = r'Documents/Final_Paper/duepapers_fixed.docx'
    doc.save(out_final_paper)
    print(f"Successfully saved clean fixed document to: {out_final_paper}")

    out_downloads_fixed = r'C:\Users\kymer\Downloads\duepapers (Fixed).docx'
    try:
        doc.save(out_downloads_fixed)
        print(f"Successfully saved to: {out_downloads_fixed}")
    except Exception as e:
        print(f"Warning: Could not save to {out_downloads_fixed}: {e}")

    out_downloads = r'C:\Users\kymer\Downloads\duepapers.docx'
    try:
        doc.save(out_downloads)
        print(f"Successfully overwritten: {out_downloads}")
    except Exception as e:
        print(f"Note: Could not overwrite {out_downloads} directly (file locked by Word). {out_downloads_fixed} is available.")

if __name__ == '__main__':
    build_duepapers_fixed()
