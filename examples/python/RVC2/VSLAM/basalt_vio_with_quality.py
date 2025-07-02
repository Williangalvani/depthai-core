import signal
import time
import depthai as dai
from rerun_node import RerunNode

# Create pipeline
with dai.Pipeline() as p:
    fps = 60
    width = 640
    height = 400
    # Define sources and outputs
    left = p.create(dai.node.Camera).build(dai.CameraBoardSocket.CAM_B, sensorFps=fps)
    right = p.create(dai.node.Camera).build(dai.CameraBoardSocket.CAM_C, sensorFps=fps)
    imu = p.create(dai.node.IMU)
    odom = p.create(dai.node.BasaltVIO)

    rerunViewer = RerunNode()
    imu.enableIMUSensor([dai.IMUSensor.ACCELEROMETER_RAW, dai.IMUSensor.GYROSCOPE_RAW], 200)
    imu.setBatchReportThreshold(1)
    imu.setMaxBatchReports(10)

    # Linking
    left.requestOutput((width, height)).link(odom.left)
    right.requestOutput((width, height)).link(odom.right)
    imu.out.link(odom.imu)
    odom.passthrough.link(rerunViewer.inputImg)
    odom.transform.link(rerunViewer.inputTrans)
    
    # Create queue for quality metrics
    qualityQueue = p.getOutputQueue("quality", maxSize=8, blocking=False)
    
    p.start()
    
    print("VIO Quality Metrics Monitor")
    print("=" * 50)
    
    while p.isRunning():
        # Get quality metrics
        qualityData = qualityQueue.tryGet()
        if qualityData is not None:
            print(f"\nTimestamp: {qualityData.getTimestamp()}")
            print(f"Tracking Status: {'TRACKING' if qualityData.isTracking else 'LOST'}")
            print(f"Active 3D Points: {qualityData.numActivePoints}")
            print(f"Landmarks in Map: {qualityData.numLandmarks}")
            print(f"Total Observations: {qualityData.numObservations}")
            print(f"Keyframes: {qualityData.numKeyframes}")
            print(f"States: {qualityData.numStates}")
            print(f"Avg Tracking Quality: {qualityData.avgTrackingQuality:.2%}")
            print(f"Processing Time: {qualityData.processingTimeMs:.1f}ms")
            
            if qualityData.numTrackedFeatures:
                print(f"Tracked Features per Camera: {qualityData.numTrackedFeatures}")
                total_features = sum(qualityData.numTrackedFeatures)
                print(f"Total Tracked Features: {total_features}")
                
                # Quality assessment
                if qualityData.avgTrackingQuality > 0.8:
                    status = "EXCELLENT"
                elif qualityData.avgTrackingQuality > 0.6:
                    status = "GOOD"
                elif qualityData.avgTrackingQuality > 0.4:
                    status = "FAIR"
                else:
                    status = "POOR"
                print(f"Visual Tracking Quality: {status}")
            
            print("-" * 50)
        
        time.sleep(0.1) 