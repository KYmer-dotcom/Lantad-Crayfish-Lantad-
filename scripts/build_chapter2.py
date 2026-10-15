import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

def set_cell_border(cell, **kwargs):
    """
    Set cell borders
    kwargs: top, bottom, left, right
    values: dict(sz=12, val='single', color='000000', space='0')
    """
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>\n'
        f'<w:top w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/>\n'
        f'<w:left w:val="none"/>\n'
        f'<w:bottom w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/>\n'
        f'<w:right w:val="none"/>\n'
        f'</w:tcBorders>'
    )
    tcPr.append(tcBorders)

def set_table_header_row(row, bg_hex="F2F2F2"):
    trPr = row._tr.get_or_add_trPr()
    trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))
    for cell in row.cells:
        tcPr = cell._tc.get_or_add_tcPr()
        tcPr.append(parse_xml(f'<w:shd {nsdecls("w")} w:fill="{bg_hex}"/>'))
        borders = parse_xml(
            f'<w:tcBorders {nsdecls("w")}>\n'
            f'<w:top w:val="single" w:sz="8" w:space="0" w:color="000000"/>\n'
            f'<w:left w:val="none"/>\n'
            f'<w:bottom w:val="single" w:sz="8" w:space="0" w:color="000000"/>\n'
            f'<w:right w:val="none"/>\n'
            f'</w:tcBorders>'
        )
        tcPr.append(borders)

