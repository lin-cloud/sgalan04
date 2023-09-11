import fis


def alarma(qtc, contexto, incremento):
    fis_file = ''

    if incremento < 50:
        fis_file = 'RIESGO-2.fis.json'
    if incremento < 25:
        fis_file = 'RIESGO-1.fis.json'
    if incremento >= 50:
        fis_file = 'RIESGO-3.fis.json'

    R = fis.readfis(fis_file)
    arritmia = fis.evalfis([qtc, contexto], R)

    return arritmia
