import os
import math
import xml.etree.ElementTree as ET
import xml.dom.minidom
from PIL import Image, ImageDraw, ImageFont

def generate_perfect_uml_use_case():
    # Canvas size: 1550 x 1100
    canvas_w = 1550
    canvas_h = 1100

    # System boundary box
    sys_box = {
        'x': 280, 'y': 40, 'w': 1220, 'h': 1010,
        'title': 'Aquaculture Value Chain Management System with Predictive Analytics'
    }

    # 3 Actors on the Left
    actors = {
        'Owner': {
            'id': 'actor_owner', 'label': 'Owner',
            'x': 60, 'y': 250, 'w': 90, 'h': 130,
            'center': (105, 305), 'arm_pt': (155, 305)
        },
        'Customer': {
            'id': 'actor_customer', 'label': 'Customer',
            'x': 60, 'y': 640, 'w': 90, 'h': 130,
            'center': (105, 695), 'arm_pt': (155, 695)
        },
        'Rider': {
            'id': 'actor_rider', 'label': 'Rider',
            'x': 60, 'y': 900, 'w': 90, 'h': 130,
            'center': (105, 955), 'arm_pt': (155, 955)
        }
    }

    # Column 1 Use Cases (Primary Hubs): cx ~ 520
    # Column 2 Use Cases (Specialized / Sub operations): cx ~ 1060
    use_cases = [
        # --- OWNER SECTION ---
        {'id': 'uc_dashboard',   'label': 'View Dashboard\n& Analytics',       'cx': 520, 'cy': 100, 'w': 220, 'h': 64, 'role': 'Owner'},
        {'id': 'uc_predictive',  'label': 'Sales Forecasting\n& Clustering',  'cx': 1060,'cy': 100, 'w': 230, 'h': 64, 'role': 'Owner'},

        {'id': 'uc_ponds',       'label': 'Manage Pond\nOperations',          'cx': 520, 'cy': 190, 'w': 220, 'h': 64, 'role': 'Owner'},
        {'id': 'uc_feeding',     'label': 'Record Feeding\n& Mortality Logs', 'cx': 1060,'cy': 190, 'w': 230, 'h': 64, 'role': 'Owner'},

        {'id': 'uc_inventory',   'label': 'Manage Inventory\n& Pricing',      'cx': 520, 'cy': 280, 'w': 220, 'h': 64, 'role': 'Owner'},
        {'id': 'uc_stock_batch', 'label': 'Create Stock\nBatch',              'cx': 1060,'cy': 280, 'w': 220, 'h': 64, 'role': 'Owner'},

        {'id': 'uc_expenses',    'label': 'Manage Operational\nExpenses',     'cx': 520, 'cy': 370, 'w': 230, 'h': 64, 'role': 'Owner'},
        {'id': 'uc_reports',     'label': 'Export Printable\nReports',        'cx': 520, 'cy': 460, 'w': 220, 'h': 64, 'role': 'Owner'},

        # --- CUSTOMER SECTION ---
        {'id': 'uc_browse',      'label': 'Browse Catalog\n& Cart',           'cx': 520, 'cy': 570, 'w': 220, 'h': 64, 'role': 'Customer'},
        {'id': 'uc_address',     'label': 'Assign Delivery\n/ Pickup Option', 'cx': 1060,'cy': 570, 'w': 230, 'h': 64, 'role': 'Customer'},

        {'id': 'uc_checkout',    'label': 'Place Order\n& Checkout',          'cx': 520, 'cy': 670, 'w': 220, 'h': 64, 'role': 'Customer'},
        {'id': 'uc_payment',     'label': 'Process Payment\n(GCash / COD)',   'cx': 1060,'cy': 670, 'w': 230, 'h': 64, 'role': 'Customer'},

        {'id': 'uc_tracking',    'label': 'Track Live Order\nStatus & Map',   'cx': 520, 'cy': 770, 'w': 220, 'h': 64, 'role': 'Customer'},

        # --- RIDER SECTION ---
        {'id': 'uc_dispatch',    'label': 'View Assigned\nDeliveries',         'cx': 520, 'cy': 890, 'w': 220, 'h': 64, 'role': 'Rider'},
        {'id': 'uc_pod',         'label': 'Confirm Delivery\n(Proof of Delivery)','cx': 1060,'cy': 890, 'w': 230, 'h': 64, 'role': 'Rider'},

        {'id': 'uc_transit',     'label': 'Update Delivery\nStatus',           'cx': 520, 'cy': 980, 'w': 220, 'h': 64, 'role': 'Rider'},
    ]

    uc_map = {uc['id']: uc for uc in use_cases}

    # Associations (Actor arm -> Primary Column 1 Use Case)
    associations = [
        # Owner Associations
        ('actor_owner', 'uc_dashboard'),
        ('actor_owner', 'uc_ponds'),
        ('actor_owner', 'uc_inventory'),
        ('actor_owner', 'uc_expenses'),
        ('actor_owner', 'uc_reports'),

        # Customer Associations
        ('actor_customer', 'uc_browse'),
        ('actor_customer', 'uc_checkout'),
        ('actor_customer', 'uc_tracking'),

        # Rider Associations
        ('actor_rider', 'uc_dispatch'),
        ('actor_rider', 'uc_transit'),
    ]

    # Flow / Extension Connections between Column 1 and Column 2
    flows = [
        {'src': 'uc_dashboard', 'tgt': 'uc_predictive',  'type': 'flow',     'label': ''},
        {'src': 'uc_ponds',     'tgt': 'uc_feeding',     'type': 'flow',     'label': ''},
        {'src': 'uc_inventory', 'tgt': 'uc_stock_batch', 'type': 'flow',     'label': ''},
        {'src': 'uc_browse',    'tgt': 'uc_address',     'type': 'flow',     'label': ''},
        {'src': 'uc_checkout',  'tgt': 'uc_payment',     'type': 'include',  'label': '<<includes>>'},
        {'src': 'uc_dispatch',  'tgt': 'uc_pod',         'type': 'include',  'label': '<<includes>>'},
    ]

    # ==================== 1. GENERATE DRAW.IO XML ====================
    mxfile = ET.Element('mxfile', host='app.diagrams.net', version='21.0.0')
    diagram = ET.SubElement(mxfile, 'diagram', name='UML_Use_Case_Diagram', id='uml_uc_avcms_perfect')
    model = ET.SubElement(diagram, 'mxGraphModel', dx='1550', dy='1100', grid='1', gridSize='10', guides='1', tooltips='1', connect='1', arrows='1', fold='1', page='1', pageScale='1', pageWidth='1550', pageHeight='1100', math='0', shadow='0')
    root = ET.SubElement(model, 'root')

    ET.SubElement(root, 'mxCell', id='0')
    ET.SubElement(root, 'mxCell', id='1', parent='0')

    # System Boundary Box
    sb_style = (
        "shape=swimlane;startSize=32;rounded=0;strokeWidth=2;"
        "strokeColor=#000000;fillColor=#ffffff;fontFamily=Arial;fontSize=13;"
        "fontStyle=1;fontColor=#000000;align=center;collapsible=0;"
    )
    sb_cell = ET.SubElement(root, 'mxCell', id='system_boundary', value=sys_box['title'], style=sb_style, vertex='1', parent='1')
    ET.SubElement(sb_cell, 'mxGeometry', x=str(sys_box['x']), y=str(sys_box['y']), width=str(sys_box['w']), height=str(sys_box['h']), as_='geometry')

    # Add Actors
    for a_name, a_info in actors.items():
        actor_style = (
            "shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;"
            "outlineConnect=0;strokeWidth=2;strokeColor=#000000;fillColor=#ffffff;"
            "fontFamily=Arial;fontSize=12;fontStyle=1;fontColor=#000000;"
        )
        a_cell = ET.SubElement(root, 'mxCell', id=a_info['id'], value=a_info['label'], style=actor_style, vertex='1', parent='1')
        ET.SubElement(a_cell, 'mxGeometry', x=str(a_info['x']), y=str(a_info['y']), width=str(a_info['w']), height=str(a_info['h']), as_='geometry')

    # Add Use Cases
    for uc in use_cases:
        uc_style = (
            "shape=ellipse;perimeter=ellipsePerimeter;whiteSpace=wrap;html=1;strokeWidth=1.5;"
            "strokeColor=#000000;fillColor=#ffffff;fontFamily=Arial;fontSize=11;fontStyle=0;"
            "fontColor=#000000;align=center;verticalAlign=middle;"
        )
        x_top = uc['cx'] - uc['w'] // 2
        y_top = uc['cy'] - uc['h'] // 2
        uc_cell = ET.SubElement(root, 'mxCell', id=uc['id'], value=uc['label'], style=uc_style, vertex='1', parent='1')
        ET.SubElement(uc_cell, 'mxGeometry', x=str(x_top), y=str(y_top), width=str(uc['w']), height=str(uc['h']), as_='geometry')

    # Add Actor Associations (Solid straight lines)
    for idx, (src_id, tgt_id) in enumerate(associations):
        assoc_style = (
            "endArrow=none;html=1;rounded=0;strokeColor=#000000;strokeWidth=1.5;"
        )
        edge = ET.SubElement(root, 'mxCell', id=f'edge_assoc_{idx}', style=assoc_style, edge='1', parent='1', source=src_id, target=tgt_id)
        ET.SubElement(edge, 'mxGeometry', relative='1', as_='geometry')

    # Add Flows and Includes
    for idx, fl in enumerate(flows):
        if fl['type'] == 'include':
            fl_style = (
                "endArrow=open;dashed=1;html=1;rounded=0;strokeColor=#000000;strokeWidth=1.5;"
                "endFill=0;fontFamily=Arial;fontSize=10;fontColor=#000000;align=center;verticalAlign=middle;"
            )
        else:
            fl_style = (
                "endArrow=block;endFill=1;html=1;rounded=0;strokeColor=#000000;strokeWidth=1.5;"
            )
        edge = ET.SubElement(root, 'mxCell', id=f'edge_fl_{idx}', value=fl['label'], style=fl_style, edge='1', parent='1', source=fl['src'], target=fl['tgt'])
        ET.SubElement(edge, 'mxGeometry', relative='1', as_='geometry')

    xml_str = ET.tostring(mxfile, encoding='utf-8')
    dom = xml.dom.minidom.parseString(xml_str)
    pretty_xml = dom.toprettyxml(indent='  ')

    os.makedirs('diagram', exist_ok=True)
    drawio_path = os.path.join('diagram', 'UML_Use_Case_Diagram.drawio')
    xml_path = os.path.join('diagram', 'UML_Use_Case_Diagram.xml')
    png_path = os.path.join('diagram', 'UML_Use_Case_Diagram.png')

    with open(drawio_path, 'w', encoding='utf-8') as f:
        f.write(pretty_xml)
    with open(xml_path, 'w', encoding='utf-8') as f:
        f.write(pretty_xml)

    # ==================== 2. RENDER CRISP PNG ====================
    img = Image.new('RGB', (canvas_w, canvas_h), '#ffffff')
    draw = ImageDraw.Draw(img)

    try:
        font_title = ImageFont.truetype("arialbd.ttf", 16)
        font_actor = ImageFont.truetype("arialbd.ttf", 13)
        font_uc = ImageFont.truetype("arial.ttf", 11)
        font_inc = ImageFont.truetype("ariali.ttf", 10)
        font_sec = ImageFont.truetype("ariali.ttf", 11)
    except:
        font_title = ImageFont.load_default()
        font_actor = ImageFont.load_default()
        font_uc = ImageFont.load_default()
        font_inc = ImageFont.load_default()
        font_sec = ImageFont.load_default()

    # Draw System Boundary Box
    sb_x1, sb_y1 = sys_box['x'], sys_box['y']
    sb_x2, sb_y2 = sb_x1 + sys_box['w'], sb_y1 + sys_box['h']
    draw.rectangle([sb_x1, sb_y1, sb_x2, sb_y2], fill='#ffffff', outline='#000000', width=2)
    
    # Boundary Title
    draw.text((sb_x1 + 25, sb_y1 + 10), sys_box['title'], fill='#000000', font=font_title)

    # Section Dividers inside Boundary for visual clarity (very subtle dashed lines)
    for y_div in [515, 830]:
        for x_d in range(sb_x1 + 10, sb_x2 - 10, 16):
            draw.line([(x_d, y_div), (x_d + 8, y_div)], fill='#e2e8f0', width=1)

    # Ellipse intersection calculation
    def get_ellipse_intersection(src_pt, uc_cx, uc_cy, uc_w, uc_h):
        dx = src_pt[0] - uc_cx
        dy = src_pt[1] - uc_cy
        angle = math.atan2(dy, dx)
        a = uc_w / 2.0
        b = uc_h / 2.0
        ix = uc_cx + a * math.cos(angle)
        iy = uc_cy + b * math.sin(angle)
        return (ix, iy)

    # Draw Actor Associations (Clean straight solid lines)
    for src_id, tgt_id in associations:
        actor_key = src_id.replace('actor_', '').capitalize()
        src_pt = actors[actor_key]['arm_pt']
        tgt_uc = uc_map[tgt_id]
        tgt_pt = get_ellipse_intersection(src_pt, tgt_uc['cx'], tgt_uc['cy'], tgt_uc['w'], tgt_uc['h'])

        draw.line([src_pt, tgt_pt], fill='#000000', width=2)

    # Draw Flow and Includes Connections
    for fl in flows:
        src_uc = uc_map[fl['src']]
        tgt_uc = uc_map[fl['tgt']]
        src_pt = (src_uc['cx'], src_uc['cy'])
        tgt_pt = get_ellipse_intersection(src_pt, tgt_uc['cx'], tgt_uc['cy'], tgt_uc['w'], tgt_uc['h'])
        start_pt = get_ellipse_intersection((tgt_uc['cx'], tgt_uc['cy']), src_uc['cx'], src_uc['cy'], src_uc['w'], src_uc['h'])

        if fl['type'] == 'include':
            # Dashed line
            num_dashes = 14
            for i in range(num_dashes):
                t_s = i / num_dashes
                t_e = (i + 0.5) / num_dashes
                x1 = start_pt[0] + (tgt_pt[0] - start_pt[0]) * t_s
                y1 = start_pt[1] + (tgt_pt[1] - start_pt[1]) * t_s
                x2 = start_pt[0] + (tgt_pt[0] - start_pt[0]) * t_e
                y2 = start_pt[1] + (tgt_pt[1] - start_pt[1]) * t_e
                draw.line([(x1, y1), (x2, y2)], fill='#000000', width=2)

            # Open arrow head
            dx = tgt_pt[0] - start_pt[0]
            dy = tgt_pt[1] - start_pt[1]
            dist = math.hypot(dx, dy)
            if dist > 0:
                ux, uy = dx / dist, dy / dist
                p_back = (tgt_pt[0] - ux * 10, tgt_pt[1] - uy * 10)
                draw.line([(p_back[0] - uy * 5, p_back[1] + ux * 5), tgt_pt], fill='#000000', width=2)
                draw.line([(p_back[0] + uy * 5, p_back[1] - ux * 5), tgt_pt], fill='#000000', width=2)

            # Label '<<includes>>'
            mid_x = (start_pt[0] + tgt_pt[0]) / 2
            mid_y = (start_pt[1] + tgt_pt[1]) / 2 - 12
            bbox = draw.textbbox((0, 0), fl['label'], font=font_inc)
            lw = bbox[2] - bbox[0]
            draw.rectangle([mid_x - lw/2 - 4, mid_y - 2, mid_x + lw/2 + 4, mid_y + 14], fill='#ffffff')
            draw.text((mid_x - lw/2, mid_y), fl['label'], fill='#000000', font=font_inc)
        else:
            # Solid line with filled arrow
            draw.line([start_pt, tgt_pt], fill='#000000', width=2)
            dx = tgt_pt[0] - start_pt[0]
            dy = tgt_pt[1] - start_pt[1]
            dist = math.hypot(dx, dy)
            if dist > 0:
                ux, uy = dx / dist, dy / dist
                p_back = (tgt_pt[0] - ux * 10, tgt_pt[1] - uy * 10)
                p_left = (p_back[0] - uy * 5, p_back[1] + ux * 5)
                p_right = (p_back[0] + uy * 5, p_back[1] - ux * 5)
                draw.polygon([tgt_pt, p_left, p_right], fill='#000000')

    # Draw Use Case Ellipses
    for uc in use_cases:
        cx, cy, w, h = uc['cx'], uc['cy'], uc['w'], uc['h']
        x1 = cx - w // 2
        y1 = cy - h // 2
        x2 = cx + w // 2
        y2 = cy + h // 2

        draw.ellipse([x1, y1, x2, y2], fill='#ffffff', outline='#000000', width=2)

        # Text inside ellipse
        lines = uc['label'].split('\n')
        line_height = 13
        total_text_h = len(lines) * line_height
        cur_y = cy - total_text_h / 2

        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font_uc)
            lw = bbox[2] - bbox[0]
            draw.text((cx - lw / 2, cur_y), line, fill='#000000', font=font_uc)
            cur_y += line_height

    # Draw Stick Figure Actors
    def draw_actor(info):
        cx, cy = info['center'][0], info['center'][1] - 10

        # Head
        draw.ellipse([cx - 16, cy - 36, cx + 16, cy - 4], fill='#ffffff', outline='#000000', width=2)
        # Spine
        draw.line([(cx, cy - 4), (cx, cy + 28)], fill='#000000', width=2)
        # Arms
        draw.line([(cx - 24, cy + 8), (cx + 24, cy + 8)], fill='#000000', width=2)
        # Left leg
        draw.line([(cx, cy + 28), (cx - 20, cy + 64)], fill='#000000', width=2)
        # Right leg
        draw.line([(cx, cy + 28), (cx + 20, cy + 64)], fill='#000000', width=2)

        # Label below
        bbox = draw.textbbox((0, 0), info['label'], font=font_actor)
        lw = bbox[2] - bbox[0]
        draw.text((cx - lw / 2, cy + 72), info['label'], fill='#000000', font=font_actor)

    for a_name, a_info in actors.items():
        draw_actor(a_info)

    img.save(png_path, 'PNG', dpi=(300, 300))
    print(f"Successfully generated updated UML Use Case diagram:")
    print(f" - Draw.io: {drawio_path}")
    print(f" - XML: {xml_path}")
    print(f" - PNG: {png_path}")

if __name__ == '__main__':
    generate_perfect_uml_use_case()