def build_chapter_2():
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
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.line_spacing = None
        run = p.add_run(text)
        run.bold = True
        run.font.name = 'Arial'
        run.font.size = Pt(12)
        return p

    def p_study_title(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = None
        run = p.add_run(text)
        run.bold = True
        run.font.name = 'Arial'
        run.font.size = Pt(12)
        return p

    def p_body(text, indent=True):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        if indent:
            p.paragraph_format.first_line_indent = Inches(0.5)
        else:
            p.paragraph_format.first_line_indent = Inches(0.0)
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(10)
        p.paragraph_format.line_spacing = None
        run = p.add_run(text)
        run.font.name = 'Arial'
        run.font.size = Pt(12)
        return p

    def p_table_title(tbl_num, tbl_title):
        p1 = doc.add_paragraph()
        p1.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p1.paragraph_format.space_before = Pt(12)
        p1.paragraph_format.space_after = Pt(2)
        run1 = p1.add_run(tbl_num)
        run1.bold = True
        run1.font.name = 'Arial'
        run1.font.size = Pt(12)

        p2 = doc.add_paragraph()
        p2.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p2.paragraph_format.space_before = Pt(0)
        p2.paragraph_format.space_after = Pt(6)
        run2 = p2.add_run(tbl_title)
        run2.italic = True
        run2.font.name = 'Arial'
        run2.font.size = Pt(12)

    def p_reference_item(ref_text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.left_indent = Inches(0.5)
        p.paragraph_format.first_line_indent = Inches(-0.5)
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.line_spacing = None
        run = p.add_run(ref_text)
        run.font.name = 'Arial'
        run.font.size = Pt(12)
        return p

    # ==================== CHAPTER II ====================
    p_chapter_head("CHAPTER II")
    p_chapter_head("REVIEW OF RELATED LITERATURE AND SYSTEMS")

    p_body("This chapter contains the selected review of related literature, studies, and the interrelated system as proponents’ basis for making and developing the Aquaculture Value Chain Management System with Predictive Analytics.", indent=True)

    # 2.1 Foreign Related Literature
    p_heading_2("2.1 Foreign Related Literature")

    p_study_title("Bait composition, feeding frequency, stocking density, and water quality for the effective cultivation of large-sized redclaw crayfish seedlings")
    p_body("Cheng et al. (2025) investigated the effects of bait composition, feeding frequency, stocking density, and water quality management on the cultivation of redclaw crayfish (Cherax quadricarinatus) seedlings. The study found that juveniles fed with a combination of formulated feed, Spirulina powder, and Antarctic krill oil two to three times daily achieved better survival and growth than those given formulated feed alone. Lower stocking density also resulted in higher survival, while regular monitoring of water quality helped maintain suitable conditions for crayfish development. The authors concluded that proper feeding, appropriate stocking density, and water quality management are essential for improving crayfish seedling production. This study is relevant to the present research because it highlights the importance of monitoring production activities, feeding practices, and farm conditions, which can be supported through a centralized value chain management system.", indent=True)

    p_study_title("Deep Learning for Sustainable Aquaculture: Opportunities and Challenges")
    p_body("Wu et al. (2025) reviewed the application of deep learning technologies in aquaculture, focusing on fish detection, growth prediction, health monitoring, intelligent feeding, water quality forecasting, and behavior analysis. The study found that deep learning can improve aquaculture operations by automating monitoring, supporting feeding decisions, predicting environmental conditions, and identifying potential health problems. However, challenges such as limited datasets, real-time processing, and differences among farming environments remain. The authors emphasized the potential of advanced data-driven technologies to improve productivity, reduce resource waste, and promote sustainable aquaculture. This study is relevant to the present research because it supports the use of predictive analytics and digital technologies for monitoring farm operations and assisting management decision-making.", indent=True)

    p_study_title("Mapping the use of insects in animal feed: scientific and technological data of Tenebrio molitor, Hermetia illucens, and Zophobas morio")
    p_body("Oliveira et al. (2025) reviewed the scientific and technological development of Tenebrio molitor, Hermetia illucens, and Zophobas morio as alternative ingredients for animal feed. The study analyzed scientific publications and patent records to identify research trends and applications of these insect species. The findings showed that T. molitor and H. illucens have received greater scientific and technological attention, particularly in aquaculture and poultry production, while Z. morio remains comparatively underdeveloped despite its nutritional potential. The authors emphasized that insect-based feed can contribute to sustainable animal production, reduce dependence on conventional feed ingredients, and support circular economy practices. This study is relevant to the present research because it highlights the potential of Zophobas morio as an emerging resource and supports the need for improved production management and monitoring of superworm farming activities.", indent=True)

    p_study_title("Nutritional Potential of Edible Insects as Alternative Ingredients in Fish Feed: A Path to Modern Aquaculture")
    p_body("Ragozzino-Paulino, Cocato, and de Souza Sarkis (2025) reviewed the nutritional potential of edible insects as alternative ingredients in aquaculture feeds. The study found that insect meals are rich in protein, amino acids, lipids, minerals, and other nutrients that can support fish growth, feed efficiency, and immune function. The authors emphasized that insect-based feeds can reduce dependence on fishmeal and fish oil while promoting sustainable aquaculture. This study supports the present research by highlighting the increasing importance of insect production, particularly superworms, as a sustainable source of animal feed.", indent=True)

    p_study_title("The Superworm, Zophobas morio (Coleoptera:Tenebrionidae): A ‘Sleeping Giant’ in Nutrient Sources")
    p_body("Rumbos and Athanassiou (2021) reviewed the biological characteristics, nutritional composition, and potential applications of superworm (Zophobas morio) in animal feed, human food, and waste management. The study found that Z. morio contains high levels of protein, fat, minerals, amino acids, and chitin, making it a promising alternative nutrient source. The authors also highlighted its potential contribution to sustainable production and waste reduction but noted the need for further research on safety, mass production, and regulatory requirements. This study is relevant to the present research because it establishes the nutritional and economic potential of Z. morio and supports the importance of effective management of superworm production.", indent=True)

    # 2.2 Local Related Literature
    p_heading_2("2.2 Local Related Literature")

    p_study_title("A time series analysis of aquaculture milkfish production volume using the Box-Jenkins SARIMA Model: A case study from Davao Oriental, Philippines")
    p_body("Jimmy Jr and Gente (2024) investigated the use of the Box-Jenkins Seasonal Autoregressive Integrated Moving Average (SARIMA) model to forecast milkfish production in Davao Oriental, Philippines. Using production data from 1996 to 2023, the study analyzed historical trends and developed a seasonal forecasting model. The results identified SARIMA (2,0,2)(1,1,1)₄ as the most suitable model for predicting future milkfish production, although fluctuations and uncertainties remained due to possible environmental and climate-related factors. The authors concluded that time-series forecasting can assist farmers, planners, and local government units in anticipating production trends and improving aquaculture planning. This study is relevant to the present research because it demonstrates how historical production data and predictive analytics can be used to forecast future farm production and support data-driven decision-making. It also supports the proposed system's predictive analytics feature for forecasting production, expenses, and market demand.", indent=True)

    p_study_title("Assessment of Indigenous Feed Ingredients on Growth and Feed Utilization Efficiency in Juvenile Milkfish (Chanos chanos Forsskål, 1775)")
    p_body("Macusi et al. (2025) investigated the use of indigenous and locally available feed ingredients for juvenile milkfish (Chanos chanos) aquaculture in the Philippines. The study evaluated alternative feed materials such as copra meal, azolla, taro, blood meal, golden apple snail, cacao pod, banana stem, and soybean meal based on their effects on fish growth and feed utilization. The results showed that copra meal and azolla produced the highest final weights and favorable feed conversion performance, while all alternative diets performed comparably to the control diet. The authors concluded that locally available and agricultural waste-based ingredients can be used as alternative feed resources without negatively affecting milkfish growth. This study is relevant to the present research because it demonstrates the importance of utilizing locally available resources and managing feed-related data to improve production efficiency, reduce costs, and promote sustainable farming practices.", indent=True)

    p_study_title("A review of the impacts of laws and policies on the nexus of the fisheries sector and gender in the Philippines")
    p_body("Durano et al. (2025) reviewed Philippine fisheries laws and policies to examine their effects on gender equality and women's participation in the fisheries sector. The study found that women play important roles in fisheries production, processing, marketing, and resource management, but their contributions may be overlooked when policies do not adequately consider gender-related concerns. The authors emphasized the need for stronger implementation of gender-responsive policies, greater participation of women, and improved recognition of their roles in the fisheries sector. This study is relevant to the present research because it highlights the importance of inclusive management systems that recognize different stakeholders involved in agricultural and aquaculture value chains. It also supports the inclusion of organized records and management features that can improve the visibility, participation, and coordination of workers and other stakeholders within farm operations.", indent=True)

    p_study_title("Developing a self-sufficient Philippine milkfish industry through value chain analysis")
    p_body("Salayo et al. (2021) examined the Philippine milkfish (Chanos chanos) industry through value chain analysis, focusing on the production and supply of eggs, larvae, fry, and fingerlings needed for grow-out operations. The study found that the industry remains dependent on imported juveniles due to declining wild fry production and insufficient local hatchery capacity. The authors emphasized the need to strengthen local breeding, hatchery, nursery, and grow-out enterprises through public-private partnerships to achieve a more self-sufficient milkfish industry. This study is relevant to the present research because it highlights the importance of value chain coordination, production monitoring, resource planning, and supply management in aquaculture. It supports the development of a centralized management system that can help organize production, inventory, supply, and distribution information to improve farm operations and strengthen the aquaculture value chain.", indent=True)

    p_study_title("Environmental Impacts of Aquaculture in the Philippines")
    p_body("Tahiluddin et al. (2025) reviewed the environmental impacts of aquaculture in the Philippines, focusing on its effects on marine habitats, biodiversity, water quality, sediments, and pollution. The study found that although aquaculture contributes to food security, employment, and economic development, poorly managed operations may result in mangrove and seagrass degradation, water pollution, biodiversity loss, sediment disturbance, and waste-related environmental problems. The authors emphasized the importance of water quality monitoring, proper waste management, biosecurity, environmental regulations, and sustainable aquaculture practices. This study is relevant to the present research because it highlights the importance of monitoring and managing farm resources and environmental conditions. It supports the development of a centralized management system that can help organize production and operational records, improve resource management, and provide data that can assist farmers in making more sustainable decisions.", indent=True)

    # 2.3 Foreign System
    p_heading_2("2.3 Foreign System")

    p_study_title("Applying Artificial Intelligence (AI) Techniques to Implement a Practical Smart Cage Aquaculture Management System")
    p_body("Chang et al. (2021) developed an artificial intelligence and Internet of Things (AIoT)-based smart cage aquaculture management system to improve the monitoring and management of fish production. The system collected farm data through an Ocean Cloud platform and applied data analysis and artificial intelligence to monitor fish health, survival, growth, and feed residues. The results showed that the system could support more efficient feeding, reduce feed waste, improve survival and feed conversion, and assist farmers in making timely management decisions. The authors concluded that AIoT technologies can improve aquaculture efficiency and sustainability by reducing labor requirements and providing more accurate production information. This study is relevant to the present research because it demonstrates how digital technologies and data analytics can be applied to aquaculture management and supports the use of centralized data management and predictive analytics in monitoring farm operations and improving decision-making.", indent=True)

    p_study_title("Detection of water quality in crayfish ponds with IoT")
    p_body("Abdurrasyid et al. (2021) developed an Internet of Things (IoT)-based system for monitoring water quality in crayfish ponds. The system used sensors, Arduino, an ESP8266 module, cloud services, and a smartphone interface to monitor important water parameters such as temperature and pH. The results showed that the system achieved 98.06% accuracy in classifying pond water conditions as suitable or unsuitable. The authors concluded that IoT-based monitoring can reduce the need for manual water-quality checking and help farmers maintain suitable conditions for crayfish production. This study is relevant to the present research because it demonstrates how digital technologies can improve crayfish farm monitoring and provide timely information for management decisions.", indent=True)

    p_study_title("DEVELOPMENT AND EVALUATION OF AN IoT-BASED PORTABLE WATER QUALITY MONITORING SYSTEM FOR AQUACULTURE")
    p_body("Xu et al. (2023) developed and evaluated a portable Internet of Things (IoT)-based water quality monitoring system designed for small and medium-sized aquaculture farms. The system monitored important water-quality parameters, including temperature, dissolved oxygen, ammonia nitrogen, and pH, and transmitted the collected data wirelessly to a cloud platform for remote monitoring. The results showed that the system provided accurate and stable data transmission with minimal data loss across the monitored parameters. The authors concluded that the portable system can support both fixed and remote water-quality monitoring and help farmers detect environmental problems at an earlier stage. This study is relevant to the present research because it demonstrates the benefits of digital technologies in monitoring aquaculture conditions and improving farm management. However, unlike the proposed system, the present study does not include real-time IoT sensor integration and instead relies on manually entered farm data for monitoring and predictive analytics.", indent=True)

    p_study_title("Development of smart aquaculture farm management system using IoT and AI-based surrogate models")
    p_body("Chiu et al. (2022) developed a smart aquaculture farm management system that integrated Internet of Things (IoT) and artificial intelligence (AI) technologies to improve fishpond monitoring and feeding management. The system collected real-time environmental and operational data and used a deep learning model with Bayesian optimization to predict the growth of California bass. The optimized model achieved an R² value of 0.94 and a mean square error of 0.0015, indicating strong predictive performance. The study showed that AIoT-based systems can support remote monitoring, improve feeding decisions, reduce feed waste, and lessen labor requirements. This study is relevant to the present research because it demonstrates how predictive analytics and digital technologies can be applied to production management and decision-making. While the proposed system does not use real-time IoT monitoring or advanced deep learning, it similarly applies data analysis and forecasting to support more efficient superworm and crayfish farm operations.", indent=True)

    p_study_title("IoT-based real-time biofloc monitoring and controlling system")
    p_body("Al Mamun et al. (2024) developed an Internet of Things (IoT)-based real-time monitoring and control system for biofloc aquaculture. The system used multiple sensors and an ESP32 microcontroller to continuously monitor water temperature, dissolved oxygen, pH, total dissolved solids, turbidity, and water level. Data were transmitted to mobile and computer devices through the Blynk application, allowing users to monitor pond conditions remotely. The system could also automatically activate or deactivate equipment when water conditions exceeded predetermined ranges. The results demonstrated that the system maintained suitable water conditions and reduced the need for manual monitoring. The authors concluded that IoT-based monitoring and automated control can improve aquaculture productivity, water-quality management, and sustainability. This study is relevant to the present research because it demonstrates how digital technologies can improve aquaculture management through centralized data monitoring and timely decision-making. However, real-time sensor integration and automated equipment control are beyond the scope of the proposed system, which relies on manually entered data and predictive analytics.", indent=True)

    # 2.4 Local System
    p_heading_2("2.4 Local System")

    p_study_title("A Solar-Powered Aquaponics with IoT-Based Monitoring and Data Gathering at the Technological University of the Philippines-Taguig")
    p_body("Garcia and Tibo (2023) developed a solar-powered aquaponics system with Internet of Things (IoT)-based monitoring and data gathering at the Technological University of the Philippines–Taguig. The system was designed for lettuce and tilapia production and used sensors to monitor pH, total dissolved solids, room temperature, humidity, and water temperature. Solar panels provided the system's energy, while the IoT website allowed users to collect and view environmental and water-quality data. The results showed that the system could effectively monitor important production conditions and support the growth of lettuce and tilapia. The study emphasized the importance of regular environmental monitoring and the potential of renewable energy in sustainable food production. This study is relevant to the present research because it demonstrates how digital monitoring and data management can support agricultural and aquaculture operations. It also reinforces the potential of technology to improve resource management and decision-making in small-scale farming systems.", indent=True)

    p_study_title("Development of an IoT-based Intensive Aquaculture Monitoring System with Automatic Water Correction")
    p_body("Tolentino (2021) developed an Internet of Things (IoT)-based intensive aquaculture monitoring system with automatic water-quality correction. The system used sensors, Arduino, Raspberry Pi, LoRaWAN, a database, and a web application to monitor parameters such as temperature, pH, turbidity, salinity, oxidation-reduction potential, and dissolved oxygen. It also included automated devices that corrected water conditions when measurements exceeded desired levels. The results showed that fish in the IoT-controlled setup achieved better growth than those in the conventional setup, increasing from 24 g to 41 g compared with 24 g to 35 g. The study concluded that automated water-quality monitoring and correction can improve aquaculture conditions, reduce manual work, and increase production efficiency. This study is relevant to the present research because it demonstrates how centralized digital monitoring and data management can support aquaculture operations and improve decision-making. However, automatic sensor-based monitoring and water correction are outside the scope of the proposed system, which focuses on manually entered production data and predictive analytics.", indent=True)

    p_study_title("Internet of things (IoT) based aquaponics management system adaptive to climate change")
    p_body("Dawa, Lausa, and Tibon (2022) developed an Internet of Things (IoT)-based aquaponics management system designed to support climate-adaptive and sustainable food production. The system used sensors, Arduino, NodeMCU, cloud storage, a mobile application, and solar power to monitor and manage important water-quality parameters such as pH, temperature, and dissolved oxygen. It also provided features for scheduled feeding, water-release management, remote monitoring, report generation, and automated control. The results showed that the system effectively provided real-time monitoring and received a high average evaluation rating of 4.32, interpreted as “Strongly Agree,” indicating that users considered it reliable, efficient, applicable, portable, and economically feasible. The authors concluded that IoT-based aquaponics systems can reduce manual labor and improve resource and water-quality management. This study is relevant to the present research because it demonstrates how digital systems, centralized data management, and automated reporting can improve farming and aquaculture operations. It also supports the proposed system's goal of providing organized production records, analytics, and decision-support features for more efficient farm management.", indent=True)

    p_study_title("Integrating AIoT Technologies in Aquaculture: A Systematic Review")
    p_body("Tina et al. (2025) conducted a systematic review on the integration of Artificial Intelligence of Things (AIoT) technologies in aquaculture. The study examined the use of IoT sensors and artificial intelligence in areas such as water-quality monitoring, smart feeding, disease detection, fish behavior analysis, automated counting, and production management. The findings showed that AIoT can improve aquaculture operations through real-time monitoring, automated decision-making, feeding optimization, early disease detection, and improved resource management. However, challenges such as implementation costs, scalability, technical requirements, and model generalization remain. The authors concluded that AIoT has significant potential to make aquaculture more efficient and sustainable as these challenges are addressed. This study is relevant to the present research because it supports the use of digital technologies and predictive analytics in managing aquaculture operations. It also reinforces the importance of centralized data collection and analysis in improving production monitoring, resource allocation, and farm decision-making. Unlike the AIoT systems discussed in the study, the proposed system focuses on manually entered farm data and predictive analytics rather than real-time sensor integration.", indent=True)

    p_study_title("Internet of Things-Based Water Quality Monitoring System for Brackish Water Fishponds")
    p_body("Caluag et al. (2025) developed an IoT-based water-quality monitoring system for brackish-water fishponds to improve aquaculture monitoring and decision-making. The system uses sensors to collect and transmit water-quality data, providing fishpond operators with timely information and reducing reliance on manual monitoring. The study demonstrated that IoT technology can improve the efficiency of water-quality monitoring and help farmers respond to changing pond conditions. However, the system focuses mainly on water-quality monitoring and does not cover the entire aquaculture value chain or predictive analytics. Thus, it provides a foundation for the proposed Aquaculture Value Chain Management System with Predictive Analytics, which can integrate real-time monitoring with production, inventory, harvesting, pricing, sales, distribution, and demand forecasting.", indent=True)

    # 2.5 Synthesis
    p_heading_2("2.5 Synthesis")
    p_body("The reviewed literature and systems provide the basis for the development of the Aquaculture Value Chain Management System with Predictive Analytics. The synthesis is presented in two tables: the Synthesis of Related Literature and the Synthesis of Related Systems.", indent=True)

    # Table 1: Synthesis of Related Literature
    p_table_title("Table 1", "Synthesis of Related Literature")

    table1_data = [
        ("Related Literature", "Features and Functionalities", "Developed System"),
        (
            "Bait Composition, Feeding Frequency, Stocking Density, and Water Quality for the Effective Cultivation of Large-Sized Redclaw Crayfish Seedlings",
            "• Bait composition\n• Feeding frequency\n• Stocking density\n• Water-quality monitoring",
            "Aquaculture management system with production, stocking, and pond-monitoring functions"
        ),
        (
            "Deep Learning for Sustainable Aquaculture: Opportunities and Challenges",
            "• Fish detection and counting\n• Growth prediction\n• Health monitoring\n• Intelligent feeding\n• Water-quality forecasting",
            "Predictive analytics and decision-support tools for aquaculture management"
        ),
        (
            "Fishery Wastes as Feed Additive for the Red Claw Crayfish Cherax quadricarinatus",
            "• Fishery-waste feed additives\n• Growth evaluation\n• Digestive-activity monitoring",
            "Alternative-feed management and production-monitoring functions"
        ),
        (
            "Mapping the Use of Insects in Animal Feed",
            "• Insect-based feed resources\n• Feed source documentation",
            "Alternative-feed recording and management system"
        ),
        (
            "Nutritional Potential of Edible Insects as Alternative Ingredients in Fish Feed",
            "• Alternative feed ingredients\n• Nutritional assessment",
            "Alternative-feed selection and management tools"
        ),
        (
            "Optimal Feeding Levels to Enhance Growth Performance and Gut Microbiota Balance in Red Swamp Crayfish",
            "• Feeding-level optimization\n• Growth-performance monitoring\n• Gut microbiota analysis",
            "Feed monitoring and production-performance tracking"
        ),
        (
            "Preliminary Evaluation of Superworm (Zophobas morio) Larval Meal",
            "• Superworm meal utilization\n• Protein-source evaluation",
            "Alternative-feed inventory and production monitoring"
        ),
        (
            "Protein Hydrolysates Derived from Superworm (Zophobas morio)",
            "• Protein composition analysis\n• Bioactivity assessment\n• Functional properties evaluation",
            "Evaluation and management of alternative-feed materials"
        ),
        (
            "The Superworm, Zophobas morio: A ‘Sleeping Giant’ in Nutrient Sources",
            "• Nutritional composition analysis\n• Feed potential assessment",
            "Alternative-feed management support"
        ),
        (
            "The Effects of Dietary Fishmeal Substitution by Zophobas morio Larvae Meals",
            "• Fishmeal substitution strategies\n• Alternative-feed evaluation",
            "Recording and comparison of alternative-feed utilization"
        ),
        (
            "A Time Series Analysis of Aquaculture Milkfish Production Volume Using the Box-Jenkins SARIMA Model",
            "• Time-series analysis\n• Production forecasting",
            "Predictive analytics and production-forecasting module"
        ),
        (
            "Assessment of Indigenous Feed Ingredients on Growth and Feed Utilization Efficiency in Juvenile Milkfish",
            "• Indigenous feed ingredients\n• Growth monitoring\n• Feed-utilization efficiency",
            "Feed management and production-efficiency monitoring"
        ),
        (
            "A Review of the Impacts of Laws and Policies on the Fisheries Sector and Gender in the Philippines",
            "• Fisheries regulations\n• Policy impact assessment\n• Gender considerations",
            "Policy-informed aquaculture management framework"
        ),
        (
            "Developing a Self-Sufficient Philippine Milkfish Industry Through Value Chain Analysis",
            "• Value-chain analysis\n• Industry self-sufficiency strategies",
            "Integrated production, sales, and value-chain management"
        ),
        (
            "Development of Smart Food Value Chain Intervention Models for the Milkfish Industry",
            "• Smart value-chain interventions\n• Data-driven management approaches",
            "Value-chain integration and analytics system"
        ),
        (
            "Environmental Impacts of Aquaculture in the Philippines",
            "• Environmental impact assessment\n• Sustainability monitoring",
            "Sustainability-oriented aquaculture management tools"
        ),
        (
            "Environmental and Socioeconomic Impacts of Shrimp Farming in the Philippines",
            "• Environmental analysis\n• Socioeconomic assessment",
            "Environmental and socioeconomic monitoring support"
        ),
        (
            "Gut Microbiome Composition and Diversity of Wild-Caught and Hatchery-Bred Milkfish Fry",
            "• Gut microbiome analysis\n• Biological-performance monitoring",
            "Biological health and performance monitoring"
        ),
        (
            "Supply Response of Seaweeds in the Philippines: An Autoregressive Distributed Lag Model",
            "• Supply-response analysis\n• Forecasting models",
            "Data analysis and supply-management forecasting"
        ),
        (
            "Vulnerability Drivers for Small Pelagics and Milkfish Aquaculture Value Chain",
            "• Vulnerability assessment\n• Risk identification\n• Value-chain analysis",
            "Risk-aware value-chain monitoring and management system"
        )
    ]

    t1 = doc.add_table(rows=len(table1_data), cols=3)
    t1.alignment = WD_TABLE_ALIGNMENT.CENTER
    col_widths1 = [Inches(2.3), Inches(2.0), Inches(2.2)]

    for row_idx, row_data in enumerate(table1_data):
        row = t1.rows[row_idx]
        for col_idx, text in enumerate(row_data):
            cell = row.cells[col_idx]
            cell.width = col_widths1[col_idx]
            cell.vertical_alignment = WD_ALIGN_VERTICAL.TOP
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(3)
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.line_spacing = None
            run = p.add_run(text)
            run.font.name = 'Arial'
            run.font.size = Pt(10) if row_idx > 0 else Pt(11)
            if row_idx == 0:
                run.bold = True
            set_cell_border(cell)
    set_table_header_row(t1.rows[0])

    p_body("Table 1 presents the synthesis of the related literature reviewed in this study. The literature emphasizes production management, alternative feeds, forecasting, value-chain analysis, environmental considerations, and data-driven decision-making. These findings provide a basis for the proposed system's production, inventory, sales, expense, and predictive-analytics functions.", indent=True)

    # Table 2: Synthesis of Related Systems
    p_table_title("Table 2", "Synthesis of Related Systems")

    table2_data = [
        ("Related Systems", "Features and Functionalities", "Developed System"),
        (
            "Detection of Water Quality in Crayfish Ponds with IoT",
            "• IoT-based water-quality detection\n• Water-quality monitoring",
            "Real-time pond and water-quality monitoring system"
        ),
        (
            "Development and Evaluation of an IoT-Based Portable Water Quality Monitoring System for Aquaculture",
            "• Portable IoT monitoring\n• Water-quality data collection",
            "Accessible water-quality monitoring and data management"
        ),
        (
            "Development of Smart Aquaculture Farm Management System Using IoT and AI-Based Surrogate Models",
            "• IoT-based monitoring\n• AI surrogate models\n• Predictive analytics",
            "Integrated monitoring and predictive analytics for aquaculture operations"
        ),
        (
            "IoT-Based Real-Time Biofloc Monitoring and Controlling System",
            "• Real-time biofloc monitoring\n• Automated control mechanisms",
            "Real-time monitoring and environmental control functions"
        ),
        (
            "A Solar-Powered Aquaponics with IoT-Based Monitoring and Data Gathering at the Technological University of the Philippines–Taguig",
            "• Solar-powered aquaponics\n• IoT monitoring\n• Data gathering",
            "Cost-effective monitoring and local aquaculture data collection"
        ),
        (
            "Development of an IoT-Based Intensive Aquaculture Monitoring System with Automatic Water Correction",
            "• IoT monitoring\n• Automatic water correction",
            "Water-quality monitoring with corrective-action support"
        ),
        (
            "Internet of Things (IoT)-Based Aquaponics Management System Adaptive to Climate Change",
            "• Climate-adaptive aquaponics management\n• IoT monitoring",
            "Sustainable and adaptive aquaculture management system"
        ),
        (
            "Integrating AIoT Technologies in Aquaculture: A Systematic Review",
            "• AI and IoT integration\n• Smart aquaculture technologies",
            "Combined IoT monitoring and AI-driven predictive functions"
        ),
        (
            "An IoT-Enabled Intelligent Monitoring System for Sustainable Aquaculture / iPond: An Internet of Things–Based Water Quality Monitoring System for Fishpond",
            "• IoT-enabled intelligent monitoring\n• Water-quality monitoring\n• Sustainability support",
            "Real-time monitoring system focused on sustainability and water-quality management"
        )
    ]

    t2 = doc.add_table(rows=len(table2_data), cols=3)
    t2.alignment = WD_TABLE_ALIGNMENT.CENTER
    col_widths2 = [Inches(2.3), Inches(2.0), Inches(2.2)]

    for row_idx, row_data in enumerate(table2_data):
        row = t2.rows[row_idx]
        for col_idx, text in enumerate(row_data):
            cell = row.cells[col_idx]
            cell.width = col_widths2[col_idx]
            cell.vertical_alignment = WD_ALIGN_VERTICAL.TOP
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(3)
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.line_spacing = None
            run = p.add_run(text)
            run.font.name = 'Arial'
            run.font.size = Pt(10) if row_idx > 0 else Pt(11)
            if row_idx == 0:
                run.bold = True
            set_cell_border(cell)
    set_table_header_row(t2.rows[0])

    p_body("Table 2 presents the synthesis of the related systems reviewed in this study. The systems demonstrate the use of IoT, AI, sensors, monitoring, automated water correction, and data gathering to improve aquaculture operations. These features support the proposed system's goal of integrating operational management with predictive analytics and efficient aquaculture monitoring.", indent=True)

    # ==================== REFERENCES (STRICTLY ALPHABETICAL) ====================
    doc.add_page_break()
    p_chapter_head("REFERENCES")

    references = [
        "Abdurrasyid, A., Indrianto, I., Susanti, M. N. I., & Purwanto, Y. S. (2021). Detection of water quality in crayfish ponds with IoT. Bulletin of Electrical Engineering and Informatics, 10(2), 886–897.",
        "Al Mamun, M. R., Ashik-E-Rabbani, M., Haque, M. M., & Upoma, S. M. (2024). IoT-based real-time biofloc monitoring and controlling system. Smart Agricultural Technology, 9, 100598.",
        "Asimaki, A., Psofakis, P., Gkalogianni, E. Z., Katouni, A. M., Berillis, P., Kormas, K. A., ... & Karapanagiotidis, I. T. (2025). The Effects of Dietary Fishmeal Substitution by Full‐Fat and Defatted Zophobas morio Larvae Meals on Juvenile Gilthead Seabream (Sparus aurata): An Integrative Approach. Aquaculture Nutrition, 2025(1), 8885509.",
        "Bouzidi, D., Mohamed, M. B., Ibraheem, M. K., Al-Abadi, A. A. J., & Fakhfakh, A. (2025). An IoT-Enabled Intelligent Monitoring System for Sustainable Aquaculture.",
        "Caluag, J., et al. (2025). Internet of Things-Based Water Quality Monitoring System for Brackish Water Fishponds.",
        "Chang, C. C., Wang, J. H., Wu, J. L., Hsieh, Y. Z., Wu, T. D., Cheng, S. C., ... & Lin, C. Y. (2021). Applying artificial intelligence (AI) techniques to implement a practical smart cage aquaculture management system. Journal of Medical and Biological Engineering, 41(5), 652–658.",
        "Cheng, S., Han, Y. L., Chi, M. L., Zheng, J. B., Liu, S. L., Zhu, C., ... & Jiang, W. P. (2025). Bait composition, feeding frequency, stocking density, and water quality for the effective cultivation of large-sized redclaw crayfish seedlings.",
        "Chiu, M. C., Yan, W. M., Bhat, S. A., & Huang, N. F. (2022). Development of a smart aquaculture farm management system using IoT and AI-based surrogate models. Journal of Agriculture and Food Research, 9, 100357.",
        "Dawa, M., Lausa, S. M., & Tibon, M. R. (2022). Internet of things (IoT) based aquaponics management system adaptive to climate change. AIP Conference Proceedings, 2502(1), 050004.",
        "de Sousa Araujo, A. C., Pereira, A. C., Gomes, R. M. M., Ramirez, J. R. B., da Silva Noda, K., Santos, L. G., ... & Martins, V. G. (2025). Protein hydrolysates derived from superworm (Zophobas morio): Composition, bioactivity, and techno-functional properties. International Journal of Biological Macromolecules, 295, 139668.",
        "Durano, F. L. A., Romo, G. D. A., Sarmiento, J. M. P., Lopez, R. A., Hollite, J. B. D., & Padios, P. A. B. (2025). A review of the impacts of laws and policies on the nexus of the fisheries sector and gender in the Philippines. Marine Policy, 180, 106810.",
        "Garcia, C., & Tibo, H. (2023). A solar-powered aquaponics with IoT-based monitoring and data gathering at the Technological University of the Philippines-Taguig.",
        "Gulifardo, A. B. E., Balane, B. J. D., Ebora, M. T., Serrano, M. R., Ellazar, E. P., Nicolas, A. V., & Maaño, R. C. (2025). iPond: An Internet of Things–Based Water Quality Monitoring System for Fishpond. IOP Conference Series: Earth and Environmental Science, 1446(1), 012005.",
        "Jimmy Jr, C. L., & Gente, J. M. D. (2024). A time series analysis of aquaculture milkfish production volume using the Box-Jenkins SARIMA Model: A case study from Davao Oriental, Philippines. Davao Research Journal, 15(3), 6–19.",
        "Macusi, E. D., Estor, D. E. P., Borazon, E. Q., Clapano, M. B., & Santos, M. D. (2022). Environmental and socioeconomic impacts of shrimp farming in the Philippines: A critical analysis using PRISMA. Sustainability, 14(5), 2977.",
        "Macusi, E. D., Geronimo, R. C., & Santos, M. D. (2021). Vulnerability drivers for small pelagics and milkfish aquaculture value chain determined through online participatory approach. Marine Policy, 133, 104710.",
        "Macusi, E. D., Sales, A. C., Jimenez, J. E. M., Vender, E. K. E., Bongas, H. P., Macusi, E. S., & Andam, M. B. (2025). Assessment of Indigenous Feed Ingredients on Growth and Feed Utilization Efficiency in Juvenile Milkfish (Chanos chanos Forsskål, 1775). Israeli Journal of Aquaculture-Bamidgeh, 77(2), 231–244.",
        "Martínez, E. G., Stumpf, L., Planas, M., Gimenez, A. F., & Greco, L. L. (2024). Fishery wastes as feed additive for the red claw crayfish Cherax quadricarinatus: Impact on growth, biochemical composition, and digestive activity. Animal Feed Science and Technology, 318, 116116.",
        "Oliveira, J. S., Ribeiro, C. D. F., Souza, C. O. D., & Ribeiro, C. V. D. M. (2025). Mapping the use of insects in animal feed: scientific and technological data of Tenebrio molitor, Hermetia illucens, and Zophobas morio. Animal Production Science, 65(9), AN24415.",
        "Paz, K. S. D. (2019). Supply Response of Seaweeds in Philippines: An Autoregressive Distributive Lag Model.",
        "Prachom, N., Boonyoung, S., Hassaan, M. S., El‐Haroun, E., & Davies, S. J. (2021). Preliminary evaluation of Superworm (Zophobas morio) larval meal as a partial protein source in experimental diets for juvenile Asian sea bass, Lates calcarifer. Aquaculture Nutrition, 27(5), 1304–1314.",
        "Ragozzino-Paulino, P., Cocato, M. L., & de Souza Sarkis, J. E. (2025). Nutritional Potential of Edible Insects as Alternative Ingredients in Fish Feed: A Path to Modern Aquaculture. Aquaculture Nutrition, 2025(1), 7009004.",
        "Rumbos, C. I., & Athanassiou, C. G. (2021). The superworm, Zophobas morio (Coleoptera: Tenebrionidae): A ‘sleeping giant’ in nutrient sources. Journal of Insects as Food and Feed, 7(5), 785–802.",
        "Salayo, N. D., Marte, C. L., Toledo, J. D., Gaitan, A. G., & Agbayani, R. F. (2021). Developing a self-sufficient Philippine milkfish industry through value chain analysis. Ocean & Coastal Management, 201, 105426.",
        "Silvederio, G. X. L., Javellana, T. F., Genciana, A. B. N., Fontanilla, M. A. G., Traifalgar, R. F. M., Huervana, F. H., & Del Castillo, C. S. (2025). Gut microbiome composition and diversity of wild-caught and hatchery-bred milkfish (Chanos chanos) fry. Journal of Genetic Engineering and Biotechnology, 23(3), 100520.",
        "Tahiluddin, A. B., Bornales, J. C., Limbaro, G. R. A., Paudac, M. A. T. U., Amarille, R. K., Sirad, N. R., ... & Esguerra, J. P. (2025). Environmental impacts of aquaculture in the Philippines.",
        "Tina, F. W., Afsarimanesh, N., Nag, A., & Alahi, M. E. E. (2025). Integrating AIoT technologies in aquaculture: A systematic review. Future Internet, 17(5), 199.",
        "Tolentino, L. K. (2021). Development of an IoT-based intensive aquaculture monitoring system with automatic water correction. International Journal of Computing and Digital Systems.",
        "Wu, A. Q., Li, K. L., Song, Z. Y., Lou, X., Hu, P., Yang, W., & Wang, R. F. (2025). Deep learning for sustainable aquaculture: Opportunities and challenges. Sustainability, 17(11), 5084.",
        "Xu, Y., Jin, J. D., Zeng, S. W., Zhang, Y., & Xiao, Q. L. (2023). Development and evaluation of an IoT-based portable water quality monitoring system for aquaculture.",
        "Yang, X., Tang, Z., Huang, K., Guo, R., Wang, D., Jiang, S., & Yu, K. (2025). Optimal feeding levels to enhance growth performance and gut microbiota balance in red swamp crayfish (Procambarus clarkii). Aquaculture Reports, 41, 102717.",
        "Zapata Jr, N. R., Sarmiento, J. A. C., & Cruz, M. B. (2023). Development of smart food value chain intervention models for the milkfish industry in Region 1, Philippines. Asian Journal of Agriculture and Development, 20(1), 87–108."
    ]

    # Sort strictly alphabetically (A-Z)
    references_sorted = sorted(references, key=lambda s: s.lower())

    for ref in references_sorted:
        p_reference_item(ref)

    output_path = r'c:\Users\kymer\Desktop\Lantad ACarwfish Django\Documents\Final_Paper\Chapter_2.docx'
    doc.save(output_path)
    print(f"Successfully generated Chapter_2.docx with {len(references_sorted)} sorted references!")

if __name__ == '__main__':
    build_chapter_2()
