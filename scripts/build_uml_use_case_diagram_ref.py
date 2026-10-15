import os
import math
import xml.etree.ElementTree as ET
import xml.dom.minidom
from PIL import Image, ImageDraw, ImageFont

def generate_uml_use_case_diagram():
    # Canvas size: 1400 x 950
    canvas_w = 1400
    canvas_h = 950

    # System boundary box
    sys_box = {
        'x': 320, 'y': 50, 'w': 1020, 'h': 840,
        'title': 'Aquaculture Value Chain Management System with Predictive Analytics'
    }

    # Actors on Left
    actors = {
        'Owner': {
            'id': 'actor_owner', 'label': 'Owner',
            'x': 80, 'y': 150, 'w': 100, 'h': 130,
            'center': (130, 215), 'arm_pt': (180, 205)
        },
        'Customer': {
            'id': 'actor_customer', 'label': 'Customer',
            'x': 80, 'y': 440, 'w': 100, 'h': 130,
            'center': (130, 505), 'arm_pt': (180, 495)
        },
        'Rider': {
            'id': 'actor_rider', 'label': 'Rider',
            'x': 80, 'y': 710, 'w': 100, 'h': 130,
            'center': (130, 775), 'arm_pt': (180, 765)
        }
    }

    # Use Cases positioned in clean columns
    # Column 1 (Primary Hubs): x ~ 480..620
    # Column 2 (Sub / Downstream operations): x ~ 780..940
    # Column 3 (Advanced / Secondary): x ~ 1080..1240
    use_cases = [
        # Central Core / Authentication
        {'id': 'uc_login',       'label': 'Login',                        'cx': 480, 'cy': 380, 'w': 180, 'h': 64},
        
        # Upper Column 1 (Manager/Owner Hubs)
        {'id': 'uc_dashboard',   'label': 'View Dashboard',               'cx': 580, 'cy': 130, 'w': 200, 'h': 64},
        {'id': 'uc_purchase',    'label': 'Customer Purchase',            'cx': 580, 'cy': 250, 'w': 210, 'h': 64},
        {'id': 'uc_process_order','label': 'Process Sales Order',         'cx': 600, 'cy': 500, 'w': 210, 'h': 64},
        {'id': 'uc_inventory',   'label': 'Update Inventory',             'cx': 580, 'cy': 630, 'w': 200, 'h': 64},
        {'id': 'uc_dispatch',    'label': 'Courier Dispatch',             'cx': 560, 'cy': 760, 'w': 200, 'h': 64},

        # Column 2: Downstream Operational Use Cases
        {'id': 'uc_stock_batch', 'label': 'Create Stock Batch',           'cx': 960, 'cy': 130, 'w': 210, 'h': 64},
        {'id': 'uc_assign_ponds','label': 'Assign Ponds',                 'cx': 960, 'cy': 270, 'w': 200, 'h': 64},
        {'id': 'uc_export_report','label': 'Export Report',               'cx': 960, 'cy': 430, 'w': 200, 'h': 64},
        {'id': 'uc_predictive',  'label': 'Sales Forecasting',            'cx': 960, 'cy': 580, 'w': 210, 'h': 64},
        {'id': 'uc_delivery_pod','label': 'Confirm Delivery (POD)',       'cx': 960, 'cy': 760, 'w': 220, 'h': 64},
    ]

    uc_map = {uc['id']: uc for uc in use_cases}

    # Association Lines (Solid line from Actor arm to Use Case)
    associations = [
        # Owner Associations
        ('actor_owner', 'uc_dashboard'),
        ('actor_owner', 'uc_login'),
        ('actor_owner', 'uc_process_order'),
        ('actor_owner', 'uc_inventory'),

        # Customer Associations
        ('actor_customer', 'uc_login'),
        ('actor_customer', 'uc_purchase'),

        # Rider Associations
        ('actor_rider', 'uc_login'),
        ('actor_rider', 'uc_dispatch'),
        ('actor_rider', 'uc_delivery_pod'),
    ]

    # Includes / Extends Dependencies (Dashed arrow with <<includes>>)
    includes = [
        {'src': 'uc_login', 'tgt': 'uc_purchase',      'label': 'includes'},
        {'src': 'uc_login', 'tgt': 'uc_process_order', 'label': 'includes'},
        {'src': 'uc_login', 'tgt': 'uc_inventory',     'label': 'includes'},
        {'src': 'uc_purchase', 'tgt': 'uc_process_order', 'label': 'includes'},
        {'src': 'uc_dispatch', 'tgt': 'uc_delivery_pod',  'label': 'includes'},
    ]

    # Flow / Extends Connections between Use Cases (Solid line or arrow between use cases)
    uc_flows = [
        {'src': 'uc_dashboard',    'tgt': 'uc_stock_batch'},
        {'src': 'uc_purchase',     'tgt': 'uc_assign_ponds'},
        {'src': 'uc_process_order','tgt': 'uc_export_report'},
        {'src': 'uc_process_order','tgt': 'uc_predictive'},
        {'src': 'uc_inventory',    'tgt': 'uc_stock_batch'},
    ]

    # ==================== 1. GENERATE DRAW.IO XML ====================
    mxfile = ET.Element('mxfile', host='app.diagrams.net', version='21.0.0')
    diagram = ET.SubElement(mxfile, 'diagram', name='UML_Use_Case_Diagram', id='uml_uc_avcms_clean')
    model = ET.SubElement(diagram, 'mxGraphModel', dx='1400', dy='950', grid='1', gridSize='10', guides='1', tooltips='1', connect='1', arrows='1', fold='1', page='1', pageScale='1', pageWidth='1400', pageHeight='950', math='0', shadow='0')
    root = ET.SubElement(model, 'root')

    ET.SubElement(root, 'mxCell', id='0')
    ET.SubElement(root, 'mxCell', id='1', parent='0')

    # System Boundary Box
    sb_style = (
        "shape=swimlane;startSize=30;rounded=0;strokeWidth=2;"
        "strokeColor=#000000;fillColor=#ffffff;fontFamily=Arial;fontSize=12;"
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

    # Add Actor Associations (with solid arrows pointing to Use Cases)
    for idx, (src_id, tgt_id) in enumerate(associations):
        assoc_style = (
            "endArrow=block;endFill=1;html=1;rounded=0;strokeColor=#000000;strokeWidth=1.2;"
        )
        edge = ET.SubElement(root, 'mxCell', id=f'edge_assoc_{idx}', style=assoc_style, edge='1', parent='1', source=src_id, target=tgt_id)
        ET.SubElement(edge, 'mxGeometry', relative='1', as_='geometry')

    # Add Includes Dependencies (dashed arrows with 'includes')
    for idx, inc in enumerate(includes):
        inc_style = (
            "endArrow=open;dashed=1;html=1;rounded=0;strokeColor=#000000;strokeWidth=1.2;"
            "endFill=0;fontFamily=Arial;fontSize=10;fontColor=#000000;align=center;verticalAlign=middle;"
        )
        edge = ET.SubElement(root, 'mxCell', id=f'edge_inc_{idx}', value=inc['label'], style=inc_style, edge='1', parent='1', source=inc['src'], target=inc['tgt'])
        ET.SubElement(edge, 'mxGeometry', relative='1', as_='geometry')

    # Add Use Case to Use Case Connections
    for idx, flow in enumerate(uc_flows):
        flow_style = (
            "endArrow=block;endFill=1;html=1;rounded=0;strokeColor=#000000;strokeWidth=1.2;"
        )
        edge = ET.SubElement(root, 'mxCell', id=f'edge_flow_{idx}', style=flow_style, edge='1', parent='1', source=flow['src'], target=flow['tgt'])
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
    except:
        font_title = ImageFont.load_default()
        font_actor = ImageFont.load_default()
        font_uc = ImageFont.load_default()
        font_inc = ImageFont.load_default()

    # Draw System Boundary Box (Clean Rectangle like the user image)
    sb_x1, sb_y1 = sys_box['x'], sys_box['y']
    sb_x2, sb_y2 = sb_x1 + sys_box['w'], sb_y1 + sys_box['h']
    draw.rectangle([sb_x1, sb_y1, sb_x2, sb_y2], fill='#ffffff', outline='#000000', width=2)
    
    # Boundary Title
    draw.text((sb_x1 + 20, sb_y1 + 10), sys_box['title'], fill='#000000', font=font_title)

    # Function to calculate ellipse edge intersection point from a source point
    def get_ellipse_intersection(src_pt, uc_cx, uc_cy, uc_w, uc_h):
        dx = src_pt[0] - uc_cx
        dy = src_pt[1] - uc_cy
        angle = math.atan2(dy, dx)
        a = uc_w / 2.0
        b = uc_h / 2.0
        # point on ellipse: (a*cos, b*sin)
        ix = uc_cx + a * math.cos(angle)
        iy = uc_cy + b * math.sin(angle)
        return (ix, iy)

    # Draw Actor Associations (Arrows from Actor Arm to Use Case)
    for src_id, tgt_id in associations:
        actor_key = src_id.replace('actor_', '').capitalize()
        src_pt = actors[actor_key]['arm_pt']
        tgt_uc = uc_map[tgt_id]
        tgt_pt = get_ellipse_intersection(src_pt, tgt_uc['cx'], tgt_uc['cy'], tgt_uc['w'], tgt_uc['h'])

        # Draw line
        draw.line([src_pt, tgt_pt], fill='#000000', width=2)
        # Draw Arrow head
        dx = tgt_pt[0] - src_pt[0]
        dy = tgt_pt[1] - src_pt[1]
        dist = math.hypot(dx, dy)
        if dist > 0:
            ux, uy = dx / dist, dy / dist
            p_back = (tgt_pt[0] - ux * 10, tgt_pt[1] - uy * 10)
            p_left = (p_back[0] - uy * 5, p_back[1] + ux * 5)
            p_right = (p_back[0] + uy * 5, p_back[1] - ux * 5)
            draw.polygon([tgt_pt, p_left, p_right], fill='#000000')

    # Draw Use Case to Use Case Connections
    for flow in uc_flows:
        src_uc = uc_map[flow['src']]
        tgt_uc = uc_map[flow['tgt']]
        src_pt = (src_uc['cx'], src_uc['cy'])
        tgt_pt = get_ellipse_intersection(src_pt, tgt_uc['cx'], tgt_uc['cy'], tgt_uc['w'], tgt_uc['h'])
        start_pt = get_ellipse_intersection((tgt_uc['cx'], tgt_uc['cy']), src_uc['cx'], src_uc['cy'], src_uc['w'], src_uc['h'])

        draw.line([start_pt, tgt_pt], fill='#000000', width=2)
        # Arrow head
        dx = tgt_pt[0] - start_pt[0]
        dy = tgt_pt[1] - start_pt[1]
        dist = math.hypot(dx, dy)
        if dist > 0:
            ux, uy = dx / dist, dy / dist
            p_back = (tgt_pt[0] - ux * 10, tgt_pt[1] - uy * 10)
            p_left = (p_back[0] - uy * 5, p_back[1] + ux * 5)
            p_right = (p_back[0] + uy * 5, p_back[1] - ux * 5)
            draw.polygon([tgt_pt, p_left, p_right], fill='#000000')

    # Draw Includes Dependencies (Dashed arrow + 'includes')
    for inc in includes:
        src_uc = uc_map[inc['src']]
        tgt_uc = uc_map[inc['tgt']]
        src_pt = (src_uc['cx'], src_uc['cy'])
        tgt_pt = get_ellipse_intersection(src_pt, tgt_uc['cx'], tgt_uc['cy'], tgt_uc['w'], tgt_uc['h'])
        start_pt = get_ellipse_intersection((tgt_uc['cx'], tgt_uc['cy']), src_uc['cx'], src_uc['cy'], src_uc['w'], src_uc['h'])

        # Dashed line
        num_dashes = 10
        for i in range(num_dashes):
            t_s = i / num_dashes
            t_e = (i + 0.5) / num_dashes
            x1 = start_pt[0] + (tgt_pt[0] - start_pt[0]) * t_s
            y1 = start_pt[1] + (tgt_pt[1] - start_pt[1]) * t_s
            x2 = start_pt[0] + (tgt_pt[0] - start_pt[0]) * t_e
            y2 = start_pt[1] + (tgt_pt[1] - start_pt[1]) * t_e
            draw.line([(x1, y1), (x2, y2)], fill='#000000', width=2)

        # Arrow head
        dx = tgt_pt[0] - start_pt[0]
        dy = tgt_pt[1] - start_pt[1]
        dist = math.hypot(dx, dy)
        if dist > 0:
            ux, uy = dx / dist, dy / dist
            p_back = (tgt_pt[0] - ux * 10, tgt_pt[1] - uy * 10)
            draw.line([(p_back[0] - uy * 5, p_back[1] + ux * 5), tgt_pt], fill='#000000', width=2)
            draw.line([(p_back[0] + uy * 5, p_back[1] - ux * 5), tgt_pt], fill='#000000', width=2)

        # Label 'includes'
        mid_x = (start_pt[0] + tgt_pt[0]) / 2
        mid_y = (start_pt[1] + tgt_pt[1]) / 2 - 12
        bbox = draw.textbbox((0, 0), inc['label'], font=font_inc)
        lw = bbox[2] - bbox[0]
        # White background behind text for readability
        draw.rectangle([mid_x - lw/2 - 2, mid_y - 2, mid_x + lw/2 + 2, mid_y + 14], fill='#ffffff')
        draw.text((mid_x - lw/2, mid_y), inc['label'], fill='#000000', font=font_inc)

    # Draw Use Case Ellipses
    for uc in use_cases:
        cx, cy, w, h = uc['cx'], uc['cy'], uc['w'], uc['h']
        x1 = cx - w // 2
        y1 = cy - h // 2
        x2 = cx + w // 2
        y2 = cy + h // 2

        draw.ellipse([x1, y1, x2, y2], fill='#ffffff', outline='#000000', width=2)

        # Text
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
    print(f"Successfully generated clean UML Use Case diagram matching reference style:")
    print(f" - Draw.io: {drawio_path}")
    print(f" - XML: {xml_path}")
    print(f" - PNG: {png_path}")

if __name__ == '__main__':
    generate_uml_use_case_diagram()
