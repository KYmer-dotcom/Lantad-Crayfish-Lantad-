import os

def build_all_md():
    with open('Documents/Final_Paper/Chapter_1.md', 'r', encoding='utf-8') as f:
        ch1 = f.read().split('# REFERENCES')[0].split('## REFERENCES')[0].strip()

    with open('Documents/Final_Paper/Chapter_2.md', 'r', encoding='utf-8') as f:
        ch2 = f.read().split('# REFERENCES')[0].split('## REFERENCES')[0].strip()

    ch3 = """# CHAPTER III
# METHODOLOGY

This chapter presents the methods and tools used to develop the system, including the software development life cycle, the operational framework, the system design, the technologies used, the respondents, and the research instruments.

<br>

## 3.1 Systems Development Life Cycle

The system development life cycle is crucial in creating effective and efficient systems. In this study, the proponents adopted the Scrum-based development model to accommodate iterative progress and continuous feedback throughout the project.

To satisfy academic milestones while maintaining Agile flexibility, the methodology incorporates a linear release pipeline wrapping an active, multi-sprint development loop. This hybrid structure establishes clear pre-conditions for development and provides a structured mechanism for deployment and post-implementation evaluation.

<br>

**Figure 1**  
*Adapted Scrum-Based Development Model*

![Figure 1: Adapted Scrum-Based Development Model](ch3_extracted_images/img_1_image10.jpg)

Figure 1 shows the adapted Scrum-based development model used in the study. The model is structured as an Agile release pipeline containing three main components: (1) Pre-Sprint: Planning & Design (Phases 1 & 2), which represents requirements gathering and schema modeling; (2) The Active 14-Day Sprint Loop: Development & Testing (Phases 3 & 4), where coding and quality assurance are executed iteratively; and (3) Post-Sprint: Deploy, Review, & Launch (Phases 5, 6, & 7), representing production deployment, empirical ISO evaluation, and project handover. Each active sprint included Scrum practices such as Sprint Planning, Daily Scrum, Sprint Review, and Sprint Retrospective to allow continuous feedback, improvement, and refinement of the system throughout the development process.

<br>

### Phase 1: Planning Phase
This phase lasted 14 days and corresponds to the initialization of the Product Backlog (Sprint Zero). The research team coordinated with the farm owner and stakeholders of Silay Superworm & Crayfish to gather and document system requirements. A Sprint Planning session defined the scope of deliverables, identified user roles (Farm Owner, Delivery Riders, and Customers), and mapped production and fulfillment protocols. Core modules identified included Production Tracking, Pond and Batch Monitoring, Sales and Inventory Management, Expense Recording, Predictive Analytics, Order Management, and Delivery Tracking, which were prioritized in a Product Backlog to guide subsequent sprints.

<br>

### Phase 2: Design Phase
This phase took 17 days and focused on preparing architectural design assets and sprint-level guidelines. A Sprint Planning session initiated task allocation and established coding standards. Technical outputs included Entity-Relationship Diagrams (ERD), a compiled Data Dictionary, UML Use Case Diagrams, Use Case Scenarios, and Data Flow Diagrams (DFDs) drawn in Gane and Sarson notation. Interface wireframes, along with the system's Operational Framework and Context Diagram, were also finalized.

<br>

### Phase 3: Development Phase
This phase spanned 84 days and served as the primary core construction period, executed across six active 14-day sprints (Sprints 1 to 6). Each sprint began with a Sprint Planning session to construct a Sprint Backlog and ended with a Sprint Review and Retrospective. System features were built incrementally: Sprints 1 and 2 focused on the User Authentication, Role-Based Access Control, and Product Catalog modules; Sprints 3 and 4 delivered the Production Management, Pond Monitoring, and Inventory Tracking modules; and Sprints 5 and 6 delivered the Order Fulfillment, Rider Dispatching, Expense Logging, and Predictive Analytics Dashboard modules.

<br>

### Phase 4: Testing Phase
This phase spanned 98 days and was executed as seven active QA and verification sprints (Sprints 7 to 13) to ensure comprehensive system validation. Sprints 7 and 8 focused on automated white-box and black-box testing of API compliance and form gates. Sprints 9 and 10 were dedicated to security testing, validating role-based boundaries, authentication exceptions, and transaction audit trails. Sprints 11 and 12 involved internal Alpha testing and Beta testing with end-users under operational conditions. Sprint 13 focused on performance optimization and query tuning. All evaluations aligned with the ISO/IEC 25010:2011 Software Quality Model.

<br>

### Phase 5: Deployment Phase
This phase took 21 days and was executed as a production release sprint. The server environment was provisioned and configured for web deployment. The database was deployed, and Django database migrations were executed to establish active database schemas. Initial farm production records, product classifications, user accounts, and role-based permissions were applied and verified.

<br>

### Phase 6: Review Phase
This phase required 21 days to collect and evaluate user feedback under a formal stakeholder review sprint. Structured evaluation instruments based on the ISO/IEC 25010:2011 standard were administered to end-users, IT experts, and farm stakeholders. A Sprint Review session was held to present the evaluation results, and the collected survey data were statistically analyzed to confirm that the developed system satisfies the functional and quality requirements established in the study.

<br>

### Phase 7: Launch Phase
This phase lasted 14 days and served as the final project closeout and handover sprint. The system was officially released to Silay Superworm & Crayfish. Activities included user orientation sessions, administrator training, and system monitoring during initial operations. Technical documentation, user manuals, and database schemas were handed over to support continued maintenance. A final Sprint Retrospective was conducted to document lessons learned and complete project turnover.

<br>

## 3.2 Operational Framework

**Figure 2**  
*Operational Framework of the Aquaculture Value Chain Management System with Predictive Analytics*

![Figure 2: Operational Framework](ch3_extracted_images/img_2_image6.png)

Figure 2 presents the operational framework of the proposed system, illustrating how the Farm Owner, Delivery Riders, and Customers interact through a centralized web-based infrastructure. The server infrastructure serves as the central middleware, managing all data transactions with the database while coordinating real-time production monitoring, order tracking, inventory balances, expense summaries, and predictive analytics forecasting.

<br>

## 3.3 Data Flow Diagram

**Figure 3**  
*Context Diagram (Level 0) of the Aquaculture Value Chain Management System with Predictive Analytics*

![Figure 3: Context Diagram (Level 0)](ch3_extracted_images/img_0_image24.png)

Figure 3 presents the Context Diagram (Level 0) of the Aquaculture Value Chain Management System with Predictive Analytics, detailing data exchanges among external entities. The Farm Owner inputs system configurations, user credentials, production logs, harvest records, product categories, inventory updates, and expense entries; in return, the system generates analytics dashboards, yield forecasts, demand predictions, financial reports, and transaction logs. The Delivery Rider accesses assigned dispatch orders and submits proof of delivery and fulfillment statuses. The Customer inputs product orders, reservation details, delivery locations, and payment confirmations, receiving order confirmations, real-time tracking updates, and sales receipts.

<br>

**Figure 4**  
*Level 1 Data Flow Diagram of Aquaculture Value Chain Management System with Predictive Analytics*

![Figure 4: Level 1 Data Flow Diagram](ch3_extracted_images/level_1_dfd_exact.png)

Figure 4 illustrates the Level 1 Data Flow Diagram of the Aquaculture Value Chain Management System with Predictive Analytics, detailing data flows across three external entities (Customer, Rider, and Manager), seven core processes, and six data stores. In Process 1.0 (Browse and Select), customers browse the product list and select items against available stock retrieved from D3 Production and order information from D1 Order and D2 Customer. In Process 2.0 (Order Management), customer order requests and manager order approvals are processed to generate order confirmations, committing order records into D1 Order and updating D2 Customer. In Process 3.0 (Payment & Set Location), delivery/pickup addresses, payment details, and rider-collected COD cash are validated against D5 Payment, D6 Delivery, and D1 Order. In Process 4.0 (Delivery Dispatch), delivery assignments, route maps, and customer contacts are dispatched to riders, while real-time tracking and delivery completions are routed to customers, updating D1 Order, D3 Production (stock deduction), and D6 Delivery (dispatch records). In Process 5.0 (Management), manager-approved expense entries and stock replenishment updates are processed alongside delivery, payment, production, and expense records from D3, D4, D5, and D6. In Process 6.0 (Report and Monitoring), manager report requests are fulfilled with comprehensive sales, inventory, and expense summaries derived from D3 Production and D6 Delivery. Finally, in Process 7.0 (Predictive Analytics), summarized operational data are transformed into actionable forecast and customer clustering reports delivered directly to the manager for strategic planning."""

    # Consolidated references
    all_refs = [
        "Abdurrasyid, A., Indrianto, I., Susanti, M. N. I., & Purwanto, Y. S. (2021). Detection of water quality in crayfish ponds with IoT. *Bulletin of Electrical Engineering and Informatics*, 10(2), 886–897.",
        "Al Mamun, M. R., Ashik-E-Rabbani, M., Haque, M. M., & Upoma, S. M. (2024). IoT-based real-time biofloc monitoring and controlling system. *Smart Agricultural Technology*, 9, 100598.",
        "Asimaki, A., Psofakis, P., Gkalogianni, E. Z., Katouni, A. M., Berillis, P., Kormas, K. A., ... & Karapanagiotidis, I. T. (2025). The Effects of Dietary Fishmeal Substitution by Full‐Fat and Defatted Zophobas morio Larvae Meals on Juvenile Gilthead Seabream (Sparus aurata): An Integrative Approach. *Aquaculture Nutrition*, 2025(1), 8885509.",
        "Bouzidi, D., Mohamed, M. B., Ibraheem, M. K., Al-Abadi, A. A. J., & Fakhfakh, A. (2025). An IoT-Enabled Intelligent Monitoring System for Sustainable Aquaculture.",
        "Bush, S. R., Belton, B., Little, D. C., & Islam, M. S. (2019). The emerging aquaculture value chain: Spatial and social transformations in seafood production. *Global Food Security*, 21, 63–71.",
        "Caluag, J., et al. (2025). Internet of Things-Based Water Quality Monitoring System for Brackish Water Fishponds.",
        "Chang, C. C., Wang, J. H., Wu, J. L., Hsieh, Y. Z., Wu, T. D., Cheng, S. C., ... & Lin, C. Y. (2021). Applying artificial intelligence (AI) techniques to implement a practical smart cage aquaculture management system. *Journal of Medical and Biological Engineering*, 41(5), 652–658.",
        "Cheng, S., Han, Y. L., Chi, M. L., Zheng, J. B., Liu, S. L., Zhu, C., ... & Jiang, W. P. (2025). Bait composition, feeding frequency, stocking density, and water quality for the effective cultivation of large-sized redclaw crayfish seedlings.",
        "Chiu, M. C., Yan, W. M., Bhat, S. A., & Huang, N. F. (2022). Development of a smart aquaculture farm management system using IoT and AI-based surrogate models. *Journal of Agriculture and Food Research*, 9, 100357.",
        "Dawa, M., Lausa, S. M., & Tibon, M. R. (2022). Internet of things (IoT) based aquaponics management system adaptive to climate change. *AIP Conference Proceedings*, 2502(1), 050004.",
        "de Sousa Araujo, A. C., Pereira, A. C., Gomes, R. M. M., Ramirez, J. R. B., da Silva Noda, K., Santos, L. G., ... & Martins, V. G. (2025). Protein hydrolysates derived from superworm (Zophobas morio): Composition, bioactivity, and techno-functional properties. *International Journal of Biological Macromolecules*, 295, 139668.",
        "Durano, F. L. A., Romo, G. D. A., Sarmiento, J. M. P., Lopez, R. A., Hollite, J. B. D., & Padios, P. A. B. (2025). A review of the impacts of laws and policies on the nexus of the fisheries sector and gender in the Philippines. *Marine Policy*, 180, 106810.",
        "Food and Agriculture Organization. (2022). *The State of World Fisheries and Aquaculture 2022: Towards Blue Transformation*. FAO.",
        "Garcia, C., & Tibo, H. (2023). A solar-powered aquaponics with IoT-based monitoring and data gathering at the Technological University of the Philippines-Taguig.",
        "Gulifardo, A. B. E., Balane, B. J. D., Ebora, M. T., Serrano, M. R., Ellazar, E. P., Nicolas, A. V., & Maaño, R. C. (2025). iPond: An Internet of Things–Based Water Quality Monitoring System for Fishpond. *IOP Conference Series: Earth and Environmental Science*, 1446(1), 012005.",
        "Hu, Y., Zhang, L., Wang, Q., & Chen, J. (2025). Predictive models and time-series forecasting in aquaculture production management: A review. *Aquacultural Engineering*, 108, 102430.",
        "Jimmy Jr, C. L., & Gente, J. M. D. (2024). A time series analysis of aquaculture milkfish production volume using the Box-Jenkins SARIMA Model: A case study from Davao Oriental, Philippines. *Davao Research Journal*, 15(3), 6–19.",
        "Macusi, E. D., Estor, D. E. P., Borazon, E. Q., Clapano, M. B., & Santos, M. D. (2022). Environmental and socioeconomic impacts of shrimp farming in the Philippines: A critical analysis using PRISMA. *Sustainability*, 14(5), 2977.",
        "Macusi, E. D., Geronimo, R. C., & Santos, M. D. (2021). Vulnerability drivers for small pelagics and milkfish aquaculture value chain determined through online participatory approach. *Marine Policy*, 133, 104710.",
        "Macusi, E. D., Sales, A. C., Jimenez, J. E. M., Vender, E. K. E., Bongas, H. P., Macusi, E. S., & Andam, M. B. (2025). Assessment of Indigenous Feed Ingredients on Growth and Feed Utilization Efficiency in Juvenile Milkfish (Chanos chanos Forsskål, 1775). *Israeli Journal of Aquaculture-Bamidgeh*, 77(2), 231–244.",
        "Martínez, E. G., Stumpf, L., Planas, M., Gimenez, A. F., & Greco, L. L. (2024). Fishery wastes as feed additive for the red claw crayfish Cherax quadricarinatus: Impact on growth, biochemical composition, and digestive activity. *Animal Feed Science and Technology*, 318, 116116.",
        "Oliveira, J. S., Ribeiro, C. D. F., Souza, C. O. D., & Ribeiro, C. V. D. M. (2025). Mapping the use of insects in animal feed: scientific and technological data of Tenebrio molitor, Hermetia illucens, and Zophobas morio. *Animal Production Science*, 65(9), AN24415.",
        "Paz, K. S. D. (2019). Supply Response of Seaweeds in Philippines: An Autoregressive Distributive Lag Model.",
        "Prachom, N., Boonyoung, S., Hassaan, M. S., El‐Haroun, E., & Davies, S. J. (2021). Preliminary evaluation of Superworm (Zophobas morio) larval meal as a partial protein source in experimental diets for juvenile Asian sea bass, Lates calcarifer. *Aquaculture Nutrition*, 27(5), 1304–1314.",
        "Ragozzino-Paulino, P., Cocato, M. L., & de Souza Sarkis, J. E. (2025). Nutritional Potential of Edible Insects as Alternative Ingredients in Fish Feed: A Path to Modern Aquaculture. *Aquaculture Nutrition*, 2025(1), 7009004.",
        "Rigg, D. P., Wang, C. M., & Jerry, D. R. (2020). Aquaculture of the redclaw crayfish Cherax quadricarinatus: A review of farming practices, nutrition, and genetics. *Reviews in Aquaculture*, 13(1), 145–167.",
        "Rumbos, C. I., & Athanassiou, C. G. (2021). The superworm, Zophobas morio (Coleoptera: Tenebrionidae): A ‘sleeping giant’ in nutrient sources. *Journal of Insects as Food and Feed*, 7(5), 785–802.",
        "Salayo, N. D., Marte, C. L., Toledo, J. D., Gaitan, A. G., & Agbayani, R. F. (2021). Developing a self-sufficient Philippine milkfish industry through value chain analysis. *Ocean & Coastal Management*, 201, 105426.",
        "Silvederio, G. X. L., Javellana, T. F., Genciana, A. B. N., Fontanilla, M. A. G., Traifalgar, R. F. M., Huervana, F. H., & Del Castillo, C. S. (2025). Gut microbiome composition and diversity of wild-caught and hatchery-bred milkfish (Chanos chanos) fry. *Journal of Genetic Engineering and Biotechnology*, 23(3), 100520.",
        "Tahiluddin, A. B., Bornales, J. C., Limbaro, G. R. A., Paudac, M. A. T. U., Amarille, R. K., Sirad, N. R., ... & Esguerra, J. P. (2025). Environmental impacts of aquaculture in the Philippines.",
        "Tina, F. W., Afsarimanesh, N., Nag, A., & Alahi, M. E. E. (2025). Integrating AIoT technologies in aquaculture: A systematic review. *Future Internet*, 17(5), 199.",
        "Tolentino, L. K. (2021). Development of an IoT-based intensive aquaculture monitoring system with automatic water correction. *International Journal of Computing and Digital Systems*.",
        "WorldFish. (2021). *Digital Innovations for Aquatic Food Systems: Annual Report 2021*. WorldFish.",
        "WorldFish. (2022). *Small-scale aquaculture digital value chains and market linkages in Southeast Asia*. WorldFish Policy Brief.",
        "Wu, A. Q., Li, K. L., Song, Z. Y., Lou, X., Hu, P., Yang, W., & Wang, R. F. (2025). Deep learning for sustainable aquaculture: Opportunities and challenges. *Sustainability*, 17(11), 5084.",
        "Xu, Y., Jin, J. D., Zeng, S. W., Zhang, Y., & Xiao, Q. L. (2023). Development and evaluation of an IoT-based portable water quality monitoring system for aquaculture.",
        "Yang, X., Tang, Z., Huang, K., Guo, R., Wang, D., Jiang, S., & Yu, K. (2025). Optimal feeding levels to enhance growth performance and gut microbiota balance in red swamp crayfish (Procambarus clarkii). *Aquaculture Reports*, 41, 102717.",
        "Zapata Jr, N. R., Sarmiento, J. A. C., & Cruz, M. B. (2023). Development of smart food value chain intervention models for the milkfish industry in Region 1, Philippines. *Asian Journal of Agriculture and Development*, 20(1), 87–108."
    ]

    refs_formatted = "\n\n".join(sorted(all_refs, key=lambda s: s.lower()))

    combined = f"""{ch1}

<br><br>

---

<br><br>

{ch2}

<br><br>

---

<br><br>

{ch3}

<br><br>

---

# REFERENCES

{refs_formatted}
"""

    with open('Documents/Final_Paper/Final_Paper.md', 'w', encoding='utf-8') as f:
        f.write(combined)

    with open('Documents/Final_Paper/Chapter_3.md', 'w', encoding='utf-8') as f:
        f.write(f"{ch3}\n\n<br><br>\n\n---\n\n# REFERENCES\n\n{refs_formatted}")

    print("Successfully built Final_Paper.md and Chapter_3.md!")

if __name__ == '__main__':
    build_all_md()
