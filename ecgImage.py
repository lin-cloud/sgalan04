import os
import glob
import cv2
import numpy as np
import scipy.signal as signal
import scipy.io as sio
from pdf2image import convert_from_path
from matplotlib import pyplot as plt
# from scipy.io import savemat
# plt.switch_backend('MacOSX')


# ---------------------------------------------------------------------------------------
# Funciones Auxiliares
# ---------------------------------------------------------------------------------------
def indices(a, func):
    return [i for (i, val) in enumerate(a) if func(val)]


def imadjust(image, gamma=1.0):
    lookUpTable = np.empty((1, 256), np.uint8)
    for i in range(256):
        lookUpTable[0, i] = np.clip(pow(i / 255.0, gamma) * 255.0, 0, 255)
    return cv2.LUT(image, lookUpTable)


def ResizeWithAspectRatio(image, width=None, height=None, inter=cv2.INTER_AREA):
    dim = None
    (h, w) = image.shape[:2]

    if width is None and height is None:
        return image
    if width is None:
        r = height / float(h)
        dim = (int(w * r), height)
    else:
        r = width / float(w)
        dim = (width, int(h * r))

    return cv2.resize(image, dim, interpolation=inter)


def convert(img, target_type_min, target_type_max, target_type):
    imin = img.min()
    imax = img.max()

    a = (target_type_max - target_type_min) / (imax - imin)
    b = target_type_max - a * imax
    new_img = (a * img + b).astype(target_type)
    return new_img


def displayImage(image):
    cv2.namedWindow("output", cv2.WINDOW_NORMAL)        # Create window with freedom of dimensions
    resize = ResizeWithAspectRatio(image, width=1280)  # Resize by width OR
    # resize = ResizeWithAspectRatio(image, height=1280) # Resize by height
    cv2.imshow('resize', resize)
    cv2.waitKey(0)  # Display the image infinitely until any keypressq113' # hit q to exit
    return

# ---------------------------------------------------------------------------------------
# Funciones Principales
# ---------------------------------------------------------------------------------------
def estimacion_periodo_muestreo(imagen, sondeos=5):
    # entrada: imagen , numero lineas para sondear
    # salida: periodo de muestreo estimado
    # funcion:calculo de Ts buscando numero de pixeles en cada cuadr�culo y
    # considerando 0.04 segundos por cuadricula
    nfila, ncol = imagen.shape
    lineas = np.floor(np.random.rand(sondeos)*nfila/2).astype(int)
    periodo = []
    for cont_periodo in np.arange(sondeos):
        linea = imagen[lineas[cont_periodo], :]
        locs, _ = signal.find_peaks(linea, prominence=[0.1])
        # figure(30);findpeaks(linea,'MinPeakProminence',0.1)
        dif_locs = np.diff(locs)
        # dif_locs_ord=sort(dif_locs)
        media_dif = np.mean(dif_locs)
        desv = np.std(dif_locs)
        umbral_periodo = desv/4.
        periodos_validos = dif_locs[np.abs(dif_locs-media_dif) < umbral_periodo]
        if len(periodos_validos) > 0:
            periodo.append(np.mean(periodos_validos))

    periodo_medio = np.mean(periodo)
    Ts = 0.04/periodo_medio
    return Ts


def imagen2vector(imagen):
    # entrada: imagen con ecg
    # salida: vector con ecg
    # funcion: obtener para el vector ecg de la imagen
    # para cada columna de la imagen (instante de tiempo) calcular que valor de
    # amplitud (posicion media de pixeles activos)
    nfila, ncol = imagen.shape
    ecg = np.zeros(ncol)
    ecg[0] = -1  # eliminar, caso primer pixel.
    for cont in np.arange(1, ncol):
        vector = imagen[:, cont]
        inds = indices(vector, lambda x: x == 255)
        if len(inds) > 0:
            mediana_indices = np.median(inds)
            ecg[cont] = mediana_indices
        else:
            ecg[cont] = ecg[cont-1]

    # En caso de blanco inicial, cojo valores siguientes
    for cont in np.fliplr([np.arange(ncol)])[0]:
        if ecg[cont] == -1:
            ecg[cont] = ecg[cont+1]

    # ajustar origen de coordenadas
    out = np.zeros((len(ecg), 1))
    out[:,0] = nfila-ecg
    return out


def elimina_region(imagen, min_area=30):
    # find all your connected components (white blobs in your image)
    nb_components, output, stats, centroids = cv2.connectedComponentsWithStats(imagen, connectivity=8)
    # connectedComponentswithStats yields every separated component with information on each of them,
    # such as size the following part is just taking out the background which is also considered a
    # component, but most of the time we don't want that.
    sizes = stats[1:, -1]
    nb_components = nb_components - 1

    # minimum size of particles we want to keep (number of pixels)
    img2 = np.zeros((output.shape))
    # for every component in the image, you keep it only if it's above min_size
    for i in range(0, nb_components):
        if sizes[i] >= min_area:
            img2[output == i + 1] = 255
    return img2


