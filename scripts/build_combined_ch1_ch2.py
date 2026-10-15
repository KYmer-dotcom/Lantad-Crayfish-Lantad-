import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

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

def build_combined_ch1_and_2():
    doc = docx.Document()

    # Short bond paper (Letter: 8.5" x 11.0") with 1.5" left margin
    for section in doc.sections:
        section.page_width = Inches(8.5)
        section.page_height = Inches(11.0)
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.5)
        section.right_margin = Inches(1.0)

    # Base Normal Style: Arial 12pt
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Arial'
    normal_style.font.size = Pt(12)
    normal_style.font.color.rgb = RGBColor(0, 0, 0)
    normal_style.paragraph_format.line_spacing = None
    normal_style.paragraph_format.space_before = Pt(10)
    normal_style.paragraph_format.space_after = Pt(10)

    def p_title_line(text, bold=True, size=12):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = None
        run = p.add_run(text)
        run.bold = bold
        run.font.name = 'Arial'
        run.font.size = Pt(size)
        return p

    def p_blank(count=1):
        for _ in range(count):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = None

    def p_chapter_head(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(10)
        p.paragraph_format.line_spacing = None
        run = p.add_run(text)
        run.bold = True
        run.font.name = 'Arial'
        run.font.size = Pt(12)
        return p

    def p_heading_2(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(8)
        p.paragraph_format.line_spacing = None
        run = p.add_run(text)
        run.bold = True
        run.font.name = 'Arial'
        run.font.size = Pt(12)
        return p

    def p_heading_3(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.line_spacing = None
        run = p.add_run(text)
        run.bold = True
        run.font.name = 'Arial'
        run.font.size = Pt(12)
        return p

    def p_body(text, indent=True):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(10)
        p.paragraph_format.line_spacing = None
        if indent:
            p.paragraph_format.first_line_indent = Inches(0.5)
        run = p.add_run(text)
        run.font.name = 'Arial'
        run.font.size = Pt(12)
        return p

    def p_bullet(num_str, text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = None
        p.paragraph_format.left_indent = Inches(0.5)
        p.paragraph_format.first_line_indent = Inches(-0.25)
        run_num = p.add_run(num_str + " ")
        run_num.font.name = 'Arial'
        run_num.font.size = Pt(12)
        run_txt = p.add_run(text)
        run_txt.font.name = 'Arial'
        run_txt.font.size = Pt(12)
        return p

    def p_term(term, definition):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(10)
        p.paragraph_format.line_spacing = None
        p.paragraph_format.first_line_indent = Inches(0.5)
        run_t = p.add_run(term + " ")
        run_t.bold = True
        run_t.font.name = 'Arial'
        run_t.font.size = Pt(12)
        run_d = p.add_run(definition)
        run_d.font.name = 'Arial'
        run_d.font.size = Pt(12)
        return p

    def p_table_title(table_num, table_name):
        p1 = doc.add_paragraph()
        p1.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p1.paragraph_format.space_before = Pt(14)
        p1.paragraph_format.space_after = Pt(2)
        p1.paragraph_format.line_spacing = None
        run1 = p1.add_run(table_num)
        run1.bold = True
        run1.font.name = 'Arial'
        run1.font.size = Pt(12)

        p2 = doc.add_paragraph()
        p2.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p2.paragraph_format.space_before = Pt(0)
        p2.paragraph_format.space_after = Pt(6)
        p2.paragraph_format.line_spacing = None
        run2 = p2.add_run(table_name)
        run2.italic = True
        run2.font.name = 'Arial'
        run2.font.size = Pt(12)

    def p_reference_item(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(8)
        p.paragraph_format.line_spacing = None
        p.paragraph_format.left_indent = Inches(0.5)
        p.paragraph_format.first_line_indent = Inches(-0.5)
        run = p.add_run(text)
        run.font.name = 'Arial'
        run.font.size = Pt(12)
        return p

    # ==================== COVER PAGE ====================
    p_blank(2)
    p_title_line("AQUACULTURE VALUE CHAIN MANAGEMENT SYSTEM WITH PREDICTIVE ANALYTICS", bold=True, size=14)
    p_blank(4)
    p_title_line("A Capstone Project", bold=True, size=12)
    p_title_line("Presented to the Faculty of the", bold=True, size=12)
    p_title_line("College of Computer Studies", bold=True, size=12)
    p_title_line("Carlos Hilado Memorial State University", bold=True, size=12)
    p_blank(3)
    p_title_line("In Partial Fulfilment", bold=True, size=12)
    p_title_line("of the Requirements for the Degree", bold=True, size=12)
    p_title_line("BACHELOR OF SCIENCE IN INFORMATION SYSTEMS", bold=True, size=12)
    p_blank(3)
    p_title_line("By", bold=True, size=12)
    p_blank(1)
    p_title_line("[RESEARCH PROPONENTS]", bold=True, size=12)
    p_blank(3)
    p_title_line("OCTOBER 2026", bold=True, size=12)

    doc.add_page_break()

    # ==================== CHAPTER I ====================
    p_chapter_head("CHAPTER I")
    p_chapter_head("INTRODUCTION")

    p_body("Superworm and crayfish production play an emerging role in sustainable food production, animal feed development, and livelihood generation, particularly in small-scale and rural farming communities. Superworms (Zophobas morio) are increasingly recognized as a promising insect-based protein source for animal feed and other nutritional applications, while crayfish, particularly freshwater species such as redclaw crayfish (Cherax quadricarinatus), are cultivated as high-value freshwater crustaceans in aquaculture systems (Rumbos & Athanassiou, 2021; Rigg et al., 2020). As demand for alternative protein sources and freshwater aquatic products continues to rise, the expansion of superworm and crayfish farming has highlighted the need for more efficient management across breeding, feeding, harvesting, inventory, and distribution systems. Digital tools are becoming increasingly important in improving productivity, resource monitoring, and decision-making in aquatic food and farm production systems (Food and Agriculture Organization, 2022; WorldFish, 2021). Aquaculture value chain research also emphasizes the importance of understanding the linkages among producers, input suppliers, market intermediaries, and consumers across production, processing, and distribution activities (Bush et al., 2019).", indent=True)

    p_body("One of the major challenges faced by superworm and crayfish farms is the lack of centralized systems capable of managing operational data across different production units, species, batches, and growth cycles. Without an integrated digital platform, farm managers may encounter difficulties in consolidating production records, monitoring feed and water usage, tracking mortality and growth performance, and evaluating overall farm productivity. Many small and medium farm enterprises continue to experience inefficient data management and limited technological integration. Digital platforms can support farmers and value chain actors by improving access to production information, feed management, market linkages, and farm performance tracking (WorldFish, 2021; WorldFish, 2022).", indent=True)

    p_body("To address these challenges, the development of a Superworm and Crayfish Value Chain Management System with Predictive Analytics is proposed to support more efficient data management and value chain coordination. The proposed system aims to provide a centralized digital platform capable of storing, organizing, and analyzing data related to superworm rearing, crayfish pond operations, feeding activities, inventory, harvesting, supply transactions, and market distribution. By incorporating predictive analytics, the system can generate data-driven insights that support planning and strategic decision-making, such as estimating production trends, forecasting harvest volume, monitoring supply levels, and improving resource allocation. Recent research in aquatic production forecasting demonstrates that predictive models using historical and environmental data can support producers and decision-makers in improving planning and resource management across aquaculture-related value chains (Hu et al., 2025).", indent=True)

    # 1.1 Background
    p_heading_2("1.1 Background of the Study")
    p_body("Silay Superworm & Crayfish, a farming enterprise located in Brgy. Lantad, Silay City, operates production areas for superworm rearing and crayfish cultivation. As the demand for alternative protein sources and freshwater aquaculture products continues to grow, the farm needs to modernize its operations to meet increasing market demand and manage growing production complexity. Stakeholders, including the farm owner, delivery riders, and customers, require timely and accurate information to monitor production, manage resources, and coordinate activities across different production and distribution channels.", indent=True)
    p_body("Currently, Silay Superworm & Crayfish faces challenges in managing operational data and coordinating value chain activities due to fragmented record-keeping practices. These include manual logs and paper-based systems, which limit efficient monitoring of superworm batches, crayfish pond performance, inventory tracking, feeding schedules, harvesting activities, and sales records. This fragmented approach reduces transparency and slows down decision-making, potentially leading to inefficient resource allocation and reduced competitiveness.", indent=True)
    p_body("To address these issues, a centralized digital management system with predictive analytics is proposed. The system will integrate superworm production management, crayfish pond monitoring, feed and harvest data, inventory records, and sales information into a unified web-based platform. By providing real-time insights and predictive forecasts, the system aims to improve coordination, enhance productivity, support better decision-making, and contribute to the sustainable growth of Silay Superworm & Crayfish.", indent=True)

    # 1.2 Objectives
    p_heading_2("1.2 Objectives of the Study")
    p_body("The purpose of the study is to develop a Silay Superworm & Crayfish Value Chain Management System with Predictive Analytics that improves the monitoring, management, and analysis of farm operations, including production, inventory, sales, and expenses.", indent=True)
    p_body("Specifically, this study aims to:", indent=True)
    p_bullet("1.", "Design and develop a Silay Superworm & Crayfish Value Chain Management System with the following features:")
    p_bullet("   1.1.", "Documentation of superworm and crayfish production processes, including breeding, feeding, harvesting, processing, distribution, and delivery;")
    p_bullet("   1.2.", "Sales and inventory management for tracking stock, transactions, and product availability;")
    p_bullet("   1.3.", "Product classification based on type, category, and scientific name;")
    p_bullet("   1.4.", "Monitoring of monthly operational expenses;")
    p_bullet("   1.5.", "Forecasting and predictive analytics for production, expenses, and market demand;")
    p_bullet("   1.6.", "Customer transaction management, including wholesale, retail, and reservations;")
    p_bullet("   1.7.", "Data clustering for analyzing production, sales patterns, and customer behavior; and")
    p_bullet("   1.8.", "Report generation and analytics for decision-making.")
    p_bullet("2.", "Test the functionality of the developed system.")
    p_bullet("3.", "Evaluate the usability of the system in terms of:")
    p_bullet("   3.1.", "System usefulness;")
    p_bullet("   3.2.", "Quality of information;")
    p_bullet("   3.3.", "Interface quality; and")
    p_bullet("   3.4.", "Overall usability.")
    p_bullet("4.", "Develop a User Manual for the system.")

    # 1.3 Scope and Limitations
    p_heading_2("1.3 Scope and Limitations of the Study")
    p_body("This study focuses on the development of a Silay Superworm & Crayfish Value Chain Management System with Predictive Analytics designed for Silay Superworm & Crayfish. The system provides a centralized platform for managing farm production data, including superworm rearing, crayfish pond operations, harvest records, product classification, inventory, sales transactions, and operational expenses. It also includes predictive analytics to generate forecasts related to production, expenses, and market demand. The system supports customer transaction management and generates analytical reports for decision-making. The system will be web-based and accessible through standard browsers, with data stored in a centralized database.", indent=True)
    p_body("The study has limitations. The system will not include real-time sensor integration, such as temperature, dissolved oxygen, pH levels, or humidity monitoring, since data will be manually entered by authorized users. Predictive analytics will rely on historical data and will not include advanced machine learning models. Furthermore, the system is tailored specifically for Silay Superworm & Crayfish and may require modifications if applied to other farming or aquaculture enterprises.", indent=True)

    # 1.4 Significance
    p_heading_2("1.4 Significance of the Study")
    p_body("The development of the Silay Superworm & Crayfish Value Chain Management System with Predictive Analytics is expected to benefit several stakeholders involved in superworm and crayfish production and distribution operations.", indent=True)
    p_term("Farm Owners.", "The system provides a centralized executive management platform that unifies production monitoring, inventory balances, sales turnover, and operational expenses into comprehensive reports. It assists the farm owner in making timely and data-driven business decisions through predictive yield estimations, expense tracking, and market demand forecasts.")
    p_term("Delivery Riders.", "The system provides a dedicated mobile delivery interface that streamlines order dispatching, provides accurate customer delivery addresses and contact information, facilitates navigation, and allows the capture of photo-verified Proof of Delivery upon successful product turnover.")
    p_term("Customers and Buyers.", "The system offers an accessible and transparent online marketplace where customers can browse live superworm and crayfish inventories, select flexible fulfillment options (such as pickup or home delivery with GPS location pinning), and complete secure transactions through digital payment gateways or cash on delivery.")
    p_term("Researchers and Future Developers.", "This study provides an empirical reference and architectural framework for future research on the digital transformation of small-scale agricultural enterprises, aquaculture supply chain automation, and the integration of predictive analytics in specialized farm management systems.")
    p_term("The University and Academic Community.", "The study contributes to the academic literature in information systems by demonstrating the practical application of web development technologies, data analytics, and value chain modernization to enhance productivity and sustainability in local agro-aquaculture businesses.")

    # 1.5 Definition of Terms
    p_heading_2("1.5 Definition of Terms")
    p_term("Analytics Dashboard.", "A specialized graphical user interface within the system that aggregates, summarizes, and visually displays farm production statistics, inventory levels, financial performance, and sales trends. It utilizes charts, metrics cards, and data summaries to facilitate monitoring and informed decision-making.")
    p_term("Aquaculture.", "The controlled cultivation and breeding of aquatic organisms, specifically redclaw crayfish (Cherax quadricarinatus), encompassing pond management, water parameter maintenance, scheduled feeding, and harvest operations.")
    p_term("Clustering.", "An analytical data-grouping method implemented within the system to categorize customers, order sizes, and sales patterns based on purchasing frequency, geographic distribution, and transaction volumes.")
    p_term("Inventory Management.", "The centralized digital tracking and recording of live superworm stages and crayfish size classifications, monitoring batch quantities, daily mortality, stock deductions, and real-time stock levels.")
    p_term("Operational Expenses.", "The recurring financial costs incurred during farm operations, including feed purchases, utility bills, packaging, transport, and maintenance, recorded to compute net profit and financial health.")
    p_term("Predictive Analytics.", "The application of statistical models and time-series forecasting techniques to historical farm data to project future harvest yields, anticipated operational costs, and customer market demand.")
    p_term("Proof of Delivery.", "A digital verification feature enabling delivery riders to upload photo evidence and recipient confirmations upon successful order handover.")
    p_term("Value Chain.", "The full range of interconnected activities involved in bringing superworm and crayfish products from initial breeding and rearing through harvesting, packaging, pricing, inventory management, order processing, and final delivery.")
    p_term("Wholesale and Retail Sales.", "The dual commercial distribution channels managed by the system, where wholesale pertains to bulk-volume pricing for commercial resellers and retail involves standard-unit purchases by individual end-consumers.")

    # ==================== CHAPTER II ====================
    doc.add_page_break()
    p_chapter_head("CHAPTER II")
    p_chapter_head("REVIEW OF RELATED LITERATURE AND SYSTEMS")

    p_body("This chapter contains the selected review of related literature, studies, and the interrelated system as proponents’ basis for making and developing the Aquaculture Value Chain Management System with Predictive Analytics.", indent=True)

    # 2.1 Foreign Related Literature
    p_heading_2("2.1 Foreign Related Literature")

    p_heading_3("Bait composition, feeding frequency, stocking density, and water quality for the effective cultivation of large-sized redclaw crayfish seedlings")
    p_body("Cheng et al. (2025) investigated the effects of bait composition, feeding frequency, stocking density, and water quality management on the cultivation of redclaw crayfish (Cherax quadricarinatus) seedlings. The study found that juveniles fed with a combination of formulated feed, Spirulina powder, and Antarctic krill oil two to three times daily achieved better survival and growth than those given formulated feed alone. Lower stocking density also resulted in higher survival, while regular monitoring of water quality helped maintain suitable conditions for crayfish development. The authors concluded that proper feeding, appropriate stocking density, and water quality management are essential for improving crayfish seedling production. This study is relevant to the present research because it highlights the importance of monitoring production activities, feeding practices, and farm conditions, which can be supported through a centralized value chain management system.", indent=True)

    p_heading_3("Deep Learning for Sustainable Aquaculture: Opportunities and Challenges")
    p_body("Wu et al. (2025) reviewed the application of deep learning technologies in aquaculture, focusing on fish detection, growth prediction, health monitoring, intelligent feeding, water quality forecasting, and behavior analysis. The study found that deep learning can improve aquaculture operations by automating monitoring, supporting feeding decisions, predicting environmental conditions, and identifying potential health problems. However, challenges such as limited datasets, real-time processing, and differences among farming environments remain. The authors emphasized the potential of advanced data-driven technologies to improve productivity, reduce resource waste, and promote sustainable aquaculture. This study is relevant to the present research because it supports the use of predictive analytics and digital technologies for monitoring farm operations and assisting management decision-making.", indent=True)

    p_heading_3("Mapping the use of insects in animal feed: scientific and technological data of Tenebrio molitor, Hermetia illucens, and Zophobas morio")
    p_body("Oliveira et al. (2025) reviewed the scientific and technological development of Tenebrio molitor, Hermetia illucens, and Zophobas morio as alternative ingredients for animal feed. The study analyzed scientific publications and patent records to identify research trends and applications of these insect species. The findings showed that T. molitor and H. illucens have received greater scientific and technological attention, particularly in aquaculture and poultry production, while Z. morio remains comparatively underdeveloped despite its nutritional potential. The authors emphasized that insect-based feed can contribute to sustainable animal production, reduce dependence on conventional feed ingredients, and support circular economy practices. This study is relevant to the present research because it highlights the potential of Zophobas morio as an emerging resource and supports the need for improved production management and monitoring of superworm farming activities.", indent=True)

    p_heading_3("Nutritional Potential of Edible Insects as Alternative Ingredients in Fish Feed: A Path to Modern Aquaculture")
    p_body("Ragozzino-Paulino, Cocato, and de Souza Sarkis (2025) reviewed the nutritional potential of edible insects as alternative ingredients in aquaculture feeds. The study found that insect meals are rich in protein, amino acids, lipids, minerals, and other nutrients that can support fish growth, feed efficiency, and immune function. The authors emphasized that insect-based feeds can reduce dependence on fishmeal and fish oil while promoting sustainable aquaculture. This study supports the present research by highlighting the increasing importance of insect production, particularly superworms, as a sustainable source of animal feed.", indent=True)

    p_heading_3("The Superworm, Zophobas morio (Coleoptera:Tenebrionidae): A ‘Sleeping Giant’ in Nutrient Sources")
    p_body("Rumbos and Athanassiou (2021) reviewed the biological characteristics, nutritional composition, and potential applications of superworm (Zophobas morio) in animal feed, human food, and waste management. The study found that Z. morio contains high levels of protein, fat, minerals, amino acids, and chitin, making it a promising alternative nutrient source. The authors also highlighted its potential contribution to sustainable production and waste reduction but noted the need for further research on safety, mass production, and regulatory requirements. This study is relevant to the present research because it establishes the nutritional and economic potential of Z. morio and supports the importance of effective management of superworm production.", indent=True)

    # 2.2 Local Related Literature
    p_heading_2("2.2 Local Related Literature")

    p_heading_3("A time series analysis of aquaculture milkfish production volume using the Box-Jenkins SARIMA Model: A case study from Davao Oriental, Philippines")
    p_body("Jimmy Jr and Gente (2024) investigated the use of the Box-Jenkins Seasonal Autoregressive Integrated Moving Average (SARIMA) model to forecast milkfish production in Davao Oriental, Philippines. Using production data from 1996 to 2023, the study analyzed historical trends and developed a seasonal forecasting model. The results identified SARIMA (2,0,2)(1,1,1)₄ as the most suitable model for predicting future milkfish production, although fluctuations and uncertainties remained due to possible environmental and climate-related factors. The authors concluded that time-series forecasting can assist farmers, planners, and local government units in anticipating production trends and improving aquaculture planning. This study is relevant to the present research because it demonstrates how historical production data and predictive analytics can be used to forecast future farm production and support data-driven decision-making. It also supports the proposed system's predictive analytics feature for forecasting production, expenses, and market demand.", indent=True)

    p_heading_3("Assessment of Indigenous Feed Ingredients on Growth and Feed Utilization Efficiency in Juvenile Milkfish (Chanos chanos Forsskål, 1775)")
    p_body("Macusi et al. (2025) investigated the use of indigenous and locally available feed ingredients for juvenile milkfish (Chanos chanos) aquaculture in the Philippines. The study evaluated alternative feed materials such as copra meal, azolla, taro, blood meal, golden apple snail, cacao pod, banana stem, and soybean meal based on their effects on fish growth and feed utilization. The results showed that copra meal and azolla produced the highest final weights and favorable feed conversion performance, while all alternative diets performed comparably to the control diet. The authors concluded that locally available and agricultural waste-based ingredients can be used as alternative feed resources without negatively affecting milkfish growth. This study is relevant to the present research because it demonstrates the importance of utilizing locally available resources and managing feed-related data to improve production efficiency, reduce costs, and promote sustainable farming practices.", indent=True)

    p_heading_3("A review of the impacts of laws and policies on the nexus of the fisheries sector and gender in the Philippines")
    p_body("Durano et al. (2025) reviewed Philippine fisheries laws and policies to examine their effects on gender equality and women's participation in the fisheries sector. The study found that women play important roles in fisheries production, processing, marketing, and resource management, but their contributions may be overlooked when policies do not adequately consider gender-related concerns. The authors emphasized the need for stronger implementation of gender-responsive policies, greater participation of women, and improved recognition of their roles in the fisheries sector. This study is relevant to the present research because it highlights the importance of inclusive management systems that recognize different stakeholders involved in agricultural and aquaculture value chains. It also supports the inclusion of organized records and management features that can improve the visibility, participation, and coordination of workers and other stakeholders within farm operations.", indent=True)

    p_heading_3("Developing a self-sufficient Philippine milkfish industry through value chain analysis")
    p_body("Salayo et al. (2021) examined the Philippine milkfish (Chanos chanos) industry through value chain analysis, focusing on the production and supply of eggs, larvae, fry, and fingerlings needed for grow-out operations. The study found that the industry remains dependent on imported juveniles due to declining wild fry production and insufficient local hatchery capacity. The authors emphasized the need to strengthen local breeding, hatchery, nursery, and grow-out enterprises through public-private partnerships to achieve a more self-sufficient milkfish industry. This study is relevant to the present research because it highlights the importance of value chain coordination, production monitoring, resource planning, and supply management in aquaculture. It supports the development of a centralized management system that can help organize production, inventory, supply, and distribution information to improve farm operations and strengthen the aquaculture value chain.", indent=True)

    p_heading_3("Environmental Impacts of Aquaculture in the Philippines")
    p_body("Tahiluddin et al. (2025) reviewed the environmental impacts of aquaculture in the Philippines, focusing on its effects on marine habitats, biodiversity, water quality, sediments, and pollution. The study found that although aquaculture contributes to food security, employment, and economic development, poorly managed operations may result in mangrove and seagrass degradation, water pollution, biodiversity loss, sediment disturbance, and waste-related environmental problems. The authors emphasized the importance of water quality monitoring, proper waste management, biosecurity, environmental regulations, and sustainable aquaculture practices. This study is relevant to the present research because it highlights the importance of monitoring and managing farm resources and environmental conditions. It supports the development of a centralized management system that can help organize production and operational records, improve resource management, and provide data that can assist farmers in making more sustainable decisions.", indent=True)

    # 2.3 Foreign System
    p_heading_2("2.3 Foreign System")

    p_heading_3("Applying Artificial Intelligence (AI) Techniques to Implement a Practical Smart Cage Aquaculture Management System")
    p_body("Chang et al. (2021) developed an artificial intelligence and Internet of Things (AIoT)-based smart cage aquaculture management system to improve the monitoring and management of fish production. The system collected farm data through an Ocean Cloud platform and applied data analysis and artificial intelligence to monitor fish health, survival, growth, and feed residues. The results showed that the system could support more efficient feeding, reduce feed waste, improve survival and feed conversion, and assist farmers in making timely management decisions. The authors concluded that AIoT technologies can improve aquaculture efficiency and sustainability by reducing labor requirements and providing more accurate production information. This study is relevant to the present research because it demonstrates how digital technologies and data analytics can be applied to aquaculture management and supports the use of centralized data management and predictive analytics in monitoring farm operations and improving decision-making.", indent=True)

    p_heading_3("Detection of water quality in crayfish ponds with IoT")
    p_body("Abdurrasyid et al. (2021) developed an Internet of Things (IoT)-based system for monitoring water quality in crayfish ponds. The system used sensors, Arduino, an ESP8266 module, cloud services, and a smartphone interface to monitor important water parameters such as temperature and pH. The results showed that the system achieved 98.06% accuracy in classifying pond water conditions as suitable or unsuitable. The authors concluded that IoT-based monitoring can reduce the need for manual water-quality checking and help farmers maintain suitable conditions for crayfish production. This study is relevant to the present research because it demonstrates how digital technologies can improve crayfish farm monitoring and provide timely information for management decisions.", indent=True)

    p_heading_3("DEVELOPMENT AND EVALUATION OF AN IoT-BASED PORTABLE WATER QUALITY MONITORING SYSTEM FOR AQUACULTURE")
    p_body("Xu et al. (2023) developed and evaluated a portable Internet of Things (IoT)-based water quality monitoring system designed for small and medium-sized aquaculture farms. The system monitored important water-quality parameters, including temperature, dissolved oxygen, ammonia nitrogen, and pH, and transmitted the collected data wirelessly to a cloud platform for remote monitoring. The results showed that the system provided accurate and stable data transmission with minimal data loss across the monitored parameters. The authors concluded that the portable system can support both fixed and remote water-quality monitoring and help farmers detect environmental problems at an earlier stage. This study is relevant to the present research because it demonstrates the benefits of digital technologies in monitoring aquaculture conditions and improving farm management. However, unlike the proposed system, the present study does not include real-time IoT sensor integration and instead relies on manually entered farm data for monitoring and predictive analytics.", indent=True)

    p_heading_3("Development of smart aquaculture farm management system using IoT and AI-based surrogate models")
    p_body("Chiu et al. (2022) developed a smart aquaculture farm management system that integrated Internet of Things (IoT) and artificial intelligence (AI) technologies to improve fishpond monitoring and feeding management. The system collected real-time environmental and operational data and used a deep learning model with Bayesian optimization to predict the growth of California bass. The optimized model achieved an R² value of 0.94 and a mean square error of 0.0015, indicating strong predictive performance. The study showed that AIoT-based systems can support remote monitoring, improve feeding decisions, reduce feed waste, and lessen labor requirements. This study is relevant to the present research because it demonstrates how predictive analytics and digital technologies can be applied to production management and decision-making. While the proposed system does not use real-time IoT monitoring or advanced deep learning, it similarly applies data analysis and forecasting to support more efficient superworm and crayfish farm operations.", indent=True)

    p_heading_3("IoT-based real-time biofloc monitoring and controlling system")
    p_body("Al Mamun et al. (2024) developed an Internet of Things (IoT)-based real-time monitoring and control system for biofloc aquaculture. The system used multiple sensors and an ESP32 microcontroller to continuously monitor water temperature, dissolved oxygen, pH, total dissolved solids, turbidity, and water level. Data were transmitted to mobile and computer devices through the Blynk application, allowing users to monitor pond conditions remotely. The system could also automatically activate or deactivate equipment when water conditions exceeded predetermined ranges. The results demonstrated that the system maintained suitable water conditions and reduced the need for manual monitoring. The authors concluded that IoT-based monitoring and automated control can improve aquaculture productivity, water-quality management, and sustainability. This study is relevant to the present research because it demonstrates how digital technologies can improve aquaculture management through centralized data monitoring and timely decision-making. However, real-time sensor integration and automated equipment control are beyond the scope of the proposed system, which relies on manually entered data and predictive analytics.", indent=True)

    # 2.4 Local System
    p_heading_2("2.4 Local System")

    p_heading_3("A Solar-Powered Aquaponics with IoT-Based Monitoring and Data Gathering at the Technological University of the Philippines-Taguig")
    p_body("Garcia and Tibo (2023) developed a solar-powered aquaponics system with Internet of Things (IoT)-based monitoring and data gathering at the Technological University of the Philippines–Taguig. The system was designed for lettuce and tilapia production and used sensors to monitor pH, total dissolved solids, room temperature, humidity, and water temperature. Solar panels provided the system's energy, while the IoT website allowed users to collect and view environmental and water-quality data. The results showed that the system could effectively monitor important production conditions and support the growth of lettuce and tilapia. The study emphasized the importance of regular environmental monitoring and the potential of renewable energy in sustainable food production. This study is relevant to the present research because it demonstrates how digital monitoring and data management can support agricultural and aquaculture operations. It also reinforces the potential of technology to improve resource management and decision-making in small-scale farming systems.", indent=True)

    p_heading_3("Development of an IoT-based Intensive Aquaculture Monitoring System with Automatic Water Correction")
    p_body("Tolentino (2021) developed an Internet of Things (IoT)-based intensive aquaculture monitoring system with automatic water-quality correction. The system used sensors, Arduino, Raspberry Pi, LoRaWAN, a database, and a web application to monitor parameters such as temperature, pH, turbidity, salinity, oxidation-reduction potential, and dissolved oxygen. It also included automated devices that corrected water conditions when measurements exceeded desired levels. The results showed that fish in the IoT-controlled setup achieved better growth than those in the conventional setup, increasing from 24 g to 41 g compared with 24 g to 35 g. The study concluded that automated water-quality monitoring and correction can improve aquaculture conditions, reduce manual work, and increase production efficiency. This study is relevant to the present research because it demonstrates how centralized digital monitoring and data management can support aquaculture operations and improve decision-making. However, automatic sensor-based monitoring and water correction are outside the scope of the proposed system, which focuses on manually entered production data and predictive analytics.", indent=True)

    p_heading_3("Internet of things (IoT) based aquaponics management system adaptive to climate change")
    p_body("Dawa, Lausa, and Tibon (2022) developed an Internet of Things (IoT)-based aquaponics management system designed to support climate-adaptive and sustainable food production. The system used sensors, Arduino, NodeMCU, cloud storage, a mobile application, and solar power to monitor and manage important water-quality parameters such as pH, temperature, and dissolved oxygen. It also provided features for scheduled feeding, water-release management, remote monitoring, report generation, and automated control. The results showed that the system effectively provided real-time monitoring and received a high average evaluation rating of 4.32, interpreted as “Strongly Agree,” indicating that users considered it reliable, efficient, applicable, portable, and economically feasible. The authors concluded that IoT-based aquaponics systems can reduce manual labor and improve resource and water-quality management. This study is relevant to the present research because it demonstrates how digital systems, centralized data management, and automated reporting can improve farming and aquaculture operations. It also supports the proposed system's goal of providing organized production records, analytics, and decision-support features for more efficient farm management.", indent=True)

    p_heading_3("Integrating AIoT Technologies in Aquaculture: A Systematic Review")
    p_body("Tina et al. (2025) conducted a systematic review on the integration of Artificial Intelligence of Things (AIoT) technologies in aquaculture. The study examined the use of IoT sensors and artificial intelligence in areas such as water-quality monitoring, smart feeding, disease detection, fish behavior analysis, automated counting, and production management. The findings showed that AIoT can improve aquaculture operations through real-time monitoring, automated decision-making, feeding optimization, early disease detection, and improved resource management. However, challenges such as implementation costs, scalability, technical requirements, and model generalization remain. The authors concluded that AIoT has significant potential to make aquaculture more efficient and sustainable as these challenges are addressed. This study is relevant to the present research because it supports the use of digital technologies and predictive analytics in managing aquaculture operations. It also reinforces the importance of centralized data collection and analysis in improving production monitoring, resource allocation, and farm decision-making. Unlike the AIoT systems discussed in the study, the proposed system focuses on manually entered farm data and predictive analytics rather than real-time sensor integration.", indent=True)

    p_heading_3("Internet of Things-Based Water Quality Monitoring System for Brackish Water Fishponds")
    p_body("Caluag et al. (2025) developed an IoT-based water-quality monitoring system for brackish-water fishponds to improve aquaculture monitoring and decision-making. The system uses sensors to collect and transmit water-quality data, providing fishpond operators with timely information and reducing reliance on manual monitoring. The study demonstrated that IoT technology can improve the efficiency of water-quality monitoring and help farmers respond to changing pond conditions. However, the system focuses mainly on water-quality monitoring and does not cover the entire aquaculture value chain or predictive analytics. Thus, it provides a foundation for the proposed Aquaculture Value Chain Management System with Predictive Analytics, which can integrate real-time monitoring with production, inventory, harvesting, pricing, sales, distribution, and demand forecasting.", indent=True)

    # ==================== 2.5 SYNTHESIS ====================
    p_heading_2("2.5 Synthesis")

    # Table 1: Synthesis of Related Literature
    p_table_title("Table 1", "Synthesis of Related Literature")

    table1_data = [
        ("Related Studies", "Features & Functionalities", "Developed System"),
        (
            "Cheng, Han, Chi, Zheng, Liu, Zhu, and Jiang (2025). Bait composition, feeding frequency, stocking density, and water quality for the effective cultivation of large-sized redclaw crayfish seedlings.",
            "Investigates the effects of formulated bait composition, feeding frequency, stocking density, and water-quality management on redclaw crayfish seedling survival and growth.",
            "Supports the integration of feeding management, pond stocking records, and water-quality monitoring modules in the developed system."
        ),
        (
            "Wu, Li, Song, Lou, Hu, Yang, and Wang (2025). Deep Learning for Sustainable Aquaculture: Opportunities and Challenges.",
            "Reviews artificial intelligence and deep learning applications in growth forecasting, environmental condition monitoring, intelligent feeding, and health analysis.",
            "Supports the incorporation of predictive analytics, time-series forecasting, and automated data dashboards for farm management decision-making."
        ),
        (
            "Oliveira, Ribeiro, Souza, and Ribeiro (2025). Mapping the use of insects in animal feed: scientific and technological data of Tenebrio molitor, Hermetia illucens, and Zophobas morio.",
            "Analyzes technological data and scientific applications of insect species including superworms as sustainable alternative ingredients for animal and aquaculture feeds.",
            "Reinforces the economic viability and necessity of centralized production, harvest, and inventory management for superworm farming operations."
        ),
        (
            "Ragozzino-Paulino, Cocato, and de Souza Sarkis (2025). Nutritional Potential of Edible Insects as Alternative Ingredients in Fish Feed: A Path to Modern Aquaculture.",
            "Evaluates the nutritional profile, protein value, and lipid composition of edible insects used as sustainable substitutes for conventional aquafeeds.",
            "Provides empirical basis for feed consumption tracking, nutritional batch logging, and feed cost analysis within the management platform."
        ),
        (
            "Rumbos and Athanassiou (2021). The Superworm, Zophobas morio (Coleoptera:Tenebrionidae): A ‘Sleeping Giant’ in Nutrient Sources.",
            "Examines the biological characteristics, growth cycles, rearing conditions, and commercial potential of superworms across modern farming sectors.",
            "Informs the design of superworm rearing stages, life-cycle tracking, colony monitoring, and batch inventory modules in the system."
        ),
        (
            "Jimmy Jr and Gente (2024). A time series analysis of aquaculture milkfish production volume using the Box-Jenkins SARIMA Model: A case study from Davao Oriental, Philippines.",
            "Implements time-series forecasting using SARIMA modeling on historical farm production data to anticipate yields and improve aquaculture planning.",
            "Validates the use of historical production and sales data to power predictive yield estimations and demand forecasting modules in the system."
        ),
        (
            "Macusi, Sales, Jimenez, Vender, Bongas, Macusi, and Andam (2025). Assessment of Indigenous Feed Ingredients on Growth and Feed Utilization Efficiency in Juvenile Milkfish (Chanos chanos Forsskål, 1775).",
            "Evaluates local and agricultural waste-derived feed ingredients to enhance feed utilization efficiency and reduce operational feed costs in Philippine aquaculture.",
            "Supports the system's feed expense tracking and supplier cost management functionalities to optimize farm operating expenses."
        ),
        (
            "Durano, Romo, Sarmiento, Lopez, Hollite, and Padios (2025). A review of the impacts of laws and policies on the nexus of the fisheries sector and gender in the Philippines.",
            "Examines stakeholder participation, labor coordination, and governance policies across Philippine agricultural and fisheries value chains.",
            "Supports multi-stakeholder coordination, role-based access control, and transparent operational records for farm owners, riders, and buyers."
        ),
        (
            "Salayo, Marte, Toledo, Gaitan, and Agbayani (2021). Developing a self-sufficient Philippine milkfish industry through value chain analysis.",
            "Conducts comprehensive value chain mapping across breeding, nursery, grow-out, logistics, and market distribution stages in local aquaculture.",
            "Guides the architectural design of end-to-end value chain workflows connecting production, inventory, logistics, and customer order fulfillment."
        ),
        (
            "Tahiluddin, Bornales, Limbaro, Paudac, Amarille, Sirad, and Esguerra (2025). Environmental Impacts of Aquaculture in the Philippines.",
            "Analyzes water quality, pond sediment, and resource management practices to promote environmentally sustainable aquaculture operations.",
            "Informs the recording of pond parameters, water maintenance schedules, and resource utilization reports to support sustainable farm management."
        )
    ]

    t1 = doc.add_table(rows=len(table1_data), cols=3)
    t1.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_apa_table_borders(t1)
    col_widths = [Inches(2.1), Inches(1.9), Inches(2.0)]

    for row_idx, row_data in enumerate(table1_data):
        row = t1.rows[row_idx]
        is_header = (row_idx == 0)
        is_last = (row_idx == len(table1_data) - 1)

        trPr = row._tr.get_or_add_trPr()
        trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")} w:val="1"/>'))
        trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")} w:val="0"/>'))

        for col_idx, text in enumerate(row_data):
            cell = row.cells[col_idx]
            cell.width = col_widths[col_idx]
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

    p_blank(1)

    # Table 2: Synthesis of Related Systems
    p_table_title("Table 2", "Synthesis of Related Systems")

    table2_data = [
        ("Related Studies", "Features & Functionalities", "Developed System"),
        (
            "Chang, Wang, Wu, Hsieh, Wu, Cheng, and Lin (2021). Applying Artificial Intelligence (AI) Techniques to Implement a Practical Smart Cage Aquaculture Management System.",
            "Deploys AIoT cloud systems for automated fish growth monitoring, feeding efficiency optimization, and real-time operational decision support.",
            "Serves as a reference for centralized data dashboards and predictive analytics to optimize feeding and yield forecasting without requiring costly sensor hardware."
        ),
        (
            "Abdurrasyid, Indrianto, Susanti, and Purwanto (2021). Detection of Water Quality in Crayfish Ponds with IoT.",
            "Utilizes microcontroller-based sensor modules and cloud mobile apps for real-time monitoring and classification of crayfish pond water parameters.",
            "Supports the system's dedicated crayfish pond management module for logging temperature, pH, and water maintenance records manually entered by farm operators."
        ),
        (
            "Xu, Jin, Zeng, Zhang, and Xiao (2023). Development and Evaluation of an IoT-Based Portable Water Quality Monitoring System for Aquaculture.",
            "Implements portable wireless multi-parameter monitoring for small and medium aquaculture farms to detect water fluctuations.",
            "Provides foundational concepts for tracking pond water parameters and environmental logs in the centralized web platform."
        ),
        (
            "Chiu, Yan, Bhat, and Huang (2022). Development of Smart Aquaculture Farm Management System Using IoT and AI-Based Surrogate Models.",
            "Integrates machine learning models with farm management software to predict aquatic growth and reduce feed waste.",
            "Inspires the predictive growth and harvest yield analytics module designed for superworm and crayfish production cycles."
        ),
        (
            "Al Mamun, Ashik-E-Rabbani, Haque, and Upoma (2024). IoT-Based Real-Time Biofloc Monitoring and Controlling System.",
            "Features multi-parameter environmental telemetry and automated control alerts for specialized aquaculture systems.",
            "Supports the centralized dashboard architecture for recording, summarizing, and alerting farm managers on critical production thresholds."
        ),
        (
            "Garcia and Tibo (2023). A Solar-Powered Aquaponics with IoT-Based Monitoring and Data Gathering at the Technological University of the Philippines-Taguig.",
            "Combines solar power with web-based environmental telemetry to log water conditions and support urban small-scale aquaculture.",
            "Demonstrates the utility of accessible web interfaces for recording and visualizing aquaculture data in local Philippine farming settings."
        ),
        (
            "Tolentino, L. K. (2021). Development of an IoT-Based Intensive Aquaculture Monitoring System with Automatic Water Correction.",
            "Implements automated water-quality monitoring and corrective feedback mechanisms using microcontrollers and web databases.",
            "Informs the design of actionable management reports and threshold alerts to assist farm owners in maintaining optimal pond conditions."
        ),
        (
            "Dawa, Lausa, and Tibon (2022). Internet of Things (IoT)-Based Aquaponics Management System Adaptive to Climate Change.",
            "Features scheduled feeding management, remote environmental monitoring, cloud data storage, and automated report generation.",
            "Supports the development of structured feeding schedule management, production logs, and automated business analytics reports."
        ),
        (
            "Tina, Afsarimanesh, Nag, and Alahi (2025). Integrating AIoT Technologies in Aquaculture: A Systematic Review.",
            "Synthesizes intelligent aquaculture architectures, data workflows, smart feeding, and predictive modeling frameworks in the Philippines.",
            "Validates the value chain integration architecture, combining production monitoring with inventory, financial tracking, and demand analytics."
        ),
        (
            "Caluag et al. (2025) & Gulifardo et al. (2025). Internet of Things-Based Water Quality Monitoring System for Brackish Water Fishponds / iPond.",
            "Deploys web-connected monitoring to provide fishpond operators with timely environmental data and alerts.",
            "Extends beyond water monitoring by offering a comprehensive value chain platform that integrates production, harvesting, inventory, order fulfillment, and sales analytics."
        )
    ]

    t2 = doc.add_table(rows=len(table2_data), cols=3)
    t2.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_apa_table_borders(t2)

    for row_idx, row_data in enumerate(table2_data):
        row = t2.rows[row_idx]
        is_header = (row_idx == 0)
        is_last = (row_idx == len(table2_data) - 1)

        trPr = row._tr.get_or_add_trPr()
        trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")} w:val="1"/>'))
        trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")} w:val="0"/>'))

        for col_idx, text in enumerate(row_data):
            cell = row.cells[col_idx]
            cell.width = col_widths[col_idx]
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
    print(f"Successfully generated merged Final_Paper.docx with {len(references_sorted)} unified alphabetical references!")

if __name__ == '__main__':
    build_combined_ch1_and_2()
