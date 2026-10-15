import xml.etree.ElementTree as ET
import xml.dom.minidom

def generate_dfd_drawio_white_bg():
    mxfile = ET.Element('mxfile', {
        'host': 'app.diagrams.net',
        'modified': '2026-09-23T03:26:00.000Z',
        'agent': 'Antigravity DFD Generator',
        'version': '24.0.0',
        'type': 'device'
    })
    
    diagram = ET.SubElement(mxfile, 'diagram', {
        'id': 'dfd_level_1_diagram',
        'name': 'Level 1 Data Flow Diagram'
    })
    
    mxGraphModel = ET.SubElement(diagram, 'mxGraphModel', {
        'dx': '1422',
        'dy': '1180',
        'grid': '1',
        'gridSize': '10',
        'guides': '1',
        'tooltips': '1',
        'connect': '1',
        'arrows': '1',
        'fold': '1',
        'page': '1',
        'pageScale': '1',
        'pageWidth': '1169',
        'pageHeight': '1654',
        'background': '#FFFFFF',
        'math': '0',
        'shadow': '0'
    })
    
    root = ET.SubElement(mxGraphModel, 'root')
    
    # Base cells
    ET.SubElement(root, 'mxCell', {'id': '0'})
    ET.SubElement(root, 'mxCell', {'id': '1', 'parent': '0'})
    
    # ------------------ NODES ------------------
    
    # 1. External Entities (Customer, Rider, Manager)
    entities = [
        ('entity_customer', 'Customer', 120, 140, 100, 60),
        ('entity_rider', 'Rider', 120, 560, 100, 50),
        ('entity_manager', 'Manager', 60, 920, 100, 50),
    ]
    
    for eid, label, x, y, w, h in entities:
        ET.SubElement(root, 'mxCell', {
            'id': eid,
            'value': f'<div style="color:#000000;font-weight:bold;font-size:13px;text-align:center;">{label}</div>',
            'style': 'rounded=0;whiteSpace=wrap;html=1;strokeColor=#000000;strokeWidth=1.5;fillColor=#FFFFFF;fontColor=#000000;fontSize=13;fontFamily=Arial;fontStyle=1;',
            'vertex': '1',
            'parent': '1'
        })
        geo = ET.SubElement(root[-1], 'mxGeometry', {
            'x': str(x), 'y': str(y), 'width': str(w), 'height': str(h), 'as': 'geometry'
        })
        
    # 2. Processes (Gane & Sarson DFD Style: Rounded box with top header for process ID)
    processes = [
        ('proc_1', '1.0', 'Browse<br>and select', 550, 20, 110, 80),
        ('proc_2', '2.0', 'Order<br>management', 550, 180, 110, 80),
        ('proc_3', '3.0', 'Payment &amp;<br>Set location', 550, 360, 110, 80),
        ('proc_4', '4.0', 'Delivery<br>dispatch', 550, 530, 110, 80),
        ('proc_5', '5.0', 'Management', 550, 700, 110, 80),
        ('proc_6', '6.0', 'Report<br>and<br>Monitoring', 550, 870, 110, 85),
        ('proc_7', '7.0', 'Predictive<br>Analytics', 550, 1040, 110, 80),
    ]
    
    for pid, pnum, pname, x, y, w, h in processes:
        label = f'<table style="width:100%;height:100%;border-collapse:collapse;color:#000000;background-color:#FFFFFF;"><tr><td style="border-bottom:1.5px solid #000000;text-align:center;font-size:12px;font-weight:bold;color:#000000;height:24px;">{pnum}</td></tr><tr><td style="text-align:center;font-size:11px;font-weight:bold;color:#000000;vertical-align:middle;padding:2px;">{pname}</td></tr></table>'
        ET.SubElement(root, 'mxCell', {
            'id': pid,
            'value': label,
            'style': 'rounded=1;arcSize=18;whiteSpace=wrap;html=1;strokeColor=#000000;strokeWidth=1.5;fillColor=#FFFFFF;fontColor=#000000;fontFamily=Arial;overflow=hidden;spacing=0;',
            'vertex': '1',
            'parent': '1'
        })
        geo = ET.SubElement(root[-1], 'mxGeometry', {
            'x': str(x), 'y': str(y), 'width': str(w), 'height': str(h), 'as': 'geometry'
        })

    # 3. Data Stores (DFD Open Rectangle Style with Store ID)
    data_stores = [
        ('store_d1', 'D1', 'Order', 780, 110, 100, 35),
        ('store_d2', 'D2', 'Customer', 780, 190, 100, 35),
        ('store_d3', 'D3', 'Production', 780, 270, 110, 35),
        ('store_d4', 'D4', 'Expense', 780, 330, 100, 35),
        ('store_d5', 'D5', 'Payment', 780, 385, 100, 35),
        ('store_d6', 'D6', 'Delivery', 780, 580, 100, 35),
    ]
    
    for sid, snum, sname, x, y, w, h in data_stores:
        label = f'<table style="width:100%;height:100%;border-collapse:collapse;color:#000000;background-color:#FFFFFF;"><tr><td style="border-right:1.5px solid #000000;width:30px;text-align:center;font-size:11px;font-weight:bold;color:#000000;">{snum}</td><td style="text-align:center;font-size:11px;color:#000000;font-weight:bold;padding-left:4px;">{sname}</td></tr></table>'
        ET.SubElement(root, 'mxCell', {
            'id': sid,
            'value': label,
            'style': 'shape=partialRectangle;right=0;left=1;top=1;bottom=1;html=1;whiteSpace=wrap;strokeColor=#000000;strokeWidth=1.5;fillColor=#FFFFFF;fontColor=#000000;fontFamily=Arial;',
            'vertex': '1',
            'parent': '1'
        })
        geo = ET.SubElement(root[-1], 'mxGeometry', {
            'x': str(x), 'y': str(y), 'width': str(w), 'height': str(h), 'as': 'geometry'
        })

    # ------------------ EDGES / DATA FLOWS ------------------
    flows = [
        # Process 1.0 Flows
        ('edge_1_1', 'entity_customer', 'proc_1', 'Selected Product', 'exitX=0.5;exitY=0;entryX=0;entryY=0.25;'),
        ('edge_1_2', 'proc_1', 'entity_customer', 'Product list', 'exitX=0;exitY=0.75;entryX=0.75;entryY=0;'),
        ('edge_1_3', 'store_d3', 'proc_1', 'Available stock', 'exitX=1;exitY=0.5;entryX=1;entryY=0.2;'),
        ('edge_1_4', 'store_d1', 'proc_1', 'Order info', 'exitX=1;exitY=0.5;entryX=1;entryY=0.5;'),
        ('edge_1_5', 'store_d2', 'proc_1', 'Order info', 'exitX=1;exitY=0.5;entryX=1;entryY=0.8;'),
        ('edge_1_6', 'proc_1', 'proc_2', 'Select product', 'exitX=0.5;exitY=1;entryX=0.5;entryY=0;'),

        # Process 2.0 Flows
        ('edge_2_1', 'entity_customer', 'proc_2', 'Order request/details', 'exitX=1;exitY=0.5;entryX=0;entryY=0.25;'),
        ('edge_2_2', 'proc_2', 'entity_customer', 'Order confirmation', 'exitX=0;exitY=0.5;entryX=1;entryY=0.75;'),
        ('edge_2_3', 'entity_manager', 'proc_2', 'Order approval', 'exitX=0.25;exitY=0;entryX=0;entryY=0.85;'),
        ('edge_2_4', 'proc_2', 'store_d1', 'Order records', 'exitX=1;exitY=0.25;entryX=0.5;entryY=1;'),
        ('edge_2_5', 'proc_2', 'store_d2', 'Customer/order info', 'exitX=1;exitY=0.5;entryX=0;entryY=0.5;'),
        ('edge_2_6', 'proc_2', 'store_d2', 'Customer/order info', 'exitX=1;exitY=0.75;entryX=0;entryY=0.75;'),
        ('edge_2_7', 'proc_2', 'proc_3', 'Order info', 'exitX=0.5;exitY=1;entryX=0.5;entryY=0;'),

        # Process 3.0 Flows
        ('edge_3_1', 'entity_customer', 'proc_3', 'Delivery/pickup address', 'exitX=0.2;exitY=1;entryX=0;entryY=0.2;'),
        ('edge_3_2', 'entity_customer', 'proc_3', 'Payment details', 'exitX=0.4;exitY=1;entryX=0;entryY=0.4;'),
        ('edge_3_3', 'proc_3', 'entity_customer', 'Payment status', 'exitX=0;exitY=0.6;entryX=0.6;entryY=1;'),
        ('edge_3_4', 'proc_3', 'entity_customer', 'Payment verification (GCash/COD)', 'exitX=0;exitY=0.8;entryX=0.8;entryY=1;'),
        ('edge_3_5', 'entity_rider', 'proc_3', 'Cash collected (COD payment)', 'exitX=0.5;exitY=0;entryX=0;entryY=0.9;'),
        ('edge_3_6', 'proc_3', 'store_d5', 'Payment info', 'exitX=1;exitY=0.25;entryX=0;entryY=0.5;'),
        ('edge_3_7', 'store_d5', 'proc_3', 'Payment data', 'exitX=0;exitY=0.75;entryX=1;entryY=0.5;'),
        ('edge_3_8', 'proc_3', 'store_d6', 'Assigned location', 'exitX=1;exitY=0.75;entryX=0.5;entryY=0;'),
        ('edge_3_9', 'proc_3', 'store_d1', 'Order details/Order record', 'exitX=1;exitY=0.9;entryX=1;entryY=0.5;'),
        ('edge_3_10', 'proc_3', 'proc_4', 'Order & location details', 'exitX=0.5;exitY=1;entryX=0.5;entryY=0;'),

        # Process 4.0 Flows
        ('edge_4_1', 'proc_4', 'entity_customer', 'Real-time tracking', 'exitX=0;exitY=0.15;entryX=0;entryY=0.5;'),
        ('edge_4_2', 'proc_4', 'entity_customer', 'Delivery status/Completion update', 'exitX=0;exitY=0.35;entryX=0;entryY=0.7;'),
        ('edge_4_3', 'proc_4', 'entity_rider', 'Delivery assignment & route map', 'exitX=0;exitY=0.5;entryX=1;entryY=0.3;'),
        ('edge_4_4', 'proc_4', 'entity_rider', 'Customer contact & Delivery address', 'exitX=0;exitY=0.65;entryX=1;entryY=0.5;'),
        ('edge_4_5', 'entity_rider', 'proc_4', 'Rider assignment/approval', 'exitX=1;exitY=0.7;entryX=0;entryY=0.8;'),
        ('edge_4_6', 'entity_rider', 'proc_4', 'Delivery status', 'exitX=1;exitY=0.9;entryX=0;entryY=0.95;'),
        ('edge_4_7', 'proc_4', 'store_d1', 'Order status update', 'exitX=1;exitY=0.2;entryX=1;entryY=0.5;'),
        ('edge_4_8', 'proc_4', 'store_d3', 'Stock deduction', 'exitX=1;exitY=0.4;entryX=1;entryY=0.5;'),
        ('edge_4_9', 'proc_4', 'store_d6', 'Dispatch records', 'exitX=1;exitY=0.8;entryX=0;entryY=0.5;'),
        ('edge_4_10', 'proc_4', 'proc_5', 'Confirmed order', 'exitX=0.5;exitY=1;entryX=0.5;entryY=0;'),

        # Process 5.0 Flows
        ('edge_5_1', 'entity_manager', 'proc_5', 'Approved expense entries', 'exitX=0.5;exitY=0;entryX=0;entryY=0.35;'),
        ('edge_5_2', 'entity_manager', 'proc_5', 'Stock/replenishment updates', 'exitX=0.75;exitY=0;entryX=0;entryY=0.7;'),
        ('edge_5_3', 'store_d6', 'proc_5', 'Delivery records', 'exitX=0.5;exitY=1;entryX=1;entryY=0.2;'),
        ('edge_5_4', 'store_d5', 'proc_5', 'Payment data', 'exitX=1;exitY=0.5;entryX=1;entryY=0.4;'),
        ('edge_5_5', 'store_d3', 'proc_5', 'Production/data&stock/replenishment', 'exitX=1;exitY=0.5;entryX=1;entryY=0.6;'),
        ('edge_5_6', 'store_d4', 'proc_5', 'Approved expense entries/Expense data', 'exitX=1;exitY=0.5;entryX=1;entryY=0.8;'),
        ('edge_5_7', 'proc_5', 'proc_6', 'Delivery data', 'exitX=0.5;exitY=1;entryX=0.5;entryY=0;'),

        # Process 6.0 Flows
        ('edge_6_1', 'entity_manager', 'proc_6', 'Request report', 'exitX=1;exitY=0.5;entryX=0;entryY=0.5;'),
        ('edge_6_2', 'proc_6', 'entity_manager', 'Sales/inventory/expense summary', 'exitX=0;exitY=0.75;entryX=0.75;entryY=1;'),
        ('edge_6_3', 'store_d3', 'proc_6', 'Inventory data', 'exitX=1;exitY=0.5;entryX=1;entryY=0.25;'),
        ('edge_6_4', 'store_d6', 'proc_6', 'Dispatch record', 'exitX=1;exitY=0.5;entryX=1;entryY=0.6;'),
        ('edge_6_5', 'proc_6', 'proc_7', 'Summarized data', 'exitX=0.5;exitY=1;entryX=0.5;entryY=0;'),

        # Process 7.0 Flows
        ('edge_7_1', 'proc_7', 'entity_manager', 'Forecast & clustering report', 'exitX=1;exitY=0.5;entryX=0.25;entryY=1;'),
    ]

    for eid, src, tgt, label, extra_style in flows:
        style = f'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#000000;strokeWidth=1.2;fontColor=#000000;fontSize=10;fontFamily=Arial;fontStyle=1;labelBackgroundColor=#FFFFFF;labelBorderColor=#FFFFFF;{extra_style}'
        edge = ET.SubElement(root, 'mxCell', {
            'id': eid,
            'value': f'<span style="color:#000000;background-color:#FFFFFF;padding:1px 2px;">{label}</span>',
            'style': style,
            'edge': '1',
            'parent': '1',
            'source': src,
            'target': tgt
        })
        ET.SubElement(edge, 'mxGeometry', {'relative': '1', 'as': 'geometry'})

    # Prettify and write to file
    xml_str = ET.tostring(mxfile, encoding='utf-8')
    dom = xml.dom.minidom.parseString(xml_str)
    pretty_xml = dom.toprettyxml(indent='  ')
    
    out_drawio = r'c:\Users\kymer\Desktop\Lantad ACarwfish Django\diagram\Level_1_DFD.drawio'
    out_xml = r'c:\Users\kymer\Desktop\Lantad ACarwfish Django\diagram\Level_1_DFD.xml'
    
    with open(out_drawio, 'w', encoding='utf-8') as f:
        f.write(pretty_xml)
        
    with open(out_xml, 'w', encoding='utf-8') as f:
        f.write(pretty_xml)
        
    print(f"Successfully generated white-background {out_drawio} and {out_xml}!")

if __name__ == '__main__':
    generate_dfd_drawio_white_bg()
