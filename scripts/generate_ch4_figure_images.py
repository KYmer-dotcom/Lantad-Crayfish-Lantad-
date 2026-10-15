import os
from PIL import Image, ImageDraw, ImageFont

def create_ui_mockup_image(output_path, title, subtitle, badges, metrics, table_headers, table_rows, chart_type=None, accent_color="#10B981"):
    # High resolution canvas 1200 x 680
    w, h = 1200, 680
    img = Image.new("RGB", (w, h), "#0F172A") # Sleek modern dark theme
    draw = ImageDraw.Draw(img)

    # Load default fonts or try PIL basic fonts
    try:
        font_title = ImageFont.truetype("arial.ttf", 26)
        font_sub = ImageFont.truetype("arial.ttf", 15)
        font_bold = ImageFont.truetype("arialbd.ttf", 16)
        font_regular = ImageFont.truetype("arial.ttf", 14)
        font_small = ImageFont.truetype("arial.ttf", 12)
        font_kpi_val = ImageFont.truetype("arialbd.ttf", 28)
        font_kpi_lbl = ImageFont.truetype("arial.ttf", 13)
    except:
        font_title = font_sub = font_bold = font_regular = font_small = font_kpi_val = font_kpi_lbl = ImageFont.load_default()

    # --- Top Navbar ---
    draw.rectangle([(0, 0), (w, 60)], fill="#1E293B")
    draw.rectangle([(0, 59), (w, 60)], fill="#334155")
    
    # Brand logo & title
    draw.ellipse([(25, 15), (55, 45)], fill="#059669")
    draw.text((68, 20), "LANTAD AQUACULTURE MANAGEMENT SYSTEM", fill="#F8FAFC", font=font_bold)
    
    # User badge
    draw.rounded_rectangle([(w - 240, 14), (w - 25, 46)], radius=6, fill="#334155")
    draw.ellipse([(w - 230, 20), (w - 210, 40)], fill="#10B981")
    draw.text((w - 200, 21), "Farm Owner (Online)", fill="#F1F5F9", font=font_small)

    # --- Main Content Header ---
    draw.text((40, 85), title, fill="#FFFFFF", font=font_title)
    draw.text((40, 122), subtitle, fill="#94A3B8", font=font_sub)

    # Badges
    bx = 40
    for b_text, b_col in badges:
        bw = len(b_text) * 8 + 24
        draw.rounded_rectangle([(bx, 150), (bx + bw, 176)], radius=12, fill=b_col)
        draw.text((bx + 12, 155), b_text, fill="#FFFFFF", font=font_small)
        bx += bw + 12

    # --- Metric KPI Cards (if any) ---
    cur_y = 195
    if metrics:
        num_m = len(metrics)
        card_w = (w - 80 - (num_m - 1) * 16) // num_m
        for i, (m_lbl, m_val, m_icon_col) in enumerate(metrics):
            mx = 40 + i * (card_w + 16)
            draw.rounded_rectangle([(mx, cur_y), (mx + card_w, cur_y + 85)], radius=8, fill="#1E293B", outline="#334155", width=1)
            draw.rectangle([(mx, cur_y), (mx + 4, cur_y + 85)], fill=m_icon_col)
            draw.text((mx + 16, cur_y + 12), m_lbl.upper(), fill="#94A3B8", font=font_kpi_lbl)
            draw.text((mx + 16, cur_y + 38), m_val, fill="#F8FAFC", font=font_kpi_val)
        cur_y += 105

    # --- Main Body Area: Table or Chart ---
    body_h = h - cur_y - 30
    draw.rounded_rectangle([(40, cur_y), (w - 40, cur_y + body_h)], radius=8, fill="#1E293B", outline="#334155", width=1)

    if chart_type == "line":
        # Draw Spline / Line Chart
        draw.text((60, cur_y + 18), "Historical Sales Revenue & 7-Day Moving Forecast (PHP)", fill="#F1F5F9", font=font_bold)
        draw.rounded_rectangle([(w - 180, cur_y + 14), (w - 60, cur_y + 42)], radius=6, fill="#334155")
        draw.text((w - 165, cur_y + 20), "LAST 30 DAYS", fill="#93C5FD", font=font_small)
        
        # Grid lines
        for gy in range(cur_y + 70, cur_y + body_h - 40, 50):
            draw.line([(80, gy), (w - 80, gy)], fill="#334155", width=1)

        # Plot synthetic line
        points = [
            (90, cur_y + 220), (180, cur_y + 200), (270, cur_y + 170), (360, cur_y + 210),
            (450, cur_y + 140), (540, cur_y + 120), (630, cur_y + 150), (720, cur_y + 90),
            (810, cur_y + 80), (900, cur_y + 60), (990, cur_y + 45), (1080, cur_y + 40)
        ]
        for idx in range(len(points) - 1):
            draw.line([points[idx], points[idx + 1]], fill="#10B981", width=3)
            draw.ellipse([(points[idx][0] - 4, points[idx][1] - 4), (points[idx][0] + 4, points[idx][1] + 4)], fill="#34D399")
        # Draw forecast dashed line
        for idx in range(7, len(points) - 1):
            draw.line([points[idx], points[idx + 1]], fill="#A855F7", width=3)
        draw.text((w - 380, cur_y + body_h - 30), "Green: Actual Sales | Purple: OLS Regression Forecast", fill="#94A3B8", font=font_small)

    elif chart_type == "cluster":
        # Draw Scatter Plot K-Means
        draw.text((60, cur_y + 18), "Customer Lifetime Value & Order Frequency (K-Means Clusters)", fill="#F1F5F9", font=font_bold)
        # Cluster 1 (Wholesale - Red)
        c1 = [(150, cur_y + 70), (180, cur_y + 90), (220, cur_y + 60), (200, cur_y + 120), (260, cur_y + 80)]
        for pt in c1:
            draw.ellipse([(pt[0]-8, pt[1]-8), (pt[0]+8, pt[1]+8)], fill="#EF4444")
        # Cluster 2 (Regular - Blue)
        c2 = [(450, cur_y + 160), (480, cur_y + 190), (520, cur_y + 140), (570, cur_y + 180), (610, cur_y + 150), (660, cur_y + 200)]
        for pt in c2:
            draw.ellipse([(pt[0]-8, pt[1]-8), (pt[0]+8, pt[1]+8)], fill="#3B82F6")
        # Cluster 3 (Occasional - Green)
        c3 = [(800, cur_y + 230), (840, cur_y + 250), (890, cur_y + 220), (930, cur_y + 260), (980, cur_y + 240), (1040, cur_y + 250)]
        for pt in c3:
            draw.ellipse([(pt[0]-8, pt[1]-8), (pt[0]+8, pt[1]+8)], fill="#10B981")
        draw.text((80, cur_y + body_h - 30), "Red: High-Value Wholesalers | Blue: Regular Retailers | Green: Occasional Buyers", fill="#CBD5E1", font=font_small)

    elif table_headers and table_rows:
        # Draw Table
        th_y = cur_y + 12
        col_w = (w - 120) // len(table_headers)
        draw.rectangle([(50, th_y), (w - 50, th_y + 36)], fill="#334155")
        for c_idx, th in enumerate(table_headers):
            draw.text((60 + c_idx * col_w, th_y + 10), th.upper(), fill="#94A3B8", font=font_small)

        row_y = th_y + 42
        for r_data in table_rows[:6]:
            draw.line([(50, row_y + 36), (w - 50, row_y + 36)], fill="#334155", width=1)
            for c_idx, cell_txt in enumerate(r_data):
                col_text = "#F8FAFC"
                if "Active" in cell_txt or "Delivered" in cell_txt or "Paid" in cell_txt or "Grade A" in cell_txt:
                    col_text = "#34D399"
                elif "Pending" in cell_txt or "In Transit" in cell_txt or "Scheduled" in cell_txt:
                    col_text = "#FBBF24"
                draw.text((60 + c_idx * col_w, row_y + 8), str(cell_txt), fill=col_text, font=font_regular)
            row_y += 42

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path, quality=95)
    print(f"Generated UI Figure: {output_path}")

