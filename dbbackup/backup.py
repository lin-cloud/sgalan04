import PySimpleGUI as sg
import time
import subprocess


def execute(user):
    sg.theme('Default1')
    # sg.theme_button_color(('black', '#6D9F85'))

    layout = [[sg.Text(key='texto', background_color='white', text_color='black', size=(40, 12))],
              [sg.Button('Salir')]]

    window = sg.Window('Copia de seguridad').Layout(layout)
    window.Finalize()

    filestamp = time.strftime('%Y-%m-%d-%H-%M')
    destination_file = "c:/Users/" + user + "/Desktop/copias_de_seguridad/copia-bd-" + filestamp + ".zip"
    source_folder = "c:/Users/" + user + "/ECG-5.1.0/mysql-data/hospital/"

    msg = 'Sincronizando la base de datos...\r\n'
    window.FindElement("texto").Update(value=msg)
    window.refresh()
    # Detiene la base de datos
    command = 'docker stop db'
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]


    msg = 'Sincronizada la base de datos\r\nRealizando copia...'
    window.FindElement("texto").Update(value=msg)
    window.refresh()
    # Crea el directorio copias
    command = 'mkdir "c:/Users/' + user + '/Desktop/copias_de_seguridad"'
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]

    # Guarda la copia en el directorio
    command = 'tar -C ' + source_folder + ' -acf ' + destination_file + ' *.*'
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]

    msg = 'Sincronizada la base de datos\r\nRealizada la copia\r\nReiniciando el sistema...'
    window.FindElement("texto").Update(value=msg)
    window.refresh()
    # Reinicia la base de datos
    command = 'docker start db'
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
    msg = 'SE HA CREADO UNA COPIA DE LOS DATOS\r\n'
    msg+= 'EN EL DIRECTORIO "copias_de_seguridad"'
    window.FindElement("texto").Update(value=msg)
    window.refresh()

    while True:
        event, values = window.Read()
        if event in (None, 'Salir', 'Exit'):
            break

    window.Close()
