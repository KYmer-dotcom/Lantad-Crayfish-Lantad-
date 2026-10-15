use_cases = [
    {
        "table_num": 3,
        "title": "Authentication, Frictionless Phone Login & Role-Based Access Control",
        "uc_id": "Use Case 1: Authentication, Frictionless Phone Login & Role-Based Access Control",
        "goal": "To allow authorized system entities (Admin / Farm Owner, Delivery Rider, and Commercial Customers / Buyers) to securely authenticate, access role-specific interfaces, enforce permission boundaries, and terminate sessions.",
        "scenarios": [
            {
                "name": "Scenario 1: Successful Admin / Farm Owner Login",
                "actor": "Admin / Farm Owner",
                "pre": "Admin / Farm Owner has an active registered account with an assigned OWNER role.",
                "steps": [
                    "User opens the unified system login page (/login/).",
                    "User enters registered administrative username and password.",
                    "User clicks the 'Sign In' button.",
                    "System validates credentials against the database and redirects the user to the Executive Dashboard (/dashboard/)."
                ],
                "pairs": [
                    ("Opens the unified login page.", "Displays the authentication form with username and password input fields."),
                    ("Enters administrative credentials and clicks 'Sign In'.", "Validates submitted credentials against User accounts and verifies the active OWNER role."),
                    ("Credentials are verified.", "Initializes authenticated session, grants administrative access permissions, and redirects the user to the Executive Dashboard.")
                ]
            },
            {
                "name": "Scenario 2: Successful Delivery Rider Mobile Login",
                "actor": "Delivery Rider",
                "pre": "Delivery Rider has a registered account with an assigned RIDER role.",
                "steps": [
                    "User opens the unified system login page (/login/).",
                    "User enters registered rider credentials.",
                    "User clicks the 'Sign In' button.",
                    "System validates credentials and redirects the user directly to the Grab-style Mobile Rider Delivery Portal (/sales/rider-portal/)."
                ],
                "pairs": [
                    ("Opens the unified login page.", "Displays the authentication form with username and password fields."),
                    ("Enters rider credentials and clicks 'Sign In'.", "Validates credentials against User accounts and confirms active RIDER role."),
                    ("Credentials are verified.", "Initializes rider mobile session state and loads the Rider Portal displaying active duty status, dispatch pool, and active tasks.")
                ]
            },
            {
                "name": "Scenario 3: Frictionless Customer Phone-Based Registration & Login",
                "actor": "Commercial Customers / Buyers",
                "pre": "Customer visits the public e-commerce storefront (/sales/market/) or dedicated customer login (/customer/login/).",
                "steps": [
                    "User clicks an ordering action or sign-in link on the storefront.",
                    "System displays the branded customer welcome modal or page requiring Phone Number and Full Name.",
                    "User enters an 11-digit mobile phone number (e.g., 09673285963) and full name.",
                    "User clicks the 'Continue / Register' button.",
                    "System validates the phone format, automatically creates or retrieves the customer profile without rigid password friction, and initializes an active consumer session."
                ],
                "pairs": [
                    ("Initiates customer sign-in on the storefront.", "Displays welcome modal with farm branding, Phone Number, and Full Name fields."),
                    ("Enters 11-digit phone number and name, then clicks 'Continue'.", "Verifies mobile number format, auto-provisions or retrieves Customer record, and initializes consumer session."),
                    ("Registration completes.", "Displays welcome banner with active shopping cart and direct access to My Orders.")
                ]
            },
            {
                "name": "Scenario 4: Failed Login Attempt & Security Alert",
                "actor": "Admin / Farm Owner, Delivery Rider",
                "pre": "User enters an incorrect password or unregistered username.",
                "steps": [
                    "User opens the unified login page.",
                    "User enters an incorrect username or invalid password.",
                    "User clicks the 'Sign In' button.",
                    "System rejects the authentication attempt and displays a security notification without creating a session."
                ],
                "pairs": [
                    ("Enters incorrect credentials and clicks 'Sign In'.", "Checks credentials, detects credential mismatch, and prevents session creation."),
                    ("Authentication fails.", "Displays error message stating 'Please enter a correct username and password' and keeps login form cleared.")
                ]
            },
            {
                "name": "Scenario 5: Unauthorized Access Boundary Interception & Redirection",
                "actor": "Commercial Customers / Buyers, Delivery Rider",
                "pre": "User is authenticated without administrative access rights.",
                "steps": [
                    "User enters an administrative URL directly into the browser address bar (e.g., /operations/ or /analytics/).",
                    "System role guard and middleware intercept the request.",
                    "System evaluates user role, blocks access to unauthorized farm controls, and redirects the user back to their permitted portal with an alert."
                ],
                "pairs": [
                    ("Inputs administrative URL into browser.", "Role-based access guard evaluates session permissions against the requested endpoint."),
                    ("Unauthorized role detected.", "Denies page access and immediately redirects user back to the public market or rider portal with an access restriction alert.")
                ]
            },
            {
                "name": "Scenario 6: User Profile Session Termination (Logout)",
                "actor": "All System Entities (Admin, Rider, Customer)",
                "pre": "User is actively logged into their respective interface.",
                "steps": [
                    "User clicks the profile badge or 'Logout' option in the navigation bar.",
                    "System terminates the active session, flushes auth tokens, and clears session cookies.",
                    "System redirects the user to the login page or public market catalog."
                ],
                "pairs": [
                    ("Clicks 'Logout' button.", "Flushes session tokens, destroys active cookies, and logs out the user."),
                    ("Session destroyed.", "Redirects browser to the login screen or public market catalog.")
                ]
            }
        ]
    },
    {
        "table_num": 4,
        "title": "Executive Farm Operations & Real-Time Alert Command Center",
        "uc_id": "Use Case 2: Executive Farm Operations & Real-Time Alert Command Center",
        "goal": "To provide the Admin / Farm Owner with a centralized operational command center displaying real-time farm KPIs, sales revenue history, 15-day Azula sanitization alerts, and recent order processing queues.",
        "scenarios": [
            {
                "name": "Scenario 1: Monitor Farm Key Performance Indicators",
                "actor": "Admin / Farm Owner",
                "pre": "Admin / Farm Owner is authenticated and accesses the Dashboard (/dashboard/).",
                "steps": [
                    "User navigates to the Overview Dashboard.",
                    "System displays six (6) real-time metric cards: Active Stocks, Daily Sales, Revenue (30D), Pending Orders, Upcoming Harvests, and Total Products.",
                    "User inspects operational counts across ponds and active product catalog items."
                ],
                "pairs": [
                    ("Opens Executive Dashboard.", "Queries live operational data stores and renders six high-contrast metric cards."),
                    ("Inspects metric values.", "Displays active stocks across active ponds/tanks, daily sales, 30-day revenue figures, pending orders, projected harvests, and active catalog items.")
                ]
            },
            {
                "name": "Scenario 2: Review Sales History and Recent Activity Trends",
                "actor": "Admin / Farm Owner",
                "pre": "Historical sales transactions exist in the system.",
                "steps": [
                    "User inspects the 'Sales History - Gross sales revenue tracking' 10-day spline line chart with 'LAST 10 DAYS' filter.",
                    "User examines the 'Recent Activity' table showing daily dates, order counts, and gross revenue figures.",
                    "System plots revenue trajectory and chronological performance logs."
                ],
                "pairs": [
                    ("Views Sales History section.", "Renders interactive smooth spline chart plotting gross daily revenue over the last 10 days."),
                    ("Reviews Recent Activity records.", "Displays table detailing completed order counts and gross monetary revenue per calendar date.")
                ]
            },
            {
                "name": "Scenario 3: Inspect 15-Day Azula Pond Sanitization Alerts & Key Notices",
                "actor": "Admin / Farm Owner",
                "pre": "Operational schedules require attention or customer orders are confirmed.",
                "steps": [
                    "User views the 'Key Alerts' notification panel and dedicated Command Center (/notifications/).",
                    "User inspects high-priority alert for overdue pond sanitization cycles calculated 15 days post-transfer (e.g., Azula Sector 1 DUE IN 3 DAYS).",
                    "User inspects status notices for confirmed customer orders and harvest windows.",
                    "User clicks 'Execute Sanitization Protocol' or 'Manage' to navigate directly to pond remediation."
                ],
                "pairs": [
                    ("Views Key Alerts panel.", "Scans operational schedules and displays overdue sanitization warnings and resolved order notices."),
                    ("Clicks an alert card.", "Redirects user directly to pond water treatment logging or order fulfillment queue.")
                ]
            },
            {
                "name": "Scenario 4: Manage Recent Orders Processing Queue",
                "actor": "Admin / Farm Owner",
                "pre": "Customer purchase orders are pending in the system.",
                "steps": [
                    "User reviews the 'Recent Orders - Processing queue overview' table at the bottom of the dashboard.",
                    "User verifies order numbers (e.g., SO-20260906-0001), customer names, status badges (CONFIRMED, COMPLETED), and total amounts.",
                    "User clicks 'Manage Portal' button to open the full sales order administration module (/sales/orders/)."
                ],
                "pairs": [
                    ("Views Recent Orders table.", "Displays recent customer orders with customer names, fulfillment status, and order values."),
                    ("Clicks 'Manage Portal' button.", "Redirects to the full Orders & Customer Purchases management screen (/sales/orders/).")
                ]
            }
        ]
    },
    {
        "table_num": 5,
        "title": "Commercial Product Inventory and Dual Pricing Management",
        "uc_id": "Use Case 3: Commercial Product Inventory and Dual Pricing Management",
        "goal": "To allow the Admin / Farm Owner to configure commercial product listings, establish piece and kilogram pricing, maintain piece-per-kilogram density ratios, and monitor aggregate inventory volumes.",
        "scenarios": [
            {
                "name": "Scenario 1: Monitor Product Inventory Overview and Stock Volumes",
                "actor": "Admin / Farm Owner",
                "pre": "Admin / Farm Owner navigates to Stock Monitoring -> Product Inventory (/products/).",
                "steps": [
                    "User reviews inventory overview cards: Available Stocks (products recorded), Active Batches (active operations), and Total Quantity (total stock across products).",
                    "User reviews interactive product cards and searchable inventory record table with pagination entries."
                ],
                "pairs": [
                    ("Navigates to Product Inventory page.", "Calculates aggregate stock across all species and batches, rendering three summary metric cards."),
                    ("Inspects catalog items.", "Displays individual product cards with dual pricing and searchable inventory table records.")
                ]
            },
            {
                "name": "Scenario 2: Configure New Market Product and Dual Pricing Ratios",
                "actor": "Admin / Farm Owner",
                "pre": "Admin / Farm Owner clicks '+ Add product +' button.",
                "steps": [
                    "User opens 'Create Product' modal dialog.",
                    "User enters Product Name (e.g., Live Tilapia, Crawfish), Price/pc, Price/kg, Pcs / KG ratio, Total Stock, and Description.",
                    "User selects Accent Color swatch and Product Icon.",
                    "User clicks 'Create Product' button.",
                    "System validates data, establishes the product catalog entry, and renders the new product card across admin and storefront."
                ],
                "pairs": [
                    ("Clicks '+ Add product +'.", "Displays Create Product modal with input fields, pricing options, color swatches, and icon picker."),
                    ("Fills product details and clicks 'Create Product'.", "Validates required fields, creates the Product record, and appends the new card to the inventory catalog."),
                    ("Configuration completes.", "Closes modal and displays the newly registered product card on the admin and storefront catalogs.")
                ]
            },
            {
                "name": "Scenario 3: Modify Commercial Pricing and Stock Parameters",
                "actor": "Admin / Farm Owner",
                "pre": "Product exists in the catalog.",
                "steps": [
                    "User clicks edit icon on an existing product card (e.g., Crawfish).",
                    "System opens 'Edit Product' modal pre-populated with current values.",
                    "User modifies Price/pc, Price/kg, Pcs / KG ratio, or Total Stock.",
                    "User clicks 'Save Changes' button.",
                    "System updates product properties and synchronizes pricing across customer storefront in real time."
                ],
                "pairs": [
                    ("Clicks edit icon on product card.", "Populates Edit Product modal with current pricing, stock counts, and description."),
                    ("Updates values and clicks 'Save Changes'.", "Updates Product record and synchronizes new pricing across admin inventory and customer market interfaces.")
                ]
            }
        ]
    },
    {
        "table_num": 6,
        "title": "Aquaculture Farm Operations - Ponds, Cabin & Azula Cultivation",
        "uc_id": "Use Case 4: Aquaculture Farm Operations - Ponds, Cabin & Azula Cultivation",
        "goal": "To allow the Admin / Farm Owner to organize physical aquaculture facilities across outdoor ponds, superworm cabin rack slots, and indoor Azula tanks, allocate breeding and juvenile stocks, and log daily nutritional feedings.",
        "scenarios": [
            {
                "name": "Scenario 1: Monitor Farm Rearing Facility Capacities",
                "actor": "Admin / Farm Owner",
                "pre": "Admin / Farm Owner accesses Operations module (/operations/?type=pond).",
                "steps": [
                    "User inspects facility capacity cards: PONDS (outdoor rearing ponds), CABIN (superworm cabin boxes), and AZULA (Azula indoor tanks).",
                    "User toggles between Pond, Cabin, and Azula subpages."
                ],
                "pairs": [
                    ("Opens Operations module.", "Displays facility overview cards detailing total operational units across sectors."),
                    ("Selects facility type tabs.", "Switches display smoothly between outdoor pond layout, indoor cabin rack shelves, and Azula tanks.")
                ]
            },
            {
                "name": "Scenario 2: Stocking and Allocating Juvenile Batches",
                "actor": "Admin / Farm Owner",
                "pre": "User opens Add Pond modal.",
                "steps": [
                    "User selects Category (Main Pond, Breeding Pond), inputs Name (e.g., POND 1), selects Product, enters Quantity, and selects Date Transferred.",
                    "User clicks 'Save Record' button.",
                    "System validates allocation, initializes pond card with Active status, and updates facility counts."
                ],
                "pairs": [
                    ("Enters pond stocking parameters and clicks Save Record.", "Validates inputs, stores Pond operational record, and appends card to designated pond sector."),
                    ("Allocation completes.", "Closes modal and updates pond grid with new batch details.")
                ]
            },
            {
                "name": "Scenario 3: Monitor Darkling Beetle Density and Shelf Container Occupancy",
                "actor": "Admin / Farm Owner",
                "pre": "User navigates to Operations -> Cabin (/operations/?type=cabin).",
                "steps": [
                    "User inspects rack shelf groupings: Left Shelf, Right Shelf, and Back Shelf.",
                    "User reviews container slots with Unused/Active badges and Darkling Beetle densities.",
                    "User clicks edit icon to update beetle density or production date."
                ],
                "pairs": [
                    ("Opens Cabin subpage.", "Renders coordinate-based rack shelf grid with container slots, unused badges, and beetle counts."),
                    ("Updates beetle count on container slot.", "Saves updated reproductive beetle density for superworm lifecycle optimization.")
                ]
            },
            {
                "name": "Scenario 4: Log Daily Aquaculture Nutritional Feeding Rations",
                "actor": "Admin / Farm Owner",
                "pre": "User clicks 'Operation' button on Main Pond section.",
                "steps": [
                    "System slides open the 'Operations Data - Detailed view of operational metrics' right side panel.",
                    "User views Main Pond feeding checklist (POND 1 to POND 10 with current quantities).",
                    "User checks active pond checkboxes.",
                    "User selects feed formulation from dropdown (Integra 1000, Integra 2000, Integra 1, PO2, PO1).",
                    "User clicks 'Record' button.",
                    "System logs feeding event and automatically deducts feed inventory."
                ],
                "pairs": [
                    ("Clicks 'Operation' button.", "Slides out Operations Data panel with pond checklist and feed dropdowns."),
                    ("Selects ponds, chooses feed formulation, and clicks 'Record'.", "Logs feeding record with timestamp, marks ponds as fed, and automatically deducts feed stock.")
                ]
            }
        ]
    },
    {
        "table_num": 7,
        "title": "Commercial Customer Browsing, Cart & Multi-Option Checkout",
        "uc_id": "Use Case 5: Commercial Customer Browsing, Cart & Multi-Option Checkout",
        "goal": "To allow Commercial Customers / Buyers to browse live aquaculture products, toggle fulfillment methods (Pickup vs Delivery), select per-piece or kilogram pricing, configure delivery addresses, pin GPS locations, and place orders.",
        "scenarios": [
            {
                "name": "Scenario 1: Interactive Product Catalog Showcase Browsing",
                "actor": "Commercial Customers / Buyers",
                "pre": "Customer visits the public storefront (/sales/market/).",
                "steps": [
                    "User views central circular showcase displaying high-resolution photography of fresh aquaculture produce (Azula, Crayfish, Superworm).",
                    "User clicks carousel navigation arrows to cycle through available products.",
                    "User inspects 'Available Products' sidebar catalog showing current price ranges."
                ],
                "pairs": [
                    ("Opens Market storefront page.", "Displays dynamic storefront with central circular product showcase, carousel dots, and product catalog menu."),
                    ("Clicks next product arrow.", "Transitions product photo, product title, description, and pricing controls smoothly.")
                ]
            },
            {
                "name": "Scenario 2: Select Delivery Method and Dual Pricing Ratios",
                "actor": "Commercial Customers / Buyers",
                "pre": "Customer selects a product (e.g., Crawfish).",
                "steps": [
                    "User toggles Delivery Method between 'PICKUP' and 'DELIVERY'.",
                    "User toggles Pricing Option between 'PER PIECE (PC)' (₱71/pc) and 'BY KG (KG)' (₱2500/kg).",
                    "User adjusts quantity counter (e.g., 1 pc = ₱71 or 3 kg = ₱213).",
                    "User clicks 'ADD TO CART +' button."
                ],
                "pairs": [
                    ("Toggles Pickup/Delivery and Per Piece/By KG.", "Dynamically updates unit price and calculates instant total amount in real time."),
                    ("Clicks 'ADD TO CART +'.", "Adds selected item, fulfillment method, and pricing option to shopping cart and increments cart counter badge.")
                ]
            },
            {
                "name": "Scenario 3: Submit Order with Establishment On-Site Pickup",
                "actor": "Commercial Customers / Buyers",
                "pre": "Customer selected 'PICKUP' fulfillment method during checkout.",
                "steps": [
                    "User views Step 2: 'PICKUP LOCATION - Please pick up your order at our main establishment below.'",
                    "User inspects establishment address: 'Silay City, Negros Occidental, Philippines (Silay Superworm & Crayfish Farm)'.",
                    "User views interactive satellite map showing exact farm pin, farm photo, and GPS coordinates (10.81519, 122.96197 at Brgy. Lantad).",
                    "User clicks 'PROCEED TO PAYMENT ->' button."
                ],
                "pairs": [
                    ("Advances to Pickup location step.", "Displays official farm establishment address, satellite map, farm photo callout, and pickup instructions."),
                    ("Clicks 'PROCEED TO PAYMENT ->'.", "Validates pickup selection and advances user to payment options step.")
                ]
            },
            {
                "name": "Scenario 4: Submit Order with Doorstep GPS Delivery Pinning",
                "actor": "Commercial Customers / Buyers",
                "pre": "Customer selected 'DELIVERY' fulfillment method.",
                "steps": [
                    "User views Step 2: 'DELIVERY ADDRESS - Please enter your complete delivery address below.'",
                    "User selects Province (Negros Occidental), City (Silay City), Barangay (Bagtic), and Street.",
                    "User enters Landmark / House Number.",
                    "User drags interactive map pin or clicks 'USE CURRENT GPS' to set precise drop-off coordinates.",
                    "User clicks 'PROCEED TO PAYMENT ->' button."
                ],
                "pairs": [
                    ("Inputs delivery address and adjusts map pin.", "Captures structured address fields and precise GPS latitude/longitude coordinates."),
                    ("Clicks 'PROCEED TO PAYMENT ->'.", "Validates coverage area and advances user to payment options.")
                ]
            }
        ]
    },
    {
        "table_num": 8,
        "title": "Digital Payment Settlement, PayMongo Gateway & Official Invoice Generation",
        "uc_id": "Use Case 6: Digital Payment Settlement, PayMongo Gateway & Official Invoice Generation",
        "goal": "To support payment processing via Handover Cash and Automated GCash Online via PayMongo Gateway, generate official sales invoices, and allow the Admin to configure receiving payment destinations.",
        "scenarios": [
            {
                "name": "Scenario 1: Confirm Handover Cash Order (Cash on Delivery / Pickup)",
                "actor": "Commercial Customers / Buyers",
                "pre": "Customer arrives at Step 3: 'CHOOSE PAYMENT METHOD'.",
                "steps": [
                    "User selects 'CASH ON DELIVERY' or 'CASH' (for pickup).",
                    "User verifies Price Details: Item Total, Delivery Charges, and Total Amount.",
                    "User clicks 'PLACE CASH ORDER ->' button.",
                    "System confirms order, sets payment status to UNPAID, order status to CONFIRMED, and generates official sales receipt."
                ],
                "pairs": [
                    ("Selects Cash payment and clicks 'PLACE CASH ORDER ->'.", "Creates SalesOrder record with payment_method='COD', generates order number (e.g., SO-20260906-0001), and locks pending stock."),
                    ("Order placed.", "Redirects user to 'My Orders' page with UNPAID and CONFIRMED status badges and 'PRINT RECEIPT' button.")
                ]
            },
            {
                "name": "Scenario 2: Authorize Automated GCash Online Payment via PayMongo Gateway",
                "actor": "Commercial Customers / Buyers",
                "pre": "Customer arrives at Step 3: 'CHOOSE PAYMENT METHOD'.",
                "steps": [
                    "User selects 'GCASH ONLINE (PAYMONGO GATEWAY)' option.",
                    "User clicks 'PAY WITH GCASH ->' button.",
                    "System redirects to the secure PayMongo hosted gateway showing order summary (e.g., Crawfish 1.00 pcs, ₱71.00).",
                    "User selects E-Wallets (GCash), enters customer name, email, and mobile phone number (+63 09231333432), and completes SMS OTP verification.",
                    "System confirms payment with 'GCash Payment Received!' notification, logs transaction Payment ID (e.g., pay_filOffryPkdV3KUQTGPpu4T3), auto-marks order as PAID, and returns to merchant."
                ],
                "pairs": [
                    ("Selects GCash Online and clicks 'PAY WITH GCASH ->'.", "Initiates PayMongo checkout session and transitions browser to the hosted payment interface."),
                    ("Submits contact details and verifies GCash SMS OTP.", "Authorizes payment through GCash gateway, debits wallet balance, and creates verified transaction ID."),
                    ("Payment confirmed.", "Displays 'GCash Payment Received!', updates order payment status to PAID, and redirects customer to My Orders.")
                ]
            },
            {
                "name": "Scenario 3: Inspect Customer Order History and Print Official Receipt",
                "actor": "Commercial Customers / Buyers",
                "pre": "Customer opens 'MY ORDERS' page (/sales/market/orders/).",
                "steps": [
                    "User reviews order cards showing order number (#SO-20260906-0002), customer details, delivery address, status (CONFIRMED), and payment status (PAID).",
                    "User clicks 'PRINT RECEIPT' button.",
                    "System opens 'OFFICIAL RECEIPT' modal displaying business header, invoice number, customer details, delivery address, itemized charges, and payment method.",
                    "User clicks 'PRINT / SAVE PDF' to trigger native print dialog."
                ],
                "pairs": [
                    ("Views My Orders page.", "Displays active and completed customer purchases with fulfillment and payment status badges."),
                    ("Clicks 'PRINT RECEIPT'.", "Renders official sales invoice modal with 'PRINT / SAVE PDF' action."),
                    ("Clicks 'PRINT / SAVE PDF'.", "Invokes browser window.print() formatted for official paper receipt printing.")
                ]
            },
            {
                "name": "Scenario 4: Configure Receiving Payment Gateways & Administrative Settings",
                "actor": "Admin / Farm Owner",
                "pre": "Admin navigates to Orders administration (/sales/orders/) and clicks 'PAYMENT OPTION' button.",
                "steps": [
                    "System slides open the 'PAYMENT SETTINGS - Configure receiving accounts & destination' side panel.",
                    "Admin configures GCash Destination receiving mobile number (e.g., 09171234567), account name ('SILAY SUPERWORM & CRAYFISH'), and optional custom QR code image upload.",
                    "Admin toggles Cash on Delivery (COD) availability switch.",
                    "Admin inputs PayMongo Live Gateway credentials (Secret Key and Public Key).",
                    "Admin clicks 'SAVE CONFIGURATION' button to persist settings."
                ],
                "pairs": [
                    ("Clicks 'PAYMENT OPTION' button.", "Slides out Payment Settings configuration panel with GCash, COD, and PayMongo gateway controls."),
                    ("Updates credentials and clicks 'SAVE CONFIGURATION'.", "Validates and saves payment parameters, instantly synchronizing gateway keys across the customer checkout portal.")
                ]
            }
        ]
    },
    {
        "table_num": 9,
        "title": "Delivery Fleet, Dispatch Pool & Driver Mobile Operations with Proof of Delivery",
        "uc_id": "Use Case 7: Delivery Fleet, Dispatch Pool & Driver Mobile Operations with Proof of Delivery",
        "goal": "To allow the Delivery Rider to manage active duty status, claim available orders from the dispatch pool, navigate routes via integrated map telemetry, capture photo Proof of Delivery (POD), and update real-time fulfillment telemetry.",
        "scenarios": [
            {
                "name": "Scenario 1: Toggle Rider Active Duty Status (Online / Off Duty)",
                "actor": "Delivery Rider",
                "pre": "Delivery Rider is logged into the Mobile Driver Portal (/sales/rider-portal/).",
                "steps": [
                    "User reviews profile header card showing status badge (AVAILABLE / OFF DUTY), vehicle type, plate number, and phone.",
                    "User taps 'Go Online' or 'Go Off Duty' button.",
                    "System updates driver status in the registry and informs admin dispatch."
                ],
                "pairs": [
                    ("Opens mobile portal.", "Displays courier details, vehicle plate number, and status toggle button."),
                    ("Taps duty toggle button.", "Updates rider status in database and toggles visual indicator between online green ping and off-duty stone.")
                ]
            },
            {
                "name": "Scenario 2: Browse and Claim Orders from Open Dispatch Pool",
                "actor": "Delivery Rider",
                "pre": "Customer delivery orders are scheduled and awaiting courier assignment.",
                "steps": [
                    "User taps 'AVAILABLE ORDERS' tab in the mobile portal.",
                    "User reviews open shipments waiting at the farm depot with order ID, customer name, product volume (e.g., Crawfish 3.00 kg), pickup location (Brgy. Lantad), destination address (Bacolod City), and payment notes.",
                    "User taps '✓ ACCEPT & CLAIM ORDER' button.",
                    "System assigns the shipment to the rider, removes it from the open pool, and moves it to 'MY ACTIVE TASKS'."
                ],
                "pairs": [
                    ("Views Available Orders pool.", "Renders unassigned shipment cards with pickup location, customer address, product volume, and payment notes."),
                    ("Clicks '✓ ACCEPT & CLAIM ORDER'.", "Assigns delivery to rider account, updates dispatch registry, and moves task to active queue.")
                ]
            },
            {
                "name": "Scenario 3: Execute Road Route Navigation & Departure (In Transit)",
                "actor": "Delivery Rider",
                "pre": "Rider has claimed an active delivery task.",
                "steps": [
                    "User taps 'MY ACTIVE TASKS' tab.",
                    "User reviews order card and inspects integrated turn-by-turn road route map connecting Farm Depot to Customer Destination.",
                    "User reviews order items and packaging details.",
                    "User clicks '⚡ START DELIVERY (IN TRANSIT)' button.",
                    "System updates shipment status to IN TRANSIT, notifying Admin and Customer live tracking in real time."
                ],
                "pairs": [
                    ("Views active task.", "Displays interactive turn-by-turn road route map, pickup and destination addresses, and product packaging specifications."),
                    ("Clicks '⚡ START DELIVERY (IN TRANSIT)'.", "Updates delivery status to IN TRANSIT, activates live telemetry, and reveals 'COMPLETE & MARK AS DELIVERED' button.")
                ]
            },
            {
                "name": "Scenario 4: Complete Verified Drop-Off with Photo Proof of Delivery (POD)",
                "actor": "Delivery Rider",
                "pre": "Shipment is in transit and rider arrives at customer destination.",
                "steps": [
                    "User delivers aquaculture items to customer (and collects cash if Cash on Delivery).",
                    "User clicks '✓ COMPLETE & MARK AS DELIVERED' button.",
                    "System opens the 'Confirm Drop-off' modal displaying order details.",
                    "User clicks 'Take Photo / Upload Proof' to capture package drop-off photo and clicks '✓ CONFIRM'.",
                    "System uploads photo proof, marks delivery as DELIVERED, updates payment to PAID (if COD), logs completion timestamp, and automatically deducts biomass stock from farm inventory."
                ],
                "pairs": [
                    ("Clicks '✓ COMPLETE & MARK AS DELIVERED'.", "Opens 'Confirm Drop-off' modal requiring photo Proof of Delivery (POD)."),
                    ("Captures photo proof and clicks '✓ CONFIRM'.", "Processes image proof, sets status to DELIVERED, marks payment as PAID, deducts sold biomass weight from inventory, and records completion timestamp.")
                ]
            },
            {
                "name": "Scenario 5: Mobile-Responsive Role-Segregated Notifications Center",
                "actor": "Delivery Rider",
                "pre": "Delivery Rider opens System Notifications (/notifications/).",
                "steps": [
                    "System detects RIDER role and renders the dedicated Driver Dispatch Center.",
                    "User reviews 2x2 responsive stat grid: Available, Active, Delivered, and Rider Profile.",
                    "User reviews live driver notification feed with direct 'CLAIM IN DRIVER PORTAL ->' action links to claim orders or update status without seeing administrative farm alerts."
                ],
                "pairs": [
                    ("Opens Notifications page.", "Detects rider role and renders clean mobile-optimized 2x2 driver dispatch cards and courier feed."),
                    ("Clicks dispatch action link.", "Redirects courier seamlessly to the relevant order in the Driver Portal.")
                ]
            }
        ]
    },
    {
        "table_num": 10,
        "title": "Real-Time GPS Order Tracking & Live Telemetry",
        "uc_id": "Use Case 8: Real-Time GPS Order Tracking & Live Telemetry",
        "goal": "To provide Admin and Customers with live GPS telemetry, road route mapping, courier vehicle details, and 4-step milestone progress tracking.",
        "scenarios": [
            {
                "name": "Scenario 1: Monitor 4-Step Milestone Progress Tracker",
                "actor": "Admin / Farm Owner, Commercial Customers / Buyers",
                "pre": "Order has been dispatched (/sales/deliveries/track/).",
                "steps": [
                    "User opens Live Order Tracking page or searches Order # in shipments queue.",
                    "User reviews order header card showing customer, item, total, and status badges.",
                    "User inspects 4-step progress tracker: Step 1 (Order Placed) -> Step 2 (Approved & Dispatched) -> Step 3 (Out for Delivery - Courier Assigned) -> Step 4 (Delivered).",
                    "System highlights active milestone in real time."
                ],
                "pairs": [
                    ("Opens Track Order page.", "Queries live shipment telemetry and renders 4-step visual milestone progress bar with completion checkmarks."),
                    ("Inspects status timeline.", "Displays active fulfillment phase and estimated delivery schedule.")
                ]
            },
            {
                "name": "Scenario 2: Inspect Road Route GPS Map and Dispatch Telemetry",
                "actor": "Admin / Farm Owner, Commercial Customers / Buyers",
                "pre": "Order tracking page is active.",
                "steps": [
                    "User inspects interactive road map of Silay City visualizing coastal and urban geography.",
                    "User reviews origin pin ('AquaFarm Depot'), purple turn-by-turn road route line, and destination drop-off pin.",
                    "User utilizes 'Fit Route' control and inspects 'SHIPMENT DISPATCH DETAILS' panel showing Destination, Assigned Courier, Vehicle Details, and Approved By authority.",
                    "User accesses top-right shortcut to 'Delivery Registry'."
                ],
                "pairs": [
                    ("Views GPS tracking map.", "Renders turn-by-turn road route overlay connecting farm depot to customer destination pin."),
                    ("Inspects dispatch panel.", "Displays courier vehicle details, approving authority, and quick navigation to Delivery Registry.")
                ]
            }
        ]
    },
    {
        "table_num": 11,
        "title": "Predictive Demand Analytics & Machine Learning Forecasting",
        "uc_id": "Use Case 9: Predictive Demand Analytics & Machine Learning Forecasting",
        "goal": "To provide the Admin / Farm Owner with predictive demand analytics, 7-day machine learning sales forecasting, linear regression trends, regional market distributions, and AI customer purchase recommendations.",
        "scenarios": [
            {
                "name": "Scenario 1: Generate 7-Day Machine Learning Sales Forecast",
                "actor": "Admin / Farm Owner",
                "pre": "Historical sales datasets are loaded into predictive engine (/analytics/).",
                "steps": [
                    "User inspects 'SALES FORECAST ANALYSIS' graph showing actual sales trajectory followed by purple dotted projection line.",
                    "User notes 'Trend: Decreasing/Increasing' indicator badge.",
                    "User clicks chart to open '7-DAY SALES FORECAST' modal.",
                    "User reviews exact predicted revenue figures across upcoming days.",
                    "System provides mathematical demand forecast to guide harvesting batches."
                ],
                "pairs": [
                    ("Opens Analytics Dashboard.", "Renders 14-day sales performance, product proportions, and 7-day sales forecast graph."),
                    ("Clicks Sales Forecast chart.", "Renders 7-Day Sales Forecast modal displaying daily projected revenues generated by regression models.")
                ]
            },
            {
                "name": "Scenario 2: Analyze Regional Market Demand & Product Proportions",
                "actor": "Admin / Farm Owner",
                "pre": "Customer orders originate from various localities.",
                "steps": [
                    "User inspects 'TOP LOCATIONS' bar chart comparing order volume across Silay City, Talisay City, and Bacolod City.",
                    "User inspects 'TOP PRODUCTS' donut chart showing sales proportions between Breeder Crayfish, Azula, and Superworms.",
                    "User reviews AI-driven customer purchase recommendations."
                ],
                "pairs": [
                    ("Views Top Locations and Products charts.", "Renders interactive geographic bar charts and product distribution donut charts."),
                    ("Reviews AI recommendations.", "Executes recommendation heuristics and renders prioritized inventory restocking alerts.")
                ]
            }
        ]
    },
    {
        "table_num": 12,
        "title": "Executive Printable Reports & Three-Tiered Audit Documentation",
        "uc_id": "Use Case 10: Executive Printable Reports & Three-Tiered Audit Documentation",
        "goal": "To allow the Admin / Farm Owner to filter, preview, and print formal operational reports, three-tiered audit logs (Product, Activity, Input), sales ledgers, feeding logs, and official customer receipt slips.",
        "scenarios": [
            {
                "name": "Scenario 1: Dedicated Multi-Tab Logistics Audit Logs Inspection",
                "actor": "Admin / Farm Owner",
                "pre": "Admin / Farm Owner navigates to Delivery Logs & Audit (/sales/deliveries/logs/).",
                "steps": [
                    "User reviews 4 logistics summary KPI cards: Completed & Delivered, Total Dispatches, Delivered Volume (kg), and Fulfilled Revenue.",
                    "User navigates across three dedicated audit tabs: (1) PRODUCT LOGS, (2) ACTIVITY LOGS, and (3) INPUT LOGS.",
                    "User inspects Product Logs for order details, customer drop-off, approver, courier, sign-off status, and 'View Receipt' button.",
                    "User inspects Activity Logs for operational events (e.g., DISPATCH APPROVED) and Input Logs with Added/Deleted record filter chips."
                ],
                "pairs": [
                    ("Navigates to Delivery Logs & Audit.", "Displays summary KPI cards, global search filter, and three audit sub-tabs."),
                    ("Toggles audit tabs.", "Renders categorized log records with user badges, timestamped mutations, and receipt links.")
                ]
            },
            {
                "name": "Scenario 2: Generate Formal Categorized Printable Reports & Logs",
                "actor": "Admin / Farm Owner",
                "pre": "User navigates to Printable Reports (/analytics/reports/).",
                "steps": [
                    "User sets Date Range (From/To dates).",
                    "User selects Report Type from dropdown: Comprehensive Summary, Sales Only, Operations Only, Receipts Only, Product Delivery Logs, Activity Audit Logs, or Input Modification Logs.",
                    "User selects Output Format (Printable PDF) and clicks 'Generate Report'.",
                    "System renders live structured table preview with logistics audit metrics and invokes formal print layout."
                ],
                "pairs": [
                    ("Selects parameters and clicks 'Generate Report'.", "Filters records by date range and selected log type, rendering structured table preview."),
                    ("Clicks print execution.", "Launches clean browser print dialog formatted for official paper documentation.")
                ]
            },
            {
                "name": "Scenario 3: Generate Official Customer Billing Slip with Signature Lines",
                "actor": "Admin / Farm Owner",
                "pre": "User selects 'Receipts Only' report type.",
                "steps": [
                    "System renders 'RECEIPT SLIPS' preview for customer orders.",
                    "User reviews Bill To details, itemized charges, subtotal, and contact info.",
                    "User clicks 'Print Report' to view official invoice print layout complete with 'Prepared By: admin', 'Authorized Signature', and 'Date' signature lines."
                ],
                "pairs": [
                    ("Previews Receipt Slips.", "Renders commercial invoice layout ready for formal customer billing."),
                    ("Launches print preview.", "Formats 8.5x11 printable slip with signature lines and business header.")
                ]
            }
        ]
    }
]
