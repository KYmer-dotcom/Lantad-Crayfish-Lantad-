import os
import xml.etree.ElementTree as ET
import xml.dom.minidom
from PIL import Image, ImageDraw, ImageFont

def build_and_render_erd():
    # Canvas sizing: 1620 x 1100
    canvas_w = 1620
    canvas_h = 1100

    # 1. ENTITY DEFINITIONS (Accurate Active Schema - No Unused Fields)
    entities = [
        # --- USER & ACCESS (Column 1) ---
        {
            'id': 'ent_user', 'name': 'AUTH_USER', 'x': 50, 'y': 60, 'w': 230, 'h': 185,
            'fields': [
                ('PK', 'id', 'INTEGER'),
                ('', 'username', 'VARCHAR(150)'),
                ('', 'email', 'VARCHAR(254)'),
                ('', 'first_name', 'VARCHAR(150)'),
                ('', 'last_name', 'VARCHAR(150)'),
                ('', 'role', 'VARCHAR(20)'),
                ('', 'is_active', 'BOOLEAN'),
                ('', 'date_joined', 'DATETIME'),
            ]
        },
        {
            'id': 'ent_customer', 'name': 'SALES_CUSTOMER', 'x': 50, 'y': 290, 'w': 230, 'h': 205,
            'fields': [
                ('PK', 'id', 'INTEGER'),
                ('FK', 'user_id', 'INTEGER (1:1)'),
                ('', 'name', 'VARCHAR(200)'),
                ('', 'customer_type', 'VARCHAR(20)'),
                ('', 'phone', 'VARCHAR(20)'),
                ('', 'address', 'TEXT'),
                ('', 'map_latitude', 'DECIMAL(9,6)'),
                ('', 'map_longitude', 'DECIMAL(9,6)'),
                ('', 'credit_limit', 'DECIMAL(12,2)'),
            ]
        },
        {
            'id': 'ent_rider', 'name': 'SALES_RIDER', 'x': 50, 'y': 540, 'w': 230, 'h': 185,
            'fields': [
                ('PK', 'id', 'INTEGER'),
                ('FK', 'user_id', 'INTEGER (1:1)'),
                ('', 'name', 'VARCHAR(150)'),
                ('', 'phone', 'VARCHAR(20)'),
                ('', 'vehicle_type', 'VARCHAR(50)'),
                ('', 'plate_number', 'VARCHAR(50)'),
                ('', 'status', 'VARCHAR(20)'),
                ('', 'is_active', 'BOOLEAN'),
            ]
        },

        # --- SALES & DISTRIBUTION (Column 2) ---
        {
            'id': 'ent_product', 'name': 'SALES_PRODUCT', 'x': 360, 'y': 60, 'w': 250, 'h': 225,
            'fields': [
                ('PK', 'id', 'INTEGER'),
                ('FK', 'species_id', 'INTEGER'),
                ('FK', 'pond_id', 'INTEGER'),
                ('', 'name', 'VARCHAR(200)'),
                ('', 'category', 'VARCHAR(20)'),
                ('', 'unit_type', 'VARCHAR(20)'),
                ('', 'quantity_kg', 'DECIMAL(12,2)'),
                ('', 'unit_price', 'DECIMAL(12,2)'),
                ('', 'pieces_per_kg', 'DECIMAL(10,2)'),
                ('', 'placement_date', 'DATE'),
            ]
        },
        {
            'id': 'ent_order', 'name': 'SALES_SALESORDER', 'x': 360, 'y': 320, 'w': 250, 'h': 265,
            'fields': [
                ('PK', 'id', 'INTEGER'),
                ('', 'order_number', 'VARCHAR(50) [UQ]'),
                ('FK', 'customer_id', 'INTEGER'),
                ('FK', 'product_id', 'INTEGER'),
                ('FK', 'harvest_record_id', 'INTEGER'),
                ('', 'order_date', 'DATE'),
                ('', 'delivery_date', 'DATE'),
                ('', 'quantity_kg', 'DECIMAL(10,2)'),
                ('', 'price_per_kg', 'DECIMAL(10,2)'),
                ('', 'total_amount', 'DECIMAL(12,2)'),
                ('', 'status', 'VARCHAR(20)'),
                ('', 'payment_status', 'VARCHAR(20)'),
            ]
        },
        {
            'id': 'ent_delivery', 'name': 'SALES_DELIVERY', 'x': 360, 'y': 620, 'w': 250, 'h': 185,
            'fields': [
                ('PK', 'id', 'INTEGER'),
                ('FK', 'order_id', 'INTEGER'),
                ('FK', 'rider_id', 'INTEGER'),
                ('', 'scheduled_date', 'DATE'),
                ('', 'delivered_date', 'DATE'),
                ('', 'delivery_location', 'VARCHAR(255)'),
                ('', 'quantity_kg', 'DECIMAL(12,2)'),
                ('', 'status', 'VARCHAR(20)'),
            ]
        },
        {
            'id': 'ent_inventory_tx', 'name': 'SALES_INVENTORYTRANSACTION', 'x': 360, 'y': 840, 'w': 250, 'h': 185,
            'fields': [
                ('PK', 'id', 'INTEGER'),
                ('FK', 'product_id', 'INTEGER'),
                ('FK', 'related_order_id', 'INTEGER'),
                ('FK', 'related_harvest_id', 'INTEGER'),
                ('', 'quantity_kg', 'DECIMAL(12,2)'),
                ('', 'transaction_type', 'VARCHAR(20)'),
                ('FK', 'created_by_id', 'INTEGER'),
                ('', 'created_at', 'DATETIME'),
            ]
        },

        # --- AQUACULTURE OPERATIONS & HARVEST (Column 3) ---
        {
            'id': 'ent_pond', 'name': 'OPERATIONS_POND', 'x': 690, 'y': 60, 'w': 250, 'h': 225,
            'fields': [
                ('PK', 'id', 'INTEGER'),
                ('', 'name', 'VARCHAR(100)'),
                ('', 'location', 'VARCHAR(255)'),
                ('', 'size', 'DECIMAL(10,2)'),
                ('', 'depth', 'DECIMAL(5,2)'),
                ('', 'capacity', 'INTEGER'),
                ('', 'breeding_type', 'VARCHAR(50)'),
                ('', 'transfer_date', 'DATE'),
                ('', 'shelf_position', 'VARCHAR(50)'),
                ('', 'status', 'VARCHAR(20)'),
            ]
        },
        {
            'id': 'ent_harvest_sched', 'name': 'HARVEST_HARVESTSCHEDULE', 'x': 690, 'y': 330, 'w': 250, 'h': 165,
            'fields': [
                ('PK', 'id', 'INTEGER'),
                ('FK', 'stock_batch_id', 'INTEGER'),
                ('', 'scheduled_date', 'DATE'),
                ('', 'estimated_quantity', 'INTEGER'),
                ('', 'estimated_weight_kg', 'DECIMAL(12,2)'),
                ('', 'target_weight_g', 'DECIMAL(8,2)'),
                ('', 'status', 'VARCHAR(20)'),
            ]
        },
        {
            'id': 'ent_harvest_rec', 'name': 'HARVEST_HARVESTRECORD', 'x': 690, 'y': 540, 'w': 250, 'h': 205,
            'fields': [
                ('PK', 'id', 'INTEGER'),
                ('FK', 'harvest_sched_id', 'INTEGER'),
                ('FK', 'stock_batch_id', 'INTEGER'),
                ('', 'harvest_date', 'DATE'),
                ('', 'quantity_harvested', 'INTEGER'),
                ('', 'total_weight_kg', 'DECIMAL(12,2)'),
                ('', 'grade_a_quantity', 'INTEGER'),
                ('', 'grade_b_quantity', 'INTEGER'),
                ('', 'grade_c_quantity', 'INTEGER'),
            ]
        },

        # --- SPECIES & STOCK BATCHES (Column 4) ---
        {
            'id': 'ent_species', 'name': 'STOCK_SPECIES', 'x': 990, 'y': 60, 'w': 250, 'h': 145,
            'fields': [
                ('PK', 'id', 'INTEGER'),
                ('', 'name', 'VARCHAR(100) [UQ]'),
                ('', 'category', 'VARCHAR(20)'),
                ('', 'scientific_name', 'VARCHAR(150)'),
                ('', 'market_weight_g', 'DECIMAL(8,2)'),
                ('', 'description', 'TEXT'),
            ]
        },
        {
            'id': 'ent_batch', 'name': 'STOCK_STOCKBATCH', 'x': 990, 'y': 250, 'w': 250, 'h': 245,
            'fields': [
                ('PK', 'id', 'INTEGER'),
                ('FK', 'pond_id', 'INTEGER'),
                ('FK', 'species_id', 'INTEGER'),
                ('', 'batch_code', 'VARCHAR(50) [UQ]'),
                ('', 'stocking_date', 'DATE'),
                ('', 'initial_quantity', 'INTEGER'),
                ('', 'current_quantity', 'INTEGER'),
                ('', 'initial_avg_weight', 'DECIMAL(8,2)'),
                ('', 'current_avg_weight', 'DECIMAL(8,2)'),
                ('', 'stage', 'VARCHAR(20)'),
                ('', 'is_active', 'BOOLEAN'),
            ]
        },

        # --- FEED INVENTORY & AUDIT LOGS (Column 5) ---
        {
            'id': 'ent_feed_type', 'name': 'FEED_FEEDTYPE', 'x': 1310, 'y': 60, 'w': 240, 'h': 165,
            'fields': [
                ('PK', 'id', 'INTEGER'),
                ('', 'name', 'VARCHAR(100)'),
                ('', 'category', 'VARCHAR(20)'),
                ('', 'accent_color', 'VARCHAR(20)'),
                ('', 'icon', 'VARCHAR(20)'),
                ('', 'description', 'TEXT'),
                ('', 'is_active', 'BOOLEAN'),
            ]
        },
        {
            'id': 'ent_feeding_log', 'name': 'FEED_FEEDINGLOG', 'x': 1310, 'y': 270, 'w': 240, 'h': 145,
            'fields': [
                ('PK', 'id', 'INTEGER'),
                ('FK', 'stock_batch_id', 'INTEGER'),
                ('FK', 'feed_type_id', 'INTEGER'),
                ('', 'quantity_kg', 'DECIMAL(8,2)'),
                ('', 'feeding_time', 'DATETIME'),
                ('FK', 'fed_by_id', 'INTEGER'),
            ]
        },
        {
            'id': 'ent_input_log', 'name': 'SALES_INPUTLOG', 'x': 1310, 'y': 460, 'w': 240, 'h': 185,
            'fields': [
                ('PK', 'id', 'INTEGER'),
                ('FK', 'user_id', 'INTEGER'),
                ('', 'user_name', 'VARCHAR(150)'),
                ('', 'user_role', 'VARCHAR(50)'),
                ('', 'action', 'VARCHAR(20)'),
                ('', 'module', 'VARCHAR(100)'),
                ('', 'target_entity', 'VARCHAR(255)'),
                ('', 'created_at', 'DATETIME'),
            ]
        },
    ]

    # Relationships (zero-box-penetration orthogonal paths)
    relationships = [
        # User -> Customer (1:1)
        ('rel_u_cust', 'ent_user', 'ent_customer', '1 : 1', [(165, 245), (165, 290)]),
        # User -> Rider (1:1, routes around left edge)
        ('rel_u_rider', 'ent_user', 'ent_rider', '1 : 1', [(50, 150), (25, 150), (25, 630), (50, 630)]),
        # Customer -> SalesOrder (1:N)
        ('rel_cust_ord', 'ent_customer', 'ent_order', '1 : N', [(280, 390), (360, 390)]),
        # Product -> SalesOrder (1:N)
        ('rel_prod_ord', 'ent_product', 'ent_order', '1 : N', [(485, 285), (485, 320)]),
        # SalesOrder -> Delivery (1:N)
        ('rel_ord_del', 'ent_order', 'ent_delivery', '1 : N', [(485, 585), (485, 620)]),
        # Rider -> Delivery (1:N)
        ('rel_rid_del', 'ent_rider', 'ent_delivery', '1 : N', [(280, 630), (320, 630), (320, 690), (360, 690)]),
        # Product -> InventoryTransaction (1:N, routes along left bypass)
        ('rel_prod_tx', 'ent_product', 'ent_inventory_tx', '1 : N', [(360, 170), (315, 170), (315, 930), (360, 930)]),
        # Pond -> StockBatch (1:N)
        ('rel_pond_batch', 'ent_pond', 'ent_batch', '1 : N', [(940, 170), (965, 170), (965, 330), (990, 330)]),
        # Species -> StockBatch (1:N)
        ('rel_spec_batch', 'ent_species', 'ent_batch', '1 : N', [(1115, 205), (1115, 250)]),
        # Species -> Product (1:N, routes cleanly above top at Y=30)
        ('rel_spec_prod', 'ent_species', 'ent_product', '1 : N', [(990, 100), (965, 100), (965, 30), (520, 30), (520, 60)]),
        # StockBatch -> HarvestSchedule (1:N)
        ('rel_batch_sched', 'ent_batch', 'ent_harvest_sched', '1 : N', [(990, 410), (940, 410)]),
        # StockBatch -> HarvestRecord (1:N)
        ('rel_batch_rec', 'ent_batch', 'ent_harvest_rec', '1 : N', [(1050, 495), (1050, 640), (940, 640)]),
        # HarvestSchedule -> HarvestRecord (1:N)
        ('rel_sched_rec', 'ent_harvest_sched', 'ent_harvest_rec', '1 : N', [(815, 495), (815, 540)]),
        # HarvestRecord -> SalesOrder (1:N, routes along middle bypass at X=650)
        ('rel_rec_ord', 'ent_harvest_rec', 'ent_order', '1 : N', [(690, 640), (650, 640), (650, 480), (610, 480)]),
        # StockBatch -> FeedingLog (1:N)
        ('rel_batch_feed', 'ent_batch', 'ent_feeding_log', '1 : N', [(1240, 340), (1310, 340)]),
        # FeedType -> FeedingLog (1:N)
        ('rel_ft_feed', 'ent_feed_type', 'ent_feeding_log', '1 : N', [(1430, 225), (1430, 270)]),
    ]

    # =========================================================================
    # 2. GENERATE DRAW.IO XML
    # =========================================================================
    mxfile = ET.Element('mxfile', {
        'host': 'app.diagrams.net',
        'modified': '2026-09-23T07:00:00.000Z',
        'agent': 'Antigravity ERD Engine',
        'version': '24.0.0',
        'type': 'device'
    })
    diagram = ET.SubElement(mxfile, 'diagram', {
        'id': 'erd_diagram_exact',
        'name': 'Entity Relationship Diagram'
    })
    mxGraphModel = ET.SubElement(diagram, 'mxGraphModel', {
        'dx': '1600', 'dy': '1400', 'grid': '0', 'gridSize': '10',
        'guides': '1', 'tooltips': '1', 'connect': '1', 'arrows': '1',
        'fold': '1', 'page': '0', 'pageScale': '1',
        'pageWidth': str(canvas_w), 'pageHeight': str(canvas_h),
        'background': '#FFFFFF', 'pageColor': '#FFFFFF', 'math': '0', 'shadow': '0'
    })
    root = ET.SubElement(mxGraphModel, 'root')
    ET.SubElement(root, 'mxCell', {'id': '0'})
    ET.SubElement(root, 'mxCell', {'id': '1', 'parent': '0'})

    for ent in entities:
        eid = ent['id']
        ename = ent['name']
        ex, ey, ew, eh = ent['x'], ent['y'], ent['w'], ent['h']

        # Entity Table Container
        tbl_cell = ET.SubElement(root, 'mxCell', {
            'id': eid,
            'value': f'<b>{ename}</b>',
            'style': (
                'shape=table;childLayout=tableLayout;startSize=28;nested=0;collapsible=0;'
                'recursiveResize=0;expand=0;fontStyle=1;align=center;verticalAlign=middle;'
                'fillColor=#F8F9FA;strokeColor=#000000;strokeWidth=1.5;fontFamily=Arial;fontSize=11;fontColor=#000000;'
            ),
            'vertex': '1',
            'parent': '1'
        })
        ET.SubElement(tbl_cell, 'mxGeometry', {
            'x': str(ex), 'y': str(ey), 'width': str(ew), 'height': str(eh), 'as': 'geometry'
        })

        # Rows for fields
        row_h = 20
        for idx, (fkey, fname, ftype) in enumerate(ent['fields']):
            row_id = f'{eid}_r{idx}'
            row_cell = ET.SubElement(root, 'mxCell', {
                'id': row_id,
                'value': '',
                'style': (
                    'shape=tableRow;horizontal=0;startSize=0;swimlaneHead=0;swimlaneBody=0;'
                    'top=0;left=0;bottom=0;right=0;collapsible=0;dropTarget=0;fillColor=none;'
                    'points=[[0,0.5],[1,0.5]];portConstraint=eastwest;'
                ),
                'vertex': '1',
                'parent': eid
            })
            ET.SubElement(row_cell, 'mxGeometry', {
                'width': str(ew), 'height': str(row_h), 'as': 'geometry'
            })

            # Key Cell (PK/FK)
            k_cell = ET.SubElement(root, 'mxCell', {
                'id': f'{row_id}_k',
                'value': f'<b>{fkey}</b>' if fkey else '',
                'style': (
                    'shape=partialRectangle;connectable=0;fillColor=none;top=0;left=0;bottom=0;right=0;'
                    'fontStyle=1;overflow=hidden;align=center;verticalAlign=middle;'
                    f'fontColor={"#E63946" if fkey == "PK" else ("#1D3557" if fkey == "FK" else "#000000")};'
                    'fontFamily=Arial;fontSize=9;'
                ),
                'vertex': '1',
                'parent': row_id
            })
            ET.SubElement(k_cell, 'mxGeometry', {
                'width': '28', 'height': str(row_h), 'as': 'geometry'
            })

            # Field Name Cell
            name_cell = ET.SubElement(root, 'mxCell', {
                'id': f'{row_id}_n',
                'value': fname,
                'style': (
                    'shape=partialRectangle;connectable=0;fillColor=none;top=0;left=0;bottom=0;right=0;'
                    'align=left;verticalAlign=middle;spacingLeft=4;overflow=hidden;'
                    'fontColor=#000000;fontFamily=Arial;fontSize=9;'
                ),
                'vertex': '1',
                'parent': row_id
            })
            ET.SubElement(name_cell, 'mxGeometry', {
                'width': str(ew - 100), 'height': str(row_h), 'as': 'geometry'
            })

            # Field Type Cell
            type_cell = ET.SubElement(root, 'mxCell', {
                'id': f'{row_id}_t',
                'value': ftype,
                'style': (
                    'shape=partialRectangle;connectable=0;fillColor=none;top=0;left=0;bottom=0;right=0;'
                    'align=right;verticalAlign=middle;spacingRight=4;overflow=hidden;'
                    'fontColor=#6C757D;fontFamily=Arial;fontSize=8;fontStyle=2;'
                ),
                'vertex': '1',
                'parent': row_id
            })
            ET.SubElement(type_cell, 'mxGeometry', {
                'width': '72', 'height': str(row_h), 'as': 'geometry'
            })

    # Relationships in Draw.io
    for rid, src, tgt, label, points in relationships:
        edge_style = (
            'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;'
            'strokeColor=#000000;strokeWidth=1.2;fontColor=#495057;fontSize=9;fontFamily=Arial;'
            'labelBackgroundColor=#FFFFFF;labelBorderColor=none;'
            'startArrow=none;endArrow=ERmany;endFill=0;endSize=7;'
        )
        if label == '1 : 1':
            edge_style = (
                'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;'
                'strokeColor=#000000;strokeWidth=1.2;fontColor=#495057;fontSize=9;fontFamily=Arial;'
                'labelBackgroundColor=#FFFFFF;labelBorderColor=none;'
                'startArrow=ERone;endArrow=ERone;endFill=0;endSize=6;startSize=6;'
            )

        e_cell = ET.SubElement(root, 'mxCell', {
            'id': rid,
            'value': f'<span style="background-color:#FFFFFF;padding:1px 3px;font-size:8px;">{label}</span>' if label else '',
            'style': edge_style,
            'edge': '1',
            'parent': '1',
            'source': src,
            'target': tgt
        })
        geom = ET.SubElement(e_cell, 'mxGeometry', {
            'relative': '1', 'as': 'geometry'
        })
        arr = ET.SubElement(geom, 'Array', {'as': 'points'})
        for px, py in points[1:-1]:
            ET.SubElement(arr, 'mxPoint', {'x': str(px), 'y': str(py)})

    # Pretty-print and Save Draw.io files
    raw_str = ET.tostring(mxfile, encoding='utf-8')
    parsed = xml.dom.minidom.parseString(raw_str)
    pretty_xml = parsed.toprettyxml(indent='    ')

    clean_lines = [l for l in pretty_xml.split('\n') if l.strip()]
    final_xml = '\n'.join(clean_lines)

    out_drawio = r'c:\Users\kymer\Desktop\Lantad ACarwfish Django\diagram\ERD_Diagram.drawio'
    out_xml = r'c:\Users\kymer\Desktop\Lantad ACarwfish Django\diagram\ERD_Diagram.xml'

    with open(out_drawio, 'w', encoding='utf-8') as f:
        f.write(final_xml)
    with open(out_xml, 'w', encoding='utf-8') as f:
        f.write(final_xml)

    # =========================================================================
    # 3. RENDER 3X SUPERSAMPLED PIXEL-PERFECT PNG
    # =========================================================================
    scale = 3
    img = Image.new('RGB', (canvas_w * scale, canvas_h * scale), '#FFFFFF')
    draw = ImageDraw.Draw(img)

    try:
        font_title = ImageFont.truetype("arialbd.ttf", 11 * scale)
        font_name = ImageFont.truetype("arial.ttf", 9 * scale)
        font_type = ImageFont.truetype("ariali.ttf", 8 * scale)
        font_key = ImageFont.truetype("arialbd.ttf", 9 * scale)
        font_rel = ImageFont.truetype("arialbd.ttf", 8 * scale)
    except:
        font_title = font_name = font_type = font_key = font_rel = ImageFont.load_default()

    box_stroke = max(2, int(1.5 * scale))
    edge_w = max(2, int(1.2 * scale))

    # Draw Entities
    for ent in entities:
        ex, ey = ent['x'] * scale, ent['y'] * scale
        ew, eh = ent['w'] * scale, ent['h'] * scale
        header_h = 26 * scale
        row_h = 20 * scale

        # Main box background & stroke
        draw.rectangle([ex, ey, ex + ew, ey + eh], fill='#FFFFFF', outline='#000000', width=box_stroke)
        # Header background
        draw.rectangle([ex, ey, ex + ew, ey + header_h], fill='#F1F3F5', outline='#000000', width=box_stroke)

        # Header Title
        tbox = draw.textbbox((0, 0), ent['name'], font=font_title)
        tw = tbox[2] - tbox[0]
        th = tbox[3] - tbox[1]
        draw.text((ex + (ew - tw) / 2, ey + (header_h - th) / 2 - 1 * scale), ent['name'], fill='#000000', font=font_title)

        # Fields
        for idx, (fkey, fname, ftype) in enumerate(ent['fields']):
            fy = ey + header_h + idx * row_h
            if idx > 0:
                draw.line([(ex, fy), (ex + ew, fy)], fill='#E9ECEF', width=max(1, int(1 * scale)))

            if fkey == 'PK':
                draw.text((ex + 8 * scale, fy + 4 * scale), fkey, fill='#E63946', font=font_key)
            elif fkey == 'FK':
                draw.text((ex + 8 * scale, fy + 4 * scale), fkey, fill='#1D3557', font=font_key)

            draw.text((ex + 32 * scale, fy + 4 * scale), fname, fill='#111111', font=font_name)

            ft_box = draw.textbbox((0, 0), ftype, font=font_type)
            ft_w = ft_box[2] - ft_box[0]
            draw.text((ex + ew - ft_w - 8 * scale, fy + 4 * scale), ftype, fill='#6C757D', font=font_type)

    # Relationships
    for rid, src, tgt, label, points in relationships:
        pts = [(px * scale, py * scale) for px, py in points]
        for i in range(len(pts) - 1):
            draw.line([pts[i], pts[i+1]], fill='#000000', width=edge_w)

        p_last = pts[-1]
        p_prev = pts[-2]
        c_len = 8 * scale
        c_w = 6 * scale
        dx = p_last[0] - p_prev[0]
        dy = p_last[1] - p_prev[1]

        if dx > 0:
            draw.line([p_last, (p_last[0] - c_len, p_last[1] - c_w)], fill='#000000', width=edge_w)
            draw.line([p_last, (p_last[0] - c_len, p_last[1] + c_w)], fill='#000000', width=edge_w)
        elif dx < 0:
            draw.line([p_last, (p_last[0] + c_len, p_last[1] - c_w)], fill='#000000', width=edge_w)
            draw.line([p_last, (p_last[0] + c_len, p_last[1] + c_w)], fill='#000000', width=edge_w)
        elif dy > 0:
            draw.line([p_last, (p_last[0] - c_w, p_last[1] - c_len)], fill='#000000', width=edge_w)
            draw.line([p_last, (p_last[0] + c_w, p_last[1] - c_len)], fill='#000000', width=edge_w)
        elif dy < 0:
            draw.line([p_last, (p_last[0] - c_w, p_last[1] + c_len)], fill='#000000', width=edge_w)
            draw.line([p_last, (p_last[0] + c_w, p_last[1] + c_len)], fill='#000000', width=edge_w)

        if label:
            mid_idx = len(pts) // 2
            lx = (pts[mid_idx-1][0] + pts[mid_idx][0]) / 2
            ly = (pts[mid_idx-1][1] + pts[mid_idx][1]) / 2 - 8 * scale
            lbox = draw.textbbox((0, 0), label, font=font_rel)
            lw, lh = lbox[2] - lbox[0], lbox[3] - lbox[1]
            draw.rectangle([lx - lw/2 - 2*scale, ly - 2*scale, lx + lw/2 + 2*scale, ly + lh + 2*scale], fill='#FFFFFF')
            draw.text((lx - lw/2, ly), label, fill='#495057', font=font_rel)

    out_png1 = r'c:\Users\kymer\Desktop\Lantad ACarwfish Django\diagram\ERD_Diagram.png'
    out_png2 = r'c:\Users\kymer\Desktop\Lantad ACarwfish Django\Documents\Final_Paper\ch3_extracted_images\erd_diagram.png'

    img.save(out_png1, 'PNG', quality=100)
    img.save(out_png2, 'PNG', quality=100)
    print("ERD Diagram generated successfully!")

if __name__ == '__main__':
    build_and_render_erd()
