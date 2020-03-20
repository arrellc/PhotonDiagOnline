import numpy as np
import epics
from bsread import source

# BAM Channels data taken from bs
#BAM1 = 'S10BC01-DBAM070:EOM1_T1'
BAM1 = 'SARES11-LSCP10-FNS:CH1:VAL_GET' ###############

# PACM PVs
LAS_XRAY_ERR = 'SLAAR11-GEN:LAS-XRAY-ERR'
LAS_XRAY_MSG = 'SLAAR11-GEN:LAS-XRAY-MSGD'
LAS_XRAY_REF = 'SLAAR11-GEN:LAS-XRAY-REF'
LAS_XRAY_BAD = 'SLAAR11-GEN:LAS-XRAY-BAD'
LAS_XRAY = 'SLAAR11-GEN:LAS-XRAY'

LAS_EVR_ERR = 'SLAAR11-GEN:LAS-EVR-ERR'
LAS_EVR_MSG = 'SLAAR11-GEN:LAS-EVR-MSGD'
LAS_EVR_REF = 'SLAAR11-GEN:LAS-EVR-REF'
LAS_EVR_BAD = 'SLAAR11-GEN:LAS-EVR-BAD'
LAS_EVR = 'SLAAR11-GEN:LAS-EVR'

XRAY_EVR_ERR = 'SLAAR11-GEN:XRAY-EVR-ERR'
XRAY_EVR_MSG = 'SLAAR11-GEN:XRAY-EVR-MSGD'
XRAY_EVR_REF = 'SLAAR11-GEN:XRAY-EVR-REF'
XRAY_EVR_BAD = 'SLAAR11-GEN:XRAY-EVR-BAD'
XRAY_EVR = 'SLAAR11-GEN:XRAY-EVR'

# Setup of PACM PVs
LAS_XRAY_ERR_pv = epics.PV(LAS_XRAY_ERR)
LAS_XRAY_MSG_pv = epics.PV(LAS_XRAY_MSG)
LAS_XRAY_REF_pv = epics.PV(LAS_XRAY_REF)
LAS_XRAY_BAD_pv = epics.PV(LAS_XRAY_BAD)
LAS_XRAY_pv = epics.PV(LAS_XRAY)

LAS_EVR_ERR_pv = epics.PV(LAS_EVR_ERR)
LAS_EVR_MSG_pv = epics.PV(LAS_EVR_MSG)
LAS_EVR_REF_pv = epics.PV(LAS_EVR_REF)
LAS_EVR_BAD_pv = epics.PV(LAS_EVR_BAD)
LAS_EVR_pv = epics.PV(LAS_EVR)

XRAY_EVR_ERR_pv = epics.PV(XRAY_EVR_ERR)
XRAY_EVR_MSG_pv = epics.PV(XRAY_EVR_MSG)
XRAY_EVR_REF_pv = epics.PV(XRAY_EVR_REF)
XRAY_EVR_BAD_pv = epics.PV(XRAY_EVR_BAD)
XRAY_EVR_pv = epics.PV(XRAY_EVR)

# PALM PVs
PALM_LIVE_ERR = 'SLAAR11-GEN:PALM-LIVE-ERR'
PALM_LIVE_MSG = 'SLAAR11-GEN:PALM-LIVE-MSGD'
PALM_LIVE_REF = 'SLAAR11-GEN:PALM-LIVE-REF'
PALM_LIVE_BAD = 'SLAAR11-GEN:PALM-LIVE-BAD'
PALM_LIVE = 'SAROP11-PALMK118:LIVE'

PALM_RAVE_ERR = 'SLAAR11-GEN:PALM-RAVE-ERR'
PALM_RAVE_MSG = 'SLAAR11-GEN:PALM-RAVE-MSGD'
PALM_RAVE_REF = 'SLAAR11-GEN:PALM-RAVE-REF'
PALM_RAVE_BAD = 'SLAAR11-GEN:PALM-RAVE-BAD'
PALM_RAVE = 'SAROP11-PALMK118:RAVE'

# Setup of PALM PVs
PALM_LIVE_ERR_pv = epics.PV(PALM_LIVE_ERR)
PALM_LIVE_MSG_pv = epics.PV(PALM_LIVE_MSG)
PALM_LIVE_REF_pv = epics.PV(PALM_LIVE_REF)
PALM_LIVE_BAD_pv = epics.PV(PALM_LIVE_BAD)
PALM_LIVE_pv = epics.PV(PALM_LIVE)

