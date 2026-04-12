# import pdfplumber

# with pdfplumber.open(r"C:\Users\yuber\OneDrive\Documents\kuka\Incoming Orders\EPS_2_26349_MH01A_A_20260304022828.pdf") as pdf:
#     page = pdf.pages[0]
#     print(page.extract_text())

# import re
# import pdfplumber

# with pdfplumber.open(r"C:\Users\yuber\OneDrive\Documents\kuka\Incoming Orders\today\EPS_2_25716_MHFD01A_B_20260324014243.pdf") as pdf:
#     page = pdf.pages[0]
#     text = page.extract_text()
            
#     for line in text.split("\n"):
#         if "Connectionstype" in line:
#             print(line)
#             matches = re.findall(r'(\d+)-\d+"\s*(PVC|Concrete)', line, re.IGNORECASE)
#             print(matches)

import sys
from workload_app.pdf_extract import extract_puck_data

sys.path.insert(0, ".")

extracted_data = extract_puck_data(r"C:\Users\yuber\OneDrive\Documents\kuka\Incoming Orders\today\EPS_2_25716_MHFD01A_B_20260324014243.pdf")
print(extracted_data)