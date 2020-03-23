from bsread import Source
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.animation as animation
from collections import deque
from datetime import datetime
import json
import numpy as np
from epics import caget
from scipy import signal as Signal
# For PSEN Bernina
########
# Channel names
########

fn = 'Bernina_PSEN.json'
with open(fn) as json_file:
    p= json.load(json_file)

#Camera_image = 'SARES20-CAMS142-M5:FPICTURE'
#ROI_background ='SARES20-CAMS142-M5.roi_background_x_profile'
#ROI_signal = 'SARES20-CAMS142-M5.roi_signal_x_profile'
#Proc_para = 'SARES20-CAMS142-M5.processing_parameters'
#events= 'SAR-CVME-TIFALL5:EvtSet'
#I0 = 'SLAAR21-LTIM01-EVR0:CALCI'

########
# setup
i_frames = 0
using_dark = True
using_ref = False
bkg_deque = deque(maxlen=5)
bkg_deque_raw = deque(maxlen=5)
ref_deque = deque(maxlen=5)
ref_deque_raw = deque(maxlen=5)
ref_correction_deque = deque(maxlen=5)
ref_correction_deque_raw = deque(maxlen=5)
I0_deque = deque(maxlen=500)
Xcor_deque = deque(maxlen=500)
Xcor_deque_ref = deque(maxlen=500)
#laser = 20
#delayed = 25
signal_bkg = np.nan
step_length = 100
savgol_period =71
########
# explict spectral encoding functions
########

def find_edge(data, step_length=50, edge_type='falling', step_type='heaviside', refinement=1, scale=10):
    # refine datacurrent_ref_correction 
    if data.ndim == 1:
        data = data[np.newaxis, :]
    def _interp(fp, xp, x):  # utility function to be used with apply_along_axis
        return np.interp(x, xp, fp)
    data_length = data.shape[1]
    refined_data = np.apply_along_axis(_interp, axis=1, arr=data, x=np.arange(0, data_length - 1, refinement),xp=np.arange(data_length),)
                                                
    # prepare a step function and refine it
    if step_type == 'heaviside':
        step_waveform = np.ones(shape=(step_length,))
        if edge_type == 'rising':
            step_waveform[: int(step_length / 2)] = -1
        elif edge_type == 'falling':
            step_waveform[int(step_length / 2) :] = -1
    elif step_type == 'erf':
        step_waveform = scipy.special.erf(np.arange(-step_length/2, step_length/2)/scale)
        if edge_type == 'falling':
            step_waveform *= -1
    
    step_waveform = np.interp(x=np.arange(0, step_length - 1, refinement),xp=np.arange(step_length),fp=step_waveform,)
    # find edges
    xcorr = np.apply_along_axis(np.correlate, 1, refined_data, v=step_waveform, mode='valid')
    edge_position = np.argmax(xcorr, axis=1).astype(float) * refinement
    xcorr_amplitude = np.amax(xcorr, axis=1)

    # correct edge_position for step_length
    edge_position += np.floor(step_length / 2)
    return {'edge_pos': edge_position, 'xcorr': xcorr, 'xcorr_ampl': xcorr_amplitude}
def interpolate_row(data, energy, interp_energy):
    return np.interp(interp_energy, energy, data)
def savgol_interpolate(data):
    lambda_nm = np.linspace(368.45, 660.70, 2038)
    c = 3
    freq = c / lambda_nm
    interp_freq = np.linspace(c/660.7, c/368.45,  2038)

    tmp = np.apply_along_axis(interpolate_row, 0, data[::-1], freq[::-1], interp_freq)[::-1]
    tmp2 = Signal.savgol_filter(tmp, savgol_period, 1)
    data_out = np.apply_along_axis(interpolate_row, 0, tmp2[::-1], interp_freq, freq[::-1])[::-1]
    return data_out