PALM_RAVE_ERR_pv = epics.PV(PALM_RAVE_ERR)
PALM_RAVE_MSG_pv = epics.PV(PALM_RAVE_MSG)
PALM_RAVE_REF_pv = epics.PV(PALM_RAVE_REF)
PALM_RAVE_BAD_pv = epics.PV(PALM_RAVE_BAD)
PALM_RAVE_pv = epics.PV(PALM_RAVE)

# PPROBE PVs
PPROBE_LIVE_ERR = 'SLAAR11-GEN:PPROBE-ERR'
PPROBE_LIVE_MSG = 'SLAAR11-GEN:PPROBE-MSGD'
PPROBE_LIVE_REF = 'SLAAR11-GEN:PPROBE-REF'
PPROBE_LIVE_BAD = 'SLAAR11-GEN:PPROBE-BAD'
PPROBE_LIVE = 'SLAAR11-PPROBE:LIVE'

PPROBE_RAVE_ERR = 'SLAAR11-GEN:PP-RAVE-ERR'
PPROBE_RAVE_MSG = 'SLAAR11-GEN:PP-RAVE-MSGD'
PPROBE_RAVE_REF = 'SLAAR11-GEN:PP-RAVE-REF'
PPROBE_RAVE_BAD = 'SLAAR11-GEN:PP-RAVE-BAD'
PPROBE_RAVE = 'SLAAR11-PPROBE:RAVE'

# Setup of PPROBE PVs
PPROBE_LIVE_ERR_pv = epics.PV(PPROBE_LIVE_ERR)
PPROBE_LIVE_MSG_pv = epics.PV(PPROBE_LIVE_MSG)
PPROBE_LIVE_REF_pv = epics.PV(PPROBE_LIVE_REF)
PPROBE_LIVE_BAD_pv = epics.PV(PPROBE_LIVE_BAD)
PPROBE_LIVE_pv = epics.PV(PPROBE_LIVE)

PPROBE_RAVE_ERR_pv = epics.PV(PPROBE_RAVE_ERR)
PPROBE_RAVE_MSG_pv = epics.PV(PPROBE_RAVE_MSG)
PPROBE_RAVE_REF_pv = epics.PV(PPROBE_RAVE_REF)
PPROBE_RAVE_BAD_pv = epics.PV(PPROBE_RAVE_BAD)
PPROBE_RAVE_pv = epics.PV(PPROBE_RAVE)

# BAM PVs
BAM1_ERR = 'SLAAR11-GEN:BAM070-ERR'
BAM1_MSG = 'SLAAR11-GEN:BAM070-MSGD'
BAM1_REF = 'SLAAR11-GEN:BAM070-REF'
BAM1_BAD = 'SLAAR11-GEN:BAM070-BAD'

# Setup of BAM PVs
BAM1_ERR_pv = epics.PV(BAM1_ERR)
BAM1_MSG_pv = epics.PV(BAM1_MSG)
BAM1_REF_pv = epics.PV(BAM1_REF)
BAM1_BAD_pv = epics.PV(BAM1_BAD)

# LAM PVs
LAM252_ERR = 'SLAAR11-GEN:LAM252-ERR'
LAM252_MSG = 'SLAAR11-GEN:LAM252-MSGD'
LAM252_REF = 'SLAAR11-GEN:LAM252-REF'
LAM252_BAD = 'SLAAR11-GEN:LAM252-BAD'
LAM252 = 'SLAAR01-LMOT-M252:MOT.RBV'

LAM11_ERR = 'SLAAR11-GEN:LAM11-ERR'
LAM11_MSG = 'SLAAR11-GEN:LAM11-MSGD'
LAM11_REF = 'SLAAR11-GEN:LAM11-REF'
LAM11_BAD = 'SLAAR11-GEN:LAM11-BAD'
LAM11= 'SLAAR11-GEN:LAM11'

# Setup of LAM PVs
LAM252_ERR_pv = epics.PV(LAM252_ERR)
LAM252_MSG_pv = epics.PV(LAM252_MSG)
LAM252_REF_pv = epics.PV(LAM252_REF)
LAM252_BAD_pv = epics.PV(LAM252_BAD)
LAM252_pv = epics.PV(LAM252)

