from bsread import source
import numpy as np
import epics
import photodiag
from collections import deque
from simple_pid import PID

Drift_Corr_Master = True 
usePID = False

E_From = 0
E_To = 0
steps = 0
E_gap = 0

# Define channels
streaked = 'SAROP11-PALMK118:CH1_BUFFER'
reference = 'SAROP11-PALMK118:CH2_BUFFER'
YAGDiode = 'SLAAR11-LSCP1-FNS:CH0:VAL_GET'
BAM1 = 'S10BC01-DBAM070:EOM1_T1'
I0 = 'SLAAR11-LSCP1-FNS:CH2:VAL_GET'
drift_corr = 'SAROP11-PALMK118:DRIFT_CORR_ON'
delay = 'SAROP11-PALMK118:ANALYSIS_PALM_DEL'
event_codes = 'SAR-CVME-TIFALL4:EvtSet'

calib_file = '/sf/photo/src/PALM/calib/2019-05-24_13:40:42.palm_etof'

# ---- PALM range setup
palm = photodiag.PalmSetup(
    channels={'0': reference, '1': streaked},
    noise_range=[0, 250], energy_range=np.linspace(0, 100, 100),
)
palm.load_etof_calib(calib_file)

# ---- PALM full range setup
palm_full = photodiag.PalmSetup(
    channels={'0': reference, '1': streaked},
    noise_range=[0, 250], energy_range=np.linspace(0, 100, 100),
)
palm_full.load_etof_calib(calib_file)

calibBAM = 1000
mm2fs = 6671.2 #was 6666.6
calibYAG = 355/0.045

# ---- Setup queues
# running average window size
runAvgWindow = 300 # was 300
runAvgWindowDark = 30 # was 30
runAvgWindowStage = 450 # was at 50*90 # was 600

# running Avg of single shot
PALM_runAvg_queue = deque(maxlen=runAvgWindow)
YAG_runAvg_queue = deque(maxlen=runAvgWindow)
BAM_runAvg_queue = deque(maxlen=runAvgWindow)
PALM_runAvgStage_queue = deque(maxlen=runAvgWindowStage)
TOF_drift_queue = deque(maxlen=runAvgWindowDark) 

E_From_PV_name = 'SLAAR11-GEN:PALM-E-FROM'
E_To_PV_name = 'SLAAR11-GEN:PALM-E-TO'
E_steps_PV_name = 'SLAAR11-GEN:PALM-E-STEPS'

# ---- Setup of PVs
def update_palm(pvname=None, value=None, char_value=None, **kw):
    global E_From, E_To, steps, E_gap
    if pvname == E_From_PV_name:
        E_From = value
        E_gap = E_To - E_From
    elif pvname == E_To_PV_name:
        E_To = value
        E_gap = E_To - E_From
    elif pvname == E_steps_PV_name:
        steps = value
    palm.energy_range = np.linspace(E_From, E_To, steps)
    palm_full.energy_range = np.linspace(E_From-2*E_gap, E_To+-2*E_gap, steps)

E_From_PV = epics.PV(E_From_PV_name, callback=update_palm)
E_To_PV = epics.PV(E_To_PV_name, callback=update_palm)
E_steps_PV = epics.PV(E_steps_PV_name, callback=update_palm)

Drift_Corr = 0
def change_drift_corr(pvname=None, value=None, char_value=None, **kw):
    global Drift_Corr
    Drift_Corr = value

drift_corr_PV = epics.PV(drift_corr, callback=change_drift_corr)

PALMpv = epics.PV('SAROP11-PALMK118:RAVE')
PALMStagepv = epics.PV('SAROP11-PALMK118:LIVE')

YAGpv = epics.PV('SLAAR11-PPROBE:RAVE')
STAGEpv = epics.PV('SLAAR11-LMOT-M452:MOTOR_1.VAL')

BAMpv = epics.PV('SLAAR11-PPROBE:BAM070-RAVE')

XCORRXpv = epics.PV('SLAAR11-GEN:PALM-XCORR-X')
XCORRYpv = epics.PV('SLAAR11-GEN:PALM-XCORR-Y')

PROCXpv = epics.PV('SLAAR11-GEN:PALM-PROC-X')
PROC1Ypv = epics.PV('SLAAR11-GEN:PALM-PROC1-Y')
PROC2Ypv = epics.PV('SLAAR11-GEN:PALM-PROC2-Y')
PROC3Ypv = epics.PV('SLAAR11-GEN:PALM-PROC3-Y')

FULLXpv = epics.PV('SLAAR11-GEN:PALM-FULL-X')
FULL1Ypv = epics.PV('SLAAR11-GEN:PALM-FULL1-Y')
FULL2Ypv = epics.PV('SLAAR11-GEN:PALM-FULL2-Y')

EnergyRBpv = epics.PV('SAROP11-ARAMIS:ENERGY')

# TODO: put the following params into the panel
PALM_ZERO = 0 
PALM_DBand = 10 #was 10... 
pid = PID(1.0, 0.002, 0.0, setpoint=PALM_ZERO)
E_range = 400
E_centre = 11800
SignalLimit = 5
StageMovLimits = 1000 #was 600