FIGURE_CONFIGS = [
    (14, "Figure_14_Login.png", "Authentication & Multi-Role Sign In", "Role-Based Access Control (Owner, Customer, Rider)",
     [("Security", "#1E40AF"), ("PBKDF2 Encryption", "#047857"), ("Unified Portal", "#7C3AED")],
     [("Total Users", "42 Active", "#3B82F6"), ("Session Status", "Encrypted", "#10B981"), ("Failed Lockout", "5 Attempts", "#EF4444")],
     ["User Handle", "Role Access", "Portal Destination", "Authentication Status"],
     [["owner_silay", "Farm Owner", "Executive Dashboard (/dashboard/)", "Authenticated (Active)"],
      ["rider_ramon", "Delivery Rider", "Mobile Courier Portal (/rider/)", "Authenticated (Active)"],
      ["buyer_lacson", "Customer / Buyer", "Public Storefront (/market/)", "Authenticated (Active)"]]),

    (15, "Figure_15_Executive_Dashboard.png", "Executive Dashboard & Real-Time Farm Monitoring", "Live Aquaculture Key Performance Indicators and Revenue Analytics",
     [("Live Farm KPIs", "#047857"), ("30-Day Revenue", "#1E40AF"), ("Sanitization Alerts", "#B45309")],
     [("Active Stocks", "3,850 Pcs", "#3B82F6"), ("Daily Sales", "PHP 14,850.00", "#10B981"), ("30D Revenue", "PHP 185,400.00", "#8B5CF6"), ("Pending Orders", "6 Orders", "#F59E0B")],
     None, None, "line"),

    (16, "Figure_16_Ponds_and_Racks.png", "Aquaculture Ponds & Superworm Racks Management", "Cultivation Infrastructure & Stocking Densities",
     [("Concrete Ponds", "#047857"), ("Earthen Ponds", "#0D9488"), ("Multi-Tier Trays", "#B45309")],
     [("Active Units", "12 Ponds / 48 Trays", "#3B82F6"), ("Total Capacity", "6,000 Headcount", "#10B981"), ("Occupancy Rate", "84.5%", "#8B5CF6")],
     ["Unit Name", "Species Cultured", "Cultivation Stage", "Density / Capacity", "Status"],
     [["Concrete Pond A-1", "Australian Redclaw Crayfish", "Adult (Growout)", "385 / 500 Pcs", "Active"],
      ["Concrete Pond A-2", "Australian Redclaw Crayfish", "Juvenile (Nursery)", "450 / 500 Pcs", "Active"],
      ["Earthen Pond B-1", "Australian Redclaw Crayfish", "Broodstock (Breeding)", "200 / 300 Pcs", "Active"],
      ["Superworm Rack T-1", "Zophobas morio (Larvae)", "Larvae Feeding Stage", "12.5 kg / 15.0 kg", "Active"],
      ["Superworm Rack T-2", "Zophobas morio (Beetles)", "Darkling Beetle Reproduction", "800 Beetles", "Active"]]),

    (17, "Figure_17_Feeding_Logs.png", "Feed Types & Daily Supply Management", "Feed Formulation Inventory and Daily Feed Administration",
     [("Sinking Pellets", "#047857"), ("Wheat Bran", "#B45309"), ("Vegetables / Azula", "#0D9488")],
     [("Daily Feed Used", "18.4 kg", "#3B82F6"), ("Active Feed Types", "5 Formulations", "#10B981"), ("Feed Stock Balance", "145.0 kg", "#8B5CF6")],
     ["Batch Code", "Target Unit", "Feed Formulation", "Quantity (kg)", "Fed By Staff", "Time Logged"],
     [["BATCH-2025-CR-01", "Pond A-1", "Sinking Crayfish Pellets (35% Pro)", "1.25 kg", "Farm Operator 1", "07:30 AM"],
      ["BATCH-2025-CR-02", "Pond A-2", "Starter Crumbles (40% Pro)", "0.85 kg", "Farm Operator 1", "07:45 AM"],
      ["BATCH-2025-SW-01", "Rack T-1", "Wheat Bran + Sliced Carrots", "2.50 kg", "Farm Operator 2", "08:15 AM"],
      ["BATCH-2025-CR-01", "Pond A-1", "Sinking Crayfish Pellets (35% Pro)", "1.25 kg", "Farm Operator 1", "05:30 PM"]]),

    (18, "Figure_18_Mortality_Tracking.png", "Azula Cultivation & 15-Day Pond Sanitization Monitoring", "Sanitization Cycle Alerts and Cultivation Pond Maintenance",
     [("Azula Cultivation", "#047857"), ("Sanitization Alert", "#D97706"), ("Pond Maintenance", "#2563EB")],
     [("Active Azula Ponds", "4 Ponds", "#10B981"), ("Sanitization Status", "All Clear", "#3B82F6"), ("Next Cycle Due", "In 4 Days", "#F59E0B")],
     ["Pond Identifier", "Species / Crop", "Cycle Day", "Sanitization Status", "Maintenance Action", "Supervisor"],
     [["Earthen Pond 1", "Azula Propagation", "Day 11 / 15", "Active Cultivation", "Water level inspection", "Farm Operator 1"],
      ["Main Pond A", "Redclaw Crayfish", "Day 15 / 15", "Sanitization Alert", "Drain & Lime Conditioning", "Farm Operator 2"],
      ["Superworm Cabin 1", "Superworm Larvae", "Cycle Active", "Optimal Substrate", "Substrate sieving completed", "Farm Operator 1"]]),

    (19, "Figure_19_Harvest_Recording.png", "Harvest Lifecycle Scheduling & Interactive Production Calendar", "Commercial Grade Sorting and Schedule Coordination",
     [("Grade A (>65g)", "#047857"), ("Grade B (45-64g)", "#2563EB"), ("Grade C (<45g)", "#D97706")],
     [("Total Schedules", "4 Active", "#3B82F6"), ("Est. Harvest Yield", "55.10 kg", "#10B981"), ("Grade A Projected", "38.20 kg", "#8B5CF6")],
     ["Schedule Code", "Cultivation Sector", "Target Date", "Est. Quantity", "Commercial Grade", "Assigned Lead"],
     [["SCH-2025-001", "Main Pond A", "2025-06-15", "25.0 kg", "Grade A (Table Grade)", "Farm Staff 1"],
      ["SCH-2025-002", "Superworm Cabin 1", "2025-06-18", "30.0 kg", "Commercial Superworms", "Farm Staff 2"],
      ["SCH-2025-003", "Breeding Pond B", "2025-06-22", "15.0 kg", "Grade B (Standard)", "Farm Staff 1"]]),

    (20, "Figure_20_Product_Catalog.png", "Commercial Product Catalog & Dual-Unit Pricing", "Inventory Item Specifications and Real-Time Reorder Controls",
     [("Live Inventory", "#047857"), ("Dual Pricing", "#7C3AED"), ("Reorder Alerts", "#D97706")],
     [("Listed Products", "8 Items", "#3B82F6"), ("Available Stock", "75.50 kg", "#10B981"), ("Stock Value", "PHP 48,250.00", "#8B5CF6")],
     ["Product Name", "Category", "Unit Type", "Stock Level", "Price / Unit", "Price / KG", "Status"],
     [["Australian Redclaw (Grade A)", "Crayfish", "Kilogram / Piece", "45.50 kg", "PHP 45.00 / pc", "PHP 650.00 / kg", "Active"],
      ["Australian Redclaw (Grade B)", "Crayfish", "Kilogram / Piece", "18.00 kg", "PHP 35.00 / pc", "PHP 520.00 / kg", "Active"],
      ["Live Superworms (Bulk Box)", "Superworm", "Kilogram", "12.00 kg", "PHP 180.00 / tub", "PHP 450.00 / kg", "Active"]]),

    (21, "Figure_21_Customer_Storefront.png", "Customer Online Storefront & Product Discovery", "Public Catalog Browsing and Real-Time Stock Validation",
     [("Storefront Portal", "#047857"), ("Live Cart", "#2563EB"), ("Instant Stock", "#7C3AED")],
     [("Catalog Items", "8 Available", "#3B82F6"), ("Cart Items", "2 Products", "#10B981"), ("Subtotal", "PHP 3,250.00", "#8B5CF6")],
     ["Selected Product", "Purchase Mode", "Unit Price", "Quantity Ordered", "Item Subtotal"],
     [["Australian Redclaw Crayfish (Grade A)", "By Weight (KG)", "PHP 650.00 / kg", "5.00 kg", "PHP 3,250.00"],
      ["Live Superworm Plastic Tub (100g)", "Per Piece / Tub", "PHP 50.00 / tub", "4 Tubs", "PHP 200.00"]]),

    (22, "Figure_22_Order_Checkout_Payment.png", "Order Checkout & Digital Payment Gateway", "PayMongo GCash Integration & Cash on Delivery Verification",
     [("PayMongo GCash", "#047857"), ("Cash on Delivery", "#2563EB"), ("SSL / TLS", "#7C3AED")],
     [("Order Gross Amount", "PHP 3,450.00", "#3B82F6"), ("Payment Channel", "GCash Verified", "#10B981"), ("Invoice Code", "INV-2025-06-001", "#8B5CF6")],
     ["Customer Name", "Delivery Address", "Selected Payment", "Transaction Reference", "Payment Status"],
     [["Bacolod Seafood Grill", "Lacson St., Bacolod City", "PayMongo GCash QR", "PM-GC-88492041", "Paid (Verified)"],
      ["Negros Exotic Pets", "Burgos St., Silay City", "Cash on Delivery (COD)", "COD-SLY-0092", "Pending Collection"]]),

    (23, "Figure_23_Sales_Order_Fulfillment.png", "Sales Order Fulfillment & Order Lifecycle Machine", "State Machine Transition Pipeline (Pending -> Delivered)",
     [("Order Processing", "#047857"), ("Atomic Stock Lock", "#2563EB"), ("Dispatch Queue", "#D97706")],
     [("Active Orders", "6 Orders", "#3B82F6"), ("Total Order Value", "PHP 22,400.00", "#10B981"), ("Dispatched Today", "4 Shipments", "#8B5CF6")],
     ["Order Number", "Customer Name", "Product Line", "Order Amount", "Lifecycle Status", "Action"],
     [["ORD-2025-06-001", "Bacolod Seafood Grill", "Redclaw Crayfish Grade A (5kg)", "PHP 3,250.00", "Dispatched (In Transit)", "Track Live"],
      ["ORD-2025-06-002", "Silay Gourmet Resto", "Redclaw Crayfish Grade B (8kg)", "PHP 4,160.00", "Scheduled for Dispatch", "Assign Rider"],
      ["ORD-2025-06-003", "Victorias Aquarium", "Live Superworms (2kg)", "PHP 900.00", "Delivered & Completed", "View POD"]]),

    (24, "Figure_24_Courier_Dispatch.png", "Courier Fleet Dispatch & Logistics Monitoring", "Delivery Vehicle Assignment & Capacity Allocation",
     [("Fleet Dispatch", "#047857"), ("Rider Assignment", "#2563EB"), ("Vehicle Capacity", "#7C3AED")],
     [("Registered Couriers", "5 Riders", "#3B82F6"), ("Active Dispatches", "3 En Route", "#10B981"), ("Avg Delivery Time", "38 Minutes", "#8B5CF6")],
     ["Rider Name", "Assigned Vehicle", "Plate Number", "Current Assigned Order", "Rider Status"],
     [["Ramon Dela Cruz", "Motorcycle w/ Insulated Box", "NEG-4582", "ORD-2025-06-001 (Bacolod)", "In Transit (En Route)"],
      ["Jose Tan", "Multicab Delivery", "NEG-1920", "ORD-2025-06-002 (Silay City)", "Available / Standby"],
      ["Mark Alcantara", "Motorcycle Cargo", "NEG-8831", "ORD-2025-06-003 (Talisay)", "Delivered (Returning)"]]),

    (25, "Figure_25_Rider_Mobile_Portal.png", "Delivery Rider Mobile Portal & Digital Proof of Delivery", "Mobile Courier Task Execution & Photo POD Verification",
     [("Mobile Responsive", "#047857"), ("Camera Capture", "#2563EB"), ("GPS Geolocation", "#D97706")],
     [("Assigned Tasks", "2 Drop-offs", "#3B82F6"), ("Completed Today", "4 Deliveries", "#10B981"), ("POD Status", "Photo & Signature Stored", "#8B5CF6")],
     ["Shipment ID", "Recipient Destination", "Payload Mass", "Customer Contact", "Handover Action"],
     [["DEL-2025-001", "Lacson St., Bacolod City", "5.0 kg Crayfish", "0917-123-4567", "Capture Photo POD & Signature"],
      ["DEL-2025-002", "Burgos St., Silay City", "2.0 kg Superworms", "0928-765-4321", "Confirm Cash Handover"]]),

    (26, "Figure_26_GPS_Tracking_Map.png", "Real-Time GPS Delivery Tracking & Leaflet GIS Map", "Live Spatial Transit Tracking & Route Navigation",
     [("Leaflet GIS Map", "#047857"), ("Live Coordinates", "#2563EB"), ("Route Polyline", "#7C3AED")],
     [("Origin", "Barangay Lantad Farm", "#3B82F6"), ("Destination", "Bacolod City Center", "#10B981"), ("Estimated Transit", "18 Mins Remaining", "#8B5CF6")],
     ["Checkpoint Stage", "Timestamp", "Spatial Coordinate", "Status Message"],
     [["Dispatch from Farm Depot", "02:15 PM", "10.7982° N, 122.9754° E", "Package loaded in insulated container"],
      ["En Route along Highway", "02:35 PM", "10.7420° N, 122.9610° E", "Rider in transit (Normal speed)"],
      ["Arrived at Customer Door", "02:50 PM", "10.6765° N, 122.9509° E", "Awaiting customer signature"]]),

    (27, "Figure_27_Predictive_Regression_Analytics.png", "Predictive Demand Analytics & OLS Linear Regression", "Ordinary Least Squares Trendline & Moving Average Forecasting",
     [("OLS Linear Regression", "#047857"), ("7-Day Moving Avg", "#2563EB"), ("R² = 0.942", "#7C3AED")],
     [("Predicted Next Week Sales", "PHP 112,500.00", "#10B981"), ("Regression Slope (m)", "+485.20 / day", "#3B82F6"), ("Confidence Interval", "95.0%", "#8B5CF6")],
     None, None, "line"),

    (28, "Figure_28_KMeans_Customer_Clustering.png", "Customer K-Means Clustering & Market Segmentation", "Unsupervised Machine Learning for Behavioral Purchasing Clusters",
     [("K-Means (k=3)", "#047857"), ("Commercial Wholesalers", "#DC2626"), ("Retail Buyers", "#2563EB")],
     [("High-Value Cluster", "8 Clients (58% Vol)", "#EF4444"), ("Regular Retail", "18 Clients (32% Vol)", "#3B82F6"), ("Occasional", "16 Clients (10% Vol)", "#10B981")],
     None, None, "cluster"),

    (29, "Figure_29_Executive_Reports_Audit_Logs.png", "Executive PDF Report Generation & Three-Tiered Audit Logs", "Automated Financial Exports and Comprehensive Security Audit Trails",
     [("PDF / Excel Engine", "#047857"), ("3-Tier Audit Trail", "#2563EB"), ("COA Ready", "#7C3AED")],
     [("Logged Actions", "1,248 Records", "#3B82F6"), ("Exports Generated", "34 Reports", "#10B981"), ("Audit Integrity", "100% Immutable", "#8B5CF6")],
     ["Event Timestamp", "User Identity", "Role Tier", "Operation Action", "Module Target", "Entity Affected"],
     [["2025-06-18 14:15:22", "owner_silay", "Farm Owner", "CREATE", "Product Catalog", "Added Redclaw Grade A"],
      ["2025-06-18 14:30:10", "buyer_lacson", "Customer", "TRANSACT", "Storefront Cart", "Checked Out ORD-001"],
      ["2025-06-18 14:55:04", "rider_ramon", "Delivery Rider", "UPDATE", "Rider Dispatch", "Uploaded POD Photo DEL-001"]]),
]

def generate_all():
    base_dir = os.path.abspath("Documents/Final_Paper/ch4_figures")
    for fig_num, fname, title, sub, badges, metrics, th, tr, *extra in FIGURE_CONFIGS:
        chart_t = extra[0] if extra else None
        out_p = os.path.join(base_dir, fname)
        create_ui_mockup_image(out_p, title, sub, badges, metrics, th, tr, chart_type=chart_t)

if __name__ == "__main__":
    generate_all()