LAM11_ERR_pv = epics.PV(LAM11_ERR)
LAM11_MSG_pv = epics.PV(LAM11_MSG)
LAM11_REF_pv = epics.PV(LAM11_REF)
LAM11_BAD_pv = epics.PV(LAM11_BAD)
LAM11_pv = epics.PV(LAM11)
# Limit calcs
with source(channels=[BAM1]) as stream:
    while True:
        message = stream.receive()
        PulseID = message.data.pulse_id
        
        # PACM    
        if PulseID%4 == 0:
            if np.logical_and(LAS_XRAY_pv.get() > LAS_XRAY_REF_pv.get()-LAS_XRAY_ERR_pv.get(),LAS_XRAY_pv.get() <  LAS_XRAY_REF_pv.get()+LAS_XRAY_ERR_pv.get()):
                LAS_XRAY_MSG_pv.put(PulseID)
            if np.logical_and(LAS_EVR_pv.get() > LAS_EVR_REF_pv.get()-LAS_EVR_ERR_pv.get(),LAS_EVR_pv.get() <  LAS_EVR_REF_pv.get()+LAS_EVR_ERR_pv.get()):
                LAS_EVR_MSG_pv.put(PulseID)
            if np.logical_and(XRAY_EVR_pv.get() > XRAY_EVR_REF_pv.get()-XRAY_EVR_ERR_pv.get(),XRAY_EVR_pv.get() <  XRAY_EVR_REF_pv.get()+XRAY_EVR_ERR_pv.get()):
                XRAY_EVR_MSG_pv.put(PulseID)
        # PALM    
        if PulseID%4 == 0:
            if np.logical_and(PALM_LIVE_pv.get() > PALM_LIVE_REF_pv.get()-PALM_LIVE_ERR_pv.get(),PALM_LIVE_pv.get() <  PALM_LIVE_REF_pv.get()+PALM_LIVE_ERR_pv.get()):
                PALM_LIVE_MSG_pv.put(PulseID)
            if np.logical_and(PALM_RAVE_pv.get() > PALM_RAVE_REF_pv.get()-PALM_RAVE_ERR_pv.get(),PALM_RAVE_pv.get() <  PALM_RAVE_REF_pv.get()+PALM_RAVE_ERR_pv.get()):
                PALM_RAVE_MSG_pv.put(PulseID)

        # BAM    
        if PulseID%4 == 0:
            BAM1Val = message.data.data[BAM1].value
            BAM1Val = BAM1Val*1000
            if np.logical_and(BAM1Val > BAM1_REF_pv.get()-BAM1_ERR_pv.get(),BAM1Val < BAM1_REF_pv.get()+BAM1_ERR_pv.get()):
                BAM1_MSG_pv.put(PulseID)
        # LAM
        LAMFAC = 6666.6    
        if PulseID%4 == 0:
            if np.logical_and(LAM252_pv.get()*LAMFAC > LAM252_REF_pv.get()-LAM252_ERR_pv.get(),LAM252_pv.get()*LAMFAC < LAM252_REF_pv.get()+LAM252_ERR_pv.get()):
                LAM252_MSG_pv.put(PulseID)
        if PulseID%4 == 0:
            if np.logical_and(LAM11_pv.get()*LAMFAC > LAM11_REF_pv.get()-LAM11_ERR_pv.get(),LAM11_pv.get()*LAMFAC < LAM11_REF_pv.get()+LAM11_ERR_pv.get()):
                LAM11_MSG_pv.put(PulseID)
         # PPROBE  
        if PulseID%4 == 0:
            if np.logical_and(PPROBE_LIVE_pv.get() > PPROBE_LIVE_REF_pv.get()-PPROBE_LIVE_ERR_pv.get(),PPROBE_LIVE_pv.get() <  PPROBE_LIVE_REF_pv.get()+PPROBE_LIVE_ERR_pv.get()):
                PPROBE_LIVE_MSG_pv.put(PulseID)
            if np.logical_and(PPROBE_RAVE_pv.get() > PPROBE_RAVE_REF_pv.get()-PPROBE_RAVE_ERR_pv.get(),PPROBE_RAVE_pv.get() <  PPROBE_RAVE_REF_pv.get()+PPROBE_RAVE_ERR_pv.get()):
                PPROBE_RAVE_MSG_pv.put(PulseID)

