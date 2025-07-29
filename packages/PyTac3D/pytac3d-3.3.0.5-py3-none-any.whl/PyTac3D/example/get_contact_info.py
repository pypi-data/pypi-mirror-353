import PyTac3D
import time
import numpy as np
import os

path = os.path.join(os.path.split(PyTac3D.__file__)[0], 'data/example_1')
SN1 = 'AD2-0065L'

loader1 = PyTac3D.DataLoader(path, SN1, skip=0)

analyzer1 = PyTac3D.Analyzer(SN1)

view1 = PyTac3D.SensorView(SN1, PyTac3D.Presets.Mesh_Color_1)
view1.setRotation(
    np.matrix( [[1,0,0],
                [0,1,0],
                [0,0,1],
                ], np.float64)
    )
view1.setTranslation([0,0,-10])
view1.enable_Mesh = True
view1.enable_Pointcloud = False
view1.enable_Contact = True
view1.enable_Displacements = False
view1.enable_Normals = False
view1.enable_Forces = True
view1.enable_Object = True
view1.enable_3D_ResForce = False
view1.enable_3D_ResMoment = False


def buttonCallback_Restart():
    global restartFlag
    restartFlag = True

def buttonCallback_Calibrate():
    pass

displayer = PyTac3D.Displayer(PyTac3D.Presets.Lights_1)
displayer.buttonCallback_Restart = buttonCallback_Restart
displayer.buttonCallback_Calibrate = buttonCallback_Calibrate
displayer.addView(view1)

dt = 0.03
restartFlag = True

while displayer.isRunning():
    if restartFlag:
        loader1.reset()
        frame1, t1, endFlag1 = loader1.get()
        startTime = time.time() - t1
        restartFlag = False

    currentTime = time.time() - startTime

    # 获取数据，时间对齐
    while not endFlag1 and t1 < currentTime:
        frame1, t1, endFlag1 = loader1.get()

    # 到达最后一帧时，重新开始
    if endFlag1:
        restartFlag = True

    if frame1:
        analyzer1.detectContact(frame1)
        view1.put(frame1)

        pointsIsContacted = np.squeeze(frame1['ContactRegion']['region'])
        contactPointsNum = frame1['ContactRegion']['area']
        print('=========================================')
        print('Contact points number: %d' % contactPointsNum)
        print('%d contact regions detected.' % len(frame1['ContactRegions']))
        # print('Contact points positions:', frame1['3D_Positions'][pointsIsContacted,:])
        # print('Contact points displacements:', frame1['3D_Displacements'][pointsIsContacted,:])
        # print('Contact points forces:', frame1['3D_Forces'][pointsIsContacted,:])
        # print('Contact points localforces:', frame1['LocalForces'][pointsIsContacted,:])

        for i in range(len(frame1['ContactRegions'])):
            region = frame1['ContactRegions'][i]
            print('  region %d:' % (i+1))
            pointsIsContacted_in_this_region = np.squeeze(region['region'])
            contactPointsNum_in_this_region = np.squeeze(region['area'])
            print('    Contact points number: %d' % contactPointsNum_in_this_region)
            # print('    Contact points:', frame1['3D_Positions'][pointsIsContacted_in_this_region,:])
            # print('    Contact points displacements:', frame1['3D_Displacements'][pointsIsContacted_in_this_region,:])
            # print('    Contact points forces:', frame1['3D_Forces'][pointsIsContacted_in_this_region,:])
            # print('    Contact points localforces:', frame1['LocalForces'][pointsIsContacted_in_this_region,:])


    time.sleep(dt)

