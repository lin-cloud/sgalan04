import PySimpleGUI as sg
import backup
import restoreBackup

image_backup = './images/backup.png'
image_recovery = './images/recovery.png'
image_exit = './images/close.png'

sg.theme('Default1')
# sg.theme_button_color(('black', '#1DA1F2'))

switcher = {
    'backup': backup.execute,
    'restore': restoreBackup.execute,
}

user = 'ecgel'


layout = [[sg.ReadFormButton('', image_filename=image_backup, image_size=(100, 100),
                                image_subsample=6, border_width=3, key='backup'), sg.Text(' ' * 12),
           sg.ReadFormButton('', image_filename=image_recovery, image_size=(100, 100),
                                image_subsample=9, border_width=3, key='restore')],
          [sg.Text('    Crear una copia'), sg.Text(' ' * 10), sg.Text(' Restaurar una copia')],
          [sg.Text(' ' * 10)],
          [sg.Button('Salir')]]

window = sg.Window('Copias de seguridad', layout, size=(504, 300), element_justification="center")

while True:
    event, values = window.Read()
    if event in (None, 'Exit', 'Salir'):
        break
    func = switcher.get(event)
    func(user)

window.Close()
