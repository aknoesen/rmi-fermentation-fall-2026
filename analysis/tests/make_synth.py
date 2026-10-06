"""
Synthetic ENLIGHTEN files for testing m1_dark.py and m2_ramp.py against known values
(offset 800 counts, dark rate 2.0 counts/s, read noise 8 counts, gain 1 count/e-,
DSNU 3 counts, linear N2 and background response with power).
Needs one real ENLIGHTEN file as a wavenumber template at t4/.
"""
import json, numpy as np, os
from pathlib import Path
rng=np.random.default_rng(1)
tpl=open('t4/Batch_40scans_System_Test_10_4_2026_N2_30psi.csv').read().splitlines()
hdr_end=[i for i,l in enumerate(tpl) if l.startswith('Wavenumber,Processed')][0]
wn=[float(l.split(',')[0]) for l in tpl[hdr_end+1:] if l.strip()]
wn=np.array(wn); n=len(wn); valid=np.r_[np.zeros(20,bool),np.ones(727,bool),np.zeros(n-747,bool)]
dsnu=rng.normal(0,3,n)
def write(path,y,t,temp,ts):
    meta={'ENLIGHTEN Version':'4.0.14','Model':'WPX-532-C2-EXR-IC','Scan Averaging':'1','Boxcar':'1','Baseline Correction Algo':'None',
     'Raman Intensity Corrected':'False','Deconvolved':'False','Integration Time':str(int(t*1000)),'Timestamp':ts,'Temperature':str(temp)}
    with open(path,'w') as f:
        for k,v in meta.items(): f.write(f'{k},{v}\n')
        f.write('\nWavenumber,Processed,Dark\n')
        for w,v,ok in zip(wn,y,valid): f.write(f'{w:.2f},{v:.2f if False else 0},\n' if False else f'{w:.2f},{(f"{v:.2f}" if ok else "NA")},\n')
def dark(t): 
    mean=800+dsnu+ 2.0*t
    return mean + rng.normal(0,np.sqrt(8**2+2.0*t),n)
os.makedirs('sM1',exist_ok=True); os.makedirs('logx/frames',exist_ok=True); os.makedirs('logx/events',exist_ok=True)
k=0
for t,c in [(0.01,2),(10,2),(30,2),(100,2),(300,2),(1000,2),(3000,1)]:
    for i in range(c):
        k+=1; write(f'sM1/M1_d{t}_{i}.csv',dark(t),t,-13+rng.normal(0,0.1),f'2026-10-06 22:{k:02d}:00.000000')
        json.dump({'id':f'f{k}','data':{'mid':'M1','plan':'d','file':f'M1_d{t}_{i}.csv','ts':'2026-10-07T05:00:00Z'}},open(f'logx/frames/f{k}.json','w'))
# M2
os.makedirs('sM2',exist_ok=True)
def air(P,t,drift=1.0):
    g=lambda c,a: a*np.exp(-0.5*((wn-c)/7.1)**2)
    sig=(g(2331,1.0)+g(1556,0.27)+0.15)*P*t*0.6*drift
    bg=0.05*P*t
    mean=800+dsnu+2.0*t+sig+bg
    return rng.poisson(np.clip(mean-800,0,None))+800+dsnu+rng.normal(0,8,n)
steps=[(70,0),(105,10),(160,20),(240,30)]
m=0
for P,hwp in steps:
    t=30000/(P*0.6)/1.0
    for i in range(3):
        m+=1; fn=f'M2_step{hwp}_{i}.csv'; write(f'sM2/{fn}',air(P,t),t,-13,f'2026-10-07 09:{m:02d}:00.000000')
        json.dump({'id':f'g{m}','data':{'mid':'M2','plan':'step','file':fn,'waveplate_angle_deg':str(hwp),'ophir_start_mW':str(P),'ophir_end_mW':str(P*1.003),'ts':'x'}},open(f'logx/frames/g{m}.json','w'))
for i in range(12):
    P=240; t=30000/(P*0.6); fn=f'M2_hold_{i}.csv'; write(f'sM2/{fn}',air(P,t,1-0.001*i),t,-13,f'2026-10-07 10:{i*5:02d}:00.000000')
    json.dump({'id':f'h{i}','data':{'mid':'M2','plan':'hold','file':fn,'waveplate_angle_deg':'30','ophir_start_mW':str(P),'ophir_end_mW':str(P),'ts':'x'}},open(f'logx/frames/h{i}.json','w'))
for i,v in enumerate([70.0,69.8]):
    json.dump({'id':f'e{i}','data':{'type':'ophir','value':str(v),'ts':f'2026-10-07T1{6+i}:00:00Z'}},open(f'logx/events/e{i}.json','w'))
