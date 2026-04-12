import pdfplumber
import re

def extract_puck_data(file_path):

    with pdfplumber.open(file_path) as pdf:
        page = pdf.pages[0]
        text = page.extract_text()
        
        for line in text.split("\n"):
            if "EPSØxH" in line:
                eps_height = float(line.split()[-1].replace(",", "."))
            if "Connectionstype" in line:
                holeformers = re.findall(r'(\d+)-\d+"\s*(PVC|Concrete)', line, re.IGNORECASE)
        return eps_height, holeformers