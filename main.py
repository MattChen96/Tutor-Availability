from flask import Flask, render_template, request, send_file, after_this_request, send_from_directory

from datetime import datetime , timedelta
import pandas as pd
from create_availability import create_availability_excel
from check_overlaps import check_overlaps
from create_aperture_excel import create_aperture_excel
import os
import json
import logging
import paths

app = Flask(__name__)

root_path = paths.ROOT_DIR
tmp_path = paths.TMP_DIR #cartella per depositari i file temporanei
data_path = paths.DATA_DIR

log_file = root_path + "/app.log"
logging.basicConfig(filename=log_file, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Route per la pagina con il form
@app.route('/', methods=['GET', 'POST'])
def home():

    lista_valori = ['U7 - U14', 'U9', 'U4', 'U16']

    if request.method == 'POST':
        # Leggere i dati inseriti dall'utente
        gruppo = request.form.get('valore')
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        file_csv = request.files['file_csv']

        # Elaborare il range di date inserito dall'utente
        start_date = datetime.strptime(start_date, '%d/%m/%Y')

        end_date = datetime.strptime(end_date, '%d/%m/%Y')

        date_list = pd.date_range(start_date, end_date).strftime('%d/%m/%Y').tolist()

        df = pd.read_csv(file_csv)

        # Elaborare il file Excel caricato dall'utente
        for data in date_list:
            output = create_availability_excel(df, data, gruppo)


        # Registra il download del file delle disponibilità
        app.logger.info(f"Scaricato file di disponibilità: disponibilità_{gruppo}.xlsx")


        return send_file(output, as_attachment=True, download_name= f"disponibilità_{gruppo}.xlsx" ,mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


    return render_template('index.html', lista_valori=lista_valori )

@app.after_request
def delete_file(response):
    file_path_output = os.path.join(root_path, "output.xlsx")
    if os.path.exists(file_path_output):
        try:
            os.remove(file_path_output)
        except Exception as error:
            app.logger.error("Errore durante l'eliminazione del file: ", error)
    return response


with open(os.path.join(root_path,data_path,"aule.json")) as f:
    aule = json.load(f)

# definisci i gruppi di aule in base al nome
gruppi_aule = {
    "Laboratori U4": ["111", "311", "4A1", "531"],
    "Laboratori U16": ["1631", "1641"],
    "Laboratori U7": ["711","712","713","714","715","716","717","718","719","732"],
    "Laboratori U9": ["904","905","906","907","908","909","910","911"],
    "Laboratori U14": ["1401", "14A1"]
}


@app.route('/aule')
def room():
    # ottieni la data corrente
    today = datetime.now()
    week = timedelta(weeks=1)
    next_week = today + week

    # genera una lista di tuple (gruppo, lista di bottoni di link)
    gruppi_links = []
    for gruppo, aule_gruppo in gruppi_aule.items():
        links = []
        for aula in aule_gruppo:
            link = f"http://gestionespazi.didattica.unimib.it/index.php?transpose=&vista=week&area=35&content=view_prenotazioni&_lang=it&day={next_week.day}&month={next_week.month}&year={next_week.year}&room={aule[aula]}"
            links.append((aula, link))
        gruppi_links.append((gruppo, links))

    # passa i gruppi di bottoni alla pagina HTML
    return render_template('aule.html', gruppi_links=gruppi_links)


@app.route('/guide-script')
def script_excel():
    files = [
        {'name': 'Controllo Disponibilità e Orari', 'filename': 'controllo_disponibilita_e_orari.pdf', 'description': 'Guida allo script che controlla che gli orari siano congrue alle disponibilità'},
        {'name': 'Script Verifica Sovrapposizioni', 'filename': 'script_verifica_sovrapposizioni.pdf', 'description': 'Guida allo script che controlla che non ci siano sovrapposizioni dello stesso tutor'},
        {'name': 'Script Visualizza Disponibilità', 'filename': 'script_disponibilità.pdf', 'description': 'Guida allo script che permette di visualizzare le disponibilità verticalmente'}
    ]
    return render_template('guide-script.html', files=files)

@app.route('/download/<filename>')
def download(filename):
    directory = os.path.join(root_path, data_path, 'guide_script/')  # Sostituisci con il percorso reale della cartella dei file PDF

    app.logger.info(f"Scaricato la guida script: {filename}")

    return send_from_directory(directory, filename)


@app.route('/controlla-sovrapposizioni', methods=['GET', 'POST'])
def controlla_sovrapposizioni():
    lista_gruppi = ["U7-U14", "U9", "U4", "U16"]  # U7-U14 sono nello stesso file excel e
                                                  # il controllo delle sovrapposizioni dev'essere fatto sull'intero excel

    if request.method == 'POST':
        # Leggere i dati inseriti dall'utente
        gruppo = request.form.get('gruppo')
        file = request.files['file_xlsx']
        file.save(os.path.join(root_path, tmp_path, 'sovrapposizioni_file.xlsx'))

        # Controllo delle sovrapposizioni e generazione del report
        report_file = check_overlaps(file, gruppo)

        app.logger.info(f"Scaricato il report: report_{gruppo}.txt")

        # Invia il report come file di testo al client
        return send_file(report_file, as_attachment=True, download_name=f"report_{gruppo}.txt", mimetype='text/plain')

    return render_template('controlla-sovrapposizioni.html', lab_groups=lista_gruppi)

@app.route('/crea-excel-aperture', methods=['GET', 'POST'])
def crea_excel_aperture():
    lista_edifici = ["U7", "U14", "U9", "U4", "U16"]  # U7 e U14 hanno 2 fogli delle aperture distinti

    if request.method == 'POST':
        # Leggere i dati inseriti dall'utente
        gruppo = request.form.get('gruppo')
        file = request.files['file_xlsx']
        file.save(os.path.join(root_path, tmp_path, 'aperture_file.xlsx'))

        print(gruppo)

        # Controllo delle sovrapposizioni e generazione del report
        file_aperture = create_aperture_excel(file, gruppo)

        app.logger.info(f"Scaricato file delle aperture: aperture_{gruppo}.xlsx")

        return send_file(file_aperture, as_attachment=True, download_name=f"aperture_{gruppo}.xlsx", mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    return render_template('crea-excel-aperture.html', lab_groups=lista_edifici)


if __name__ == '__main__':
    app.run(debug=True)
