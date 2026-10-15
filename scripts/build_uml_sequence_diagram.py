import os
import xml.etree.ElementTree as ET
import xml.dom.minidom
from PIL import Image, ImageDraw, ImageFont

def build_uml_sequence_diagram():
    # Canvas dimensions: 1700 x 1400
    canvas_w = 1700
    canvas_h = 1400

    # 6 Participants / Lifelines
    participants = [
        {'id': 'p_customer',   'label': 'Customer\n(Actor)',           'type': 'actor', 'x': 100,  'w': 120},
        {'id': 'p_webapp',     'label': 'Web App / UI\n(Boundary)',    'type': 'box',   'x': 380,  'w': 140},
        {'id': 'p_backend',    'label': 'Django Server\n(Controller)', 'type': 'box',   'x': 680,  'w': 150},
        {'id': 'p_database',   'label': 'Database\n(Entity / Storage)','type': 'box',   'x': 980,  'w': 140},
        {'id': 'p_owner',      'label': 'Farm Owner\n(Administrator)', 'type': 'actor', 'x': 1260, 'w': 140},
        {'id': 'p_rider',      'label': 'Delivery Rider\n(Courier)',   'type': 'actor', 'x': 1520, 'w': 120},
    ]

    p_map = {p['id']: p for p in participants}

    # Sequence Messages
    # Each message has: y, from, to, label, type ('call' or 'return' or 'async')
    messages = [
        # Phase 1: Browse & Checkout
        {'y': 180, 'from': 'p_customer', 'to': 'p_webapp',   'label': '1. Browse catalog & select products', 'type': 'call'},
        {'y': 220, 'from': 'p_webapp',   'to': 'p_backend',  'label': '2. GET /api/products/ (fetch stock & pricing)', 'type': 'call'},
        {'y': 260, 'from': 'p_backend',  'to': 'p_database', 'label': '3. Query active inventory & batch metrics', 'type': 'call'},
        {'y': 300, 'from': 'p_database', 'to': 'p_backend',  'label': '4. Return available stock & dual prices', 'type': 'return'},
        {'y': 340, 'from': 'p_backend',  'to': 'p_webapp',   'label': '5. Render product catalog & cart totals', 'type': 'return'},
        {'y': 380, 'from': 'p_customer', 'to': 'p_webapp',   'label': '6. Submit checkout details (address, tier)', 'type': 'call'},
        {'y': 420, 'from': 'p_webapp',   'to': 'p_backend',  'label': '7. POST /checkout/ (create order)', 'type': 'call'},
        {'y': 460, 'from': 'p_backend',  'to': 'p_database', 'label': '8. Insert Order (status: PENDING) & reserve stock', 'type': 'call'},
        {'y': 500, 'from': 'p_database', 'to': 'p_backend',  'label': '9. Order #ID confirmed & saved', 'type': 'return'},

        # Phase 2: Payment & Owner Approval
        {'y': 550, 'from': 'p_customer', 'to': 'p_webapp',   'label': '10. Upload GCash proof / Select COD', 'type': 'call'},
        {'y': 590, 'from': 'p_webapp',   'to': 'p_backend',  'label': '11. POST /payment/submit/ (receipt proof)', 'type': 'call'},
        {'y': 630, 'from': 'p_backend',  'to': 'p_database', 'label': '12. Commit Payment record (UNVERIFIED / COD)', 'type': 'call'},
        {'y': 670, 'from': 'p_backend',  'to': 'p_owner',    'label': '13. Push notification: Pending order & payment', 'type': 'call'},
        {'y': 710, 'from': 'p_owner',    'to': 'p_webapp',   'label': '14. Verify payment proof & click Approve', 'type': 'call'},
        {'y': 750, 'from': 'p_webapp',   'to': 'p_backend',  'label': '15. POST /order/approve/ (order_id)', 'type': 'call'},
        {'y': 790, 'from': 'p_backend',  'to': 'p_database', 'label': '16. Update Order = CONFIRMED, Payment = APPROVED', 'type': 'call'},

        # Phase 3: Rider Dispatch & Tracking
        {'y': 840, 'from': 'p_owner',    'to': 'p_webapp',   'label': '17. Assign order to available Delivery Rider', 'type': 'call'},
        {'y': 880, 'from': 'p_webapp',   'to': 'p_backend',  'label': '18. POST /dispatch/assign/ (rider_id, order_id)', 'type': 'call'},
        {'y': 920, 'from': 'p_backend',  'to': 'p_database', 'label': '19. Insert Dispatch record & route coordinates', 'type': 'call'},
        {'y': 960, 'from': 'p_backend',  'to': 'p_rider',    'label': '20. Push dispatch alert & route waypoints', 'type': 'call'},
        {'y': 1000,'from': 'p_rider',    'to': 'p_backend',  'label': '21. POST /delivery/transit/ (status: IN_TRANSIT)', 'type': 'call'},
        {'y': 1040,'from': 'p_backend',  'to': 'p_customer', 'label': '22. Live tracking feed & ETA notification', 'type': 'call'},

        # Phase 4: Delivery Fulfillment & Analytics Update
        {'y': 1090,'from': 'p_rider',    'to': 'p_customer', 'label': '23. Handover parcel & collect COD cash (if COD)', 'type': 'call'},
        {'y': 1130,'from': 'p_rider',    'to': 'p_webapp',   'label': '24. Capture Proof of Delivery (POD photo/sign)', 'type': 'call'},
        {'y': 1170,'from': 'p_webapp',   'to': 'p_backend',  'label': '25. POST /delivery/complete/ (POD payload)', 'type': 'call'},
        {'y': 1210,'from': 'p_backend',  'to': 'p_database', 'label': '26. Commit stock deduction & mark Order = DELIVERED', 'type': 'call'},
        {'y': 1250,'from': 'p_backend',  'to': 'p_database', 'label': '27. Log sales revenue & refresh predictive models', 'type': 'call'},
        {'y': 1290,'from': 'p_backend',  'to': 'p_customer', 'label': '28. Send official invoice & completion receipt', 'type': 'return'},
        {'y': 1330,'from': 'p_backend',  'to': 'p_owner',    'label': '29. Update dashboard revenue & forecast charts', 'type': 'return'},
    ]

    # Grouping Frames (alt / loop / opt equivalent phases)
    frames = [
        {'y1': 150, 'y2': 520, 'label': 'Phase 1: Catalog Browsing & Cart Checkout', 'fill': '#f8fafc', 'stroke': '#94a3b8'},
        {'y1': 530, 'y2': 810, 'label': 'Phase 2: Payment Settlement & Owner Verification', 'fill': '#f0fdf4', 'stroke': '#86efac'},
        {'y1': 820, 'y2': 1060, 'label': 'Phase 3: Courier Dispatch & Live Transit Tracking', 'fill': '#eff6ff', 'stroke': '#93c5fd'},
        {'y1': 1070,'y2': 1360, 'label': 'Phase 4: Delivery Handover, POD & Analytics Commitment', 'fill': '#faf5ff', 'stroke': '#d8b4fe'},
    ]

    # ==================== 1. GENERATE DRAW.IO XML ====================
    mxfile = ET.Element('mxfile', host='app.diagrams.net', version='21.0.0')
    diagram = ET.SubElement(mxfile, 'diagram', name='UML_Sequence_Diagram', id='uml_seq_avcms')
    model = ET.SubElement(diagram, 'mxGraphModel', dx='1700', dy='1400', grid='1', gridSize='10', guides='1', tooltips='1', connect='1', arrows='1', fold='1', page='1', pageScale='1', pageWidth='1700', pageHeight='1400', math='0', shadow='0')
    root = ET.SubElement(model, 'root')

    ET.SubElement(root, 'mxCell', id='0')
    ET.SubElement(root, 'mxCell', id='1', parent='0')

    # Lifeline participants
    top_y = 60
    life_len = 1310
    for p in participants:
        px = p['x'] - p['w'] // 2
        if p['type'] == 'actor':
            style_head = (
                "shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;"
                "outlineConnect=0;strokeWidth=2;strokeColor=#0f172a;fillColor=#ffffff;"
                "fontFamily=Arial;fontSize=11;fontStyle=1;fontColor=#0f172a;align=center;"
            )
            c = ET.SubElement(root, 'mxCell', id=p['id'], value=p['label'], style=style_head, vertex='1', parent='1')
            ET.SubElement(c, 'mxGeometry', x=str(px), y=str(top_y), width=str(p['w']), height='60', as_='geometry')
        else:
            style_box = (
                "shape=rectangle;rounded=1;arcSize=8;strokeWidth=2;strokeColor=#1e293b;"
                "fillColor=#f1f5f9;fontFamily=Arial;fontSize=11;fontStyle=1;fontColor=#0f172a;align=center;verticalAlign=middle;"
            )
            c = ET.SubElement(root, 'mxCell', id=p['id'], value=p['label'], style=style_box, vertex='1', parent='1')
            ET.SubElement(c, 'mxGeometry', x=str(px), y=str(top_y), width=str(p['w']), height='50', as_='geometry')

        # Lifeline dashed vertical line
        style_life = "endArrow=none;dashed=1;html=1;strokeColor=#64748b;strokeWidth=1.5;"
        edge_life = ET.SubElement(root, 'mxCell', id=f"life_{p['id']}", style=style_life, edge='1', parent='1')
        geo = ET.SubElement(edge_life, 'mxGeometry', relative='1', as_='geometry')
        src_pt = ET.SubElement(geo, 'mxPoint', x=str(p['x']), y=str(top_y + 70), as_='sourcePoint')
        tgt_pt = ET.SubElement(geo, 'mxPoint', x=str(p['x']), y=str(top_y + life_len), as_='targetPoint')

    # Add Grouping Frames
    for idx, fr in enumerate(frames):
        f_style = (
            f"shape=swimlane;startSize=25;rounded=1;arcSize=4;strokeWidth=1.5;strokeColor={fr['stroke']};"
            f"fillColor={fr['fill']};fontFamily=Arial;fontSize=11;fontStyle=1;fontColor=#1e293b;collapsible=0;"
        )
        f_cell = ET.SubElement(root, 'mxCell', id=f'frame_{idx}', value=fr['label'], style=f_style, vertex='1', parent='1')
        ET.SubElement(f_cell, 'mxGeometry', x='40', y=str(fr['y1']), width='1620', height=str(fr['y2'] - fr['y1']), as_='geometry')

    # Add Message Edges
    for idx, msg in enumerate(messages):
        src_x = p_map[msg['from']]['x']
        tgt_x = p_map[msg['to']]['x']
        my = msg['y']

        is_return = (msg['type'] == 'return')
        edge_style = (
            f"endArrow={'open' if is_return else 'block'};dashed={1 if is_return else 0};"
            f"html=1;strokeColor={'#2563eb' if is_return else '#0f172a'};strokeWidth=1.5;"
            f"fontFamily=Arial;fontSize=10;fontColor={'#1d4ed8' if is_return else '#0f172a'};align=center;verticalAlign=bottom;"
        )
        edge = ET.SubElement(root, 'mxCell', id=f'msg_{idx}', value=msg['label'], style=edge_style, edge='1', parent='1')
        geo = ET.SubElement(edge, 'mxGeometry', relative='1', as_='geometry')
        ET.SubElement(geo, 'mxPoint', x=str(src_x), y=str(my), as_='sourcePoint')
        ET.SubElement(geo, 'mxPoint', x=str(tgt_x), y=str(my), as_='targetPoint')

    xml_str = ET.tostring(mxfile, encoding='utf-8')
    dom = xml.dom.minidom.parseString(xml_str)
    pretty_xml = dom.toprettyxml(indent='  ')

    os.makedirs('diagram', exist_ok=True)
    drawio_path = os.path.join('diagram', 'UML_Sequence_Diagram.drawio')
    xml_path = os.path.join('diagram', 'UML_Sequence_Diagram.xml')
    png_path = os.path.join('diagram', 'UML_Sequence_Diagram.png')

    with open(drawio_path, 'w', encoding='utf-8') as f:
        f.write(pretty_xml)
    with open(xml_path, 'w', encoding='utf-8') as f:
        f.write(pretty_xml)

    # ==================== 2. RENDER CRISP PNG ====================
    img = Image.new('RGB', (canvas_w, canvas_h), '#ffffff')
    draw = ImageDraw.Draw(img)

    try:
        font_title = ImageFont.truetype("arialbd.ttf", 17)
        font_head = ImageFont.truetype("arialbd.ttf", 12)
        font_part = ImageFont.truetype("arialbd.ttf", 11)
        font_msg = ImageFont.truetype("arial.ttf", 10)
        font_frame = ImageFont.truetype("arialbd.ttf", 11)
    except:
        font_title = ImageFont.load_default()
        font_head = ImageFont.load_default()
        font_part = ImageFont.load_default()
        font_msg = ImageFont.load_default()
        font_frame = ImageFont.load_default()

    # Draw Title Header
    draw.text((40, 16), "UML Sequence Diagram: Order Placement, Payment Verification & Courier Dispatch Flow", fill='#0f172a', font=font_title)

    # Draw Phase Frames
    for fr in frames:
        draw.rounded_rectangle([40, fr['y1'], canvas_w - 40, fr['y2']], radius=8, fill=fr['fill'], outline=fr['stroke'], width=1)
        # Header banner
        draw.rectangle([40, fr['y1'], canvas_w - 40, fr['y1'] + 22], fill=fr['stroke'], outline=fr['stroke'])
        draw.text((50, fr['y1'] + 4), fr['label'], fill='#0f172a', font=font_frame)

    # Draw Lifelines
    for p in participants:
        px = p['x']
        # Vertical dashed lifeline
        num_dashes = 60
        y_start = top_y + 60
        y_end = top_y + life_len
        for i in range(num_dashes):
            t_s = i / num_dashes
            t_e = (i + 0.5) / num_dashes
            y1 = y_start + (y_end - y_start) * t_s
            y2 = y_start + (y_end - y_start) * t_e
            draw.line([(px, y1), (px, y2)], fill='#94a3b8', width=1)

    # Draw Participant Boxes / Actors
    for p in participants:
        px = p['x']
        pw = p['w']
        x1 = px - pw // 2
        x2 = px + pw // 2
        y1 = top_y
        y2 = top_y + 48

        if p['type'] == 'actor':
            # Draw Actor Stick Figure
            cx, cy = px, y1 + 18
            draw.ellipse([cx - 10, cy - 14, cx + 10, cy + 6], fill='#ffffff', outline='#0f172a', width=2)
            draw.line([(cx, cy + 6), (cx, cy + 24)], fill='#0f172a', width=2)
            draw.line([(cx - 14, cy + 12), (cx + 14, cy + 12)], fill='#0f172a', width=2)
            draw.line([(cx, cy + 24), (cx - 10, cy + 42)], fill='#0f172a', width=2)
            draw.line([(cx, cy + 24), (cx + 10, cy + 42)], fill='#0f172a', width=2)

            # Text
            lines = p['label'].split('\n')
            ly = cy + 46
            for l in lines:
                bbox = draw.textbbox((0, 0), l, font=font_part)
                lw = bbox[2] - bbox[0]
                draw.text((cx - lw / 2, ly), l, fill='#0f172a', font=font_part)
                ly += 13
        else:
            # Box
            draw.rounded_rectangle([x1, y1, x2, y2], radius=6, fill='#f1f5f9', outline='#1e293b', width=2)
            lines = p['label'].split('\n')
            ly = y1 + 8
            for l in lines:
                bbox = draw.textbbox((0, 0), l, font=font_part)
                lw = bbox[2] - bbox[0]
                draw.text((px - lw / 2, ly), l, fill='#0f172a', font=font_part)
                ly += 13

    # Draw Messages
    for msg in messages:
        src_x = p_map[msg['from']]['x']
        tgt_x = p_map[msg['to']]['x']
        my = msg['y']
        is_return = (msg['type'] == 'return')
        color = '#2563eb' if is_return else '#0f172a'

        if is_return:
            # Dashed line
            num_dashes = 15
            for i in range(num_dashes):
                t_s = i / num_dashes
                t_e = (i + 0.5) / num_dashes
                x1 = src_x + (tgt_x - src_x) * t_s
                x2 = src_x + (tgt_x - src_x) * t_e
                draw.line([(x1, my), (x2, my)], fill=color, width=2)
        else:
            draw.line([(src_x, my), (tgt_x, my)], fill=color, width=2)

        # Arrow head
        dx = 1 if tgt_x > src_x else -1
        if is_return:
            # Open arrow
            draw.line([(tgt_x - dx * 8, my - 5), (tgt_x, my)], fill=color, width=2)
            draw.line([(tgt_x - dx * 8, my + 5), (tgt_x, my)], fill=color, width=2)
        else:
            # Filled arrow
            draw.polygon([(tgt_x, my), (tgt_x - dx * 9, my - 5), (tgt_x - dx * 9, my + 5)], fill=color)

        # Text label above line
        mid_x = (src_x + tgt_x) / 2
        bbox = draw.textbbox((0, 0), msg['label'], font=font_msg)
        lw = bbox[2] - bbox[0]
        tx = mid_x - lw / 2
        # Keep inside canvas
        tx = max(tx, min(src_x, tgt_x) + 10)
        draw.text((tx, my - 16), msg['label'], fill=color, font=font_msg)

    img.save(png_path, 'PNG', dpi=(300, 300))
    print(f"Successfully generated UML Sequence Diagram:")
    print(f" - Draw.io: {drawio_path}")
    print(f" - XML: {xml_path}")
    print(f" - PNG: {png_path}")

if __name__ == '__main__':
    build_uml_sequence_diagram()
