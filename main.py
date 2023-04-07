from flask import Flask, render_template, request, send_file, after_this_request
from datetime import datetime , timedelta
import pandas as pd
from create_availability import create_availability_excel
import os

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


# esempio di dizionario aule-identificativi
dizionario_aule = {
    "LAB 111": "358",
    "LAB 311": "175",
    "LAB 4A1": "73"
}

@app.route('/aule')
def index():
    # ottieni la data corrente
    today = datetime.now()
    week = timedelta(weeks=1)
    next_week = today + week

    # genera la lista di bottoni di link
    links = []
    for aula, identificativo in dizionario_aule.items():
        link = f"http://gestionespazi.didattica.unimib.it/index.php?transpose=&vista=week&area=35&content=view_prenotazioni&_lang=it&day={next_week.day}&month={next_week.month}&year={next_week.year}&room={identificativo}"
        links.append((aula, link))

    # passa i bottoni alla pagina HTML
    return render_template('aule.html', links=links)

if __name__ == '__main__':
    app.run()
