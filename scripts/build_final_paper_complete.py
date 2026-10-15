import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
import os
import sys
sys.path.insert(0, os.path.abspath('scripts'))
import build_exact_use_case_scenarios_all as buc_all

def set_apa_table_borders(table):
    tblPr = table._tbl.tblPr
    tblBorders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>\n'
        f'<w:top w:val="single" w:sz="8" w:space="0" w:color="000000"/>\n'
        f'<w:left w:val="nil"/>\n'
        f'<w:bottom w:val="single" w:sz="8" w:space="0" w:color="000000"/>\n'
        f'<w:right w:val="nil"/>\n'
        f'<w:insideH w:val="nil"/>\n'
        f'<w:insideV w:val="nil"/>\n'
        f'</w:tblBorders>'
    )
    tblPr.append(tblBorders)

def set_apa_header_cell(cell):
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>\n'
        f'<w:top w:val="single" w:sz="8" w:space="0" w:color="000000"/>\n'
        f'<w:left w:val="nil"/>\n'
        f'<w:bottom w:val="single" w:sz="8" w:space="0" w:color="000000"/>\n'
        f'<w:right w:val="nil"/>\n'
        f'</w:tcBorders>'
    )
    tcPr.append(tcBorders)
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="auto" w:val="clear"/>')
    tcPr.append(shd)
    mar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>\n'
        f'<w:top w:w="120" w:type="dxa"/>\n'
        f'<w:bottom w:w="120" w:type="dxa"/>\n'
        f'<w:left w:w="100" w:type="dxa"/>\n'
        f'<w:right w:w="100" w:type="dxa"/>\n'
        f'</w:tcMar>'
    )
    tcPr.append(mar)

def set_apa_data_cell(cell, is_last_row=False):
    tcPr = cell._tc.get_or_add_tcPr()
    if is_last_row:
        tcBorders = parse_xml(
            f'<w:tcBorders {nsdecls("w")}>\n'
            f'<w:top w:val="nil"/>\n'
            f'<w:left w:val="nil"/>\n'
            f'<w:bottom w:val="single" w:sz="8" w:space="0" w:color="000000"/>\n'
            f'<w:right w:val="nil"/>\n'
            f'</w:tcBorders>'
        )
        tcPr.append(tcBorders)
    else:
        tcBorders = parse_xml(
            f'<w:tcBorders {nsdecls("w")}>\n'
            f'<w:top w:val="nil"/>\n'
            f'<w:left w:val="nil"/>\n'
            f'<w:bottom w:val="nil"/>\n'
            f'<w:right w:val="nil"/>\n'
            f'</w:tcBorders>'
        )
        tcPr.append(tcBorders)
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="auto" w:val="clear"/>')
    tcPr.append(shd)
    mar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>\n'
        f'<w:top w:w="100" w:type="dxa"/>\n'
        f'<w:bottom w:w="100" w:type="dxa"/>\n'
        f'<w:left w:w="100" w:type="dxa"/>\n'
        f'<w:right w:w="100" w:type="dxa"/>\n'
        f'</w:tcMar>'
    )
    tcPr.append(mar)

