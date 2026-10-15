import os
import xml.etree.ElementTree as ET
import xml.dom.minidom
from PIL import Image, ImageDraw, ImageFont

def build_perfect_drawio_level_0():
    # Sizing for Draw.io & Image: 1400 x 620
    canvas_w = 1400
    canvas_h = 620

    # 1. Process 0 (Center)
    proc_0 = {
        'id': 'proc_0',
        'x': 480, 'y': 100, 'w': 440, 'h': 140
    }

    # 2. External Entities
    entities = {
        'Customer': {'id': 'entity_customer', 'label': 'Customer', 'x': 40,   'y': 125, 'w': 160, 'h': 90},
        'Owner':    {'id': 'entity_owner',    'label': 'Owner',    'x': 1200, 'y': 125, 'w': 160, 'h': 90},
        'Rider':    {'id': 'entity_rider',    'label': 'Rider',    'x': 600,  'y': 440, 'w': 200, 'h': 80},
    }

    # 3. Flows with explicit Draw.io Port Attachment points (exitX/exitY and entryX/entryY)
    flows = [
        # Customer -> Process 0 (Upper horizontal line)
        {
            'id': 'flow_cust_sys',
            'src': 'entity_customer', 'tgt': 'proc_0',
            'label': 'Customer info, Order Details, Delivery option, Payment method',
            'exitX': '1', 'exitY': '0.28', 'entryX': '0', 'entryY': '0.28',
            'lx_offset': '0', 'ly_offset': '-16',
            'points': [(200, 150), (480, 150)],
            'img_lx': 340, 'img_ly': 136
        },
        # Process 0 -> Customer (Lower horizontal line)
        {
            'id': 'flow_sys_cust',
            'src': 'proc_0', 'tgt': 'entity_customer',
            'label': 'Order confirmation, Product Availability, Order tracking, Billing receipt',
            'exitX': '0', 'exitY': '0.72', 'entryX': '1', 'entryY': '0.72',
            'lx_offset': '0', 'ly_offset': '16',
            'points': [(480, 202), (200, 202)],
            'img_lx': 340, 'img_ly': 216
        },
        # Process 0 -> Owner (Upper horizontal line)
        {
            'id': 'flow_sys_owner',
            'src': 'proc_0', 'tgt': 'entity_owner',
            'label': 'Status report, Sales summary, Sales forecast, Low stock alert',
            'exitX': '1', 'exitY': '0.28', 'entryX': '0', 'entryY': '0.28',
            'lx_offset': '0', 'ly_offset': '-16',
            'points': [(920, 150), (1200, 150)],
            'img_lx': 1060, 'img_ly': 136
        },
        # Owner -> Process 0 (Lower horizontal line)
        {
            'id': 'flow_owner_sys',
            'src': 'entity_owner', 'tgt': 'proc_0',
            'label': 'Pond & feed data, Stock updates, Harvest schedule, Expense records',
            'exitX': '0', 'exitY': '0.72', 'entryX': '1', 'entryY': '0.72',
            'lx_offset': '0', 'ly_offset': '16',
            'points': [(1200, 202), (920, 202)],
            'img_lx': 1060, 'img_ly': 216
        },
        # Process 0 -> Rider (Left vertical line)
        {
            'id': 'flow_sys_rider',
            'src': 'proc_0', 'tgt': 'entity_rider',
            'label': 'Delivery assignment, Route map,\nCustomer delivery',
            'exitX': '0.38', 'exitY': '1', 'entryX': '0.25', 'entryY': '0',
            'lx_offset': '-70', 'ly_offset': '0',
            'points': [(647, 240), (647, 440)],
            'img_lx': 540, 'img_ly': 340
        },
        # Rider -> Process 0 (Right vertical line)
        {
            'id': 'flow_rider_sys',
            'src': 'entity_rider', 'tgt': 'proc_0',
            'label': 'Delivery status, Completion confirm,\nLocation update',
            'exitX': '0.75', 'exitY': '0', 'entryX': '0.62', 'entryY': '1',
            'lx_offset': '70', 'ly_offset': '0',
            'points': [(753, 440), (753, 240)],
            'img_lx': 860, 'img_ly': 340
        },
    ]

    # =========================================================================
    # 1. DRAW.IO XML GENERATION
    # =========================================================================
    mxfile = ET.Element('mxfile', {
        'host': 'app.diagrams.net',
        'modified': '2026-09-23T09:00:00.000Z',
        'agent': 'Antigravity Exact DFD Engine',
        'version': '24.0.0',
        'type': 'device'
    })
    diagram = ET.SubElement(mxfile, 'diagram', {
        'id': 'level_0_context_perfect',
        'name': 'Level 0 Context Diagram'
    })
    mxGraphModel = ET.SubElement(diagram, 'mxGraphModel', {
        'dx': '1400', 'dy': '620', 'grid': '0', 'gridSize': '10',
        'guides': '1', 'tooltips': '1', 'connect': '1', 'arrows': '1',
        'fold': '1', 'page': '0', 'pageScale': '1',
        'pageWidth': str(canvas_w), 'pageHeight': str(canvas_h),
        'background': '#FFFFFF', 'pageColor': '#FFFFFF', 'math': '0', 'shadow': '0'
    })
    root = ET.SubElement(mxGraphModel, 'root')
    ET.SubElement(root, 'mxCell', {'id': '0'})
    ET.SubElement(root, 'mxCell', {'id': '1', 'parent': '0'})

    # Process 0 Gane & Sarson Box
    p_box = ET.SubElement(root, 'mxCell', {
        'id': proc_0['id'],
        'value': '',
        'style': 'swimlane;startSize=28;horizontal=1;childLayout=stackLayout;horizontalStack=0;resizeParent=1;resizeParentMax=0;resizeLast=0;collapsible=0;marginBottom=0;html=1;whiteSpace=wrap;rounded=1;arcSize=14;strokeColor=#000000;strokeWidth=1.8;fillColor=#FFFFFF;fontFamily=Arial;fontSize=12;fontColor=#000000;align=center;',
        'vertex': '1', 'parent': '1'
    })
    ET.SubElement(p_box, 'mxGeometry', {
        'x': str(proc_0['x']), 'y': str(proc_0['y']),
        'width': str(proc_0['w']), 'height': str(proc_0['h']), 'as': 'geometry'
    })

    # Header 0 Cell
    p_hdr = ET.SubElement(root, 'mxCell', {
        'id': f"{proc_0['id']}_hdr",
        'value': '<b>0</b>',
        'style': 'text;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;spacingLeft=4;spacingRight=4;overflow=hidden;rotatable=0;points=[[0,0.5],[1,0.5]];portConstraint=eastwest;fontColor=#000000;fontFamily=Arial;fontSize=13;fontStyle=1;',
        'vertex': '1', 'parent': proc_0['id']
    })
    ET.SubElement(p_hdr, 'mxGeometry', {'width': str(proc_0['w']), 'height': '28', 'as': 'geometry'})

    # Body Cell
    p_body = ET.SubElement(root, 'mxCell', {
        'id': f"{proc_0['id']}_body",
        'value': '<b>Aquaculture Value Chain Management<br/>System With Predictive Analytics</b>',
        'style': 'text;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;spacingLeft=4;spacingRight=4;overflow=hidden;rotatable=0;points=[[0,0.5],[1,0.5]];portConstraint=eastwest;fontColor=#000000;fontFamily=Arial;fontSize=12;fontStyle=1;',
        'vertex': '1', 'parent': proc_0['id']
    })
    ET.SubElement(p_body, 'mxGeometry', {'y': '28', 'width': str(proc_0['w']), 'height': str(proc_0['h'] - 28), 'as': 'geometry'})

    # Entities
    for key, ent in entities.items():
        e_cell = ET.SubElement(root, 'mxCell', {
            'id': ent['id'],
            'value': f"<b>{ent['label']}</b>",
            'style': 'rounded=0;whiteSpace=wrap;html=1;strokeColor=#000000;strokeWidth=1.8;fillColor=#FFFFFF;fontColor=#000000;fontFamily=Arial;fontSize=14;fontStyle=1;align=center;verticalAlign=middle;',
            'vertex': '1', 'parent': '1'
        })
        ET.SubElement(e_cell, 'mxGeometry', {
            'x': str(ent['x']), 'y': str(ent['y']),
            'width': str(ent['w']), 'height': str(ent['h']), 'as': 'geometry'
        })

    # Edges with explicit port constraints
    for f in flows:
        edge_style = (
            f"edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;"
            f"exitX={f['exitX']};exitY={f['exitY']};exitDx=0;exitDy=0;"
            f"entryX={f['entryX']};entryY={f['entryY']};entryDx=0;entryDy=0;"
            f"strokeColor=#000000;strokeWidth=1.4;"
            f"endArrow=classic;endFill=1;endSize=6;"
            f"fontColor=#000000;fontSize=9.5;fontFamily=Arial;fontStyle=1;"
            f"labelBackgroundColor=#FFFFFF;labelBorderColor=none;"
        )
        f_cell = ET.SubElement(root, 'mxCell', {
            'id': f['id'],
            'value': f['label'],
            'style': edge_style,
            'edge': '1', 'parent': '1', 'source': f['src'], 'target': f['tgt']
        })
        geom = ET.SubElement(f_cell, 'mxGeometry', {
            'x': f['lx_offset'], 'y': f['ly_offset'], 'relative': '1', 'as': 'geometry'
        })
        p_offset = ET.SubElement(geom, 'mxPoint', {'as': 'offset'})
        p_offset.set('x', f['lx_offset'])
        p_offset.set('y', f['ly_offset'])

    raw_str = ET.tostring(mxfile, encoding='utf-8')
    parsed = xml.dom.minidom.parseString(raw_str)
    pretty_xml = parsed.toprettyxml(indent='    ')
    clean_lines = [l for l in pretty_xml.split('\n') if l.strip()]
    final_xml = '\n'.join(clean_lines)

    out_drawio = r'c:\Users\kymer\Desktop\Lantad ACarwfish Django\diagram\Level_0_Context_Diagram.drawio'
    out_xml = r'c:\Users\kymer\Desktop\Lantad ACarwfish Django\diagram\Level_0_Context_Diagram.xml'

    with open(out_drawio, 'w', encoding='utf-8') as f:
        f.write(final_xml)
    with open(out_xml, 'w', encoding='utf-8') as f:
        f.write(final_xml)

    # =========================================================================
    # 2. HIGH RESOLUTION PIXEL-PERFECT PNG RENDER
    # =========================================================================
    scale = 3
    img = Image.new('RGB', (canvas_w * scale, canvas_h * scale), '#FFFFFF')
    draw = ImageDraw.Draw(img)

    try:
        font_proc_num = ImageFont.truetype("arialbd.ttf", 13 * scale)
        font_proc_name = ImageFont.truetype("arialbd.ttf", 12 * scale)
        font_ent = ImageFont.truetype("arialbd.ttf", 14 * scale)
        font_flow = ImageFont.truetype("arialbd.ttf", 9 * scale)
    except:
        font_proc_num = font_proc_name = font_ent = font_flow = ImageFont.load_default()

    box_stroke = max(2, int(1.8 * scale))
    edge_w = max(2, int(1.4 * scale))

    # Process 0
    px, py = proc_0['x'] * scale, proc_0['y'] * scale
    pw, ph = proc_0['w'] * scale, proc_0['h'] * scale
    r = 16 * scale
    draw.rounded_rectangle([px, py, px + pw, py + ph], radius=r, fill='#FFFFFF', outline='#000000', width=box_stroke)
    draw.line([(px, py + 28 * scale), (px + pw, py + 28 * scale)], fill='#000000', width=box_stroke)

    # Number 0
    nbox = draw.textbbox((0, 0), "0", font=font_proc_num)
    nw = nbox[2] - nbox[0]
    draw.text((px + (pw - nw) / 2, py + 5 * scale), "0", fill='#000000', font=font_proc_num)

    # Process Name
    lines = ["Aquaculture Value Chain Management", "System With Predictive Analytics"]
    lh = 16 * scale
    start_y = py + 44 * scale
    for i, line in enumerate(lines):
        lbox = draw.textbbox((0, 0), line, font=font_proc_name)
        lw = lbox[2] - lbox[0]
        draw.text((px + (pw - lw) / 2, start_y + i * lh), line, fill='#000000', font=font_proc_name)

    # Entities
    for key, ent in entities.items():
        ex, ey = ent['x'] * scale, ent['y'] * scale
        ew, eh = ent['w'] * scale, ent['h'] * scale
        draw.rectangle([ex, ey, ex + ew, ey + eh], fill='#FFFFFF', outline='#000000', width=box_stroke)
        lbox = draw.textbbox((0, 0), ent['label'], font=font_ent)
        lw, lh_txt = lbox[2] - lbox[0], lbox[3] - lbox[1]
        draw.text((ex + (ew - lw) / 2, ey + (eh - lh_txt) / 2), ent['label'], fill='#000000', font=font_ent)

    # Edges
    for f in flows:
        pts = [(p[0] * scale, p[1] * scale) for p in f['points']]
        for i in range(len(pts) - 1):
            draw.line([pts[i], pts[i+1]], fill='#000000', width=edge_w)

        # Arrowhead
        p_last = pts[-1]
        p_prev = pts[-2]
        c_len = 9 * scale
        c_w = 6 * scale
        dx = p_last[0] - p_prev[0]
        dy = p_last[1] - p_prev[1]

        if dx > 0:
            draw.polygon([p_last, (p_last[0] - c_len, p_last[1] - c_w), (p_last[0] - c_len, p_last[1] + c_w)], fill='#000000')
        elif dx < 0:
            draw.polygon([p_last, (p_last[0] + c_len, p_last[1] - c_w), (p_last[0] + c_len, p_last[1] + c_w)], fill='#000000')
        elif dy > 0:
            draw.polygon([p_last, (p_last[0] - c_w, p_last[1] - c_len), (p_last[0] + c_w, p_last[1] - c_len)], fill='#000000')
        elif dy < 0:
            draw.polygon([p_last, (p_last[0] - c_w, p_last[1] + c_len), (p_last[0] + c_w, p_last[1] + c_len)], fill='#000000')

        # Label
        lbl_lines = f['label'].split('\n')
        line_height = 12 * scale
        total_h = len(lbl_lines) * line_height
        max_w = 0
        for ll in lbl_lines:
            lb = draw.textbbox((0, 0), ll, font=font_flow)
            max_w = max(max_w, lb[2] - lb[0])

        cx, cy = f['img_lx'] * scale, f['img_ly'] * scale
        draw.rectangle([cx - max_w/2 - 4*scale, cy - total_h/2 - 2*scale, cx + max_w/2 + 4*scale, cy + total_h/2 + 2*scale], fill='#FFFFFF')

        for i, ll in enumerate(lbl_lines):
            lb = draw.textbbox((0, 0), ll, font=font_flow)
            lw = lb[2] - lb[0]
            draw.text((cx - lw/2, cy - total_h/2 + i * line_height), ll, fill='#000000', font=font_flow)

    out_png1 = r'c:\Users\kymer\Desktop\Lantad ACarwfish Django\diagram\Level_0_Context_Diagram.png'
    out_png2 = r'c:\Users\kymer\Desktop\Lantad ACarwfish Django\Documents\Final_Paper\ch3_extracted_images\level_0_context_diagram.png'

    os.makedirs(os.path.dirname(out_png1), exist_ok=True)
    os.makedirs(os.path.dirname(out_png2), exist_ok=True)

    img.save(out_png1, 'PNG', quality=100)
    img.save(out_png2, 'PNG', quality=100)
    print("Exact, flawless Draw.io XML and PNG Level 0 Context Diagram generated successfully!")

if __name__ == '__main__':
    build_perfect_drawio_level_0()
