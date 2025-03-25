import os
import csv
from fpdf import FPDF

# Criar pasta reports se não existir
if not os.path.exists("reports"):
    os.makedirs("reports")

def generate_csv(user_id):
    file_path = f"reports/relatorio_{user_id}.csv"
    with open(file_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Campo", "Valor"])
        writer.writerow(["ID do Usuário", user_id])
        writer.writerow(["Tempo Total de Jogo", "200 minutos"])
        writer.writerow(["Total de Apostas", "15"])
        writer.writerow(["Média de Apostas", "R$ 25,00"])
        writer.writerow(["Total de Depósitos", "5"])
        writer.writerow(["Média de Depósitos", "R$ 100,00"])
    return file_path

def generate_pdf(user_id):
    file_path = f"reports/relatorio_{user_id}.pdf"
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    pdf.cell(200, 10, f"Relatório do Usuário {user_id}", ln=True, align='C')
    pdf.ln(10)
    
    pdf.cell(200, 10, "Tempo Total de Jogo: 200 minutos", ln=True)
    pdf.cell(200, 10, "Total de Apostas: 15", ln=True)
    pdf.cell(200, 10, "Média de Apostas: R$ 25,00", ln=True)
    pdf.cell(200, 10, "Total de Depósitos: 5", ln=True)
    pdf.cell(200, 10, "Média de Depósitos: R$ 100,00", ln=True)
    
    pdf.output(file_path)
    return file_path
