from flask import Flask, render_template, request, send_file, after_this_request
from datetime import datetime , timedelta
import pandas as pd
from create_availability import create_availability_excel
import os
import json

app = Flask(__name__)

# Lista predefinita di valori per il primo input
lista_valori = ['U7 - U14', 'U9', 'U4', 'U16']

# Route per la pagina con il form
@app.route('/', methods=['GET', 'POST'])
def home():
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


        return send_file(output, as_attachment=True, download_name= f"disponibilità_{gruppo}.xlsx" ,mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' )


    return render_template('index.html', lista_valori=lista_valori )

@app.after_request
def delete_file(response):
    file_path_output =  "/home/mattchen2/Tutor-Availability/output.xlsx"
    if os.path.exists(file_path_output):
        try:
            os.remove(file_path_output)
        except Exception as error:
            app.logger.error("Errore durante l'eliminazione del file: ", error)
    return response


with open('/home/mattchen2/Tutor-Availability/data/aule.json') as f:
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

if __name__ == '__main__':
    app.run()
