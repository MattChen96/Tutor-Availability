def check_overlaps(file_path, lab_group):
    # Aprire il file di lavoro
    workbook = openpyxl.load_workbook(file_path)

    ws = workbook.worksheets[0]

    # Definire gli array di laboratori e giorni della settimana
    laboratori = [
        ["LAB711", 7, 26],
        ["LAB712", 35, 54],
        ["LAB713", 63, 82],
        ["LAB714", 91, 110],
        ["LAB715", 119, 138],
        ["LAB716", 147, 166],
        ["LAB717", 175, 194],
        ["LAB718", 203, 222],
        ["LAB719", 231, 250],
        ["LAB732", 286, 306],
        ["LAB1401", 315, 334],
        ["LAB14A1", 342, 362]
    ]

    giorni_settimana = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì"]

    # Array contenente le righe di inizio dei vari laboratori
    arr_lab = [7, 35, 63, 91, 119, 147, 175, 203, 231, 286, 315, 342]

    report = ""  # Stringa di report

    for j in range(len(arr_lab)):
        for k in range(j + 1, len(arr_lab)):
            for i in range(arr_lab[j], arr_lab[j] + 20):
                for l in range(4, 9):  # Colonne D a H
                    if (
                        ws.cell(row=i, column=l).value == ws.cell(
                            row=arr_lab[k] + (i - arr_lab[j]), column=l
                        ).value
                        and ws.cell(row=i, column=l).value is not None
                    ):
                        lab1 = ""
                        lab2 = ""
                        for m in range(len(laboratori)):
                            if laboratori[m][1] <= i <= laboratori[m][2]:
                                lab1 = laboratori[m][0]
                            if (
                                arr_lab[k] + (i - arr_lab[j])
                                >= laboratori[m][1]
                                and arr_lab[k] + (i - arr_lab[j])
                                <= laboratori[m][2]
                            ):
                                lab2 = laboratori[m][0]

                        report += f"Errore: Cognome '{ws.cell(row=i, column=l).value}' duplicato rilevato nelle righe {i} e {arr_lab[k] + (i - arr_lab[j])}, giorno: {giorni_settimana[l - 4]}, Laboratorio: {lab1} e {lab2}.\n"

    if not report:
        report = "Nessun cognome duplicato rilevato."

    # Salva il report in un file di testo
    report_file = "report.txt"
    with open(report_file, "w") as f:
        f.write(report)
    return report_file

if __name__ == '__main__':
    app.run()
