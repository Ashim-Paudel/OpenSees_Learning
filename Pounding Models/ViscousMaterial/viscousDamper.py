# A simple implementation of viscousDamper material
# https://opensees.berkeley.edu/wiki/index.php/ViscousDamper_Material


import openseespy.opensees as ops

#other packages
import numpy as np
import matplotlib.pyplot as plt

# user def modules
from modelUnits import *
mm = 1000*m

ops.wipe()
ops.model("BasicBuilder", '-ndm', 1, '-ndf', 1)

gap = 2*cm
ops.node(1, *[0])
ops.node(2, *[0])

ops.mass(2, 100) # 100 kg mass

ops.fix(1, *[1])

# viscous Damper materials
damperMaterialsID = list(range(1,5))
kD = 300.0 # kN/mm

cD = np.array([280.3, 73, 1017.7, 1.2]) 
alpha = np.array((0.3, 0.6, 0.01, 1.50))

#for idamperID,icD,ialpha in zip(range(damperMaterialsID), cD, alpha):
#    #ops.uniaxialMaterial('Viscous', viscousID, C, alpha)
#    ops.uniaxialMaterial('ViscousDamper', idamperID, kD, icD*kN*pow((mm/sec), ialpha), ialpha)

ops.uniaxialMaterial('ViscousDamper', 1, kD, cD[2] , alpha[2])

#element('zeroLength', eleTag, *eleNodes, '-mat', *matTags, '-dir', *dirs)
#element('twoNodeLink', eleTag, *eleNodes, '-mat', *matTags, '-dir', *dir
ops.element('zeroLength', 1, *[1, 2], '-mat', 1, '-dir', *[1])

# sine series
sineWave = 1
#timeSeries('Trig', tag, tStart, tEnd, period, '-factor', factor=1.0, '-shift', shift=0.0, '-zeroShift', zeroShift=0.0)
ops.timeSeries('Trig', sineWave, 0, 10 , 2, '-factor', 40.0) #apply sine series for 40s
ops.pattern('UniformExcitation', sineWave, 1, '-accel', sineWave)

# ground motion
eqLoad = 2
# ops.timeSeries('Path', eqLoad, '-dt', 0.01, '-filePath', "TakY.th", '-factor', g)
# ops.pattern('UniformExcitation', eqLoad, 1, '-accel', eqLoad)


# recorders
ops.recorder('Element', '-file', 'viscousDamperDisplacement.txt', '-time', '-closeOnWrite','-ele', 1 , '-dof', 1, 'deformations')
ops.recorder('Element', '-file', 'viscousDamperReactions.txt', '-time', '-closeOnWrite','-ele', 1 , '-dof', 1, 'localForce')

# analysis


ops.constraints('Transformation')
ops.numberer('RCM')
ops.test('EnergyIncr', 1.0e-10, 100)
ops.algorithm('ModifiedNewton')
ops.system('UmfPack')
ops.integrator('Newmark', .5, .25)
#ops.integrator('DisplacementControl', 2, 1, 0.001)
ops.analysis('Transient')

for i in range(1000):
    ops.analyze(1, 0.01)
    print(f"time:{(i+1)*0.01}\tStep:{i+1}")
# run analysis up to 4000 step, with time step = 0.01s, so total time = 40s

disp = np.loadtxt("viscousDamperDisplacement.txt")
rxn = np.loadtxt("viscousDamperReactions.txt")
plt.plot(disp[:, 1], -rxn[:, 1])
plt.show()