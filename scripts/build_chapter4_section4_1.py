import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

def add_body_p(doc, text, space_after=8, indent=0.5):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.5
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if indent > 0:
        p.paragraph_format.first_line_indent = Inches(indent)
    r = p.add_run(text)
    r.font.name = 'Arial'
    r.font.size = Pt(12)
    r.font.color.rgb = RGBColor(0, 0, 0)
    return p

def add_figure_item(doc, fig_num, title, desc_text, img_filename=None):
    # Figure label paragraph
    p_lbl = doc.add_paragraph()
    p_lbl.paragraph_format.space_before = Pt(14)
    p_lbl.paragraph_format.space_after = Pt(4)
    p_lbl.paragraph_format.line_spacing = 1.15
    
    r_f = p_lbl.add_run(f"Figure {fig_num}\n")
    r_f.font.name = "Arial"
    r_f.font.size = Pt(12)
    r_f.bold = True
    r_f.font.color.rgb = RGBColor(0, 0, 0)
    
    r_t = p_lbl.add_run(title)
    r_t.font.name = "Arial"
    r_t.font.size = Pt(12)
    r_t.italic = True
    r_t.font.color.rgb = RGBColor(0, 0, 0)

    # Insert Image directly centered (no ugly empty border boxes)
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img.paragraph_format.space_before = Pt(6)
    p_img.paragraph_format.space_after = Pt(8)
    
    img_path = None
    if img_filename:
        img_path = os.path.abspath(os.path.join("Documents/Final_Paper/ch4_figures", img_filename))
    
    if img_path and os.path.exists(img_path):
        p_img.add_run().add_picture(img_path, width=Inches(5.8))
    else:
        # Fallback to general mockup
        p_img.add_run(f"[ Figure {fig_num}: {title} ]")

    # Narrative explanation paragraph below image
    add_body_p(doc, desc_text, space_after=10, indent=0.5)

