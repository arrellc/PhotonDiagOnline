import numpy as np
import io
import epics
import photodiag
import time
from collections import deque

NUM_DARK_SHOTS_FOR_BACKGROUND = 100
MIN_NUM_DARK_SHOTS_TO_START_PROC = 10
CALIB_COEFF_SPATIAL_TT = 1

def ds_filter(pulse_id):
    # return True for dark shots
    idOut = np.logical_and(pulse_id%2 == 0, pulse_id%4 != 0)
    return idOut

se = photodiag.SpatialEncoder('')

# Define channels and output PVs
all_dataChan = 'SARES21-GES1:BS_CORR.VALO'
all_dataOut = 'SARES21-GES1:PY_ANALYSIS'

background_data = deque(maxlen=NUM_DARK_SHOTS_FOR_BACKGROUND)
data = deque()

def process_data(pvname=None, value=None, char_value=None, **kw):
    pulse_id = value[0]
    signal = value[4:]
    
    if ds_filter(pulse_id):
        #dark shot
        background_data.append(signal)
        #maybe calibration needs to be done less frequently for better performance
        se.calibrate_background(np.array(background_data))
        edge_pos = np.nan
    else:
        #process
        if len(background_data) > MIN_NUM_DARK_SHOTS_TO_START_PROC:
            # backgound data has already been accumulated
            output = se.process(signal)
            edge_pos = output['edge_pos']
        else:
            edge_pos = np.nan
    
    data.append(np.concatenate(value[:4], edge_pos*CALIB_COEFF_SPATIAL_TT))

all_dataPV = epics.PV(all_dataChan, callback=process_data)
all_dataOutPV = epics.PV(all_dataOut)

while True:
    while data:
        all_dataOutPV.put(data.pop(), wait=True)
    time.sleep(0.01)