def ECG_image_values(file, draw=False):
    filename, extension = os.path.splitext(file)
    if extension == '.pdf':
        img = np.asarray(convert_from_path(file)[1])
        img = cv2.bitwise_not(cv2.cvtColor(np.array(img), cv2.COLOR_BGR2GRAY))
        img[1304:1321, 196:212] = 0  # Borro II
        n_red = 0
        im_signal = ResizeWithAspectRatio(img[1235:1480, 157:2123], height=600)
        im_grid = im_signal
    else:
        # load the image and grab its width and height
        im_gray = cv2.bitwise_not(cv2.imread(file, cv2.IMREAD_GRAYSCALE))
        im_gray = ResizeWithAspectRatio(im_gray, height=600) # [:,:10000]

    # --------- GRID COMPUTATION ------------
    # CALCULO DE PERIODO DE MUESTREO.DISTANCIA CUADRICULAS
    kernel = np.ones((100, 1), np.uint8)  # note this is a horizontal kernel
    d_im = cv2.dilate(im_gray[:100, :], kernel, iterations=1)
    e_im = cv2.erode(d_im, kernel, iterations=1)
    # --- Metodo Raul ---
    # Ts = estimacion_periodo_muestreo(e_im/255., sondeos=5)
    # --- Metodo Mediana ---
    locs, _ = signal.find_peaks(np.median(e_im/255., axis=0), prominence=[0.1])
    # plt.plot(np.median(e_im / 255., axis=0))
    # plt.stem(locs, np.median(e_im / 255., axis=0)[locs], markerfmt='rx')
    dif_locs = np.diff(locs)
    periodo = np.median(dif_locs)
    # print(dif_locs)
    # print("Mediana: {0}".format(periodo))
    #periodo = 18
    Ts = 0.04 / periodo
    # print("Ts: {0}".format(Ts))

    # --------- ECG SIGNAL COMPUTATION ------------
    # AJUSTE NO LINEAL DE CONTRASTE
    im_gray_ad = imadjust(im_gray, gamma=2)

    # BINARIZACION POR BLOQUES
    blur = cv2.GaussianBlur(im_gray_ad, (5, 5), 0)
    _, im_bw = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Si hay rojos, salta al calculo de contornos
    # if n_red > 5:
    #     im_signal = im_bw
    # else:
    #     # Si no hay rojos, intentamos reducir el efecto del grid
    #     # PROCESAMIENTO MORFOLOGICO OPENING
    #     kernel = np.array([[0, 0, 1, 0, 0],
    #                        [0, 1, 1, 1, 0],
    #                        [1, 1, 1, 1, 1],
    #                        [0, 1, 1, 1, 0],
    #                        [0, 0, 1, 0, 0]], dtype=np.uint8)  # DIAMOND KERNEL
    #     im_signal = cv2.morphologyEx(im_bw, cv2.MORPH_OPEN, kernel)
    im_signal = im_bw

    # ELIMINACION AREAS PEQUENAS
    # im_signal = cv2.bitwise_not(convert(im_signal, 0, 255, np.uint8))
    im_signal = convert(im_signal, 0, 255, np.uint8)
    # backtorgb = cv2.cvtColor(im_signal, cv2.COLOR_GRAY2RGB)
    contours, hierarchy = cv2.findContours(im_signal, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    # cv2.drawContours(backtorgb, contours, -1, (0, 255, 0), 3)
    # cv2.imshow('Contours', backtorgb)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    # Signal to extract
    contour_signal = np.zeros(im_signal.shape, np.uint8)
    # Recorro contornos de menos a mas area
    contours = sorted(contours, key=cv2.contourArea, reverse=False)  # Sort by area, descending
    for cnt in contours:
        if cv2.contourArea(cnt) > 100:
            left = tuple(cnt[cnt[:, :, 0].argmin()][0])[0]
            right = tuple(cnt[cnt[:, :, 0].argmax()][0])[0]
            mask_aux = np.zeros(contour_signal.shape, np.uint8)
            # cv2.drawContours(mask_aux, cnt, -1, 255, thickness=cv2.FILLED)
            cv2.fillPoly(mask_aux, pts=[cnt], color=255)
            contour_signal[:, left:right] = mask_aux[:, left:right]

    # CONVERSION IMAGEN A VECTOR
    ecg = imagen2vector(contour_signal)

    # draw = True
    if draw:
        print(file[5:])
        t = np.arange(0, len(ecg) * Ts, Ts)[:len(ecg)]
        fig, axs = plt.subplots(4)
        fig.suptitle('Ts ' + '{0:.4f}'.format(Ts) + ' - Procesado de ECG para image: ' + os.path.basename(file))
        axs[0].imshow(im_gray, cmap='Greys')
        axs[1].imshow(im_bw, cmap='Greys')
        axs[1].stem(locs, 50*np.ones(len(locs)), markerfmt='rx')
        axs[2].imshow(contour_signal, cmap='Greys')
        axs[3].plot(t, ecg)
        axs[3].set_xlim([0, np.max(t)])
        # plt.show()
        filepdf = file[5:]+'-image.pdf'
        plt.savefig(filepdf)

    return ecg, Ts


# MAIN FUNCTION
if __name__ == "__main__":
    # in_path ='/home/ecgtovector/input/'
    # in_path = 'ecgc-set1/'
    # in_path = 'ECG_Quiron/'
    # in_path = 'ECGs-Linares/'
    # in_path = './ECG-Elda/'
    in_path = 'test/'

    print('Processing ecgtovector')
    types = (in_path + '*.jpg', in_path + '*.png', in_path + '*.pdf')  # the tuple of file types
    files_grabbed = []
    for files in types:
        files_grabbed.extend(glob.glob(files))

    for file in files_grabbed:
        print('Procesing File: ' + file)

        ecg, Ts = ECG_image_values(file, draw=True)
        adict = {}
        adict['ecg'] = ecg
        adict['Ts'] = Ts
        filename, file_extension = os.path.splitext(file)
        sio.savemat(filename + '_python_ecg.mat', adict)