CHAPTER_4_FIGURES = [
    (
        14,
        "Figure_14_Login.png",
        "Unified Login and Multi-Role Role-Based Authentication Interface",
        "Figure 14 presents the unified Login and Multi-Role Role-Based Access Control (RBAC) authentication interface. "
        "The interface serves as the primary security gateway for all system actors (Farm Owner, Commercial Customer, and Delivery Rider). "
        "The system authenticates credentials using PBKDF2 cryptographic password hashing and dynamically routes verified sessions to their "
        "respective interfaces: the Farm Owner is directed to the Executive Dashboard, the Delivery Rider to the mobile dispatch portal, "
        "and the Commercial Customer to the online e-commerce storefront. Unauthorized administrative access attempts by non-privileged accounts "
        "are intercepted by role guard middleware and redirected with a security notification."
    ),
    (
        15,
        "Figure_15_Executive_Dashboard.png",
        "Executive Dashboard and Real-Time Farm Monitoring Interface",
        "Figure 15 illustrates the Executive Dashboard and Real-Time Farm Monitoring interface accessed by the Farm Owner. "
        "The dashboard aggregates live operational key performance indicators (KPIs) across six high-contrast metric cards: Active Stocks (headcount across ponds), "
        "Daily Sales (gross daily transactions in PHP), Revenue (30-day cumulative earnings), Pending Orders requiring fulfillment, Upcoming Harvests scheduled "
        "for maturity, and Total Active Product Catalog Listings. In addition, an interactive 10-day revenue spline line chart visualizes daily financial "
        "trajectories, while automated sanitization alert banners notify farm personnel when earthen ponds reach the 15-day post-stocking Azula treatment cycle."
    ),
    (
        16,
        "Figure_16_Ponds_and_Racks.png",
        "Aquaculture Pond, Cabin Racks, and Tank Cultivation Management Interface",
        "Figure 16 displays the Aquaculture Pond, Cabin Racks, and Tank Cultivation Management interface. The module enables the Farm Owner to monitor "
        "and configure physical rearing environments across outdoor earthen ponds for Cherax quadricarinatus (Australian Redclaw Crayfish) and indoor multi-tier "
        "shelf tray racks for Zophobas morio (Superworm larvae and darkling beetles). Each containment unit displays current stock headcount, "
        "surface footprint area (sqm), water column depth, shelf tier positioning, life cycle stage transitions, and real-time operational status (Active, Maintenance, or Fallow)."
    ),
    (
        17,
        "Figure_17_Feeding_Logs.png",
        "Feed Formulation and Daily Supply Management Interface",
        "Figure 17 presents the Feed Formulation and Daily Supply Management interface. Farm staff utilize this module to record feed administration events "
        "by selecting specific stock batches, choosing specialized feed types (e.g., Sinking Crayfish Pellets, Wheat Bran, Chopped Carrots, and PO1/PO2 formulations), "
        "inputting exact quantities in kilograms, and assigning feeding timestamps. The system automatically updates feed inventory levels to maintain optimal nutrition schedules."
    ),
    (
        18,
        "Figure_18_Mortality_Tracking.png",
        "Azula Cultivation and 15-Day Pond Sanitization Monitoring Interface",
        "Figure 18 shows the Azula Cultivation and 15-Day Pond Sanitization Monitoring interface. The interface tracks the propagation of Azula micro-crops for supplementary "
        "organic feed, monitors earthen pond sanitization cycles, and generates automated reminders when ponds reach the 15-day post-stocking maintenance interval for lime conditioning "
        "and water filtration maintenance."
    ),
    (
        19,
        "Figure_19_Harvest_Recording.png",
        "Harvest Lifecycle Scheduling and Production Calendar Interface",
        "Figure 19 illustrates the Harvest Lifecycle Scheduling and Production Calendar interface. The module tracks planned harvest schedules across rearing ponds "
        "and superworm cabins, visualizes upcoming harvest events on an interactive multi-sector calendar, and records harvested quantities (kg). An interactive sorting form "
        "allows farm technicians to categorize harvested crayfish into commercial market grades: Grade A (>65g premium table grade), Grade B (45g–64g standard restaurant grade), "
        "and Grade C (<45g juveniles or breeding stock), automatically updating inventory stock ready for market distribution."
    ),
    (
        20,
        "Figure_20_Product_Catalog.png",
        "Commercial Product Catalog and Dual-Unit Pricing Management Interface",
        "Figure 20 presents the Commercial Product Catalog and Dual-Unit Pricing Management interface. The Farm Owner configures live market products with custom "
        "species icons, color accents, stock weight availability (kg), reorder alert thresholds, and dual-unit pricing structures (supporting both Per Piece and Per Kilogram "
        "retail configurations). The module synchronizes pricing adjustments across the customer storefront in real time, displays low-stock warning chips, and allows "
        "instant toggling of product active availability states."
    ),
    (
        21,
        "Figure_21_Customer_Storefront.png",
        "Customer Online Storefront and Interactive Shopping Cart Interface",
        "Figure 21 displays the Customer Online Storefront and Interactive Shopping Cart interface. Commercial buyers and retail consumers browse available live crayfish "
        "and superworm stock, filter items by biological category, and choose between Per Piece or Per Kilogram purchasing options. Customers can add items to an interactive "
        "shopping cart, configure order quantities with real-time stock ceiling validations, select between farm pickup or home delivery, and review live subtotal calculations."
    ),
    (
        22,
        "Figure_22_Order_Checkout_Payment.png",
        "Order Checkout and PayMongo GCash / Cash on Delivery Settlement Interface",
        "Figure 22 illustrates the Order Checkout and Digital Payment Settlement interface. The module supports flexible settlement channels, including Cash on Delivery (COD) "
        "and automated digital payments powered by PayMongo GCash checkout sessions and direct GCash QR code transfer. Customers input delivery addresses, confirm contact details, "
        "and upload payment verification receipts, which are securely verified and archived in the transaction database."
    ),
    (
        23,
        "Figure_23_Sales_Order_Fulfillment.png",
        "Sales Order Fulfillment and Lifecycle State Machine Processing Interface",
        "Figure 23 shows the Sales Order Fulfillment and Lifecycle State Machine Processing interface accessed by the Farm Owner. The interface displays incoming customer "
        "orders with comprehensive billing details, customer contact numbers, itemized products, and payment status badges. The Farm Owner advances orders through a validated "
        "four-stage lifecycle: Pending -> Approved & Scheduled -> Dispatched (In Transit) -> Delivered & Completed. Atomic database transactions deduct product inventory "
        "upon order approval, preventing overselling."
    ),
    (
        24,
        "Figure_24_Courier_Dispatch.png",
        "Courier Dispatch and Delivery Fleet Monitoring Interface",
        "Figure 24 presents the Courier Dispatch and Delivery Fleet Monitoring interface. Farm administrators manage the delivery fleet by registering courier personnel, "
        "monitoring rider availability states (Available, Busy, or Offline), and assigning approved delivery orders to specific riders based on destination proximity and vehicle capacity. "
        "The interface provides an active dispatch summary table displaying assigned rider names, vehicle license plates, order quantities, and transit timestamps."
    ),
    (
        25,
        "Figure_25_Rider_Mobile_Portal.png",
        "Delivery Rider Mobile Portal and Proof of Delivery (POD) Interface",
        "Figure 25 illustrates the Delivery Rider Mobile Portal and digital Proof of Delivery (POD) interface, optimized for smartphone screens. Delivery riders access their "
        "assigned dispatch task list, review customer delivery addresses with direct navigation links, and update transit statuses (e.g., In Transit, Arrived). Upon customer handover, "
        "the rider captures a recipient photo or digital signature directly through the mobile camera, uploading cryptographic proof of delivery that finalizes the order record."
    ),
    (
        26,
        "Figure_26_GPS_Tracking_Map.png",
        "Real-Time GPS Delivery Tracking and Leaflet GIS Map Routing Interface",
        "Figure 26 displays the Real-Time GPS Delivery Tracking and Leaflet.js GIS Map Routing interface. Both the customer and farm owner can track live order transit "
        "along an interactive OpenStreetMap road network overlay connecting the aquaculture farm origin in Barangay Lantad to the customer's delivery destination in Silay City or Bacolod City. "
        "The interface displays vehicle coordinate pins, estimated time of arrival (ETA), and a four-step progress tracker."
    ),
    (
        27,
        "Figure_27_Predictive_Regression_Analytics.png",
        "Predictive Demand Analytics and OLS Linear Regression Forecasting Interface",
        "Figure 27 illustrates the Predictive Demand Analytics and Ordinary Least Squares (OLS) Linear Regression Forecasting interface. The module analyzes historical daily sales "
        "revenue and product volume trends to compute mathematical regression slopes, intercepts, and correlation coefficients (R^2). The interface visualizes historical sales "
        "alongside a 7-day rolling moving average and projected future demand curves (purple dotted spline), providing the Farm Owner with quantitative decision support for pond stocking "
        "and feed procurement."
    ),
    (
        28,
        "Figure_28_KMeans_Customer_Clustering.png",
        "Customer K-Means Clustering and Market Segmentation Analytics Interface",
        "Figure 28 shows the Customer K-Means Clustering and Market Segmentation Analytics interface. The machine learning engine groups farm buyers into three distinct clusters: "
        "High-Value Commercial Wholesalers (frequent, large-volume orders), Regular Retail Buyers (steady recurring purchases), and Occasional Small-Scale Hobbyists (infrequent, single-unit orders). "
        "The interface visualizes cluster distribution scatter plots and top product preference proportions, enabling targeted marketing and optimized commercial inventory allocation."
    ),
    (
        29,
        "Figure_29_Executive_Reports_Audit_Logs.png",
        "Executive PDF Report Generation and Three-Tiered System Audit Trail Interface",
        "Figure 29 presents the Executive PDF Report Generation and Three-Tiered System Audit Trail interface. The reporting engine produces formal, printable PDF and Excel summaries "
        "for Sales Revenue Ledgers, Daily Feeding Reports, Harvest Production Summaries, and Commercial Invoices with official signatory blocks. Furthermore, the three-tiered audit log "
        "(Product Logs, Activity Audit Logs, and Input Modification Logs) captures every data creation, modification, and deletion event with immutable timestamps and user credentials."
    ),
]

