import numpy as np
import io
import epics
import photodiag
import time
from collections import deque

# PALM setup pvs 
streaked = 'SAROP11-PALMK118:CH1_BUFFER'
reference = 'SAROP11-PALMK118:CH2_BUFFER'

palm = photodiag.PalmSetup(
    channels={'0': reference, '1': streaked},
    noise_range=[0, 250], energy_range=np.linspace(0, 100, 100),
)

calib_file = '/sf/photo/src/PALM/calib/Alvra/2020-02-01_20:28:09.palm_etof'

palm.load_etof_calib(calib_file)

# Define channels and output PVs
all_dataChan = 'SAROP11-PALMK118:ALL_DATA'
all_dataOut = 'SAROP11-PALMK118:PY_ANALYSIS'

calibPALM = -11.76
E_From = 0
E_To = 0
steps = 0

calibPALM_PV_name = 'SLAAR11-GEN:PALM_CALIB'
E_From_PV_name = 'SLAAR11-GEN:PALM-E-FROM'
E_To_PV_name = 'SLAAR11-GEN:PALM-E-TO'
E_steps_PV_name = 'SLAAR11-GEN:PALM-E-STEPS'
calib_file_PV_name = 'SLAAR11-GEN:PALM-F-NAME'

def update_palm(pvname=None, value=None, char_value=None, **kw):
    global E_From, E_To, steps, calib_PALM
    if pvname == E_From_PV_name:
        E_From = value
        palm.energy_range = np.linspace(E_From, E_To, steps)

    elif pvname == E_To_PV_name:
        E_To = value
        palm.energy_range = np.linspace(E_From, E_To, steps)

    elif pvname == E_steps_PV_name:
        steps = value
        palm.energy_range = np.linspace(E_From, E_To, steps)

    elif pvname == calibPALM_PV_name:
        calibPALM = value
#    elif pvname == calib_file_PV_name:
#        calib_file_PV_name = value
#        print(value)
calibPALM_PV = epics.PV(calibPALM_PV_name, callback=update_palm)
E_From_PV = epics.PV(E_From_PV_name, callback=update_palm)
E_To_PV = epics.PV(E_To_PV_name, callback=update_palm)
E_steps_PV = epics.PV(E_steps_PV_name, callback=update_palm)
calib_file_PV = epics.PV(calib_file_PV_name, callback=update_palm)

#calib_file =calib_file_PV.get()
#calib_file_str = calib_file.tostring().decode('ascii')
#calib_file_str.join(calib_file)
#print(calib_file_str)
#print(type(calib_file_str))
#print(steps)

data = deque()

def process_data(pvname=None, value=None, char_value=None, **kw):
    str_vals = value[:2000]
    ref_vals = value[2000:4000]

    delay, pulse_length = palm.process(
        {'0': ref_vals[np.newaxis, :], '1': str_vals[np.newaxis, :]}, noise_thr=0, jacobian=False, peak='max',
    )
    data.append(np.concatenate((value[-4:-1], delay*calibPALM, pulse_length*calibPALM)))
#    print(delay)
all_dataPV = epics.PV(all_dataChan, callback=process_data)
all_dataOutPV = epics.PV(all_dataOut)

while True:
    while data:
#        print('in loop')
        all_dataOutPV.put(data.pop(), wait=True)
    time.sleep(0.01)

