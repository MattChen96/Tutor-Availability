import openpyxl
from openpyxl import Workbook
import json

def create_aperture_excel(file_path, lab_group):

    print("START create_aperture_excel")

    with open('/home/mattchen2/Tutor-Availability/data/caselle_excel_laboratori.json') as f:
        caselle = json.load(f)

    # Aprire il file di lavoro
    workbook = openpyxl.load_workbook(file_path)
    ws = workbook.worksheets[0]

    #giorni_settimana = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì"]

    # Crea un nuovo foglio di lavoro
    wb = Workbook()
    ws_aperture = wb.active

    # Array contenente le righe di inizio dei vari laboratori
    tuple_lab = list(caselle[lab_group].items())

    for lab_name, lab_index in tuple_lab:
        for l in range(4, 9):  # Colonne D a H
            indice = tuple_lab[0][1]
            for i in range(lab_index, lab_index + 20):
                if (ws.cell(row=i, column=l).value is not None
                            and ws.cell(row=i, column=l).value != ""
                            and (ws.cell(row=i, column=l).fill.start_color.index in ['FFFFFFFF', 0 , 00000000] or (not ws.cell(row=i, column=l).fill.start_color.index.startswith('FF')) )):

                    if ws_aperture.cell(row=indice, column=l).value is None:
                        lista_lab = lab_name
                    else:
                        lista_lab = ws_aperture.cell(row=indice, column=l).value + "/" + lab_name

                    ws_aperture.cell(row=indice, column=l, value=lista_lab)

                indice+=1

    file_name = f"aperture_{lab_group}.xlsx"
    excel_file = "/home/mattchen2/Tutor-Availability/" + file_name
    wb.save(excel_file)

    return excel_file