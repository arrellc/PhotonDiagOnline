from bsread import source
import numpy as np
import epics
import photodiag
from collections import deque

# Define channels
stt_image = 'SARES20-CAMS142-M4:FPICTURE'
event_codes = 'SAR-CVME-TIFALL5:EvtSet'

se = photodiag.SpatialEncoder(
    stt_image,
)

calibConstSpatTT = 1

# ---- Setup queues
# running average window size
runAvgWindow = 300
backgroundAvgWindow = 100

# running Avg of single shot
runAvg_queue = deque(maxlen=runAvgWindow)
background_queue = deque(maxlen=backgroundAvgWindow) 

edge_pv = epics.PV('SLAAR11-PPROBE:RAVE')
waveform_x_pv = epics.PV('SLAAR11-GEN:PALM-PROC-X')
waveform_y_pv = epics.PV('SLAAR11-GEN:PALM-PROC1-Y')
corr_x_pv = epics.PV('SLAAR11-GEN:PALM-XCORR-X')
corr_y_pv = epics.PV('SLAAR11-GEN:PALM-XCORR-Y')

# ---- Start processing
with source(channels=[stt_image, event_codes]) as stream:
    while True:
        message = stream.receive()
        
        try:
            events = message.data.data[event_codes].value
        except TypeError:
            print('Type Error event_codes')
            continue

        fel_on = events[13]
	dark = events[25]
        
        try:
            image = message.data.data[stt_image].value
        except TypeError:
            print('Type Error stt_image')
            continue
        if image is None:
            continue
        image_proj = image.mean(axis=0)
        if fel_on:
            # process signal
            if len(background_queue) == backgroundAvgWindow:
                output = se.process(image_proj, debug=True)
                edge_pos = output['edge_pos'][0]
                runAvg_queue.append(edge_pos*calibConstSpatTT)

                waveform_x_pv.put(np.arange(output['raw_input'].size))
                waveform_y_pv.put(output['raw_input'][0])
                corr_x_pv.put(np.arange(output['xcorr'].size))
                corr_y_pv.put(output['xcorr'][0])
        if dark:
            # accumulate background
            background_queue.append(image_proj)
            se.calibrate_background(np.array(background_queue))

        if len(runAvg_queue) == runAvgWindow:
            edge_pv.put(sum(runAvg_queue)/len(runAvg_queue))