# ---- Start processing
with source(channels=[streaked, reference, YAGDiode, BAM1, I0, event_codes, delay]) as stream:
    diode_pumped = 1
    diode_unpumped = 1
    I0Val = 1
                   
    while True:
        message = stream.receive()
        events = message.data.data[event_codes].value
        PulseID = message.data.pulse_id
        # Diagnostics 1
        fel_on = events[13]

        # FEL off shots
        if ~fel_on:
            diode_unpumped = message.data.data[YAGDiode].value
            
        # FEL on shots
        if fel_on:
        # Read values from received message
            try:
                BAM1Val = message.data.data[BAM1].value
            except TypeError:
                print ('Type Error BAM1Val')
                continue

            try:
                I0Val = message.data.data[I0].value
            except TypeError:
                print ('Type Error I0Val')
                continue

            try:
                wf_str = message.data.data[streaked].value[np.newaxis, :]*-1
                
            except TypeError:
                print ('Type Error wf_str')
                continue

            try:
                wf_ref = message.data.data[reference].value[np.newaxis, :]*-1
            except TypeError:
                print ('Type Error wf_ref')
                continue

            try:
                diode_pumped = message.data.data[YAGDiode].value
            except TypeError:
                print ('Type Error diode_pumped')
                continue

            try:
                YAGVal = (diode_pumped/diode_unpumped)/I0Val
                #YAGVal = -np.log10(diode_pumped/diode_unpumped)
            except TypeError:
                #print('Type Error diode_pumped/diode_unpumped')
                continue

            try:
                delays = message.data.data[delay].value
            except TypeError:
                print('Type Error delay')
                continue

            _, _, (input_data, lags, corr_res_uncut, corr_results) = palm.process(
                {'0': wf_ref, '1': wf_str}, noise_thr=0, jacobian=False, debug=True, peak='max')

            if events[21]: # dark shot
                if wf_str.sum()>5 and (len(TOF_drift_queue) < 10 or 50 >= abs(np.array(TOF_drift_queue).mean() - delays)):
                    TOF_drift_queue.append(delays)
                    PROC3Ypv.put(input_data['1'][0])

            else:
                if TOF_drift_queue:
                   delays -= sum(TOF_drift_queue)/len(TOF_drift_queue)
                # If shot is good (within a specific energy range)
                if abs(EnergyRBpv.get()-E_centre) < E_range and wf_str.sum()>SignalLimit:
                    BAM_runAvg_queue.append(BAM1Val)
                
                    # Add data to queue of single shot calculated values and calibrate into fs
                    YAG_runAvg_queue.append(YAGVal)
                    YAGrunAvgValfs = (sum(YAG_runAvg_queue)/len(YAG_runAvg_queue))*calibYAG

                    PALM_runAvg_queue.append(delays)
                    PALMrunAvgValfs = (sum(PALM_runAvg_queue)/len(PALM_runAvg_queue))

                    # for stage feedback
                    PALM_runAvgStage_queue.append(delays)
                    PALMrunAvgValStagefs = (sum(PALM_runAvgStage_queue)/len(PALM_runAvgStage_queue))                
                # write PVs output
                try:
                    PALMpv.put(PALMrunAvgValfs)
                    PALMStagepv.put(PALMrunAvgValStagefs)
                    YAGpv.put(YAGrunAvgValfs)
                    BAMpv.put(sum(BAM_runAvg_queue)/len(BAM_runAvg_queue)*calibBAM)
                except TypeError:
                    print('Can not write PV')
                except NameError:
                    PrintEnergy = EnergyRBpv.get()
                    PrintSignal = wf_str.sum()
                    print('Variable not definded - FEL energy(%.1f eV) out of feedback range(%.1f +- %.1f eV) or streak signal too low(%.1f limit %.1f)'%(PrintEnergy, E_centre, E_range, PrintSignal, SignalLimit))
                # Update plots on DJ Alvra
                #if PulseID%100 == 2:
                if PulseID%100 == 0:
                    PROCXpv.put(palm.energy_range)
                    PROC1Ypv.put(input_data['0'][0])
                    PROC2Ypv.put(input_data['1'][0])

                    XCORRXpv.put(lags)
                    XCORRYpv.put(corr_res_uncut[0])

                    _, _, (input_data_full, _, _, _) = palm_full.process(
                        {'0': wf_ref, '1': wf_str}, noise_thr=0, jacobian=False, debug=True, peak='max')
                    FULLXpv.put(palm_full.energy_range)
                    FULL1Ypv.put(input_data_full['0'][0])
                    FULL2Ypv.put(input_data_full['1'][0])
                # Feedback stage of Global time laser
                #if PulseID%1000== 2:
                if PulseID%1000== 0:
                        print('Signal strength of streaked TOF signal %.2f'%wf_str.sum())

                if abs(EnergyRBpv.get()-E_centre) < E_range and wf_str.sum()>SignalLimit:

                    if PulseID%6000== 0:
                    #if PulseID%600== 0:
                        if ~usePID: 
                            if abs(PALM_ZERO-PALMrunAvgValStagefs)>PALM_DBand:
                                Movefs = PALM_ZERO - PALMrunAvgValStagefs
                                print('Distance to move %.2f if outside deadband'%Movefs)
                                if abs(Movefs)< StageMovLimits:
                                    MoveTo = STAGEpv.get()*mm2fs + Movefs

                                    if Drift_Corr_Master and Drift_Corr:
                                        print('Stage moved %.3f fs'%Movefs)
                                        STAGEpv.put(MoveTo/mm2fs)
                if usePID:
                    control = pid(PALMrunAvgValStagefs)
                    if PulseID%500 == 0:
                        print('control '+str(control))
                        if abs(control-PALMrunAvgValStagefs)>PALM_DBand:
                            Movefs = control
                            print(Movefs)
                            if abs(Movefs)< StageMovLimits:
                                MoveTo = STAGEpv.get()*mm2fs + Movefs

                                if Drift_Corr_Master and Drift_Corr:
                                    STAGEpv.put(MoveTo/mm2fs)

