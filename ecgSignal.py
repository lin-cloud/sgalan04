import numpy as np
from matplotlib import pyplot as plt
import glob
import scipy.io as sio
import wfdb
import subprocess
import scipy.signal as signal
import statistics as st
from os import remove

# plt.switch_backend('MacOSX')

# ---------------------------------------------------------------------------------------
# Funciones Auxiliares
# ---------------------------------------------------------------------------------------
def plotEstimation(ecg, tm, Q, T, R):
    plt.figure()
    plt.plot(tm, ecg, zorder=1)
    plt.scatter([tm[i] for i in R[0:-1]], [ecg[i] for i in R[0:-1]], c='r', marker='*', zorder=2)
    plt.scatter([tm[i] for i in Q[0:-1]], [ecg[i] for i in Q[0:-1]], c='m', marker='x', zorder=2)
    plt.scatter([tm[i] for i in T[0:-1]], [ecg[i] for i in T[0:-1]], c='m', marker='o', zorder=2)

    plt.xlabel('time (s)')
    plt.ylabel('amplitude ($\propto$mV)')
    plt.grid(True)

    plt.show()
    plt.savefig('example.pdf')

# ---------------------------------------------------------------------------------------
# Funciones Principales
# ---------------------------------------------------------------------------------------
def filterSignal(ecg):
    # FILTRO PRECARGADO
    b = np.array([0.0317173907324606, 0.00778412499587876, 0.00843295634586329, 0.00824238758939527, 0.00667284349229215, 0.00372047382341096, 0.000144532623390324, -0.00280380336179409, -0.00395604125287823, -0.00288335171394141, -0.000165403953551767, 0.00281789867838032, 0.00458006275858754, 0.00425524660446466, 0.00206796446508836, -0.000819375389721535, -0.00288920510049196, -0.00309722109025866, -0.00137816161668399, 0.00130466534326549, 0.00351932128126493, 0.00408991911269642, 0.00274944583918501, 0.000211696520468528, -0.00217384455101105, -0.00320055345830695, -0.00235873575094937, -0.000159365278303689, 0.00224731852111043, 0.00351994623534206, 0.00306516504076490, 0.00117860143341462, -0.00126689493603176, -0.00295268591142211, -0.00312390327803527, -0.00172428127486515, 0.000452167626705610, 0.00229104324409447, 0.00284546297125508, 0.00186752509191573, -0.000154656182557632, -0.00221542261818967, -0.00334883160084180, -0.00305598382994970, -0.00156214985850975, 0.000357595687118241, 0.00173617104726884, 0.00191474563124414, 0.000804399388600301, -0.00106216726664653, -0.00283296672752701, -0.00371283270201726, -0.00335394810231033, -0.00197070527033613, -0.000256629388718182, 0.000971241012844674, 0.00110721048839661, 6.15887575700201e-05, -0.00173049354067509, -0.00346036396961798, -0.00441222359281438, -0.00415178649986581, -0.00282736948350151, -0.00107498291944714, 0.000268049502319899, 0.000519816671771312, -0.000507844509142148, -0.00241789024514611, -0.00438378873451874, -0.00552340945195366, -0.00530836898149706, -0.00383026591758699, -0.00178620922420318, -0.000172552716013647, 0.000170615577020106, -0.00102201454757676, -0.00329327373530721, -0.00564013042189117, -0.00697699408833755, -0.00665628788267599, -0.00480796802417892, -0.00231010033593166, -0.000402832739109531, -9.21491823200220e-05, -0.00165196040145124, -0.00444772914654860, -0.00720987223901418, -0.00862567345762517, -0.00799919655300604, -0.00560069260382205, -0.00257516111240254, -0.000447722129571370, -0.000339970180474069, -0.00244244899007019, -0.00585697065230145, -0.00900543050709803, -0.0103773229877295, -0.00927436476670391, -0.00618862735650783, -0.00260416252239394, -0.000310815405781970, -0.000532042743030665, -0.00330874141226949, -0.00742637057445362, -0.0109653034386287, -0.0122116014670627, -0.0105024226263916, -0.00659804346742676, -0.00236351134970138, 9.66353818481086e-05, -0.000545236824984457, -0.00415541162594434, -0.00914137892222503, -0.0131653540054208, -0.0142505214883131, -0.0117645978280066, -0.00679188528283574, -0.00168407298653701, 0.00102852135005057, -0.000154903984299167, -0.00490168827163386, -0.0111166090480071, -0.0158754930354999, -0.0167837253227808, -0.0131971714482524, -0.00662287223470848, -0.000133752716298382, 0.00304076145009377, 0.00107023452069803, -0.00547799002239339, -0.0137503344516099, -0.0198233971658459, -0.0205393920817901, -0.0151110058051615, -0.00570335621839965, 0.00336017075167198, 0.00751161158403174, 0.00415355730112451, -0.00588456189026106, -0.0183735067715737, -0.0273757021655871, -0.0279317286154504, -0.0186030661395856, -0.00263328192045663, 0.0129479697474979, 0.0201462832841410, 0.0136633372972384, -0.00611401571750549, -0.0322190154033013, -0.0529218660746926, -0.0558509440431226, -0.0328778733177159, 0.0160489750785155, 0.0818181868755556, 0.148400920774996, 0.197810146421614, 0.216037413790102, 0.197810146421614, 0.148400920774996, 0.0818181868755556, 0.0160489750785155, -0.0328778733177159, -0.0558509440431226, -0.0529218660746926, -0.0322190154033013, -0.00611401571750549, 0.0136633372972384, 0.0201462832841410, 0.0129479697474979, -0.00263328192045663, -0.0186030661395856, -0.0279317286154504, -0.0273757021655871, -0.0183735067715737, -0.00588456189026106, 0.00415355730112451, 0.00751161158403174, 0.00336017075167198, -0.00570335621839965, -0.0151110058051615, -0.0205393920817901, -0.0198233971658459, -0.0137503344516099, -0.00547799002239339, 0.00107023452069803, 0.00304076145009377, -0.000133752716298382, -0.00662287223470848, -0.0131971714482524, -0.0167837253227808, -0.0158754930354999, -0.0111166090480071, -0.00490168827163386, -0.000154903984299167, 0.00102852135005057, -0.00168407298653701, -0.00679188528283574, -0.0117645978280066, -0.0142505214883131, -0.0131653540054208, -0.00914137892222503, -0.00415541162594434, -0.000545236824984457, 9.66353818481086e-05, -0.00236351134970138, -0.00659804346742676, -0.0105024226263916, -0.0122116014670627, -0.0109653034386287, -0.00742637057445362, -0.00330874141226949, -0.000532042743030665, -0.000310815405781970, -0.00260416252239394, -0.00618862735650783, -0.00927436476670391, -0.0103773229877295, -0.00900543050709803, -0.00585697065230145, -0.00244244899007019, -0.000339970180474069, -0.000447722129571370, -0.00257516111240254, -0.00560069260382205, -0.00799919655300604, -0.00862567345762517, -0.00720987223901418, -0.00444772914654860, -0.00165196040145124, -9.21491823200220e-05, -0.000402832739109531, -0.00231010033593166, -0.00480796802417892, -0.00665628788267599, -0.00697699408833755, -0.00564013042189117, -0.00329327373530721, -0.00102201454757676, 0.000170615577020106, -0.000172552716013647, -0.00178620922420318, -0.00383026591758699, -0.00530836898149706, -0.00552340945195366, -0.00438378873451874, -0.00241789024514611, -0.000507844509142148, 0.000519816671771312, 0.000268049502319899, -0.00107498291944714, -0.00282736948350151, -0.00415178649986581, -0.00441222359281438, -0.00346036396961798, -0.00173049354067509, 6.15887575700201e-05, 0.00110721048839661, 0.000971241012844674, -0.000256629388718182, -0.00197070527033613, -0.00335394810231033, -0.00371283270201726, -0.00283296672752701, -0.00106216726664653, 0.000804399388600301, 0.00191474563124414, 0.00173617104726884, 0.000357595687118241, -0.00156214985850975, -0.00305598382994970, -0.00334883160084180, -0.00221542261818967, -0.000154656182557632, 0.00186752509191573, 0.00284546297125508, 0.00229104324409447, 0.000452167626705610, -0.00172428127486515, -0.00312390327803527, -0.00295268591142211, -0.00126689493603176, 0.00117860143341462, 0.00306516504076490, 0.00351994623534206, 0.00224731852111043, -0.000159365278303689, -0.00235873575094937, -0.00320055345830695, -0.00217384455101105, 0.000211696520468528, 0.00274944583918501, 0.00408991911269642, 0.00351932128126493, 0.00130466534326549, -0.00137816161668399, -0.00309722109025866, -0.00288920510049196, -0.000819375389721535, 0.00206796446508836, 0.00425524660446466, 0.00458006275858754, 0.00281789867838032, -0.000165403953551767, -0.00288335171394141, -0.00395604125287823, -0.00280380336179409, 0.000144532623390324, 0.00372047382341096, 0.00667284349229215, 0.00824238758939527, 0.00843295634586329, 0.00778412499587876, 0.0317173907324606])

    sig = np.vstack((ecg[-1:0:-1],ecg,ecg[-2::-1]))
    sig = signal.lfilter(b,1,sig,axis=0)
    n = 312 # PARAMETRO DEL FILTRO
    sp = int((n / 2) + (len(ecg) - 1))

    ecg = sig[sp:sp+len(ecg):1]

    return ecg

