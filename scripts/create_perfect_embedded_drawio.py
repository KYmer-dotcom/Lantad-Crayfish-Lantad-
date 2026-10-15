import base64
import xml.etree.ElementTree as ET
import xml.dom.minidom
from PIL import Image

def build_perfect_drawio():
    img_path = r'Documents/Final_Paper/ch3_extracted_images/level_1_dfd_exact.png'
    with Image.open(img_path) as im:
        img_w, img_h = im.size

    with open(img_path, 'rb') as f:
        img_b64 = base64.b64encode(f.read()).decode('utf-8')

    mxfile = ET.Element('mxfile', {
        'host': 'app.diagrams.net',
        'modified': '2026-09-23T03:32:00.000Z',
        'agent': 'Antigravity Pixel Perfect DFD',
        'version': '24.0.0',
        'type': 'device'
    })
    
    diagram = ET.SubElement(mxfile, 'diagram', {
        'id': 'dfd_level_1_exact_canvas',
        'name': 'Level 1 Data Flow Diagram'
    })
    
    mxGraphModel = ET.SubElement(diagram, 'mxGraphModel', {
        'dx': str(img_w + 200),
        'dy': str(img_h + 200),
        'grid': '1',
        'gridSize': '10',
        'guides': '1',
        'tooltips': '1',
        'connect': '1',
        'arrows': '1',
        'fold': '1',
        'page': '1',
        'pageScale': '1',
        'pageWidth': str(img_w + 80),
        'pageHeight': str(img_h + 80),
        'background': '#FFFFFF',
        'math': '0',
        'shadow': '0'
    })
    
    root = ET.SubElement(mxGraphModel, 'root')
    
    # Base cells
    ET.SubElement(root, 'mxCell', {'id': '0'})
    ET.SubElement(root, 'mxCell', {'id': '1', 'parent': '0'})
    
    # Background Image Cell (100% exact replica of the diagram)
    img_cell = ET.SubElement(root, 'mxCell', {
        'id': 'dfd_exact_canvas',
        'value': '',
        'style': f'shape=image;image=data:image/png;base64,{img_b64};verticalLabelPosition=bottom;verticalAlign=top;imageAspect=1;aspect=fixed;',
        'vertex': '1',
        'parent': '1'
    })
    ET.SubElement(img_cell, 'mxGeometry', {
        'x': '40',
        'y': '40',
        'width': str(img_w),
        'height': str(img_h),
        'as': 'geometry'
    })

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
        
    print(f"Successfully generated 100% exact replica {out_drawio} and {out_xml} ({img_w}x{img_h}px)!")

if __name__ == '__main__':
    build_perfect_drawio()
