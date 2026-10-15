import os
import math
import xml.etree.ElementTree as ET
import xml.dom.minidom
from PIL import Image, ImageDraw, ImageFont

def build_uml_use_case_diagram():
    # Sizing for Draw.io canvas & PNG rendering: 1600 x 1150
    canvas_w = 1600
    canvas_h = 1150

    # System boundary box
    sys_box = {
        'x': 340, 'y': 60, 'w': 920, 'h': 1030,
        'title': 'Aquaculture Value Chain Management System with Predictive Analytics'
    }

    # 3 Actors
    actors = {
        'Customer': {
            'id': 'actor_customer', 'label': 'Customer',
            'x': 80, 'y': 240, 'w': 100, 'h': 140,
            'center': (130, 310)
        },
        'Rider': {
            'id': 'actor_rider', 'label': 'Delivery Rider',
            'x': 80, 'y': 700, 'w': 110, 'h': 140,
            'center': (135, 770)
        },
        'Owner': {
            'id': 'actor_owner', 'label': 'Farm Owner\n(Administrator)',
            'x': 1380, 'y': 480, 'w': 130, 'h': 140,
            'center': (1445, 550)
        }
    }

    # Use Cases inside system boundary
    # Positioned logically in 2 columns: Column 1 (x: 400..660), Column 2 (x: 820..1180)
    use_cases = [
        # Authentication (Shared)
        {'id': 'uc_auth', 'label': 'UC1: Authenticate &\nManage Profile', 'cx': 780, 'cy': 130, 'w': 210, 'h': 64},
        
        # Customer facing (Left-Center)
        {'id': 'uc_browse', 'label': 'UC2: Browse Product Catalog\n& Filter Stock', 'cx': 540, 'cy': 230, 'w': 230, 'h': 64},
        {'id': 'uc_order', 'label': 'UC3: Place Order &\nManage Shopping Cart', 'cx': 540, 'cy': 340, 'w': 230, 'h': 64},
        {'id': 'uc_payment', 'label': 'UC4: Process Payment\n(GCash / COD Settlement)', 'cx': 540, 'cy': 470, 'w': 240, 'h': 68},
        {'id': 'uc_tracking', 'label': 'UC5: Track Order Status &\nDelivery Route Map', 'cx': 540, 'cy': 600, 'w': 240, 'h': 68},
        
        # Rider facing (Bottom-Left & Center)
        {'id': 'uc_dispatch', 'label': 'UC6: Manage Courier Dispatch\n& View Delivery Orders', 'cx': 540, 'cy': 730, 'w': 240, 'h': 68},
        {'id': 'uc_pod', 'label': 'UC7: Submit Proof of Delivery\n(POD & Status Update)', 'cx': 540, 'cy': 860, 'w': 240, 'h': 68},

        # Owner / Management facing (Right column)
        {'id': 'uc_farm_ops', 'label': 'UC8: Manage Farm Operations\n(Ponds, Feeding, Harvest)', 'cx': 1020, 'cy': 250, 'w': 250, 'h': 70},
        {'id': 'uc_inventory', 'label': 'UC9: Manage Inventory &\nDual Pricing (pc/kg)', 'cx': 1020, 'cy': 370, 'w': 240, 'h': 68},
        {'id': 'uc_expenses', 'label': 'UC10: Record & Categorize\nOperational Expenses', 'cx': 1020, 'cy': 490, 'w': 240, 'h': 68},
        {'id': 'uc_reports', 'label': 'UC11: Generate Executive\nReports & Audit Trails', 'cx': 1020, 'cy': 610, 'w': 240, 'h': 68},
        {'id': 'uc_predictive', 'label': 'UC12: View Predictive Analytics\n(Sales Forecast & Clustering)', 'cx': 1020, 'cy': 750, 'w': 260, 'h': 72},
        
        # Sub-use case for predictive
        {'id': 'uc_clustering', 'label': 'UC13: Perform K-Means\nCustomer Segmentation', 'cx': 1020, 'cy': 900, 'w': 240, 'h': 64},
    ]

    uc_map = {uc['id']: uc for uc in use_cases}

    # Associations (Actor to Use Case)
    associations = [
        # Customer Associations
        ('actor_customer', 'uc_auth'),
        ('actor_customer', 'uc_browse'),
        ('actor_customer', 'uc_order'),
        ('actor_customer', 'uc_payment'),
        ('actor_customer', 'uc_tracking'),

        # Rider Associations
        ('actor_rider', 'uc_auth'),
        ('actor_rider', 'uc_tracking'),
        ('actor_rider', 'uc_dispatch'),
        ('actor_rider', 'uc_pod'),
        ('actor_rider', 'uc_payment'),

        # Owner Associations
        ('actor_owner', 'uc_auth'),
        ('actor_owner', 'uc_payment'),
        ('actor_owner', 'uc_dispatch'),
        ('actor_owner', 'uc_farm_ops'),
        ('actor_owner', 'uc_inventory'),
        ('actor_owner', 'uc_expenses'),
        ('actor_owner', 'uc_reports'),
        ('actor_owner', 'uc_predictive'),
    ]

    # Stereotypes / Dependencies (<<include>> and <<extend>>)
    dependencies = [
        # UC3 Place Order <<include>> UC4 Process Payment
        {
            'src': 'uc_order', 'tgt': 'uc_payment',
            'stereotype': '<<include>>'
        },
        # UC6 Dispatch <<include>> UC7 POD
        {
            'src': 'uc_dispatch', 'tgt': 'uc_pod',
            'stereotype': '<<include>>'
        },
        # UC12 Predictive <<include>> UC13 Clustering
        {
            'src': 'uc_predictive', 'tgt': 'uc_clustering',
            'stereotype': '<<include>>'
        },
    ]

    # ==================== 1. GENERATE DRAW.IO XML ====================
    mxfile = ET.Element('mxfile', host='app.diagrams.net', version='21.0.0')
    diagram = ET.SubElement(mxfile, 'diagram', name='UML_Use_Case_Diagram', id='uml_uc_avcms')
    model = ET.SubElement(diagram, 'mxGraphModel', dx='1600', dy='1150', grid='1', gridSize='10', guides='1', tooltips='1', connect='1', arrows='1', fold='1', page='1', pageScale='1', pageWidth='1600', pageHeight='1150', math='0', shadow='0')
    root = ET.SubElement(model, 'root')

    ET.SubElement(root, 'mxCell', id='0')
    ET.SubElement(root, 'mxCell', id='1', parent='0')

    # System Boundary Box
    sb_style = (
        "shape=swimlane;startSize=35;rounded=1;arcSize=4;strokeWidth=2;"
        "strokeColor=#1e293b;fillColor=#ffffff;fontFamily=Arial;fontSize=13;"
        "fontStyle=1;fontColor=#0f172a;align=center;collapsible=0;"
    )
    sb_cell = ET.SubElement(root, 'mxCell', id='system_boundary', value=sys_box['title'], style=sb_style, vertex='1', parent='1')
    ET.SubElement(sb_cell, 'mxGeometry', x=str(sys_box['x']), y=str(sys_box['y']), width=str(sys_box['w']), height=str(sys_box['h']), as_='geometry')

    # Add Actors
    for a_name, a_info in actors.items():
        actor_style = (
            "shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;"
            "outlineConnect=0;strokeWidth=2;strokeColor=#0f172a;fillColor=#ffffff;"
            "fontFamily=Arial;fontSize=12;fontStyle=1;fontColor=#0f172a;"
        )
        a_cell = ET.SubElement(root, 'mxCell', id=a_info['id'], value=a_info['label'], style=actor_style, vertex='1', parent='1')
        ET.SubElement(a_cell, 'mxGeometry', x=str(a_info['x']), y=str(a_info['y']), width=str(a_info['w']), height=str(a_info['h']), as_='geometry')

    # Add Use Cases
    for uc in use_cases:
        uc_style = (
            "shape=ellipse;perimeter=ellipsePerimeter;whiteSpace=wrap;html=1;strokeWidth=1.5;"
            "strokeColor=#334155;fillColor=#f8fafc;fontFamily=Arial;fontSize=11;fontStyle=1;"
            "fontColor=#0f172a;align=center;verticalAlign=middle;"
        )
        x_top = uc['cx'] - uc['w'] // 2
        y_top = uc['cy'] - uc['h'] // 2
        uc_cell = ET.SubElement(root, 'mxCell', id=uc['id'], value=uc['label'], style=uc_style, vertex='1', parent='1')
        ET.SubElement(uc_cell, 'mxGeometry', x=str(x_top), y=str(y_top), width=str(uc['w']), height=str(uc['h']), as_='geometry')

    # Add Associations
    for idx, (src_id, tgt_id) in enumerate(associations):
        assoc_style = (
            "endArrow=none;html=1;rounded=0;strokeColor=#1e293b;strokeWidth=1.5;"
        )
        edge = ET.SubElement(root, 'mxCell', id=f'edge_assoc_{idx}', style=assoc_style, edge='1', parent='1', source=src_id, target=tgt_id)
        ET.SubElement(edge, 'mxGeometry', relative='1', as_='geometry')

    # Add Dependencies (<<include>> / <<extend>>)
    for idx, dep in enumerate(dependencies):
        dep_style = (
            "endArrow=open;dashed=1;html=1;rounded=0;strokeColor=#475569;strokeWidth=1.5;"
            "endFill=0;fontFamily=Arial;fontSize=10;fontColor=#475569;align=center;verticalAlign=middle;"
        )
        edge = ET.SubElement(root, 'mxCell', id=f'edge_dep_{idx}', value=dep['stereotype'], style=dep_style, edge='1', parent='1', source=dep['src'], target=dep['tgt'])
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
        font_title = ImageFont.truetype("arialbd.ttf", 18)
        font_header = ImageFont.truetype("arialbd.ttf", 15)
        font_actor = ImageFont.truetype("arialbd.ttf", 14)
        font_uc = ImageFont.truetype("arialbd.ttf", 12)
        font_stereo = ImageFont.truetype("ariali.ttf", 11)
    except:
        font_title = ImageFont.load_default()
        font_header = ImageFont.load_default()
        font_actor = ImageFont.load_default()
        font_uc = ImageFont.load_default()
        font_stereo = ImageFont.load_default()

    # Draw System Boundary Box
    sb_x1, sb_y1 = sys_box['x'], sys_box['y']
    sb_x2, sb_y2 = sb_x1 + sys_box['w'], sb_y1 + sys_box['h']
    draw.rounded_rectangle([sb_x1, sb_y1, sb_x2, sb_y2], radius=12, fill='#fcfdfe', outline='#1e293b', width=2)
    
    # Boundary Header band
    draw.rectangle([sb_x1, sb_y1, sb_x2, sb_y1 + 40], fill='#f1f5f9', outline='#1e293b', width=2)
    # Header text
    bbox = draw.textbbox((0, 0), sys_box['title'], font=font_header)
    tw = bbox[2] - bbox[0]
    draw.text((sb_x1 + (sys_box['w'] - tw) / 2, sb_y1 + 10), sys_box['title'], fill='#0f172a', font=font_header)

    # Draw Associations First (underneath nodes)
    for src_id, tgt_id in associations:
        a_pt = actors[src_id.replace('actor_', '').capitalize()]['center']
        uc_info = uc_map[tgt_id]
        uc_pt = (uc_info['cx'], uc_info['cy'])

        # Calculate perimeter intersection for cleaner look
        dx = uc_pt[0] - a_pt[0]
        dy = uc_pt[1] - a_pt[1]
        dist = math.hypot(dx, dy)
        if dist > 0:
            # clip to ellipse boundary approximately
            clip_x = uc_pt[0] - (dx / dist) * (uc_info['w'] / 2)
            clip_y = uc_pt[1] - (dy / dist) * (uc_info['h'] / 2)
            draw.line([a_pt, (clip_x, clip_y)], fill='#475569', width=2)

    # Draw Dependencies (<<include>>)
    for dep in dependencies:
        src = uc_map[dep['src']]
        tgt = uc_map[dep['tgt']]
        p1 = (src['cx'], src['cy'] + src['h'] / 2)
        p2 = (tgt['cx'], tgt['cy'] - tgt['h'] / 2)

        # Draw dashed line
        num_dashes = 12
        for i in range(num_dashes):
            t_start = i / num_dashes
            t_end = (i + 0.5) / num_dashes
            x_s = p1[0] + (p2[0] - p1[0]) * t_start
            y_s = p1[1] + (p2[1] - p1[1]) * t_start
            x_e = p1[0] + (p2[0] - p1[0]) * t_end
            y_e = p1[1] + (p2[1] - p1[1]) * t_end
            draw.line([(x_s, y_s), (x_e, y_e)], fill='#2563eb', width=2)

        # Draw arrow head at target
        draw.line([(p2[0] - 6, p2[1] - 8), (p2[0], p2[1])], fill='#2563eb', width=2)
        draw.line([(p2[0] + 6, p2[1] - 8), (p2[0], p2[1])], fill='#2563eb', width=2)

        # Label stereotype
        mid_x = (p1[0] + p2[0]) / 2 + 10
        mid_y = (p1[1] + p2[1]) / 2 - 8
        draw.text((mid_x, mid_y), dep['stereotype'], fill='#2563eb', font=font_stereo)

    # Draw Use Case Ellipses
    for uc in use_cases:
        cx, cy, w, h = uc['cx'], uc['cy'], uc['w'], uc['h']
        x1 = cx - w // 2
        y1 = cy - h // 2
        x2 = cx + w // 2
        y2 = cy + h // 2

        # Draw ellipse shadow/fill
        draw.ellipse([x1, y1, x2, y2], fill='#f8fafc', outline='#334155', width=2)

        # Text lines
        lines = uc['label'].split('\n')
        line_height = 14
        total_text_h = len(lines) * line_height
        cur_y = cy - total_text_h / 2

        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font_uc)
            lw = bbox[2] - bbox[0]
            draw.text((cx - lw / 2, cur_y), line, fill='#0f172a', font=font_uc)
            cur_y += line_height

    # Draw Actors (Stick Figure + Label)
    def draw_stick_figure(actor_id, info):
        cx, cy = info['center'][0], info['center'][1] - 20

        # Head
        draw.ellipse([cx - 16, cy - 40, cx + 16, cy - 8], fill='#ffffff', outline='#0f172a', width=3)
        # Body
        draw.line([(cx, cy - 8), (cx, cy + 28)], fill='#0f172a', width=3)
        # Arms
        draw.line([(cx - 24, cy + 6), (cx + 24, cy + 6)], fill='#0f172a', width=3)
        # Legs
        draw.line([(cx, cy + 28), (cx - 20, cy + 62)], fill='#0f172a', width=3)
        draw.line([(cx, cy + 28), (cx + 20, cy + 62)], fill='#0f172a', width=3)

        # Actor label below
        lines = info['label'].split('\n')
        l_y = cy + 70
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font_actor)
            lw = bbox[2] - bbox[0]
            draw.text((cx - lw / 2, l_y), line, fill='#0f172a', font=font_actor)
            l_y += 16

    for a_name, a_info in actors.items():
        draw_stick_figure(a_info['id'], a_info)

    # Diagram Legend / Title Header at Top
    draw.text((30, 20), "UML Use Case Diagram: Aquaculture Value Chain Management System", fill='#0f172a', font=font_title)

    img.save(png_path, 'PNG', dpi=(300, 300))
    print(f"Successfully generated UML Use Case Diagram:")
    print(f" - Draw.io: {drawio_path}")
    print(f" - XML: {xml_path}")
    print(f" - PNG: {png_path}")

if __name__ == '__main__':
    build_uml_use_case_diagram()
