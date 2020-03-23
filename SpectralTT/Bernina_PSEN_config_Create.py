import json

Paras = {
    "Camera_image": 'SARES20-CAMS142-M5:FPICTURE',
    "ROI_background": 'SARES20-CAMS142-M5.roi_background_x_profile',
    "ROI_signal": 'SARES20-CAMS142-M5.roi_signal_x_profile',
    "Proc_para": 'SARES20-CAMS142-M5.processing_parameters',
    "events": 'SAR-CVME-TIFALL5:EvtSet',
    "I0": 'SLAAR21-LTIM01-EVR0:CALCI',
    "laser": 20,
    "delayed":25
}

with open('Bernina_PSEN.json', 'w') as json_file:
    json.dump(Paras, json_file)
