import PySimpleGUI as sg
import subprocess


def execute(user, values):
    sg.theme('Default1')
    # sg.theme_button_color(('black', '#6D9F85'))

    source_file = values['Archivo']
    destination_folder = "c:/Users/" + user + "/ECG-5.1.0/mysql-data/hospital/"

    i = 1
    sg.OneLineProgressMeter('REESTABLECIENDO LOS DATOS', i, 4, 'key', 'POR FAVOR, ESPERE',orientation='horizontal')
    # Detiene la base de datos
    command = 'docker stop db'
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]

    i = 2
    sg.OneLineProgressMeter('REESTABLECIENDO LOS DATOS', i, 4, 'key', 'POR FAVOR, ESPERE',orientation='horizontal')
    # Restaura la copia de la base de datos en el sistema
    command = 'tar -xf ' + source_file + ' -C ' + destination_folder
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]

    i = 3
    sg.OneLineProgressMeter('REESTABLECIENDO LOS DATOS', i, 4, 'key', 'POR FAVOR, ESPERE',orientation='horizontal')
    # Reinicia la base de datos
    command = 'docker start db'
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]

    i = 4
    sg.OneLineProgressMeter('REESTABLECIENDO LOS DATOS', i, 4, 'key', 'POR FAVOR, ESPERE',orientation='horizontal')
