import time
import depthai as dai

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

    # Configure IMU
    imu.enableIMUSensor([dai.IMUSensor.ACCELEROMETER_RAW, dai.IMUSensor.GYROSCOPE_RAW], 200)
    imu.setBatchReportThreshold(1)
    imu.setMaxBatchReports(10)

    # Linking
    left.requestOutput((width, height)).link(odom.left)
    right.requestOutput((width, height)).link(odom.right)
    imu.out.link(odom.imu)
    
    # Connect to the device and start the pipeline
    with dai.Device(p) as device:
        # Create output queues
        qualityQueue = device.getOutputQueue("quality", maxSize=8, blocking=False)
        transformQueue = device.getOutputQueue("transform", maxSize=8, blocking=False)
        
        print("VIO Quality Metrics Monitor")
        print("=" * 60)
        print("Waiting for VIO initialization...")
        
        frame_count = 0
        last_quality_time = time.time()
        
        while True:
            try:
                # Get quality metrics
                qualityData = qualityQueue.tryGet()
                if qualityData is not None:
                    frame_count += 1
                    current_time = time.time()
                    
                    # Print quality metrics every second or on significant changes
                    if current_time - last_quality_time > 1.0:
                        print(f"\n--- Frame {frame_count} ---")
                        print(f"Tracking Status: {'🟢 TRACKING' if qualityData.isTracking else '🔴 LOST'}")
                        print(f"Active 3D Points: {qualityData.numActivePoints}")
                        print(f"Landmarks in Map: {qualityData.numLandmarks}")
                        print(f"Total Observations: {qualityData.numObservations}")
                        print(f"Keyframes: {qualityData.numKeyframes}")
                        print(f"States: {qualityData.numStates}")
                        print(f"Avg Tracking Quality: {qualityData.avgTrackingQuality:.1%}")
                        
                        if qualityData.numTrackedFeatures:
                            print(f"Features per Camera: {qualityData.numTrackedFeatures}")
                            total_features = sum(qualityData.numTrackedFeatures)
                            print(f"Total Features: {total_features}")
                            
                            # Quality assessment with emojis
                            if qualityData.avgTrackingQuality > 0.8:
                                status = "🟢 EXCELLENT"
                            elif qualityData.avgTrackingQuality > 0.6:
                                status = "🟡 GOOD"
                            elif qualityData.avgTrackingQuality > 0.4:
                                status = "🟠 FAIR"
                            else:
                                status = "🔴 POOR"
                            print(f"Visual Quality: {status}")
                        
                        # Show transform data if available
                        transformData = transformQueue.tryGet()
                        if transformData is not None:
                            translation = transformData.getTranslation()
                            print(f"Position: x={translation.x:.2f}, y={translation.y:.2f}, z={translation.z:.2f}")
                        
                        last_quality_time = current_time
                        
                # Handle tracking loss
                elif frame_count > 100:  # Only check after some frames
                    print("⚠️  No quality data received - VIO may not be initialized")
                
                time.sleep(0.01)  # Small delay to prevent busy waiting
                
            except KeyboardInterrupt:
                print("\n🛑 Stopping VIO quality monitor...")
                break 