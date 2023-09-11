import PySimpleGUI as sg
import loadbar


def execute(user):
    switcher = {
        'load': loadbar.execute,
    }
    image_recovery = './images/recovery.png'
    sg.theme('Default1')
    # sg.theme_button_color(('black', '#6D9F85'))

    layout = [[sg.Text('SELECCIONE LA COPIA SEGURIDAD QUE DESEA RESTAURAR')],
              [sg.Text(' ' * 10)],
              [sg.FileBrowse("Archivo"), sg.InputText('Default Folder')],
              [sg.Text(' ' * 10)],
              [sg.Button('Restaura', key='load'), sg.Button('Salir')]]

    window = sg.Window('Restaurar los datos').Layout(layout)

    while True:
        event, values = window.Read()
        if event in (None, 'Salir', 'Exit'):
            break
        func = switcher.get(event)
        func(user,values)
    window.Close()