def build_complete_final_paper():
    doc = docx.Document()

    # Page setup - Short Letter (8.5 x 11 in), Margins: Left 1.5", Top/Right/Bottom 1.0"
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

    def p_title_line(text, bold=True, size=12):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        run = p.add_run(text)
        run.font.name = 'Arial'
        run.font.size = Pt(size)
        run.bold = bold
        return p

    def p_blank(count=1):
        for _ in range(count):
            p = doc.add_paragraph()
            p.paragraph_format.line_spacing = 1.5
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)

    def p_chapter_head(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(6)
        run = p.add_run(text)
        run.font.name = 'Arial'
        run.font.size = Pt(12)
        run.bold = True
        return p

    def p_heading_2(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(4)
        run = p.add_run(text)
        run.font.name = 'Arial'
        run.font.size = Pt(12)
        run.bold = True
        return p

    def p_heading_3(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(2)
        run = p.add_run(text)
        run.font.name = 'Arial'
        run.font.size = Pt(12)
        run.bold = True
        return p

    def p_body(text, indent=True):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(6)
        if indent:
            p.paragraph_format.first_line_indent = Inches(0.5)
        run = p.add_run(text)
        run.font.name = 'Arial'
        run.font.size = Pt(12)
        return p

    def p_bullet(num_str, text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.left_indent = Inches(0.5)
        p.paragraph_format.first_line_indent = Inches(-0.5)
        r1 = p.add_run(num_str + " ")
        r1.font.name = 'Arial'
        r1.font.size = Pt(12)
        r2 = p.add_run(text)
        r2.font.name = 'Arial'
        r2.font.size = Pt(12)
        return p

    def p_term(term, definition):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.first_line_indent = Inches(0.5)
        r_term = p.add_run(term + ". ")
        r_term.font.name = 'Arial'
        r_term.font.size = Pt(12)
        r_term.bold = True
        r_def = p.add_run(definition)
        r_def.font.name = 'Arial'
        r_def.font.size = Pt(12)
        return p

    def p_table_title(table_num, table_name):
        p1 = doc.add_paragraph()
        p1.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p1.paragraph_format.line_spacing = 1.5
        p1.paragraph_format.space_before = Pt(12)
        p1.paragraph_format.space_after = Pt(0)
        r1 = p1.add_run(table_num)
        r1.font.name = 'Arial'
        r1.font.size = Pt(12)
        r1.bold = True

        p2 = doc.add_paragraph()
        p2.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p2.paragraph_format.line_spacing = 1.5
        p2.paragraph_format.space_before = Pt(0)
        p2.paragraph_format.space_after = Pt(4)
        r2 = p2.add_run(table_name)
        r2.font.name = 'Arial'
        r2.font.size = Pt(12)
        r2.italic = True

    def p_figure_title(fig_num, fig_name):
        p1 = doc.add_paragraph()
        p1.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p1.paragraph_format.line_spacing = 1.5
        p1.paragraph_format.space_before = Pt(12)
        p1.paragraph_format.space_after = Pt(0)
        r1 = p1.add_run(fig_num)
        r1.font.name = 'Arial'
        r1.font.size = Pt(12)
        r1.bold = True

        p2 = doc.add_paragraph()
        p2.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p2.paragraph_format.line_spacing = 1.5
        p2.paragraph_format.space_before = Pt(0)
        p2.paragraph_format.space_after = Pt(6)
        r2 = p2.add_run(fig_name)
        r2.font.name = 'Arial'
        r2.font.size = Pt(12)
        r2.italic = True

    def p_image(image_path, width_in_inches=5.8):
        if os.path.exists(image_path):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(6)
            run = p.add_run()
            run.add_picture(image_path, width=Inches(width_in_inches))
        else:
            p = doc.add_paragraph(f"[Image not found: {image_path}]")
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    def p_reference_item(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.left_indent = Inches(0.5)
        p.paragraph_format.first_line_indent = Inches(-0.5)
        run = p.add_run(text)
        run.font.name = 'Arial'
        run.font.size = Pt(12)
        return p

    # ==================== COVER / TITLE PAGE ====================
    p_blank(2)
    p_title_line("AQUACULTURE VALUE CHAIN MANAGEMENT SYSTEM WITH PREDICTIVE ANALYTICS", bold=True, size=14)
    p_blank(4)
    p_title_line("A Capstone Project Presented to", bold=False, size=12)
    p_title_line("The Faculty of the College of Computer Studies", bold=False, size=12)
    p_title_line("Carlos Hilado Memorial State University", bold=False, size=12)
    p_title_line("Talisay City, Negros Occidental", bold=False, size=12)
    p_blank(4)
    p_title_line("In Partial Fulfillment of the Requirements for the Degree", bold=False, size=12)
    p_title_line("Bachelor of Science in Information Systems", bold=False, size=12)
    p_blank(4)
    p_title_line("Researchers:", bold=True, size=12)
    p_title_line("Hulleza, John Vincent", bold=False, size=12)
    p_title_line("Opjer, Kymer", bold=False, size=12)
    p_title_line("Herbais, Michael Dave", bold=False, size=12)
    p_blank(2)
    p_title_line("May 2026", bold=False, size=12)

    # ==================== CHAPTER I ====================
    doc.add_page_break()
    p_chapter_head("CHAPTER I")
    p_chapter_head("INTRODUCTION")

    p_heading_2("1.1 Background of the Study")
    p_body("Aquaculture is one of the fastest-growing food production sectors globally, playing an increasingly crucial role in enhancing global food security and providing sustainable protein sources (Food and Agriculture Organization [FAO], 2022). In the Philippines, the sector significantly contributes to national economic development, rural livelihoods, and domestic food supply across diverse sub-sectors, ranging from large-scale commercial fisheries to specialized inland smallholder enterprises (Durano et al., 2025; Salayo et al., 2021). Within this expanding landscape, the cultivation of alternative aquatic and biological species—notably the Australian redclaw crayfish (Cherax quadricarinatus) and superworms (Zophobas morio)—has emerged as a highly promising agribusiness niche. Redclaw crayfish cultivation has gained substantial traction due to the species' rapid growth rates, high commercial market value, and favorable adaptability to tropical climatic conditions (Cheng et al., 2025; Rigg et al., 2020). Concurrently, superworm production has expanded rapidly, serving both as high-protein commercial pet feeds and as a sustainable, cost-effective feed ingredient for aquaculture and poultry diets (de Sousa Araujo et al., 2025; Oliveira et al., 2025; Rumbos & Athanassiou, 2021).", indent=True)

    p_body("Despite these compelling economic advantages, local micro and small-scale aquaculture enterprises, such as Silay Superworm & Crayfish situated in Barangay Lantad, Silay City, Negros Occidental, encounter substantial operational bottlenecks across their internal value chains. As highlighted by Bush et al. (2019) and WorldFish (2022), smallholder agri-aquaculture value chains in developing economies frequently suffer from structural fragmentation, localized information asymmetry, and poor digital connectivity between upstream production facilities and downstream consumer markets. At Silay Superworm & Crayfish, day-to-day administrative procedures—including pond environmental monitoring, sanitization tracking, feeding schedule administration, stock transfers, batch lifecycle recording, and point-of-sale customer order fulfillment—are documented using manual, paper-bound logbooks and disparate, unstructured messaging channels. This heavy reliance on manual data entry causes chronic record inconsistencies, administrative delays, and inventory inaccuracies, creating severe blind spots that impede the farm owner's ability to maintain real-time operational visibility and sound financial control.", indent=True)

    p_body("Furthermore, managing perishable biological stock requires proactive inventory forecasting and data-driven harvest planning. Without automated analytical tools, farm operators struggle to accurately correlate input costs (e.g., feed expenditures and labor overhead) with operational yield outputs, often resulting in feed waste, delayed harvests, or unexpected stock shortages during peak market demand periods (Hu et al., 2025; Tina et al., 2025). Digital supply chain integration and business intelligence offer transformative solutions to these challenges, enabling real-time inventory synchronization, transparent order fulfillment, and automated harvest scheduling (Chiu et al., 2022; Wu et al., 2025). To directly resolve these operational deficits, this capstone study designs, develops, and implements the Aquaculture Value Chain Management System with Predictive Analytics for Silay Superworm & Crayfish. The system provides a centralized, web-based platform that digitizes pond lifecycle operations, automates direct-to-consumer e-commerce transactions, coordinates delivery logistics with automated route mapping, and integrates linear regression predictive modeling and K-Means customer segmentation clustering to drive operational sustainability and data-informed decision-making.", indent=True)

    p_heading_2("1.2 Statement of the Problem")
    p_body("Silay Superworm & Crayfish operates through manual and fragmented administrative workflows that hinder production efficiency, compromise inventory reliability, and limit market reach. Specifically, the study sought to answer the following research questions:", indent=True)

    p_bullet("1.", "What are the specific operational limitations and workflow challenges currently encountered by Silay Superworm & Crayfish regarding production tracking, inventory management, customer order processing, delivery logistics, and operational expense accounting?")
    p_bullet("2.", "What architectural framework, functional modules, and database structures must be designed and developed to deliver a centralized, responsive web platform tailored to the enterprise's end-to-end value chain?")
    p_bullet("3.", "How can predictive analytics algorithms—specifically Linear Regression for sales and yield forecasting, and K-Means clustering for customer segmentation—be integrated into the management system to provide actionable operational insights?")
    p_bullet("4.", "What is the level of software quality and user acceptability of the developed Aquaculture Value Chain Management System with Predictive Analytics when evaluated by end-users and IT professionals based on the ISO/IEC 25010:2011 Software Quality Model across the following quality characteristics?")

    p_body("a. Functional Suitability", indent=True)
    p_body("b. Performance Efficiency", indent=True)
    p_body("c. Compatibility", indent=True)
    p_body("d. Usability", indent=True)
    p_body("e. Reliability", indent=True)
    p_body("f. Security", indent=True)
    p_body("g. Maintainability", indent=True)
    p_body("h. Portability", indent=True)

    p_heading_2("1.3 Objectives of the Study")
    p_body("The primary objective of this study was to design, develop, and evaluate a comprehensive Aquaculture Value Chain Management System with Predictive Analytics for Silay Superworm & Crayfish. Specifically, the study aimed to achieve the following specific objectives:", indent=True)

    p_bullet("1.", "Identify and document the precise operational requirements, administrative pain points, and workflow bottlenecks in the existing production, inventory, sales, and logistics workflows of Silay Superworm & Crayfish.")
    p_bullet("2.", "Design and develop a robust, modular web-based system comprising a Farm Operations and Pond Management Module, Inventory and Batch Tracking Module, Customer E-Commerce and Order Processing Module, Rider Dispatch and Delivery Tracking Module, and Financial/Expense Accounting Module.")
    p_bullet("3.", "Implement predictive analytics and business intelligence capabilities, utilizing Linear Regression algorithms to forecast future sales trends and harvest yields, alongside K-Means clustering to analyze customer purchasing patterns and geographical demand density.")
    p_bullet("4.", "Evaluate the technical software quality, operational reliability, and user acceptability of the developed system in compliance with the ISO/IEC 25010:2011 international software quality standards.")

    p_heading_2("1.4 Scope and Delimitations of the Study")
    p_body("This capstone project focuses on the design, implementation, and empirical evaluation of a web-based value chain management system for Silay Superworm & Crayfish, located in Barangay Lantad, Silay City, Negros Occidental. The system encompasses end-to-end operational modules including pond environment and sanitization cycle logging, feed consumption and balance recording, batch growth stage tracking, multi-category inventory management (live crayfish, packaged superworms, specialized feeds, and biological fertilizers), customer online shopping cart and checkout, multi-tier payment recording (Cash on Delivery and GCash manual receipt verification), delivery rider dispatching with integrated Leaflet OpenStreetMap route visualization, operational expense categorization, and printable financial reporting.", indent=True)

    p_body("The analytical core of the platform utilizes scikit-learn machine learning libraries to generate short-term revenue forecasts, harvest yield predictions, and customer purchasing segmentation. The system was developed using Python and the Django web framework for backend logic, PostgreSQL/SQLite for relational database storage, and HTML5, Vanilla CSS, and modern JavaScript for responsive frontend user interfaces.", indent=True)

    p_body("The study is subject to several delimitations. The platform is implemented as a web application optimized for modern desktop and mobile browsers and does not include a native standalone mobile application (APK/IPA). While the system features digital payment logging, it does not directly process automated banking payment gateways via direct API webhooks, relying instead on customer receipt uploads and administrator payment verification. Delivery tracking utilizes OpenStreetMap routing coordinates rather than active real-time GPS telemetry streaming. Finally, the empirical evaluation of the system is delimited to the farm owner, delivery riders, registered enterprise customers, and invited IT professional evaluators situated in Negros Occidental.", indent=True)

    p_heading_2("1.5 Significance of the Study")
    p_body("The successful development and deployment of this capstone project provides substantial practical and academic benefits to multiple stakeholder groups:", indent=True)

    p_bullet("•", "Silay Superworm & Crayfish Management: Provides the farm owner with centralized real-time operational visibility, eliminating manual bookkeeping errors, preventing inventory shrinkage, optimizing feed supply allocation, and providing data-driven sales and harvest forecasts to maximize operational profitability.")
    p_bullet("•", "Delivery Personnel and Logistics Riders: Equips delivery staff with streamlined mobile-accessible dispatch schedules, customer contact directories, delivery destination maps, and proof-of-delivery logging.")
    p_bullet("•", "Enterprise Customers: Offers customers a seamless, transparent digital ordering catalog, direct order status tracking, digital transaction histories, and flexible payment options.")
    p_bullet("•", "Local Aquaculture Agribusiness Sector: Demonstrates the practical viability and economic impact of deploying low-cost, open-source web technologies and predictive analytics in micro, small, and medium aquaculture enterprises.")
    p_bullet("•", "Future Researchers and Academia: Serves as a comprehensive technical reference and foundational architecture for developing intelligent value chain systems and decision-support platforms in the broader agricultural and fisheries domain.")

    p_heading_2("1.6 Definition of Terms")
    p_body("To establish conceptual and operational clarity, the following key terms are defined within the context of this study:", indent=True)

    p_term("Aquaculture", "The controlled breeding, rearing, and harvesting of aquatic organisms. In this study, it specifically refers to the commercial farming of Australian redclaw crayfish and superworm larvae managed by the enterprise.")
    p_term("Value Chain Management", "The comprehensive coordination of all business activities required to bring a biological product from initial pond rearing through harvest, inventory packaging, direct sales, and final logistics delivery.")
    p_term("Predictive Analytics", "Advanced analytical techniques that extract historical data patterns to forecast future outcomes. In this system, it refers to Linear Regression algorithms applied to predict future sales revenues and expected pond harvest yields.")
    p_term("K-Means Clustering", "An unsupervised machine learning algorithm that partitions customer data into distinct clusters based on purchase frequency, total order monetary value, and geographical location.")
    p_term("Django Web Framework", "A high-level, open-source Python web framework that follows the Model-View-Template (MVT) architectural pattern, utilized to build the backend server and API endpoints of the system.")
    p_term("ISO/IEC 25010:2011", "An internationally recognized software engineering standard for evaluating system and software product quality across eight core characteristics.")

    # ==================== CHAPTER II ====================
    doc.add_page_break()
    p_chapter_head("CHAPTER II")
    p_chapter_head("REVIEW OF RELATED LITERATURE AND STUDIES")

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
    p_blank(1)
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

    # ==================== CHAPTER III (COMPLETE AS IN CHAPTER 3 (1).DOCX) ====================
    doc.add_page_break()
    p_chapter_head("CHAPTER III")
    p_chapter_head("METHODOLOGY")

    p_body("This chapter presents the research methodology used in the development of the Aquaculture Value Chain Management System with Predictive Analytics. It describes the research design, data gathering procedures, system development process, and tools utilized in the study. The chapter also explains the process modeling about the context and data flow diagram and uml use case diagram, how the researchers analyzed the existing aquaculture operations and translated the identified problems into system requirements.", indent=True)

    # 3.1 Systems Development Life Cycle
    p_heading_2("3.1 Systems Development Life Cycle")
    p_body("The study employed a developmental research design, focusing on the creation and evaluation of a system that addresses the challenges identified in Chapter 1, particularly the use of manual and fragmented record-keeping practices. Through a structured system development approach, the proposed system was designed to provide a centralized platform for managing production, inventory, sales, and expenses, while incorporating predictive analytics to support informed decision-making.", indent=True)

    # Figure 1
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

    # 3.3 Data Flow Diagram
    p_heading_2("3.3 Data Flow Diagram")

    # Figure 3 (Context Diagram Level 0)
    p_figure_title("Figure 3", "Context Diagram (Level 0) Aquaculture Value Chain Management System with Predictive Analytics")
    p_image(r"diagram/Level_0_Context_Diagram.png", width_in_inches=5.8)
    p_body("Figure 3 illustrates the Level 0 Context Diagram of the Aquaculture Value Chain Management System with Predictive Analytics, showing the interaction between the system and its three main external entities: the Customer, Manager, and Rider. The diagram presents the flow of customer information, order details, payment methods, delivery options, farm and inventory records, delivery updates, and management reports between the users and the system. It also shows how the system provides order confirmations, product availability, billing receipts, delivery assignments, sales summaries, sales forecasts, low-stock alerts, and order tracking information to support the overall management of aquaculture operations.", indent=True)

    # Figure 4 (DFD Level 1 Explosion)
    p_figure_title("Figure 4", "Data Flow Diagram Level 1 Explosion Aquaculture Value Chain Management System with Predictive Analytics")
    p_image(r"diagram/Level_1_DFD.png", width_in_inches=6.0)
    p_body("Figure 4 illustrates the Level 1 Data Flow Diagram (DFD) Explosion of the Aquaculture Value Chain Management System with Predictive Analytics. It presents the detailed flow of information among the Customer, Rider, Manager, system processes, and data stores. The diagram shows the major processes involved in the system, including browsing and product selection, order management, payment and settlement, delivery dispatch, management, report and monitoring, and predictive analytics. It also demonstrates how data such as customer and order information, production records, expenses, payment details, delivery records, inventory updates, and sales information are stored, processed, and exchanged to support ordering, payment, delivery, farm management, reporting, and predictive analysis.", indent=True)

    # Figure 5 (DFD Level 2 Product Browsing and Selection)
    p_figure_title("Figure 5", "Data Flow Diagram Level 2 of the Product Browsing and Selection process")
    p_image(r"Documents/Final_Paper/ch3_extracted_images/image6.jpeg", width_in_inches=5.5)
    p_body("Figure 5 illustrates the Level 2 Data Flow Diagram (DFD) Explosion of the Product Browsing and Selection process of the Aquaculture Value Chain Management System with Predictive Analytics. It provides a detailed view of how the system handles customer product selection through the processes of displaying the product catalog, searching and filtering products, checking stock availability, and selecting the product and quantity. The diagram also shows the flow of product information, stock status, available stock, order information, and reserved stock between the Customer, Order (D1), and Production (D3) data stores. The selected product and quantity are then forwarded to the Order Management process for subsequent order processing.", indent=True)

    # Figure 6 (DFD Level 2 Order Management)
    p_figure_title("Figure 6", "Data Flow Diagram Level 2 Explosion of Order Management process")
    p_image(r"Documents/Final_Paper/ch3_extracted_images/image7.jpeg", width_in_inches=5.5)
    p_body("Figure 6 illustrates the Level 2 Data Flow Diagram (DFD) Explosion of the Order Management process of the Aquaculture Value Chain Management System with Predictive Analytics. It presents the detailed flow of order processing through the processes of creating an order request, validating the order and customer information, and confirming or approving the order. The diagram shows how order details are received from the Customer, stored in the Order (D1) and Customer (D2) data stores, and validated before approval. The Manager reviews and approves the order, after which the confirmed order information is forwarded to the Payment and Set Location process for subsequent transaction and delivery processing.", indent=True)

    # Figure 7 (DFD Level 2 Payment and Set Location)
    p_figure_title("Figure 7", "Data Flow Diagram Level 2 Explosion of Payment and Set Location process")
    p_image(r"Documents/Final_Paper/ch3_extracted_images/image8.jpeg", width_in_inches=5.5)
    p_body("Figure 7 illustrates the Level 2 Data Flow Diagram (DFD) Explosion of the Payment and Set Location process of the Aquaculture Value Chain Management System with Predictive Analytics. It presents the detailed flow of payment and delivery information through the processes of setting the delivery or pickup location, processing GCash payments, and verifying and recording payments including Cash on Delivery (COD). The diagram shows the exchange of payment details, payment requests, payment responses, order records, and delivery information among the Customer, Rider, Order (D1), and Payment (D5) data stores. After payment verification and recording, the order details and location information are forwarded to the Delivery Dispatch process for subsequent delivery processing.", indent=True)

    # Figure 8 (DFD Level 2 Delivery Dispatch)
    p_figure_title("Figure 8", "Data Flow Diagram Level 2 Explosion of Delivery Dispatch process")
    p_image(r"Documents/Final_Paper/ch3_extracted_images/image9.jpeg", width_in_inches=5.5)
    p_body("Figure 8 illustrates the Level 2 Data Flow Diagram (DFD) Explosion of the Delivery Dispatch process of the Aquaculture Value Chain Management System with Predictive Analytics. It presents the detailed flow of delivery operations through the processes of assigning riders and generating route maps, tracking delivery status, and confirming delivery while updating stock. The diagram shows the exchange of order details, delivery records, rider assignments, route information, real-time tracking, and delivery status updates among the Customer, Rider, Manager, Order (D1), Production (D3), and Delivery (D6) data stores. Upon delivery completion, the system records the delivery confirmation, updates the order status, and processes the corresponding stock deduction before forwarding the confirmed order to the Management process.", indent=True)

    # Figure 9 (DFD Level 2 Management process)
    p_figure_title("Figure 9", "Data Flow Diagram Level 2 Explosion of Management process")
    p_image(r"Documents/Final_Paper/ch3_extracted_images/image10.jpeg", width_in_inches=5.5)
    p_body("Figure 9 illustrates the Level 2 Data Flow Diagram (DFD) Explosion of the Management process of the Aquaculture Value Chain Management System with Predictive Analytics. It presents the detailed flow of management activities through the processes of recording production and feeding data, managing expenses, and managing stock and replenishment. The diagram shows how delivery records, order information, production data, expense records, payment information, and stock levels are processed and exchanged among the Manager, Delivery (D6), Production (D3), Expense (D4), and Payment (D5) data stores. The processed delivery, expense, production, and inventory information is then forwarded to the Report and Monitoring process to support management reporting and operational monitoring.", indent=True)

    # Figure 10 (DFD Level 2 Report and Monitoring process)
    p_figure_title("Figure 10", "Data Flow Diagram Level 2 Explosion of Report and Monitoring process")
    p_image(r"Documents/Final_Paper/ch3_extracted_images/image11.jpeg", width_in_inches=5.5)
    p_body("Figure 10 illustrates the Level 2 Data Flow Diagram (DFD) Explosion of the Report and Monitoring process of the Aquaculture Value Chain Management System with Predictive Analytics. It presents the detailed flow of reporting activities through the processes of compiling inventory and dispatch data, generating sales and expense summaries, and generating printable reports. The diagram shows how inventory, dispatch, delivery, and expense information are collected from the Production (D3), Delivery (D6), and Expense (D4) data stores. The compiled and summarized data are processed into printable reports and provided to the Manager for monitoring and decision-making. The summarized data are also forwarded to the Predictive Analytics process for further analysis and forecasting.", indent=True)

    # Figure 11 (DFD Level 2 Predictive Analytics process)
    p_figure_title("Figure 11", "Data Flow Diagram Level 2 Explosion of Predictive Analytics process")
    p_image(r"Documents/Final_Paper/ch3_extracted_images/image12.jpeg", width_in_inches=5.5)
    p_body("Figure 11 illustrates the Level 2 Data Flow Diagram (DFD) Explosion of the Predictive Analytics process of the Aquaculture Value Chain Management System with Predictive Analytics. It presents the detailed flow of predictive analysis through the processes of sales forecasting using linear regression, customer and regional clustering, and harvest readiness prediction. The diagram shows how summary information from the Report and Monitoring process is used to generate forecasts and clustering analyses. The resulting forecast and clustering reports and harvest readiness predictions are provided to the Manager to support data-driven monitoring, planning, and decision-making.", indent=True)

    # 3.4 Entity Relationship Diagram
    p_heading_2("3.4 Entity Relationship Diagram")
    p_figure_title("Figure 12", "Entity-Relationship Diagram of Aquaculture Value Chain Management System with Predictive Analytics")
    p_image(r"diagram/ERD_Diagram.png", width_in_inches=6.0)
    p_body("Figure 12 illustrates the Entity-Relationship Diagram (ERD) of the Aquaculture Value Chain Management System with Predictive Analytics, showing the normalized physical database schema and relational constraints governing the aquaculture enterprise in Barangay Lantad, Silay City. The database architecture is organized into 15 core entities structured across user authentication, pond cultivation lifecycle, commercial inventory, point-of-sale customer transactions, logistics dispatching, and operational expense accounting. Relational integrity is enforced using primary keys (PK) and foreign keys (FK) across all tables to maintain referential consistency.", indent=True)
    p_body("At the user management foundation, the User entity manages credentials and role assignments (Owner, Customer, and Rider), linked one-to-one with the Profile and Customer entities. The cultivation lifecycle is modeled through the Operations_Pond entity, which tracks physical rearing ponds and coordinates with Cultivation_Batch to record species batches (Zophobas morio superworms and Cherax quadricarinatus redclaw crayfish), stage transitions, and stocking counts. Operational farm data is logged through child tables Feeding_Log (capturing feeding schedules and feed quantities) and Operations_Pond maintenance records, while completed rearing cycles are finalized in Harvest_Record. The commercial downstream value chain is governed by Inventory_Item (supporting dual pricing per piece and per kilogram) and Stock_Movement, directly connected to Order and Order_Item records. Transactions are finalized through Payment records (handling GCash receipt verification and Cash on Delivery), Delivery_Dispatch (capturing rider assignments, route coordinates, and Proof of Delivery), and Expense records (categorizing feeds, utilities, fuel, and facility maintenance overhead).", indent=True)

    # 3.5 UML Use Case Diagram
    p_heading_2("3.5 UML Use Case Diagram")
    p_figure_title("Figure 13", "UML Use Case Diagram of Aquaculture Value Chain Management System with Predictive Analytics")
    p_image(r"diagram/UML_Use_Case_Diagram.png", width_in_inches=6.0)
    p_body("Figure 13 illustrates the UML Use Case Diagram of the Aquaculture Value Chain Management System with Predictive Analytics, presenting the functional boundary and direct interactions between the system and its three primary actors: Owner, Customer, and Rider. The diagram defines the functional scope across user roles. The Owner manages executive analytics dashboards, pond cultivation operations (feeding schedules and Azula sanitization tracking), commercial inventory and batch production, expense logging, executive reporting, and predictive analytics forecasting (Linear Regression and K-Means customer segmentation). The Customer interacts with the storefront to browse available stock, configure delivery or pickup options, submit cart checkouts with integrated GCash or COD payment processing, and track live order transit. The Delivery Rider accesses assigned delivery pools, submits proof of delivery confirmations (recipient photo and signature), and updates delivery transit statuses.", indent=True)

    # 3.6 Use Case Scenario
    p_heading_2("3.6 Use Case Scenario")
    p_body("The Use Case Scenario describes the interaction between the primary entities (Farm Owner, Delivery Rider, and Commercial Customers) and the Aquaculture Value Chain Management System with Predictive Analytics. Each table details the operational goal, prerequisites, step-by-step main flow of activities, and summary user action and system response across farm operations, inventory management, order processing, courier dispatch, and predictive analytics forecasting.", indent=True)

    # Insert all 13 Use Case Tables (Tables 3 to 15) formatted exactly like the screenshot template
    for uc in buc_all.ALL_USE_CASES:
        buc_all.render_exact_use_case_table(doc, uc)

    # 3.7 Data Dictionary
    p_heading_2("3.7 Data Dictionary")
    p_body("The data dictionary describes the structure, data types, formats, field sizes, descriptions, and example values for each table in the Lantad Superworm & Crayfish Management System database. The tables documented below represent the core data entities of the system.", indent=True)

    import build_data_dictionary as bdd
    for item in bdd.DATA_DICTIONARY_TABLES:
        bdd.add_data_table(doc, item["num"], item["name"], item["fields"])

    # 3.8 System Requirements
    import build_section_3_8 as bs38
    bs38.add_section_3_8(doc)

    # 3.9 System Evaluation Tools & 3.10 Ethical Consideration
    import build_sections_eval_ethics as bsee
    bsee.add_eval_and_ethics_sections(doc)

    # ==================== CHAPTER IV: RESULTS AND DISCUSSION ====================
    doc.add_page_break()
    p_chapter_head("CHAPTER IV\nRESULTS AND DISCUSSION")

    p_body(
        "This chapter presents the results and discussions based on the development and evaluation of the "
        "Aquaculture Value Chain Management System with Predictive Analytics for Silay Superworm & Crayfish, in line "
        "with the objectives established in Chapter I. It includes comprehensive interface walkthroughs of the system's "
        "operational modules, the rigorous results of functionality testing (encompassing 68 Black-box functional test cases "
        "across twelve operational modules and 16 White-box structural test cases), and the software quality evaluation conducted in accordance with the "
        "ISO/IEC 25010:2011 Software Quality Model. Data were gathered from key stakeholders, including the Farm Owner, "
        "commercial buyers, retail customers, delivery riders, and independent IT experts, utilizing a five-point Likert scale "
        "ranging from 1 (Strongly Disagree) to 5 (Strongly Agree).",
        indent=True
    )

    p_body(
        "Furthermore, this chapter provides an empirical analysis of the system's execution under real-world aquaculture farm "
        "workflows in Barangay Lantad, Silay City, Negros Occidental. The findings demonstrate the system's technical effectiveness, "
        "operational reliability, data security, calculation precision in dual-unit pricing and inventory stock reconciliation, and capacity "
        "to eliminate manual recordkeeping inefficiencies while providing predictive decision-support capabilities through machine learning "
        "forecasting and customer segmentation.",
        indent=True
    )

    # 4.1 Results of the Study
    p_heading_2("4.1 Results of the Study")
    p_body(
        "The first objective of this study aimed to design and develop an Aquaculture Value Chain Management System with Predictive "
        "Analytics equipped with technical features including: (1) multi-role user authentication and session security, (2) an executive "
        "dashboard with real-time farm KPIs and sanitization alerts, (3) pond, cabin rack, and tank cultivation management, (4) feed formulation and daily "
        "supply logging, (5) Azula cultivation and 15-day pond sanitization monitoring, (6) harvest lifecycle scheduling and interactive production calendar, (7) "
        "commercial product catalog with dual-unit pricing (Per Piece and Per KG), (8) customer storefront with online cart checkout, (9) "
        "digital payment settlement supporting PayMongo GCash and COD, (10) sales order fulfillment and lifecycle state machine, (11) courier "
        "fleet dispatch and mobile rider portal with Proof of Delivery (POD), (12) real-time GPS tracking with Leaflet GIS maps, (13) predictive "
        "demand forecasting using Ordinary Least Squares Linear Regression, (14) customer segmentation using K-Means clustering, and (15) executive "
        "PDF/Excel report generation with a three-tiered audit trail.",
        indent=True
    )

    p_body(
        "The development of the system was completed using an enterprise Model-View-Template (MVT) architecture combining Python 3.11 with the "
        "Django 5.1 framework on the backend, supported by an ACID-compliant PostgreSQL / SQLite relational database, responsive HTML5/CSS3/JavaScript "
        "frontend with Bootstrap 5 and Tailwind CSS styling, Chart.js/ApexCharts interactive visualization libraries, and Leaflet.js GIS spatial "
        "mapping. The operational interfaces of the developed system are presented in Figures 14 through 29.",
        indent=True
    )

    import build_chapter4_section4_1 as bc4
    for fig_num, fname, title, desc in bc4.CHAPTER_4_FIGURES:
        bc4.add_figure_item(doc, fig_num, title, desc, img_filename=fname)

    # 4.2 Black-box and White-box Testing Results & 4.3 ISO 25010 Quality Evaluation (Tables 34 to 50)
    import build_chapter4_testing_tables as bc4t
    bc4t.add_section_4_2_and_4_3_to_doc(doc)

    # ==================== REFERENCES (STRICTLY ALPHABETICAL CONSOLIDATED) ====================
    doc.add_page_break()
    p_chapter_head("REFERENCES")

    references = [
        "Abdurrasyid, A., Indrianto, I., Susanti, M. N. I., & Purwanto, Y. S. (2021). Detection of water quality in crayfish ponds with IoT. Bulletin of Electrical Engineering and Informatics, 10(2), 886–897.",
        "Al Mamun, M. R., Ashik-E-Rabbani, M., Haque, M. M., & Upoma, S. M. (2024). IoT-based real-time biofloc monitoring and controlling system. Smart Agricultural Technology, 9, 100598.",
        "Asimaki, A., Psofakis, P., Gkalogianni, E. Z., Katouni, A. M., Berillis, P., Kormas, K. A., ... & Karapanagiotidis, I. T. (2025). The Effects of Dietary Fishmeal Substitution by Full‐Fat and Defatted Zophobas morio Larvae Meals on Juvenile Gilthead Seabream (Sparus aurata): An Integrative Approach. Aquaculture Nutrition, 2025(1), 8885509.",
        "Bouzidi, D., Mohamed, M. B., Ibraheem, M. K., Al-Abadi, A. A. J., & Fakhfakh, A. (2025). An IoT-Enabled Intelligent Monitoring System for Sustainable Aquaculture.",
        "Bush, S. R., Belton, B., Little, D. C., & Islam, M. S. (2019). The emerging aquaculture value chain: Spatial and social transformations in seafood production. Global Food Security, 21, 63–71.",
        "Caluag, J., et al. (2025). Internet of Things-Based Water Quality Monitoring System for Brackish Water Fishponds.",
        "Chang, C. C., Wang, J. H., Wu, J. L., Hsieh, Y. Z., Wu, T. D., Cheng, S. C., ... & Lin, C. Y. (2021). Applying artificial intelligence (AI) techniques to implement a practical smart cage aquaculture management system. Journal of Medical and Biological Engineering, 41(5), 652–658.",
        "Cheng, S., Han, Y. L., Chi, M. L., Zheng, J. B., Liu, S. L., Zhu, C., ... & Jiang, W. P. (2025). Bait composition, feeding frequency, stocking density, and water quality for the effective cultivation of large-sized redclaw crayfish seedlings.",
        "Chiu, M. C., Yan, W. M., Bhat, S. A., & Huang, N. F. (2022). Development of a smart aquaculture farm management system using IoT and AI-based surrogate models. Journal of Agriculture and Food Research, 9, 100357.",
        "Dawa, M., Lausa, S. M., & Tibon, M. R. (2022). Internet of things (IoT) based aquaponics management system adaptive to climate change. AIP Conference Proceedings, 2502(1), 050004.",
        "de Sousa Araujo, A. C., Pereira, A. C., Gomes, R. M. M., Ramirez, J. R. B., da Silva Noda, K., Santos, L. G., ... & Martins, V. G. (2025). Protein hydrolysates derived from superworm (Zophobas morio): Composition, bioactivity, and techno-functional properties. International Journal of Biological Macromolecules, 295, 139668.",
        "Durano, F. L. A., Romo, G. D. A., Sarmiento, J. M. P., Lopez, R. A., Hollite, J. B. D., & Padios, P. A. B. (2025). A review of the impacts of laws and policies on the nexus of the fisheries sector and gender in the Philippines. Marine Policy, 180, 106810.",
        "Food and Agriculture Organization. (2022). The State of World Fisheries and Aquaculture 2022: Towards Blue Transformation. FAO.",
        "Garcia, C., & Tibo, H. (2023). A solar-powered aquaponics with IoT-based monitoring and data gathering at the Technological University of the Philippines-Taguig.",
        "Gulifardo, A. B. E., Balane, B. J. D., Ebora, M. T., Serrano, M. R., Ellazar, E. P., Nicolas, A. V., & Maaño, R. C. (2025). iPond: An Internet of Things–Based Water Quality Monitoring System for Fishpond. IOP Conference Series: Earth and Environmental Science, 1446(1), 012005.",
        "Hu, Y., Zhang, L., Wang, Q., & Chen, J. (2025). Predictive models and time-series forecasting in aquaculture production management: A review. Aquacultural Engineering, 108, 102430.",
        "Jimmy Jr, C. L., & Gente, J. M. D. (2024). A time series analysis of aquaculture milkfish production volume using the Box-Jenkins SARIMA Model: A case study from Davao Oriental, Philippines. Davao Research Journal, 15(3), 6–19.",
        "Macusi, E. D., Estor, D. E. P., Borazon, E. Q., Clapano, M. B., & Santos, M. D. (2022). Environmental and socioeconomic impacts of shrimp farming in the Philippines: A critical analysis using PRISMA. Sustainability, 14(5), 2977.",
        "Macusi, E. D., Geronimo, R. C., & Santos, M. D. (2021). Vulnerability drivers for small pelagics and milkfish aquaculture value chain determined through online participatory approach. Marine Policy, 133, 104710.",
        "Macusi, E. D., Sales, A. C., Jimenez, J. E. M., Vender, E. K. E., Bongas, H. P., Macusi, E. S., & Andam, M. B. (2025). Assessment of Indigenous Feed Ingredients on Growth and Feed Utilization Efficiency in Juvenile Milkfish (Chanos chanos Forsskål, 1775). Israeli Journal of Aquaculture-Bamidgeh, 77(2), 231–244.",
        "Martínez, E. G., Stumpf, L., Planas, M., Gimenez, A. F., & Greco, L. L. (2024). Fishery wastes as feed additive for the red claw crayfish Cherax quadricarinatus: Impact on growth, biochemical composition, and digestive activity. Animal Feed Science and Technology, 318, 116116.",
        "Oliveira, J. S., Ribeiro, C. D. F., Souza, C. O. D., & Ribeiro, C. V. D. M. (2025). Mapping the use of insects in animal feed: scientific and technological data of Tenebrio molitor, Hermetia illucens, and Zophobas morio. Animal Production Science, 65(9), AN24415.",
        "Paz, K. S. D. (2019). Supply Response of Seaweeds in Philippines: An Autoregressive Distributive Lag Model.",
        "Prachom, N., Boonyoung, S., Hassaan, M. S., El‐Haroun, E., & Davies, S. J. (2021). Preliminary evaluation of Superworm (Zophobas morio) larval meal as a partial protein source in experimental diets for juvenile Asian sea bass, Lates calcarifer. Aquaculture Nutrition, 27(5), 1304–1314.",
        "Ragozzino-Paulino, P., Cocato, M. L., & de Souza Sarkis, J. E. (2025). Nutritional Potential of Edible Insects as Alternative Ingredients in Fish Feed: A Path to Modern Aquaculture. Aquaculture Nutrition, 2025(1), 7009004.",
        "Rigg, D. P., Wang, C. M., & Jerry, D. R. (2020). Aquaculture of the redclaw crayfish Cherax quadricarinatus: A review of farming practices, nutrition, and genetics. Reviews in Aquaculture, 13(1), 145–167.",
        "Rumbos, C. I., & Athanassiou, C. G. (2021). The superworm, Zophobas morio (Coleoptera: Tenebrionidae): A ‘sleeping giant’ in nutrient sources. Journal of Insects as Food and Feed, 7(5), 785–802.",
        "Salayo, N. D., Marte, C. L., Toledo, J. D., Gaitan, A. G., & Agbayani, R. F. (2021). Developing a self-sufficient Philippine milkfish industry through value chain analysis. Ocean & Coastal Management, 201, 105426.",
        "Silvederio, G. X. L., Javellana, T. F., Genciana, A. B. N., Fontanilla, M. A. G., Traifalgar, R. F. M., Huervana, F. H., & Del Castillo, C. S. (2025). Gut microbiome composition and diversity of wild-caught and hatchery-bred milkfish (Chanos chanos) fry. Journal of Genetic Engineering and Biotechnology, 23(3), 100520.",
        "Tahiluddin, A. B., Bornales, J. C., Limbaro, G. R. A., Paudac, M. A. T. U., Amarille, R. K., Sirad, N. R., ... & Esguerra, J. P. (2025). Environmental impacts of aquaculture in the Philippines.",
        "Tina, F. W., Afsarimanesh, N., Nag, A., & Alahi, M. E. E. (2025). Integrating AIoT technologies in aquaculture: A systematic review. Future Internet, 17(5), 199.",
        "Tolentino, L. K. (2021). Development of an IoT-based intensive aquaculture monitoring system with automatic water correction. International Journal of Computing and Digital Systems.",
        "WorldFish. (2021). Digital Innovations for Aquatic Food Systems: Annual Report 2021. WorldFish.",
        "WorldFish. (2022). Small-scale aquaculture digital value chains and market linkages in Southeast Asia. WorldFish Policy Brief.",
        "Wu, A. Q., Li, K. L., Song, Z. Y., Lou, X., Hu, P., Yang, W., & Wang, R. F. (2025). Deep learning for sustainable aquaculture: Opportunities and challenges. Sustainability, 17(11), 5084.",
        "Xu, Y., Jin, J. D., Zeng, S. W., Zhang, Y., & Xiao, Q. L. (2023). Development and evaluation of an IoT-based portable water quality monitoring system for aquaculture.",
        "Yang, X., Tang, Z., Huang, K., Guo, R., Wang, D., Jiang, S., & Yu, K. (2025). Optimal feeding levels to enhance growth performance and gut microbiota balance in red swamp crayfish (Procambarus clarkii). Aquaculture Reports, 41, 102717.",
        "Zapata Jr, N. R., Sarmiento, J. A. C., & Cruz, M. B. (2023). Development of smart food value chain intervention models for the milkfish industry in Region 1, Philippines. Asian Journal of Agriculture and Development, 20(1), 87–108."
    ]

    references_sorted = sorted(references, key=lambda s: s.lower())

    for ref in references_sorted:
        p_reference_item(ref)

    output_path = r'c:\Users\kymer\Desktop\Lantad ACarwfish Django\Documents\Final_Paper\Final_Paper.docx'
    doc.save(output_path)
    print(f"Successfully generated merged Final_Paper.docx with complete Chapter 3 (Figures 1-11)!")

if __name__ == '__main__':
    build_complete_final_paper()
