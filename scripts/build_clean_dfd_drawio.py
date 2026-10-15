import os
import xml.etree.ElementTree as ET
import xml.dom.minidom
from PIL import Image, ImageDraw, ImageFont

def build_and_render_flawless_dfd():
    # Canvas parameters
    canvas_w = 1420
    canvas_h = 1260

    # 1. Left Entities
    entities = {
        'Customer': {'id': 'entity_customer', 'label': 'Customer', 'x': 130, 'y': 100, 'w': 110, 'h': 60},
        'Rider':    {'id': 'entity_rider',    'label': 'Rider',    'x': 130, 'y': 520, 'w': 110, 'h': 50},
        'Owner':    {'id': 'entity_owner',    'label': 'Owner',    'x': 70,  'y': 860, 'w': 110, 'h': 50},
    }

    # 2. Center Processes
    processes = {
        '1.0': {'id': 'proc_1', 'num': '1.0', 'name': 'Browse and select',      'lines': ['Browse', 'and select'],        'x': 560, 'y': 35,   'w': 120, 'h': 70},
        '2.0': {'id': 'proc_2', 'num': '2.0', 'name': 'Order management',       'lines': ['Order', 'management'],         'x': 560, 'y': 180,  'w': 120, 'h': 70},
        '3.0': {'id': 'proc_3', 'num': '3.0', 'name': 'Payment & Set location', 'lines': ['Payment &', 'Set location'],   'x': 555, 'y': 340,  'w': 130, 'h': 70},
        '4.0': {'id': 'proc_4', 'num': '4.0', 'name': 'Delivery dispatch',      'lines': ['Delivery', 'dispatch'],        'x': 560, 'y': 510,  'w': 120, 'h': 70},
        '5.0': {'id': 'proc_5', 'num': '5.0', 'name': 'Management',             'lines': ['Management'],                  'x': 560, 'y': 680,  'w': 120, 'h': 65},
        '6.0': {'id': 'proc_6', 'num': '6.0', 'name': 'Report and Monitoring',  'lines': ['Report and', 'Monitoring'],    'x': 555, 'y': 840,  'w': 130, 'h': 75},
        '7.0': {'id': 'proc_7', 'num': '7.0', 'name': 'Predictive Analytics',   'lines': ['Predictive', 'Analytics'],     'x': 555, 'y': 1005, 'w': 130, 'h': 70},
    }

    # 3. Right Data Stores
    stores = {
        'D1': {'id': 'store_d1', 'num': 'D1', 'name': 'Order',      'x': 830, 'y': 90,  'w': 110, 'h': 34},
        'D2': {'id': 'store_d2', 'num': 'D2', 'name': 'Customer',   'x': 830, 'y': 180, 'w': 120, 'h': 34},
        'D3': {'id': 'store_d3', 'num': 'D3', 'name': 'Production', 'x': 830, 'y': 270, 'w': 130, 'h': 34},
        'D4': {'id': 'store_d4', 'num': 'D4', 'name': 'Expense',    'x': 830, 'y': 360, 'w': 120, 'h': 34},
        'D5': {'id': 'store_d5', 'num': 'D5', 'name': 'Payment',    'x': 830, 'y': 445, 'w': 120, 'h': 34},
        'D6': {'id': 'store_d6', 'num': 'D6', 'name': 'Delivery',   'x': 830, 'y': 580, 'w': 120, 'h': 34},
    }

    # 4. Data Flows with zero-overlap routing
    edges = [
        # --- 1.0 FLOWS ---
        ('e_cust_1', 'entity_customer', 'proc_1', 'Selected Product',
         [(190, 100), (190, 50), (560, 50)], (320, 38)),
        ('e_1_cust', 'proc_1', 'entity_customer', 'Product list',
         [(560, 75), (220, 75), (220, 100)], (340, 63)),
        ('e_1_2', 'proc_1', 'proc_2', 'Select product',
         [(620, 105), (620, 180)], (628, 140)),
        ('e_d3_1', 'store_d3', 'proc_1', 'Available stock',
         [(960, 280), (1160, 280), (1160, 50), (680, 50)], (890, 38)),
        ('e_d1_1', 'store_d1', 'proc_1', 'Order info',
         [(940, 100), (1190, 100), (1190, 75), (680, 75)], (890, 63)),
        ('e_1_d1', 'proc_1', 'store_d1', 'Order info',
         [(680, 90), (760, 90), (760, 105), (830, 105)], (705, 80)),

        # --- 2.0 FLOWS ---
        ('e_cust_2', 'entity_customer', 'proc_2', 'Order request/details',
         [(240, 130), (380, 130), (380, 195), (560, 195)], (395, 182)),
        ('e_2_cust', 'proc_2', 'entity_customer', 'Order confirmation',
         [(560, 220), (240, 220), (240, 150)], (360, 208)),
        ('e_owner_2', 'entity_owner', 'proc_2', 'Order approval',
         [(120, 860), (70, 860), (70, 235), (560, 235)], (300, 222)),
        ('e_2_d1', 'proc_2', 'store_d1', 'Order records',
         [(680, 195), (760, 195), (760, 118), (830, 118)], (705, 150)),
        ('e_d2_2', 'store_d2', 'proc_2', 'Customer/order info',
         [(830, 190), (680, 190)], (705, 177)),
        ('e_2_d2', 'proc_2', 'store_d2', '',
         [(680, 210), (830, 210)], (0, 0)),
        ('e_2_3', 'proc_2', 'proc_3', 'Order info',
         [(620, 250), (620, 340)], (628, 290)),

        # --- 3.0 FLOWS ---
        ('e_cust_3a', 'entity_customer', 'proc_3', 'Delivery/pickup address',
         [(195, 160), (195, 350), (555, 350)], (330, 337)),
        ('e_cust_3b', 'entity_customer', 'proc_3', 'Payment details',
         [(175, 160), (175, 368), (555, 368)], (350, 355)),
        ('e_3_custa', 'proc_3', 'entity_customer', 'Payment status',
         [(555, 385), (155, 385), (155, 160)], (350, 372)),
        ('e_3_custb', 'proc_3', 'entity_customer', 'Payment verification (GCash/COD)',
         [(555, 400), (135, 400), (135, 160)], (280, 388)),
        ('e_rider_3', 'entity_rider', 'proc_3', 'Cash collected (COD payment)',
         [(215, 520), (215, 420), (555, 420)], (310, 408)),

        ('e_3_d5', 'proc_3', 'store_d5', 'Payment data',
         [(685, 360), (760, 360), (760, 455), (830, 455)], (705, 375)),
        ('e_d5_3', 'store_d5', 'proc_3', '',
         [(830, 470), (745, 470), (745, 375), (685, 375)], (0, 0)),
        ('e_3_d6', 'proc_3', 'store_d6', 'Assigned location',
         [(685, 395), (775, 395), (775, 595), (830, 595)], (705, 500)),
        ('e_3_d1', 'proc_3', 'store_d1', 'Order details/Order record',
         [(685, 410), (1220, 410), (1220, 110), (940, 110)], (890, 300)),
        ('e_3_4', 'proc_3', 'proc_4', 'Order & location details',
         [(620, 410), (620, 510)], (500, 455)),

        # --- 4.0 FLOWS ---
        ('e_4_cust1', 'proc_4', 'entity_customer', 'Real-time tracking',
         [(560, 520), (20, 520), (20, 115), (130, 115)], (290, 508)),
        ('e_4_cust2', 'proc_4', 'entity_customer', 'Delivery status/Completion update',
         [(560, 538), (45, 538), (45, 140), (130, 140)], (250, 526)),
        ('e_4_rider', 'proc_4', 'entity_rider', 'Delivery dispatch',
         [(560, 555), (240, 555)], (360, 543)),
        ('e_rider_4', 'entity_rider', 'proc_4', 'Delivery status update',
         [(240, 570), (560, 570)], (350, 573)),

        ('e_4_d1', 'proc_4', 'store_d1', 'Order status update',
         [(680, 520), (1250, 520), (1250, 120), (940, 120)], (890, 508)),
        ('e_4_d3', 'proc_4', 'store_d3', 'Stock deduction',
         [(680, 538), (1280, 538), (1280, 290), (960, 290)], (890, 526)),
        ('e_4_d2', 'proc_4', 'store_d2', 'Order status update',
         [(680, 555), (790, 555), (790, 205), (830, 205)], (705, 235)),
        ('e_4_d6', 'proc_4', 'store_d6', 'Dispatch records',
         [(680, 570), (830, 570)], (715, 558)),
        ('e_4_5', 'proc_4', 'proc_5', 'Confirmed order',
         [(620, 580), (620, 680)], (628, 625)),

        # --- 5.0 FLOWS ---
        ('e_owner_5a', 'entity_owner', 'proc_5', 'Approved expense entries',
         [(180, 860), (340, 860), (340, 695), (560, 695)], (300, 682)),
        ('e_owner_5b', 'entity_owner', 'proc_5', 'Stock/replenishment updates',
         [(150, 860), (310, 860), (310, 720), (560, 720)], (270, 708)),

        ('e_d6_5', 'store_d6', 'proc_5', 'Delivery records',
         [(950, 600), (980, 600), (980, 690), (680, 690)], (770, 678)),
        ('e_d5_5', 'store_d5', 'proc_5', 'Payment data',
         [(950, 460), (1040, 460), (1040, 705), (680, 705)], (790, 693)),
        ('e_d3_5', 'store_d3', 'proc_5', 'Production data & stock replenishment',
         [(960, 295), (1100, 295), (1100, 720), (680, 720)], (810, 708)),
        ('e_d4_5', 'store_d4', 'proc_5', 'Approved expense entries/Expense data',
         [(950, 380), (1070, 380), (1070, 735), (680, 735)], (810, 723)),
        ('e_5_6', 'proc_5', 'proc_6', 'Delivery data',
         [(620, 745), (620, 840)], (628, 785)),

        # --- 6.0 FLOWS ---
        ('e_owner_6', 'entity_owner', 'proc_6', 'Request report',
         [(180, 885), (555, 885)], (340, 872)),
        ('e_d3_6', 'store_d3', 'proc_6', 'Inventory data',
         [(960, 275), (1130, 275), (1130, 860), (685, 860)], (880, 848)),
        ('e_d6_6', 'store_d6', 'proc_6', 'Dispatch record',
         [(950, 610), (1010, 610), (1010, 880), (685, 880)], (780, 868)),
        ('e_6_owner', 'proc_6', 'entity_owner', 'Sales/inventory/expense summary',
         [(685, 900), (1320, 900), (1320, 1140), (100, 1140), (100, 910)], (760, 1126)),
        ('e_6_7', 'proc_6', 'proc_7', 'Summarized data',
         [(620, 915), (620, 1005)], (628, 955)),

        # --- 7.0 FLOWS ---
        ('e_7_6', 'proc_7', 'proc_6', '',
         [(685, 1025), (770, 1025), (770, 925), (660, 925), (660, 915)], (0, 0)),
        ('e_7_owner', 'proc_7', 'entity_owner', 'Forecast & clustering report',
         [(685, 1055), (1355, 1055), (1355, 1180), (70, 1180), (70, 910)], (740, 1166))
    ]

    # Save to Draw.io
    mxfile = ET.Element('mxfile', {
        'host': 'app.diagrams.net',
        'modified': '2026-09-23T06:00:00.000Z',
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
        'pageWidth': str(canvas_w), 'pageHeight': str(canvas_h),
        'background': '#FFFFFF', 'pageColor': '#FFFFFF', 'math': '0', 'shadow': '0'
    })
    root = ET.SubElement(mxGraphModel, 'root')
    ET.SubElement(root, 'mxCell', {'id': '0'})
    ET.SubElement(root, 'mxCell', {'id': '1', 'parent': '0'})

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
        ET.SubElement(root, 'mxCell', {
            'id': f'{pid}_num',
            'value': f'<b style="color:#000000;font-size:11px;font-family:Arial;">{proc["num"]}</b>',
            'style': 'text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontColor=#000000;fontFamily=Arial;',
            'vertex': '1', 'parent': pid
        })
        ET.SubElement(root[-1], 'mxGeometry', {'x': '0', 'y': '0', 'width': str(pw), 'height': '22', 'as': 'geometry'})
        ET.SubElement(root, 'mxCell', {
            'id': f'{pid}_line', 'value': '',
            'style': 'endArrow=none;html=1;strokeColor=#000000;strokeWidth=1.5;rounded=0;',
            'edge': '1', 'parent': pid
        })
        gline = ET.SubElement(root[-1], 'mxGeometry', {'width': '50', 'height': '50', 'relative': '1', 'as': 'geometry'})
        ET.SubElement(gline, 'mxPoint', {'x': '0', 'y': '22', 'as': 'sourcePoint'})
        ET.SubElement(gline, 'mxPoint', {'x': str(pw), 'y': '22', 'as': 'targetPoint'})
        pname_html = "<br>".join(proc['lines'])
        ET.SubElement(root, 'mxCell', {
            'id': f'{pid}_txt',
            'value': f'<b style="color:#000000;font-size:10px;font-family:Arial;">{pname_html}</b>',
            'style': 'text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontColor=#000000;fontFamily=Arial;',
            'vertex': '1', 'parent': pid
        })
        ET.SubElement(root[-1], 'mxGeometry', {'x': '0', 'y': '22', 'width': str(pw), 'height': str(ph - 22), 'as': 'geometry'})

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
        ET.SubElement(root, 'mxCell', {
            'id': f'{sid}_div', 'value': '',
            'style': 'endArrow=none;html=1;strokeColor=#000000;strokeWidth=1.5;rounded=0;',
            'edge': '1', 'parent': sid
        })
        gsdiv = ET.SubElement(root[-1], 'mxGeometry', {'width': '50', 'height': '50', 'relative': '1', 'as': 'geometry'})
        ET.SubElement(gsdiv, 'mxPoint', {'x': '26', 'y': '0', 'as': 'sourcePoint'})
        ET.SubElement(gsdiv, 'mxPoint', {'x': '26', 'y': str(sh), 'as': 'targetPoint'})
        ET.SubElement(root, 'mxCell', {
            'id': f'{sid}_num',
            'value': f'<b style="color:#000000;font-size:10px;font-family:Arial;">{store["num"]}</b>',
            'style': 'text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontColor=#000000;fontFamily=Arial;',
            'vertex': '1', 'parent': sid
        })
        ET.SubElement(root[-1], 'mxGeometry', {'x': '0', 'y': '0', 'width': '26', 'height': str(sh), 'as': 'geometry'})
        ET.SubElement(root, 'mxCell', {
            'id': f'{sid}_name',
            'value': f'<b style="color:#000000;font-size:10px;font-family:Arial;">{store["name"]}</b>',
            'style': 'text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontColor=#000000;fontFamily=Arial;',
            'vertex': '1', 'parent': sid
        })
        ET.SubElement(root[-1], 'mxGeometry', {'x': '26', 'y': '0', 'width': str(sw - 26), 'height': str(sh), 'as': 'geometry'})

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

    xml_str = ET.tostring(mxfile, encoding='utf-8')
    dom = xml.dom.minidom.parseString(xml_str)
    pretty_xml = dom.toprettyxml(indent='  ')
    
    out_drawio = r'c:\Users\kymer\Desktop\Lantad ACarwfish Django\diagram\Level_1_DFD.drawio'
    out_xml = r'c:\Users\kymer\Desktop\Lantad ACarwfish Django\diagram\Level_1_DFD.xml'
    
    with open(out_drawio, 'w', encoding='utf-8') as f:
        f.write(pretty_xml)
    with open(out_xml, 'w', encoding='utf-8') as f:
        f.write(pretty_xml)

    # Render PNG with PIL
    scale = 3
    cw, ch = canvas_w * scale, canvas_h * scale
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

    for key, ent in entities.items():
        x, y, ew, eh = ent['x'] * scale, ent['y'] * scale, ent['w'] * scale, ent['h'] * scale
        draw.rectangle([x, y, x + ew, y + eh], fill='#FFFFFF', outline='#000000', width=line_w)
        bbox = draw.textbbox((0, 0), ent['label'], font=font_entity)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text((x + (ew - tw) / 2, y + (eh - th) / 2 - 1 * scale), ent['label'], fill='#000000', font=font_entity)

    for key, proc in processes.items():
        x, y, pw, ph = proc['x'] * scale, proc['y'] * scale, proc['w'] * scale, proc['h'] * scale
        r = 12 * scale
        draw.rounded_rectangle([x, y, x + pw, y + ph], radius=r, fill='#FFFFFF', outline='#000000', width=line_w)
        hdr_y = y + int(22 * scale)
        draw.line([x, hdr_y, x + pw, hdr_y], fill='#000000', width=line_w)
        bbox = draw.textbbox((0, 0), proc['num'], font=font_proc_num)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text((x + (pw - tw) / 2, y + (22 * scale - th) / 2 - 1 * scale), proc['num'], fill='#000000', font=font_proc_num)
        lines = proc['lines']
        total_th = len(lines) * (12 * scale)
        start_y = hdr_y + (ph - 22 * scale - total_th) / 2
        for i, line in enumerate(lines):
            lbox = draw.textbbox((0, 0), line, font=font_proc_txt)
            ltw = lbox[2] - lbox[0]
            draw.text((x + (pw - ltw) / 2, start_y + i * 12 * scale), line, fill='#000000', font=font_proc_txt)

    for key, store in stores.items():
        x, y, sw, sh = store['x'] * scale, store['y'] * scale, store['w'] * scale, store['h'] * scale
        draw.line([x, y, x + sw, y], fill='#000000', width=line_w)
        draw.line([x, y, x, y + sh], fill='#000000', width=line_w)
        draw.line([x, y + sh, x + sw, y + sh], fill='#000000', width=line_w)
        div_x = x + int(26 * scale)
        draw.line([div_x, y, div_x, y + sh], fill='#000000', width=line_w)
        nbox = draw.textbbox((0, 0), store['num'], font=font_store_num)
        ntw, nth = nbox[2] - nbox[0], nbox[3] - nbox[1]
        draw.text((x + (26 * scale - ntw) / 2, y + (sh - nth) / 2 - 1 * scale), store['num'], fill='#000000', font=font_store_num)
        sbox = draw.textbbox((0, 0), store['name'], font=font_store_txt)
        stw, sth = sbox[2] - sbox[0], sbox[3] - sbox[1]
        draw.text((div_x + (sw - 26 * scale - stw) / 2, y + (sh - sth) / 2 - 1 * scale), store['name'], fill='#000000', font=font_store_txt)

    for eid, src, tgt, label, points, lpos in edges:
        pts = [(px * scale, py * scale) for px, py in points]
        for i in range(len(pts) - 1):
            draw.line([pts[i], pts[i+1]], fill='#000000', width=edge_w)
        
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
    print("Flawless Level 1 DFD generated!")

if __name__ == '__main__':
    build_and_render_flawless_dfd()