def build_chapter4_document():
    doc = Document()

    for section in doc.sections:
        section.page_width = Inches(8.5)
        section.page_height = Inches(11.0)
        section.left_margin = Inches(1.5)
        section.right_margin = Inches(1.0)
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)

    # Document Header - CHAPTER IV
    p_ch = doc.add_paragraph()
    p_ch.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_ch.paragraph_format.space_before = Pt(0)
    p_ch.paragraph_format.space_after = Pt(2)
    p_ch.paragraph_format.line_spacing = 1.0
    r_ch = p_ch.add_run("CHAPTER IV")
    r_ch.bold = True
    r_ch.font.name = "Arial"
    r_ch.font.size = Pt(12)
    r_ch.font.color.rgb = RGBColor(0, 0, 0)

    # RESULTS AND DISCUSSION
    p_rd = doc.add_paragraph()
    p_rd.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_rd.paragraph_format.space_before = Pt(0)
    p_rd.paragraph_format.space_after = Pt(14)
    p_rd.paragraph_format.line_spacing = 1.0
    r_rd = p_rd.add_run("RESULTS AND DISCUSSION")
    r_rd.bold = True
    r_rd.font.name = "Arial"
    r_rd.font.size = Pt(12)
    r_rd.font.color.rgb = RGBColor(0, 0, 0)

    # Introductory Narrative
    add_body_p(
        doc,
        "This chapter presents the results and discussions based on the development and evaluation of the Aquaculture Value Chain Management System "
        "with Predictive Analytics for Silay Superworm & Crayfish, in line with the objectives established in Chapter I. It includes comprehensive "
        "interface walkthroughs of the system's operational modules, the rigorous results of functionality testing (encompassing 40 Black-box functional "
        "test cases and 16 White-box structural test cases), and the software quality evaluation conducted in accordance with the ISO/IEC 25010:2011 Software "
        "Quality Model. Data were gathered from key stakeholders, including the Farm Owner, commercial buyers, retail customers, delivery riders, and "
        "independent IT experts, utilizing a five-point Likert scale ranging from 1 (Strongly Disagree) to 5 (Strongly Agree)."
    )

    add_body_p(
        doc,
        "Furthermore, this chapter provides an empirical analysis of the system's execution under real-world aquaculture farm workflows in Barangay Lantad, "
        "Silay City, Negros Occidental. The findings demonstrate the system's technical effectiveness, operational reliability, data security, calculation "
        "precision in dual-unit pricing and biological growth tracking, and capacity to eliminate manual recordkeeping inefficiencies while providing "
        "predictive decision-support capabilities through machine learning forecasting and customer segmentation."
    )

    # 4.1 Results of the Study
    p_h1 = doc.add_paragraph()
    p_h1.paragraph_format.space_before = Pt(14)
    p_h1.paragraph_format.space_after = Pt(6)
    p_h1.paragraph_format.line_spacing = 1.5
    r_h1 = p_h1.add_run("4.1 Results of the Study")
    r_h1.bold = True
    r_h1.font.name = "Arial"
    r_h1.font.size = Pt(12)
    r_h1.font.color.rgb = RGBColor(0, 0, 0)

    add_body_p(
        doc,
        "The first objective of this study aimed to design and develop an Aquaculture Value Chain Management System with Predictive Analytics equipped "
        "with technical features including: (1) multi-role user authentication and session security, (2) an executive dashboard with real-time "
        "farm KPIs, (3) pond, cabin rack, and tank cultivation management, (4) feed formulation and daily feeding logging, (5) mortality tracking and survival "
        "rate computation, (6) harvest scheduling and commercial grade sorting, (7) commercial product catalog with dual-unit pricing (Per Piece and Per KG), "
        "(8) customer storefront with online cart checkout, (9) digital payment settlement supporting PayMongo GCash and COD, (10) sales order fulfillment "
        "and lifecycle state machine, (11) courier fleet dispatch and mobile rider portal with Proof of Delivery (POD), (12) real-time GPS tracking with Leaflet GIS maps, "
        "(13) predictive demand forecasting using Ordinary Least Squares Linear Regression, (14) customer segmentation using K-Means clustering, and (15) executive "
        "PDF/Excel report generation with a three-tiered audit trail."
    )

    add_body_p(
        doc,
        "The development of the system was completed using an enterprise Model-View-Template (MVT) architecture combining Python 3.11 with the Django 5.1 "
        "framework on the backend, supported by an ACID-compliant PostgreSQL / SQLite relational database, responsive HTML5/CSS3/JavaScript frontend with "
        "Bootstrap 5 and Tailwind CSS styling, Chart.js/ApexCharts interactive visualization libraries, and Leaflet.js GIS spatial mapping. The operational "
        "interfaces of the developed system are presented in Figures 14 through 29."
    )

    # Insert Figures 14 through 29 with high-res images
    for fig_num, fname, title, desc in CHAPTER_4_FIGURES:
        add_figure_item(doc, fig_num, title, desc, img_filename=fname)

    out_path = os.path.abspath("Documents/Chapter 4/Chapter_4_Section_4_1.docx")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    doc.save(out_path)
    print(f"Chapter 4 Section 4.1 DOCX saved successfully: {out_path}")
    doc.save(os.path.abspath("Documents/Chapter_4_Section_4_1.docx"))

if __name__ == "__main__":
    build_chapter4_document()