def animate(i):

    global stream, i_frames 

    message = stream.receive()
    Events = message.data.data[p['events']].value
    Current_pulseID = caget('SLAAR21-LTIM01-EVR0:RX-PULSEID')
    PulseID_offset = Current_pulseID - message.data.pulse_id
    if Events[p['laser']:
        try:
            ROIs=json.loads(message.data.data[p['Proc_para']].value)
        except:
            print('Error: PSEN processing running at lower rate than laser')
            return
        i_frames += 1
        index_probed = np.logical_and(Events[p['laser']].astype(bool), ~Events[p['delayed']].astype(bool))
        index_unpumped = np.logical_and(Events[p['laser']].astype(bool), Events[p['delayed']].astype(bool)) 

        # get waveforms
        signal = message.data.data[p['ROI_signal']].value
        ref = message.data.data[p['ROI_background']].value
        I0_val = message.data.data[p['I0']].value
        signal_raw = signal
        ref_raw = ref

        signal = savgol_interpolate(signal)
        ref = savgol_interpolate(ref)
        
        ref_deque.append(ref)
        ref_deque_raw.append(ref_raw)

        if bkg_deque:
            current_bkg = sum(bkg_deque)/len(bkg_deque)
            current_bkg_raw = sum(bkg_deque_raw)/len(bkg_deque_raw)
            signal_bkg = signal/current_bkg
            plt.grid()
            signal_bkg_raw = signal_raw/current_bkg_raw
        if ref_deque:
            current_ref = sum(ref_deque)/len(ref_deque)
            current_ref_raw = sum(ref_deque_raw)/len(ref_deque_raw)
            if ref_correction_deque and index_probed:
                print('In ref_correction loop')
                current_ref_correction = sum(ref_correction_deque)/len(ref_correction_deque)
                current_ref_correction_raw = sum(ref_correction_deque_raw)/len(ref_correction_deque_raw)
                current_ref /= current_ref_correction
                current_ref_raw /= current_ref_correction_raw
                signal_ref = signal/current_ref
                signal_ref_raw = signal_raw/current_ref_raw
            else:
                current_ref = sum(ref_deque)/len(ref_deque)
                current_ref_raw = sum(ref_deque_raw)/len(ref_deque_raw)
                signal_ref_raw = signal_raw/current_ref_raw
                signal_ref = signal_raw/current_ref

        if index_probed:
            try:
                res = find_edge(signal_bkg, step_length=step_length, edge_type='rising')
                res_raw = find_edge(signal_bkg_raw, step_length=step_length, edge_type='rising')
                res_ref = find_edge(signal_ref, step_length=step_length, edge_type='rising')
                res_ref_raw = find_edge(signal_ref_raw, step_length= step_length, edge_type='rising')
                I0_deque.append(I0_val)
                Xcor_deque.append(np.max(res['xcorr'][0]))
                Xcor_deque_ref.append(np.max(res_ref['xcorr'][0]))
                print(index_probed, index_unpumped)
            except:
                print('Failed in edge finding')
                
        if index_unpumped:
            bkg_deque.append(signal)
            bkg_deque_raw.append(signal_raw)
            try:
                ref_correction_deque.append(signal_ref)
                ref_correction_deque_raw.append(signal_ref_raw)
            except:
                print(len(ref_correction_deque), len(ref_deque))
                print('No signal_ref or signal_ref_raw yet')
        x_axis = np.arange(0, len(signal))

        # update plot
        if i_frames%3 == 1:
            plt.clf()
            plt.subplot(421)
            plt.title('Siganl '+str(datetime.fromtimestamp(message.data.global_timestamp)))
            plt.plot(x_axis,signal_raw, label='Unfiltered')
            plt.plot(x_axis,signal, label='PulseID '+str(message.data.pulse_id))
            plt.grid()
            plt.legend(loc =1)
            
            plt.subplot(423)
            plt.title('Signal/runAvg(unpumped)')
            try:
                plt.plot(x_axis, signal_bkg_raw, label='Signal/unpumped_runAvg(deque lenght %.0f, stream offset[s] %.0f)'%(len(bkg_deque_raw),PulseID_offset/100))
                plt.plot(x_axis, signal_bkg, label='Signal/unpumped_runAvg(deque lenght %.0f, stream offset[s] %.0f)'%(len(bkg_deque),PulseID_offset/100))
                plt.legend(loc =1)
                plt.grid()
            except:
                print('Error ploting signal_bkg')
                print(index_unpumped, index_probed)
                return
            
            plt.subplot(425)
            try:
                #plt.title(index_probed, index_unpumped)
                plt.plot(res_raw['xcorr'][0])
                plt.plot(res['xcorr'][0])
            except:
                print('Error plotting xcorr')
                print(index_unpumped, index_probed)
            plt.grid()
            
            plt.subplot(427)
            try:
                plt.plot(I0_deque, Xcor_deque,'.') 
                plt.plot(I0_deque[-1], Xcor_deque[-1],'.r')
                plt.grid()
                plt.xlabel('I0')
                plt.ylabel('XCor max')
            except: 
                print('Error plotting I0 correlation') 
                            
            plt.subplot(422)
            plt.title('Reference'+str(datetime.fromtimestamp(message.data.global_timestamp)))
            plt.plot(x_axis,ref_raw, label='Unfiltered')
            plt.plot(x_axis,ref, label='PulseID '+str(message.data.pulse_id))
            plt.grid()
            plt.legend(loc =1)
            
            plt.subplot(424)
            plt.title('Signal/runAvg(reference)')
            try:
                plt.plot(x_axis, signal_ref_raw, label='Signal/ref_runAvg(deque lenght %.0f, stream offset[s] %.0f)'%(len(ref_deque_raw),PulseID_offset/100))
                plt.plot(x_axis, signal_ref, label='Signal/ref_runAvg(deque lenght %.0f, stream offset[s] %.0f)'%(len(ref_deque),PulseID_offset/100))
                if index_probed:
                    plt.plot(x_axis,current_ref_correction, label='Signal/ref unpumped correction wf')
                plt.legend(loc =1)
                plt.grid()
            except:
                print('Error ploting signal_bkg')
            
            plt.subplot(426)
            try:
                plt.plot(res_ref_raw['xcorr'][0])
                plt.plot(res_ref['xcorr'][0])
            except:
                print('Error plotting xcorr')
            plt.grid()

            plt.subplot(428)
            plt.title(index_probed)
            try:
                plt.plot(I0_deque, Xcor_deque_ref,'.')
                plt.plot(I0_deque[-1], Xcor_deque_ref[-1], '.r')
                plt.xlabel('I0')
                plt.ylabel('Xcor max')
                plt.grid()
            except:
                print('Error plotting I0 correlation')
            plt.tight_layout()
            
#Channels = [p['Camera_image'], p['ROI_background'], p['ROI_signal'], p['Proc_para'], p['events'], p['I0']]
Channels = [p['ROI_background'], p['ROI_signal'], p['Proc_para, events'], p['I0']]

stream = Source(channels=Channels, queue_size=1)
stream.connect()

fig = plt.figure("PSEN monitor", figsize=[10,10])
ani = animation.FuncAnimation(fig, animate, interval=10)
plt.show()


