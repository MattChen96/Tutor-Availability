import pandas as pd
from datetime import datetime, timedelta
import os.path
from openpyxl import Workbook



def clear(df):
    df['Informazioni cronologiche'] = pd.to_datetime(df['Informazioni cronologiche'], format='%d/%m/%Y %H.%M.%S')
    oggi = datetime.today()
    seimesti_fa = oggi - timedelta(days=1 * 30)
    df = df[df['Informazioni cronologiche'] >= seimesti_fa]
    return df


def create_availability_excel(df, data_da_filtrare, gruppo):

    #file_path_output = os.path.join(os.getcwd(), "output.xlsx")
    file_path_output = "/home/mattchen2/Tutor-Availability/output.xlsx"

    if not os.path.isfile(file_path_output):
        # se il file non esiste, crea un nuovo file Excel e aggiungi il primo foglio
        wb = Workbook()
        ws = wb.active
        ws.title = data_da_filtrare.replace('/', '-')
        wb.save(file_path_output)

    gruppo_tutor_da_filtrare = gruppo
    df = df[(df['Data'] == data_da_filtrare) & (df['Gruppo Tutor'] == gruppo_tutor_da_filtrare)]

    # crea una lista di tutte le fasce orarie divisi in blocchi da 30 minuti
    start_time = datetime.strptime('8:00', '%H:%M')
    end_time = datetime.strptime('19:00', '%H:%M')
    time_blocks = []
    while start_time <= end_time:
        time_blocks.append(start_time.strftime('%H:%M'))
        start_time += timedelta(minutes=30)

    # crea un dizionario in cui ogni chiave è una combinazione di nome e cognome, e ogni valore è una lista di stringhe che indica la disponibilità in ogni blocco di tempo
    availability_dict = {}
    for _, row in df.iterrows():
        name = row['Cognome e Nome']
        availability = [' '] * len(time_blocks)
        from_time = datetime.strptime(row['Da quando?'], '%H.%M.%S')

        if from_time.minute < 30:
            rounded_time = from_time.replace(minute=30, second=0, microsecond=0)
        else:
            rounded_time = from_time.replace(hour=from_time.hour + 1, minute=0, second=0, microsecond=0)

        from_time = rounded_time

        to_time = datetime.strptime(row['A quando?'], '%H.%M.%S')

        if to_time.minute >= 30:
            rounded_time = to_time.replace(minute=30, second=0, microsecond=0)
        else:
            rounded_time = to_time.replace(minute=0, second=0, microsecond=0)

        to_time = rounded_time


        if from_time.time() >= datetime.strptime('19:00', '%H:%M').time() or to_time.time() <= datetime.strptime('08:00', '%H:%M').time():
            continue  # salta la riga se la disponibilità cade durante la fascia notturna

        if from_time.time() < datetime.strptime('8:00', '%H:%M').time():
            from_time = datetime.strptime('8:00', '%H:%M')

        if to_time.time() > datetime.strptime('19:00', '%H:%M').time():
            to_time = datetime.strptime('19:00', '%H:%M')

        from_index = time_blocks.index(from_time.strftime('%H:%M'))
        to_index = time_blocks.index(to_time.strftime('%H:%M'))


        for i in range(from_index -1 , to_index):
            availability[i] = name
        if name in availability_dict:
            availability_dict[name] = [max(x) for x in zip(availability_dict[name], availability)]
        else:
            availability_dict[name] = availability

    # crea un dataframe Pandas a partire dal dizionario e trasponilo
    df_availability = pd.DataFrame.from_dict(availability_dict, orient='index', columns=time_blocks).T
    df_availability.index.name = 'Ora'
    df_availability = df_availability.reset_index()

    # Aggiungi colonna 'Fine' che indica la fine del blocco di tempo
    time_blocks.append('19:00')
    fine_blocks = [time_blocks[i + 1] for i in range(len(time_blocks) - 1)]


    df_availability.insert(1, "Fine", fine_blocks)


    with pd.ExcelWriter(file_path_output, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        df_availability.to_excel(writer, sheet_name=data_da_filtrare.replace('/', '-'), index=False)

    return file_path_output


