from pathlib import Path
import nbformat
from nbconvert import WebPDFExporter

input_path = Path("cuadernos/04_bonus_debayerizado.ipynb")
output_path = Path("cuadernos/04_bonus_debayerizado.pdf")

# Cargar el notebook
with open(input_path, "r", encoding="utf-8") as f:
    nb = nbformat.read(f, as_version=4)

# Configurar el exportador WebPDF
exporter = WebPDFExporter()
exporter.allow_chromium_download = True

# Convertir y escribir
pdf_data, _ = exporter.from_notebook_node(nb)

with open(output_path, "wb") as f:
    f.write(pdf_data)

print(f"Generado exitosamente en: {output_path}")
