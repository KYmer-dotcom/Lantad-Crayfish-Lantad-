import xml.etree.ElementTree as ET
import xml.dom.minidom

def generate_exact_match_dfd():
    mxfile = ET.Element('mxfile', {
        'host': 'app.diagrams.net',
        'modified': '2026-09-23T03:32:00.000Z',
        'agent': 'Antigravity Exact DFD Generator',
        'version': '24.0.0',
        'type': 'device'
    })
    
    diagram = ET.SubElement(mxfile, 'diagram', {
        'id': 'dfd_level_1_exact',
        'name': 'Level 1 Data Flow Diagram'
    })
    
    mxGraphModel = ET.SubElement(diagram, 'mxGraphModel', {
        'dx': '1200',
        'dy': '1100',
        'grid': '1',
        'gridSize': '5',
        'guides': '1',
        'tooltips': '1',
        'connect': '1',
        'arrows': '1',
        'fold': '1',
        'page': '1',
        'pageScale': '1',
        'pageWidth': '1100',
        'pageHeight': '1100',
        'background': '#FFFFFF',
        'math': '0',
        'shadow': '0'
    })
    
    root = ET.SubElement(mxGraphModel, 'root')
    
    # Base cells
    ET.SubElement(root, 'mxCell', {'id': '0'})
    ET.SubElement(root, 'mxCell', {'id': '1', 'parent': '0'})
    
    # ------------------ NODES ------------------
    # Entities (Rectangles)
    entities = [
        ('Customer', 'Customer', 90, 105, 85, 40),
        ('Rider', 'Rider', 90, 460, 85, 35),
        ('Manager', 'Manager', 40, 755, 80, 35),
    ]
    for eid, label, x, y, w, h in entities:
        ET.SubElement(root, 'mxCell', {
            'id': eid,
            'value': label,
            'style': 'rounded=0;whiteSpace=wrap;html=1;strokeColor=#000000;strokeWidth=1;fillColor=#FFFFFF;fontColor=#000000;fontSize=11;fontFamily=Arial;fontStyle=1;',
            'vertex': '1',
            'parent': '1'
        })
        ET.SubElement(root[-1], 'mxGeometry', {
            'x': str(x), 'y': str(y), 'width': str(w), 'height': str(h), 'as': 'geometry'
        })

    # Processes (Gane & Sarson DFD format)
    processes = [
        ('P1', '1.0', 'Browse<br>and select', 460, 0, 90, 65),
        ('P2', '2.0', 'Order<br>management', 460, 150, 90, 65),
        ('P3', '3.0', 'Payment &amp;<br>Set location', 460, 305, 90, 65),
        ('P4', '4.0', 'Delivery<br>dispatch', 460, 455, 90, 65),
        ('P5', '5.0', 'Management', 460, 595, 90, 65),
        ('P6', '6.0', 'Report<br>and<br>Monitoring', 460, 735, 90, 70),
        ('P7', '7.0', 'Predictive<br>Analytics', 460, 880, 90, 65),
    ]
    for pid, pnum, pname, x, y, w, h in processes:
        label = f'<table style="width:100%;height:100%;border-collapse:collapse;color:#000000;background-color:#FFFFFF;"><tr><td style="border-bottom:1px solid #000000;text-align:center;font-size:11px;font-weight:bold;color:#000000;height:20px;">{pnum}</td></tr><tr><td style="text-align:center;font-size:10px;font-weight:normal;color:#000000;vertical-align:middle;padding:1px;">{pname}</td></tr></table>'
        ET.SubElement(root, 'mxCell', {
            'id': pid,
            'value': label,
            'style': 'rounded=1;arcSize=22;whiteSpace=wrap;html=1;strokeColor=#000000;strokeWidth=1;fillColor=#FFFFFF;fontColor=#000000;fontFamily=Arial;overflow=hidden;spacing=0;',
            'vertex': '1',
            'parent': '1'
        })
        ET.SubElement(root[-1], 'mxGeometry', {
            'x': str(x), 'y': str(y), 'width': str(w), 'height': str(h), 'as': 'geometry'
        })

    # Data Stores (Open on right)
    data_stores = [
        ('D1', 'D1', 'Order', 630, 85, 80, 26),
        ('D2', 'D2', 'Customer', 630, 160, 85, 26),
        ('D3', 'D3', 'Production', 630, 225, 90, 26),
        ('D4', 'D4', 'Expense', 630, 275, 80, 26),
        ('D5', 'D5', 'Payment', 630, 320, 80, 26),
        ('D6', 'D6', 'Delivery', 630, 500, 80, 26),
    ]
    for sid, snum, sname, x, y, w, h in data_stores:
        label = f'<table style="width:100%;height:100%;border-collapse:collapse;color:#000000;background-color:#FFFFFF;"><tr><td style="border-right:1px solid #000000;width:26px;text-align:center;font-size:10px;font-weight:bold;color:#000000;">{snum}</td><td style="text-align:center;font-size:10px;color:#000000;padding-left:2px;">{sname}</td></tr></table>'
        ET.SubElement(root, 'mxCell', {
            'id': sid,
            'value': label,
            'style': 'shape=partialRectangle;right=0;left=1;top=1;bottom=1;html=1;whiteSpace=wrap;strokeColor=#000000;strokeWidth=1;fillColor=#FFFFFF;fontColor=#000000;fontFamily=Arial;',
            'vertex': '1',
            'parent': '1'
        })
        ET.SubElement(root[-1], 'mxGeometry', {
            'x': str(x), 'y': str(y), 'width': str(w), 'height': str(h), 'as': 'geometry'
        })

    # ------------------ EDGES ------------------
    # Exact geometric lines with directional arrows and exact label coordinates
    flows = [
        # Top-left Process 1.0
        ('Customer', 'P1', 'Selected Product', [(140, 105), (140, 20), (460, 20)]),
        ('P1', 'Customer', 'Product list', [(460, 35), (160, 35), (160, 105)]),
        ('P1', 'P2', 'Select product', [(505, 65), (505, 150)]),
        
        # Top-right Process 1.0
        ('D3', 'P1', 'Available stock', [(720, 235), (800, 235), (800, 20), (550, 20)]),
        ('D1', 'P1', 'Order info', [(710, 95), (770, 95), (770, 35), (550, 35)]),
        ('D2', 'P1', 'Order info', [(715, 170), (745, 170), (745, 50), (550, 50)]),

        # Process 2.0 (Order management)
        ('Customer', 'P2', 'Order request/details', [(175, 170), (460, 170)]),
        ('P2', 'Customer', 'Order confirmation', [(460, 190), (175, 190)]),
        ('Manager', 'P2', 'Order approval', [(75, 755), (75, 210), (460, 210)]),
        ('P2', 'D1', 'Order records', [(550, 160), (590, 160), (590, 95), (630, 95)]),
        ('D1', 'P2', 'Customer/order info', [(670, 111), (670, 135), (575, 135), (575, 175), (550, 175)]),
        ('P2', 'D2', 'Customer/order info', [(550, 190), (630, 190)]),
        ('P2', 'P3', 'Order info', [(505, 215), (505, 305)]),

        # Process 3.0 (Payment & Set location)
        ('Customer', 'P3', 'Delivery/pickup address', [(105, 145), (105, 320), (460, 320)]),
        ('Customer', 'P3', 'Payment details', [(120, 145), (120, 335), (460, 335)]),
        ('P3', 'Customer', 'Payment status', [(460, 350), (135, 350), (135, 145)]),
        ('P3', 'Customer', 'Payment verification (GCash/COD)', [(460, 365), (150, 365), (150, 145)]),
        ('Rider', 'P3', 'Cash collected (COD payment)', [(130, 460), (130, 380), (460, 380)]),
        ('P3', 'D5', 'Payment info', [(550, 320), (630, 320)]),
        ('D5', 'P3', 'Payment data', [(630, 335), (550, 335)]),
        ('P3', 'D6', 'Assigned location', [(550, 350), (600, 350), (600, 508), (630, 508)]),
        ('P3', 'D1', 'Order details/Order record', [(550, 365), (780, 365), (780, 95), (710, 95)]),
        ('P3', 'P4', 'Order & location details', [(505, 370), (505, 455)]),

        # Process 4.0 (Delivery dispatch)
        ('P4', 'Customer', 'Real-time tracking', [(460, 465), (20, 465), (20, 60), (105, 60), (105, 105)]),
        ('P4', 'Customer', 'Delivery status/Completion update', [(460, 477), (35, 477), (35, 75), (120, 75), (120, 105)]),
        ('P4', 'Rider', 'Delivery assignment & route map', [(460, 490), (175, 490)]),
        ('P4', 'Rider', 'Customer contact & Delivery address', [(460, 502), (175, 502)]),
        ('Rider', 'P4', 'Rider assignment/approval', [(175, 514), (460, 514)]),
        ('Rider', 'P4', 'Delivery status', [(175, 526), (460, 526)]),
        ('P4', 'D1', 'Order status update', [(550, 470), (765, 470), (765, 105), (710, 105)]),
        ('P4', 'D3', 'Stock deduction', [(550, 485), (745, 485), (745, 245), (720, 245)]),
        ('P4', 'D6', 'Dispatch records', [(550, 510), (630, 510)]),
        ('P4', 'P5', 'Confirmed order', [(505, 520), (505, 595)]),

        # Process 5.0 (Management)
        ('Manager', 'P5', 'Approved expense entries', [(85, 755), (85, 620), (460, 620)]),
        ('Manager', 'P5', 'Stock/replenishment updates', [(105, 755), (105, 645), (460, 645)]),
        ('D6', 'P5', 'Delivery records', [(670, 526), (670, 610), (550, 610)]),
        ('D5', 'P5', 'Payment data', [(710, 335), (730, 335), (730, 625), (550, 625)]),
        ('D3', 'P5', 'Production/data&stock/replenishment', [(720, 235), (750, 235), (750, 640), (550, 640)]),
        ('D4', 'P5', 'Approved expense entries/Expense data', [(710, 288), (765, 288), (765, 655), (550, 655)]),
        ('P5', 'P6', 'Delivery data', [(505, 660), (505, 735)]),

        # Process 6.0 (Report and Monitoring)
        ('Manager', 'P6', 'Request report', [(120, 770), (460, 770)]),
        ('P6', 'Manager', 'Sales/inventory/expense summary', [(460, 790), (120, 790)]),
        ('D3', 'P6', 'Inventory data', [(720, 225), (785, 225), (785, 750), (550, 750)]),
        ('D6', 'P6', 'Dispatch record', [(710, 510), (735, 510), (735, 770), (550, 770)]),
        ('P6', 'P7', 'Summarized data', [(505, 805), (505, 880)]),

        # Process 7.0 (Predictive Analytics)
        ('P7', 'Manager', 'Forecast & clustering report', [(550, 915), (835, 915), (835, 980), (60, 980), (60, 790)])
    ]

    for idx, (src, tgt, label, pts) in enumerate(flows):
        edge_id = f'flow_{idx+1}'
        style = 'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#000000;strokeWidth=1;fontColor=#000000;fontSize=9;fontFamily=Arial;labelBackgroundColor=#FFFFFF;labelBorderColor=none;'
        edge = ET.SubElement(root, 'mxCell', {
            'id': edge_id,
            'value': label,
            'style': style,
            'edge': '1',
            'parent': '1',
            'source': src,
            'target': tgt
        })
        geo = ET.SubElement(edge, 'mxGeometry', {'relative': '1', 'as': 'geometry'})
        if len(pts) > 2:
            arr = ET.SubElement(geo, 'Array', {'as': 'points'})
            for px, py in pts[1:-1]:
                ET.SubElement(arr, 'mxPoint', {'x': str(px), 'y': str(py)})

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
        
    print(f"Successfully generated exact match {out_drawio} and {out_xml}!")

if __name__ == '__main__':
    generate_exact_match_dfd()
