from flask import Flask, render_template, request, send_from_directory
import os
from gerar_relatorio import generate_csv_report  # Certifique-se de importar a função correta
from gerar_relatorio_pdf import generate_pdf_report  # Importação para PDF

app = Flask(__name__)

# Criar pasta reports se não existir
if not os.path.exists("reports"):
    os.makedirs("reports")

@app.route("/", methods=["GET", "POST"])
def index():
    report_status = None
    file_path = None

    if request.method == "POST":
        user_id = request.form["user_id"]
        report_type = request.form["report_type"]

        if user_id:
            if report_type == "csv":
                file_path = generate_csv_report(user_id)  # Agora chama a função diretamente
                if file_path:
                    report_status = f"✅ CSV gerado com sucesso! <a href='/download/{os.path.basename(file_path)}'>Baixar</a>"
                else:
                    report_status = "❌ Erro ao gerar CSV!"

            elif report_type == "pdf":
                file_path = generate_pdf_report(user_id)  # Agora chama a função diretamente
                if file_path:
                    report_status = f"✅ PDF gerado com sucesso! <a href='/download/{os.path.basename(file_path)}'>Baixar</a>"
                else:
                    report_status = "❌ Erro ao gerar PDF!"

    return render_template("index.html", report_status=report_status)

# 📌 Endpoint para baixar os arquivos gerados
@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory("reports", filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