def readAnnotation(name):
    # LECTURA DEL FICHERO DE ANOTACION
    annotation = wfdb.rdann(name, 'test')

    anntype = annotation.symbol
    ann = annotation.sample

    # LEYENDO R
    R_est_ann = np.char.find(anntype, 'N')
    R_est = [ann[i] for i in range(0, len(R_est_ann)) if R_est_ann[i] == 0]

    # LEYENDO Q
    Q_ini_est_ann = np.char.find(anntype, 'N')
    Q_ini_est = [ann[i - 1] for i in range(0, len(Q_ini_est_ann)) if Q_ini_est_ann[i] == 0 and anntype[i - 1] == '(']

    # LEYENDO T
    T_end_est_ann = np.char.find(anntype, 't')
    T_end_est = [ann[i + 1] for i in range(0, len(T_end_est_ann)) if T_end_est_ann[i] == 0 and anntype[i + 1] == ')']

    R_est_ann = [i for i in range(0, len(R_est_ann)) if R_est_ann[i] == 0] # SE UTILIZA EN EL CALCULO QT

    return Q_ini_est, T_end_est, R_est, anntype, ann, R_est_ann


def computeQTtimes(anntype, ann, R, tm, R_est, ecg):
    rr_qt_matrix = np.zeros([len(R),4],dtype=int)
    rr_qt_index = -1
    correct = []

    for rinx in range(len(R)):
        r1 = R[rinx]
        #VARIABLES DE CONTROL
        q_init = np.nan
        t_end = np.nan
        r2 = np.nan
        tt_detect = np.nan
        tt_detect_control = False

        if r1 > 0: # EVITAR VALORES NEGATIVOS
            if anntype[r1-1] == '(': # Q ENCONTRADO
                q_init = r1-1

        ann_add = 1
        if ~np.isnan(q_init):
            while np.isnan(r2) and ((r1+ann_add)<(len(anntype)-1)):
                if anntype[r1+ann_add] =='N': # SIGUIENTE R ENCONTRADO
                    r2 = r1+ann_add
                elif (anntype[r1+ann_add-1]+anntype[r1+ann_add]+anntype[r1+ann_add+1] == 'tt)') and np.isnan(t_end): # TT_END ENCONTRADO
                    t_end = r1+ann_add+1
                    tt_detect = [r1 + ann_add - 1,r1 + ann_add]
                    tt_detect_control = True
                elif (anntype[r1+ann_add]+anntype[r1+ann_add+1] == 't)') and np.isnan(t_end): # T_END ENCONTRADO
                    t_end = r1+ann_add+1

                ann_add = ann_add + 1

            # GUARDA PARAMETROS
            if ~np.isnan(q_init) and ~np.isnan(t_end) and ~np.isnan(r2):
                rr_qt_index = rr_qt_index+1
                rr_qt_matrix[rr_qt_index, :] = [r1,r2,q_init,t_end]
                #if (~np.isnan(tt_detect)):
                if tt_detect_control==True:
                    block = {
                        "tt": tt_detect,
                        "rr_qt_index": rr_qt_index
                    }
                    correct.append(block)

    # CALCULO DEL QTC
    if rr_qt_index > -1:
        rr_qt_matrix = rr_qt_matrix[:rr_qt_index+1,:]
        rr_qt_times = np.zeros((rr_qt_index+1,4))

        for i in range(rr_qt_index+1):
            for j in range(4):
                rr_qt_times[i, j] = tm[ann[rr_qt_matrix[i,j]]]

        for i in range(len(correct)):
            ecg_sublist = ecg[range(ann[correct[i]['tt'][0]],ann[correct[i]['tt'][1]])]
            min_indx = np.argmin(ecg_sublist)
            rr_qt_times[correct[i]['rr_qt_index'], -1] = tm[min_indx + ann[correct[i]['tt'][0]]-1]

        r_times = np.array(rr_qt_times[:,0])
        rr_qt_times[:,0] = rr_qt_times[:,1] - rr_qt_times[:,0]
        rr_qt_times[:,1] = rr_qt_times[:,3] - rr_qt_times[:,2]
        rr_qt_times = rr_qt_times[:,:2]

        qtc_times = np.divide(rr_qt_times[:,1],np.power(rr_qt_times[:,0], 1/3))
        qtc = np.mean(qtc_times)

        FC = st.median(60/np.diff(tm[R_est]))

    else:
        qtc = -3
        FC = -3
        qtc_times = -3
        r_times = -3

    return qtc, FC, qtc_times, r_times


