from bsread import source
import numpy as np
import epics
import photodiag
from collections import deque
from simple_pid import PID
import time

class Adeque(deque):
    def _init_(self, *args, **kwargs):
        super()._init_(*args, **kwargs)

    @property
    def mean(self):
        if len(self) == 0:
            return 0
        else:
            return sum(self)/len(self)

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
I0 = 'SARES11-LSCP10-FNS:CH0:VAL_GET'
event_codes = 'SAR-CVME-TIFALL5:EvtSet'
drift_corr = 'SAROP11-PALMK118:DRIFT_CORR_ON'
PALM_DELAY = 'SAROP11-PALMK118:ANALYSIS_PALM_DEL'


calib_file = '/sf/photo/src/PALM/calib/2019-05-24_13:40:42.palm_etof'

# ---- PALM range setup
palm = photodiag.PalmSetup(
    channels={'0': reference, '1': streaked},
    noise_range=[0, 250], energy_range=np.linspace(2000, 2400, 1000),
)
palm.load_etof_calib(calib_file)


calibBAM = 1000
mm2fs = 6666.6
calibYAG = 187/0.08

# ---- Setup queues
# running average window size
Window = 300
WindowStage = 50*30

# running Avg of single shot
PALM_queue = Adeque(maxlen=Window)
BAM_queue = Adeque(maxlen=Window)
PALM_Stage_queue = Adeque(maxlen=WindowStage)
PALM_LASER_OFF_queue = Adeque(maxlen=Window) 

PALMpv = epics.PV('SAROP11-PALMK118:RAVE')
PALMStagepv = epics.PV('SAROP11-PALMK118:LIVE')

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


# TODO: put the following params into the panel
PALM_ZERO = 0 
PALM_DBand = 10 #was 17... 

StageMovLimits = 200


channels = [streaked, reference, YAGDiode, event_codes, BAM1, I0, PALM_DELAY]

# ---- Start processing
with source(channels=channels) as stream:
    diode_pumped = 1
    diode_unpumped = 1
    I0Val = 1
                   
    while True:
        message = stream.receive()
        #events = message.data.data[event_codes].value
        PulseID = message.data.pulse_id

        storage = dict()

        for channel in channels:
            try:
                storage[channel] = message.data.data[channel].value
            except Exception as err:
                print("Error retrieving %s, error was '%s'"%(channel,err))

        print(storage)
        input("ok to continue")

        PALM_LASER_OFF_AV = PALM_LASER_OFF_queue.mean
        
        # Diagnostics 1
        # fel_on = events[13]
        fel_on = PulseID % 2 == 0

        # FEL on shots
        if fel_on:

            #if events[21]:  # Darkshot
            if PulseID % 24 == 0:
                PALM_LASER_OFF_queue.append(storage[PALM_DELAY])

            else:
                storage[PALM_DELAY] -= PALM_LASER_OFF_AV

                # If shot is good (within a specific energy range)
                if abs(EnergyRBpv.get()-E_centre) < E_range and storage[reference].sum()>4.5:

                    # bam
                    BAM_queue.append(storage[BAM1Val])

                    # palm
                    PALM_queue.append(storage[PALM_DELAY])

                    # for stage feedback
                    PALM_Stage_queue.append(storage[PALM_DELAY])

                # write PVs output
                try:
                    PALMpv.put(PALM_queue.mean)
                    PALMStagepv.put(PALM_Stage_queue.mean )
                    BAMpv.put( BAM_queue.mean )
                except TypeError:
                    print('Can not write PV')

        # Update plots on DJ Alvra
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
        if abs(PALM_ZERO-PALM_Stage_queue.mean ):
             Movefs = PALM_ZERO - PALM_Stage_queue.mean
             print(Movefs)
             if abs(Movefs)< StageMovLimits:
                 MoveTo = STAGEpv.get()*mm2fs + Movefs
                 if Drift_Corr_Master and Drift_Corr:
                     STAGEpv.put(MoveTo/mm2fs)

