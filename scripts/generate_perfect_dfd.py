import os
import xml.etree.ElementTree as ET
import xml.dom.minidom
from PIL import Image, ImageDraw, ImageFont

def build_and_render_perfect_dfd():
    # =========================================================================
    # 1. DEFINE EXACT GEOMETRY & COORDINATES (Canvas: 1250 x 1200)
    # =========================================================================
    
    # Left Entities (X=140 to 250, distinct Y positions)
    entities = {
        'Customer': {'id': 'entity_customer', 'label': 'Customer', 'x': 140, 'y': 90,  'w': 100, 'h': 55},
        'Rider':    {'id': 'entity_rider',    'label': 'Rider',    'x': 140, 'y': 480, 'w': 100, 'h': 45},
        'Manager':  {'id': 'entity_manager',  'label': 'Manager',  'x': 90,  'y': 780, 'w': 100, 'h': 45},
    }

    # Center Processes (X=480, W=110)
    processes = {
        '1.0': {'id': 'proc_1', 'num': '1.0', 'name': 'Browse and select',      'lines': ['Browse', 'and select'],        'x': 480, 'y': 25,   'w': 105, 'h': 65},
        '2.0': {'id': 'proc_2', 'num': '2.0', 'name': 'Order management',       'lines': ['Order', 'management'],         'x': 480, 'y': 160,  'w': 105, 'h': 65},
        '3.0': {'id': 'proc_3', 'num': '3.0', 'name': 'Payment & Set location', 'lines': ['Payment &', 'Set location'],   'x': 480, 'y': 310,  'w': 115, 'h': 65},
        '4.0': {'id': 'proc_4', 'num': '4.0', 'name': 'Delivery dispatch',      'lines': ['Delivery', 'dispatch'],        'x': 480, 'y': 470,  'w': 105, 'h': 65},
        '5.0': {'id': 'proc_5', 'num': '5.0', 'name': 'Management',             'lines': ['Management'],                  'x': 480, 'y': 625,  'w': 105, 'h': 60},
        '6.0': {'id': 'proc_6', 'num': '6.0', 'name': 'Report and Monitoring',  'lines': ['Report and', 'Monitoring'],    'x': 480, 'y': 770,  'w': 110, 'h': 68},
        '7.0': {'id': 'proc_7', 'num': '7.0', 'name': 'Predictive Analytics',   'lines': ['Predictive', 'Analytics'],     'x': 480, 'y': 920,  'w': 110, 'h': 65},
    }

    # Right Data Stores (X=680, W=110, H=32, uniformly spaced so NO overlap)
    stores = {
        'D1': {'id': 'store_d1', 'num': 'D1', 'name': 'Order',      'x': 680, 'y': 80,  'w': 105, 'h': 32},
        'D2': {'id': 'store_d2', 'num': 'D2', 'name': 'Customer',   'x': 680, 'y': 160, 'w': 115, 'h': 32},
        'D3': {'id': 'store_d3', 'num': 'D3', 'name': 'Production', 'x': 680, 'y': 240, 'w': 120, 'h': 32},
        'D4': {'id': 'store_d4', 'num': 'D4', 'name': 'Expense',    'x': 680, 'y': 315, 'w': 110, 'h': 32},
        'D5': {'id': 'store_d5', 'num': 'D5', 'name': 'Payment',    'x': 680, 'y': 385, 'w': 110, 'h': 32},
        'D6': {'id': 'store_d6', 'num': 'D6', 'name': 'Delivery',   'x': 680, 'y': 510, 'w': 110, 'h': 32},
    }

    # RIGHT-HAND VERTICAL TRACKS (all > store max X=800):
    # TR_D6_5   = 820  (D6 -> 5.0)
    # TR_D6_6   = 840  (D6 -> 6.0)
    # TR_D5_5   = 860  (D5 -> 5.0)
    # TR_D4_5   = 880  (D4 -> 5.0)
    # TR_D3_5   = 900  (D3 -> 5.0)
    # TR_D3_1   = 920  (D3 -> 1.0)
    # TR_D3_6   = 940  (D3 -> 6.0)
    # TR_D1_1   = 960  (D1 -> 1.0)
    # TR_D1_3   = 980  (3.0 -> D1)
    # TR_D1_4   = 1000 (4.0 -> D1)
    # TR_D3_4   = 1020 (4.0 -> D3)
    # TR_6_MGR  = 1050 (6.0 -> Manager)
    # TR_7_MGR  = 1075 (7.0 -> Manager)

    # LEFT-HAND VERTICAL TRACKS (all < Entity Customer X=140):
    # TL_4_CUST1 = 20  (4.0 -> Customer Real-time tracking)
    # TL_4_CUST2 = 40  (4.0 -> Customer Delivery status)
    # TL_MGR_2   = 60  (Manager -> 2.0 Order approval)
    # TL_MGR_5A  = 75  (Manager -> 5.0 Expense entries)
    # TL_3_CUSTB = 100 (3.0 -> Customer Payment verification)
    # TL_3_CUSTA = 115 (3.0 -> Customer Payment status)
    # TL_CUST_3B = 125 (Customer -> 3.0 Payment details)

    edges = [
        # ==================== 1.0 FLOWS ====================
        # Customer -> 1.0 Selected Product
        ('e_cust_1', 'entity_customer', 'proc_1', 'Selected Product',
         [(190, 90), (190, 40), (480, 40)], (295, 29)),
        
        # 1.0 -> Customer Product list
        ('e_1_cust', 'proc_1', 'entity_customer', 'Product list',
         [(480, 60), (220, 60), (220, 90)], (315, 49)),
        
        # 1.0 -> 2.0 Select product
        ('e_1_2', 'proc_1', 'proc_2', 'Select product',
         [(532, 90), (532, 160)], (538, 120)),
        
        # D3 -> 1.0 Available stock (Exits D3 right -> Track 920 -> 1.0 right)
        ('e_d3_1', 'store_d3', 'proc_1', 'Available stock',
         [(800, 250), (920, 250), (920, 40), (585, 40)], (760, 29)),
        
        # D1 -> 1.0 Order info (Exits D1 right -> Track 960 -> 1.0 right)
        ('e_d1_1', 'store_d1', 'proc_1', 'Order info',
         [(785, 90), (960, 90), (960, 60), (585, 60)], (760, 49)),
        
        # 1.0 -> D1 Order info (Direct top branch into D1 top/left)
        ('e_1_d1', 'proc_1', 'store_d1', 'Order info',
         [(585, 75), (650, 75), (650, 90), (680, 90)], (605, 64)),

        # ==================== 2.0 FLOWS ====================
        # Customer -> 2.0 Order request/details
        ('e_cust_2', 'entity_customer', 'proc_2', 'Order request/details',
         [(240, 120), (330, 120), (330, 175), (480, 175)], (340, 164)),
        
        # 2.0 -> Customer Order confirmation
        ('e_2_cust', 'proc_2', 'entity_customer', 'Order confirmation',
         [(480, 195), (230, 195), (230, 145)], (305, 184)),
        
        # Manager -> 2.0 Order approval (From Manager top -> TL_MGR_2(60) -> 2.0 left)
        ('e_mgr_2', 'entity_manager', 'proc_2', 'Order approval',
         [(110, 780), (60, 780), (60, 215), (480, 215)], (240, 204)),
        
        # 2.0 -> D1 Order records (2.0 right -> up to D1)
        ('e_2_d1', 'proc_2', 'store_d1', 'Order records',
         [(585, 175), (640, 175), (640, 105), (680, 105)], (595, 135)),
        
        # D2 -> 2.0 Customer/order info (D2 left -> 2.0 right)
        ('e_d2_2', 'store_d2', 'proc_2', 'Customer/order info',
         [(680, 170), (585, 170)], (595, 158)),
        
        # 2.0 -> D2 Customer/order info (2.0 right -> D2 left)
        ('e_2_d2', 'proc_2', 'store_d2', '',
         [(585, 185), (680, 185)], (0, 0)),
        
        # 2.0 -> 3.0 Order info
        ('e_2_3', 'proc_2', 'proc_3', 'Order info',
         [(537, 225), (537, 310)], (545, 260)),

        # ==================== 3.0 FLOWS ====================
        # Customer -> 3.0 Delivery/pickup address
        ('e_cust_3a', 'entity_customer', 'proc_3', 'Delivery/pickup address',
         [(180, 145), (180, 320), (480, 320)], (275, 309)),
        
        # Customer -> 3.0 Payment details
        ('e_cust_3b', 'entity_customer', 'proc_3', 'Payment details',
         [(165, 145), (165, 335), (480, 335)], (295, 324)),
        
        # 3.0 -> Customer Payment status
        ('e_3_custa', 'proc_3', 'entity_customer', 'Payment status',
         [(480, 350), (130, 350), (130, 145)], (295, 339)),
        
        # 3.0 -> Customer Payment verification (GCash/COD)
        ('e_3_custb', 'proc_3', 'entity_customer', 'Payment verification (GCash/COD)',
         [(480, 365), (105, 365), (105, 145)], (240, 354)),
        
        # Rider -> 3.0 Cash collected (COD payment)
        ('e_rider_3', 'entity_rider', 'proc_3', 'Cash collected (COD payment)',
         [(190, 480), (190, 385), (480, 385)], (260, 374)),

        # 3.0 -> D5 Payment data (3.0 right -> D5 left)
        ('e_3_d5', 'proc_3', 'store_d5', 'Payment data',
         [(595, 330), (640, 330), (640, 395), (680, 395)], (610, 345)),
        
        # D5 -> 3.0 Payment data
        ('e_d5_3', 'store_d5', 'proc_3', '',
         [(680, 405), (630, 405), (630, 345), (595, 345)], (0, 0)),
        
        # 3.0 -> D6 Assigned location (3.0 right -> D6 left)
        ('e_3_d6', 'proc_3', 'store_d6', 'Assigned location',
         [(595, 360), (650, 360), (650, 520), (680, 520)], (605, 440)),
        
        # 3.0 -> D1 Order details/Order record (3.0 right -> TR_D1_3(980) -> D1 right)
        ('e_3_d1', 'proc_3', 'store_d1', 'Order details/Order record',
         [(595, 370), (980, 370), (980, 100), (785, 100)], (760, 280)),
        
        # 3.0 -> 4.0 Order & location details
        ('e_3_4', 'proc_3', 'proc_4', 'Order & location details',
         [(532, 375), (532, 470)], (435, 415)),

        # ==================== 4.0 FLOWS ====================
        # 4.0 -> Customer Real-time tracking (TL_4_CUST1 = 20)
        ('e_4_cust1', 'proc_4', 'entity_customer', 'Real-time tracking',
         [(480, 480), (20, 480), (20, 105), (140, 105)], (250, 469)),
        
        # 4.0 -> Customer Delivery status/Completion update (TL_4_CUST2 = 40)
        ('e_4_cust2', 'proc_4', 'entity_customer', 'Delivery status/Completion update',
         [(480, 495), (40, 495), (40, 125), (140, 125)], (210, 484)),
        
        # 4.0 -> Rider Delivery dispatch (Direct horizontal)
        ('e_4_rider', 'proc_4', 'entity_rider', 'Delivery dispatch',
         [(480, 510), (240, 510)], (325, 499)),
        
        # Rider -> 4.0 Delivery status update (Direct horizontal)
        ('e_rider_4', 'entity_rider', 'proc_4', 'Delivery status update',
         [(240, 525), (480, 525)], (315, 528)),

        # 4.0 -> D1 Order status update (4.0 right -> TR_D1_4(1000) -> D1 right)
        ('e_4_d1', 'proc_4', 'store_d1', 'Order status update',
         [(585, 480), (1000, 480), (1000, 110), (785, 110)], (760, 469)),
        
        # 4.0 -> D3 Stock deduction (4.0 right -> TR_D3_4(1020) -> D3 right)
        ('e_4_d3', 'proc_4', 'store_d3', 'Stock deduction',
         [(585, 495), (1020, 495), (1020, 255), (800, 255)], (760, 484)),
        
        # 4.0 -> D2 Order status update (4.0 right -> up to D2 left)
        ('e_4_d2', 'proc_4', 'store_d2', 'Order status update',
         [(585, 510), (660, 510), (660, 185), (680, 185)], (610, 215)),
        
        # 4.0 -> D6 Dispatch records (4.0 right -> D6 left)
        ('e_4_d6', 'proc_4', 'store_d6', 'Dispatch records',
         [(585, 530), (680, 530)], (605, 519)),
        
        # 4.0 -> 5.0 Confirmed order
        ('e_4_5', 'proc_4', 'proc_5', 'Confirmed order',
         [(532, 535), (532, 625)], (540, 575)),

        # ==================== 5.0 FLOWS ====================
        # Manager -> 5.0 Approved expense entries
        ('e_mgr_5a', 'entity_manager', 'proc_5', 'Approved expense entries',
         [(190, 795), (310, 795), (310, 640), (480, 640)], (270, 629)),
        
        # Manager -> 5.0 Stock/replenishment updates
        ('e_mgr_5b', 'entity_manager', 'proc_5', 'Stock/replenishment updates',
         [(170, 825), (290, 825), (290, 660), (480, 660)], (250, 649)),

        # D6 -> 5.0 Delivery records (Exits D6 right -> TR_D6_5(820) -> 5.0 right)
        ('e_d6_5', 'store_d6', 'proc_5', 'Delivery records',
         [(790, 525), (820, 525), (820, 635), (585, 635)], (670, 624)),
        
        # D5 -> 5.0 Payment data (Exits D5 right -> TR_D5_5(860) -> 5.0 right)
        ('e_d5_5', 'store_d5', 'proc_5', 'Payment data',
         [(790, 400), (860, 400), (860, 650), (585, 650)], (690, 639)),
        
        # D3 -> 5.0 Production data & stock replenishment (Exits D3 right -> TR_D3_5(900) -> 5.0 right)
        ('e_d3_5', 'store_d3', 'proc_5', 'Production data & stock replenishment',
         [(800, 260), (900, 260), (900, 665), (585, 665)], (700, 654)),
        
        # D4 -> 5.0 Approved expense entries/Expense data (Exits D4 right -> TR_D4_5(880) -> 5.0 right)
        ('e_d4_5', 'store_d4', 'proc_5', 'Approved expense entries/Expense data',
         [(790, 330), (880, 330), (880, 680), (585, 680)], (705, 669)),
        
        # 5.0 -> 6.0 Delivery data
        ('e_5_6', 'proc_5', 'proc_6', 'Delivery data',
         [(532, 685), (532, 770)], (540, 725)),

        # ==================== 6.0 FLOWS ====================
        # Manager -> 6.0 Request report
        ('e_mgr_6', 'entity_manager', 'proc_6', 'Request report',
         [(190, 810), (480, 810)], (310, 799)),
        
        # D3 -> 6.0 Inventory data (Exits D3 right -> TR_D3_6(940) -> 6.0 right)
        ('e_d3_6', 'store_d3', 'proc_6', 'Inventory data',
         [(800, 245), (940, 245), (940, 785), (590, 785)], (770, 774)),
        
        # D6 -> 6.0 Dispatch record (Exits D6 right -> TR_D6_6(840) -> 6.0 right)
        ('e_d6_6', 'store_d6', 'proc_6', 'Dispatch record',
         [(790, 535), (840, 535), (840, 805), (590, 805)], (670, 794)),
        
        # 6.0 -> Manager Sales/inventory/expense summary (6.0 right -> TR_6_MGR(1050) -> bottom -> Manager)
        ('e_6_mgr', 'proc_6', 'entity_manager', 'Sales/inventory/expense summary',
         [(590, 825), (1050, 825), (1050, 1020), (140, 1020), (140, 825)], (660, 1008)),
        
        # 6.0 -> 7.0 Summarized data
        ('e_6_7', 'proc_6', 'proc_7', 'Summarized data',
         [(532, 838), (532, 920)], (540, 875)),

        # ==================== 7.0 FLOWS ====================
        # 7.0 -> 6.0 Summarized data (Right loopback)
        ('e_7_6', 'proc_7', 'proc_6', 'Summarized data',
         [(590, 935), (650, 935), (650, 855), (560, 855), (560, 838)], (605, 885)),
        
        # 7.0 -> Manager Forecast & clustering report (7.0 right -> TR_7_MGR(1075) -> bottom -> Manager)
        ('e_7_mgr', 'proc_7', 'entity_manager', 'Forecast & clustering report',
         [(590, 955), (1075, 955), (1075, 1050), (115, 1050), (115, 825)], (660, 1038))
    ]

    # =========================================================================
    # 2. BUILD DRAW.IO XML (.drawio and .xml)
    # =========================================================================
    mxfile = ET.Element('mxfile', {
        'host': 'app.diagrams.net',
        'modified': '2026-09-23T05:15:00.000Z',
        'agent': 'Antigravity Pixel Perfect DFD',
        'version': '24.0.0',
        'type': 'device'
    })
    diagram = ET.SubElement(mxfile, 'diagram', {
        'id': 'level_1_dfd_exact',
        'name': 'Level 1 Data Flow Diagram'
    })
    mxGraphModel = ET.SubElement(diagram, 'mxGraphModel', {
        'dx': '1422', 'dy': '1180', 'grid': '0', 'gridSize': '10',
        'guides': '1', 'tooltips': '1', 'connect': '1', 'arrows': '1',
        'fold': '1', 'page': '0', 'pageScale': '1',
        'pageWidth': '1250', 'pageHeight': '1200',
        'background': '#FFFFFF', 'pageColor': '#FFFFFF', 'math': '0', 'shadow': '0'
    })
    root = ET.SubElement(mxGraphModel, 'root')
    ET.SubElement(root, 'mxCell', {'id': '0'})
    ET.SubElement(root, 'mxCell', {'id': '1', 'parent': '0'})

    # Entities
    for key, ent in entities.items():
        ET.SubElement(root, 'mxCell', {
            'id': ent['id'],
            'value': f'<b style="color:#000000;font-size:12px;font-family:Arial;">{ent["label"]}</b>',
            'style': 'rounded=0;whiteSpace=wrap;html=1;strokeColor=#000000;strokeWidth=1.5;fillColor=#FFFFFF;fontColor=#000000;fontFamily=Arial;align=center;verticalAlign=middle;',
            'vertex': '1', 'parent': '1'
        })
        ET.SubElement(root[-1], 'mxGeometry', {
            'x': str(ent['x']), 'y': str(ent['y']), 'width': str(ent['w']), 'height': str(ent['h']), 'as': 'geometry'
        })

    # Processes
    for key, proc in processes.items():
        pid = proc['id']
        pw, ph = proc['w'], proc['h']
        ET.SubElement(root, 'mxCell', {
            'id': pid, 'value': '',
            'style': 'rounded=1;arcSize=18;whiteSpace=wrap;html=1;strokeColor=#000000;strokeWidth=1.5;fillColor=#FFFFFF;fontFamily=Arial;',
            'vertex': '1', 'parent': '1'
        })
        ET.SubElement(root[-1], 'mxGeometry', {
            'x': str(proc['x']), 'y': str(proc['y']), 'width': str(pw), 'height': str(ph), 'as': 'geometry'
        })
        # Number
        ET.SubElement(root, 'mxCell', {
            'id': f'{pid}_num',
            'value': f'<b style="color:#000000;font-size:11px;font-family:Arial;">{proc["num"]}</b>',
            'style': 'text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontColor=#000000;fontFamily=Arial;',
            'vertex': '1', 'parent': pid
        })
        ET.SubElement(root[-1], 'mxGeometry', {'x': '0', 'y': '0', 'width': str(pw), 'height': '22', 'as': 'geometry'})
        # Divider Line
        ET.SubElement(root, 'mxCell', {
            'id': f'{pid}_line', 'value': '',
            'style': 'endArrow=none;html=1;strokeColor=#000000;strokeWidth=1.5;rounded=0;',
            'edge': '1', 'parent': pid
        })
        gline = ET.SubElement(root[-1], 'mxGeometry', {'width': '50', 'height': '50', 'relative': '1', 'as': 'geometry'})
        ET.SubElement(gline, 'mxPoint', {'x': '0', 'y': '22', 'as': 'sourcePoint'})
        ET.SubElement(gline, 'mxPoint', {'x': str(pw), 'y': '22', 'as': 'targetPoint'})
        # Name
        pname_html = "<br>".join(proc['lines'])
        ET.SubElement(root, 'mxCell', {
            'id': f'{pid}_txt',
            'value': f'<b style="color:#000000;font-size:10px;font-family:Arial;">{pname_html}</b>',
            'style': 'text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontColor=#000000;fontFamily=Arial;',
            'vertex': '1', 'parent': pid
        })
        ET.SubElement(root[-1], 'mxGeometry', {'x': '0', 'y': '22', 'width': str(pw), 'height': str(ph - 22), 'as': 'geometry'})

    # Data Stores
    for key, store in stores.items():
        sid = store['id']
        sw, sh = store['w'], store['h']
        ET.SubElement(root, 'mxCell', {
            'id': sid, 'value': '',
            'style': 'shape=partialRectangle;right=0;left=1;top=1;bottom=1;html=1;whiteSpace=wrap;strokeColor=#000000;strokeWidth=1.5;fillColor=#FFFFFF;fontFamily=Arial;',
            'vertex': '1', 'parent': '1'
        })
        ET.SubElement(root[-1], 'mxGeometry', {
            'x': str(store['x']), 'y': str(store['y']), 'width': str(sw), 'height': str(sh), 'as': 'geometry'
        })
        # Divider Line
        ET.SubElement(root, 'mxCell', {
            'id': f'{sid}_div', 'value': '',
            'style': 'endArrow=none;html=1;strokeColor=#000000;strokeWidth=1.5;rounded=0;',
            'edge': '1', 'parent': sid
        })
        gsdiv = ET.SubElement(root[-1], 'mxGeometry', {'width': '50', 'height': '50', 'relative': '1', 'as': 'geometry'})
        ET.SubElement(gsdiv, 'mxPoint', {'x': '26', 'y': '0', 'as': 'sourcePoint'})
        ET.SubElement(gsdiv, 'mxPoint', {'x': '26', 'y': str(sh), 'as': 'targetPoint'})
        # D-num
        ET.SubElement(root, 'mxCell', {
            'id': f'{sid}_num',
            'value': f'<b style="color:#000000;font-size:10px;font-family:Arial;">{store["num"]}</b>',
            'style': 'text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontColor=#000000;fontFamily=Arial;',
            'vertex': '1', 'parent': sid
        })
        ET.SubElement(root[-1], 'mxGeometry', {'x': '0', 'y': '0', 'width': '26', 'height': str(sh), 'as': 'geometry'})
        # Store Name
        ET.SubElement(root, 'mxCell', {
            'id': f'{sid}_name',
            'value': f'<b style="color:#000000;font-size:10px;font-family:Arial;">{store["name"]}</b>',
            'style': 'text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontColor=#000000;fontFamily=Arial;',
            'vertex': '1', 'parent': sid
        })
        ET.SubElement(root[-1], 'mxGeometry', {'x': '26', 'y': '0', 'width': str(sw - 26), 'height': str(sh), 'as': 'geometry'})

    # Edges
    for eid, src, tgt, label, pts, lpos in edges:
        style = 'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#000000;strokeWidth=1.2;fontColor=#000000;fontSize=9;fontFamily=Arial;labelBackgroundColor=#FFFFFF;labelBorderColor=none;'
        edge = ET.SubElement(root, 'mxCell', {
            'id': eid,
            'value': f'<span style="color:#000000;background-color:#FFFFFF;padding:1px 2px;font-size:9px;font-family:Arial;">{label}</span>' if label else '',
            'style': style, 'edge': '1', 'parent': '1', 'source': src, 'target': tgt
        })
        geo = ET.SubElement(edge, 'mxGeometry', {'relative': '1', 'as': 'geometry'})
        if len(pts) > 2:
            arr = ET.SubElement(geo, 'Array', {'as': 'points'})
            for px, py in pts[1:-1]:
                ET.SubElement(arr, 'mxPoint', {'x': str(px), 'y': str(py)})

    # Save XML & Drawio
    xml_str = ET.tostring(mxfile, encoding='utf-8')
    dom = xml.dom.minidom.parseString(xml_str)
    pretty_xml = dom.toprettyxml(indent='  ')
    
    out_drawio = r'c:\Users\kymer\Desktop\Lantad ACarwfish Django\diagram\Level_1_DFD.drawio'
    out_xml = r'c:\Users\kymer\Desktop\Lantad ACarwfish Django\diagram\Level_1_DFD.xml'
    
    with open(out_drawio, 'w', encoding='utf-8') as f:
        f.write(pretty_xml)
    with open(out_xml, 'w', encoding='utf-8') as f:
        f.write(pretty_xml)

    # =========================================================================
    # 3. RENDER 3X SUPERSAMPLED ULTRA-CRISP PNG (PIL)
    # =========================================================================
    scale = 3
    cw, ch = 1120 * scale, 1100 * scale
    img = Image.new('RGB', (cw, ch), color='#FFFFFF')
    draw = ImageDraw.Draw(img)

    try:
        font_entity = ImageFont.truetype('arialbd.ttf', 11 * scale)
        font_proc_num = ImageFont.truetype('arialbd.ttf', 11 * scale)
        font_proc_txt = ImageFont.truetype('arialbd.ttf', 9 * scale)
        font_store_num = ImageFont.truetype('arialbd.ttf', 9 * scale)
        font_store_txt = ImageFont.truetype('arialbd.ttf', 9 * scale)
        font_edge = ImageFont.truetype('arial.ttf', 8 * scale)
    except:
        font_entity = ImageFont.load_default()
        font_proc_num = font_entity
        font_proc_txt = font_entity
        font_store_num = font_entity
        font_store_txt = font_store_num
        font_edge = font_entity

    line_w = int(1.5 * scale)
    edge_w = int(1.1 * scale)

    # Draw Entities
    for key, ent in entities.items():
        x, y, ew, eh = ent['x'] * scale, ent['y'] * scale, ent['w'] * scale, ent['h'] * scale
        draw.rectangle([x, y, x + ew, y + eh], fill='#FFFFFF', outline='#000000', width=line_w)
        bbox = draw.textbbox((0, 0), ent['label'], font=font_entity)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text((x + (ew - tw) / 2, y + (eh - th) / 2 - 1 * scale), ent['label'], fill='#000000', font=font_entity)

    # Draw Processes
    for key, proc in processes.items():
        x, y, pw, ph = proc['x'] * scale, proc['y'] * scale, proc['w'] * scale, proc['h'] * scale
        r = 12 * scale
        draw.rounded_rectangle([x, y, x + pw, y + ph], radius=r, fill='#FFFFFF', outline='#000000', width=line_w)
        hdr_y = y + int(22 * scale)
        draw.line([x, hdr_y, x + pw, hdr_y], fill='#000000', width=line_w)
        # Number
        bbox = draw.textbbox((0, 0), proc['num'], font=font_proc_num)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text((x + (pw - tw) / 2, y + (22 * scale - th) / 2 - 1 * scale), proc['num'], fill='#000000', font=font_proc_num)
        # Text lines
        lines = proc['lines']
        total_th = len(lines) * (12 * scale)
        start_y = hdr_y + (ph - 22 * scale - total_th) / 2
        for i, line in enumerate(lines):
            lbox = draw.textbbox((0, 0), line, font=font_proc_txt)
            ltw = lbox[2] - lbox[0]
            draw.text((x + (pw - ltw) / 2, start_y + i * 12 * scale), line, fill='#000000', font=font_proc_txt)

    # Draw Data Stores
    for key, store in stores.items():
        x, y, sw, sh = store['x'] * scale, store['y'] * scale, store['w'] * scale, store['h'] * scale
        draw.line([x, y, x + sw, y], fill='#000000', width=line_w)
        draw.line([x, y, x, y + sh], fill='#000000', width=line_w)
        draw.line([x, y + sh, x + sw, y + sh], fill='#000000', width=line_w)
        div_x = x + int(26 * scale)
        draw.line([div_x, y, div_x, y + sh], fill='#000000', width=line_w)
        # D-num
        nbox = draw.textbbox((0, 0), store['num'], font=font_store_num)
        ntw, nth = nbox[2] - nbox[0], nbox[3] - nbox[1]
        draw.text((x + (26 * scale - ntw) / 2, y + (sh - nth) / 2 - 1 * scale), store['num'], fill='#000000', font=font_store_num)
        # Store Name
        sbox = draw.textbbox((0, 0), store['name'], font=font_store_txt)
        stw, sth = sbox[2] - sbox[0], sbox[3] - sbox[1]
        draw.text((div_x + (sw - 26 * scale - stw) / 2, y + (sh - sth) / 2 - 1 * scale), store['name'], fill='#000000', font=font_store_txt)

    # Draw Edges & Labels
    for eid, src, tgt, label, points, lpos in edges:
        pts = [(px * scale, py * scale) for px, py in points]
        for i in range(len(pts) - 1):
            draw.line([pts[i], pts[i+1]], fill='#000000', width=edge_w)
        
        # Arrowhead
        p_last = pts[-1]
        p_prev = pts[-2]
        alen = 6 * scale
        aw = 3.2 * scale
        dx = p_last[0] - p_prev[0]
        dy = p_last[1] - p_prev[1]
        
        if dx > 0:
            draw.polygon([p_last, (p_last[0] - alen, p_last[1] - aw), (p_last[0] - alen, p_last[1] + aw)], fill='#000000')
        elif dx < 0:
            draw.polygon([p_last, (p_last[0] + alen, p_last[1] - aw), (p_last[0] + alen, p_last[1] + aw)], fill='#000000')
        elif dy > 0:
            draw.polygon([p_last, (p_last[0] - aw, p_last[1] - alen), (p_last[0] + aw, p_last[1] - alen)], fill='#000000')
        elif dy < 0:
            draw.polygon([p_last, (p_last[0] - aw, p_last[1] + alen), (p_last[0] + aw, p_last[1] + alen)], fill='#000000')

        # Label
        if label:
            lbox = draw.textbbox((0, 0), label, font=font_edge)
            ltw, lth = lbox[2] - lbox[0], lbox[3] - lbox[1]
            if lpos and lpos != (0, 0):
                lx, ly = lpos[0] * scale, lpos[1] * scale
            else:
                mid_idx = len(pts) // 2
                lx = (pts[mid_idx-1][0] + pts[mid_idx][0]) / 2 - ltw / 2
                ly = (pts[mid_idx-1][1] + pts[mid_idx][1]) / 2 - lth / 2
            
            pad = 2 * scale
            draw.rectangle([lx - pad, ly - pad, lx + ltw + pad, ly + lth + pad], fill='#FFFFFF')
            draw.text((lx, ly), label, fill='#000000', font=font_edge)

    out_png1 = r'c:\Users\kymer\Desktop\Lantad ACarwfish Django\diagram\Level_1_DFD.png'
    out_png2 = r'c:\Users\kymer\Desktop\Lantad ACarwfish Django\Documents\Final_Paper\ch3_extracted_images\level_1_dfd_exact.png'
    
    img.save(out_png1, 'PNG', quality=100)
    img.save(out_png2, 'PNG', quality=100)
    print("Perfect Level 1 DFD rebuilt successfully!")

if __name__ == '__main__':
    build_and_render_perfect_dfd()
