import openpyxl
from openpyxl import Workbook
import json

with open('/home/mattchen2/Tutor-Availability/data/caselle_excel_laboratori.json') as f:
    caselle = json.load(f)

def create_aperture_excel(file_path, lab_group):

    # Aprire il file di lavoro
    workbook = openpyxl.load_workbook(file_path)

    ws = workbook.worksheets[0]

    # Crea un nuovo foglio di lavoro
    wb = Workbook()

    ws_aperture = wb.active

    giorni_settimana = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì"]

    # Array contenente le righe di inizio dei vari laboratori
    arr_lab = list(caselle[lab_group].values())

    report = ""  # Stringa di report

    tmp_lab= set()

    for j in range(len(arr_lab)):
        for k in range(j + 1, len(arr_lab)):
            for i in range(arr_lab[j], arr_lab[j] + 20):
                for l in range(4, 9):  # Colonne D a H
                    if (ws.cell(row=i, column=l).value is not None
                            and ws.cell(row=i, column=l).value != ""  # Controlla che la casella non sia vuota
                            and ws.cell(row=i, column=l).fill.start_color.index == 'FFFFFFFF' # Controlla che la casella sia bianca (codice colore RGB per bianco)
                    ):
                        lab1 = ""
                        lab2 = ""
                        for lab, start_row in caselle[lab_group].items():
                            if start_row <= i <= start_row + 19:
                                lab1 = lab
                            if (
                                arr_lab[k] + (i - arr_lab[j])
                                >= start_row
                                and arr_lab[k] + (i - arr_lab[j])
                                <= start_row + 19
                            ):
                                lab2 = lab

                        #report += f"Errore: Cognome '{ws.cell(row=i, column=l).value}' duplicato rilevato nelle righe {i} e {arr_lab[k] + (i - arr_lab[j])}, giorno: {giorni_settimana[l - 4]}, Laboratorio: {lab1} e {lab2}.\n"
                        tmp_lab.add(lab1)
                        tmp_lab.add(lab2)

            lista_lab = '/'.join(map(str, tmp_lab))
            ws_aperture.cell(row=i, column=l, value=lista_lab)
            tmp_lab.clear()

    file_name = f"aperture_{lab_group}.xlsx"
    excel_file = "/home/mattchen2/Tutor-Availability/" + file_name
    ws_aperture.save(excel_file)

    return excel_file


