import docx

doc = docx.Document(r'c:\Users\kymer\Desktop\Lantad ACarwfish Django\Documents\Final_Paper\Chapter_1.docx')
sec = doc.sections[0]
print(f"Chapter_1.docx Dimensions: width={sec.page_width.inches} inches, height={sec.page_height.inches} inches")
print(f"Margins: top={sec.top_margin.inches} in, bottom={sec.bottom_margin.inches} in, left={sec.left_margin.inches} in, right={sec.right_margin.inches} in")