def ECG_signal2QRS(ecg, Ts, draw=False):
    if ~np.isnan(Ts): # ES NECESARIO Ts
        # RESAMPLE DE LA SEÑAL
        ecg = signal.resample_poly(ecg,360,round(1/Ts))
        Ts = 1/360
        ecg = filterSignal(ecg)

        tm = np.arange(0, len(ecg) * Ts, Ts)[:len(ecg)]

        # GENERA FILENAME RANDOM
        filename = 'tmp' + str(int(np.mean(ecg)*10))

        # GUARDA LA SENAL ECG EN FORMATO WFDB
        wfdb.wrsamp(filename, fs=1 / Ts, units=['mV'], sig_name=['I'], p_signal=ecg, fmt=['212'])

        # ESTIMA EL COMPLEJO QRS
        try:
            out = subprocess.Popen(['ecgpuwave','-r',filename,'-a','test'],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
            stdout, stderr = out.communicate()

            # LEE LA ESTIMACION DEL COMPLEJO QRS
            Q, T, R, anntype, ann, R_ann = readAnnotation(filename)

            # DIBUJA LAS ESTIMACION REALIZADA POR ECGPUWAVE
            if draw:
                plotEstimation(ecg, tm, Q, T, R)

            # CALCULO DEL TIEMPO QT
            qtc, FC, qtc_times, r_times = computeQTtimes(anntype, ann, R_ann, tm, R, ecg)
            remove(filename+'.dat')
            remove(filename + '.hea')
            remove(filename + '.test')
        except:
            qtc = -1
            FC = -1
            qtc_times = -1
            r_times = -1
            remove(filename+'.dat')
            remove(filename + '.hea')
            remove(filename + '.test')
    else:
        qtc = -2
        FC = -2
        qtc_times = -2
        r_times = -2

    return qtc, FC, qtc_times, r_times


# MAIN FUNCTION
if __name__ == "__main__":

    print('Processing ecgtovector')

    #for file in glob.glob("../../Desktop/COVID19/data_Raul/ecgc-set1/*.mat"):
    for file in glob.glob("./NUEVO/*.mat"):
        # print('Procesing File: ' + file)

        # LECTURA FICHERO .MAT
        mat = sio.loadmat(file)
        ecg = mat['ecg']
        #ecg = np.transpose(ecg)  # FORMATO: MxN (M:LENGTH,N:CHANNELS)

        Ts = mat['Ts'][0,0]

        # FUNCION PRINCIPAL
        qtc,FC,qtc_times,r_times = ECG_signal2QRS(ecg, Ts, draw=False)

        # print('Valor estimado: ' + str(value))

        print(file + ' ' + str(qtc) + ' ' + str(FC))
        print(qtc_times)
        print(r_times)