#include "depthai/pipeline/datatype/VIOQualityData.hpp"

namespace dai {

VIOQualityData::VIOQualityData() {
    // Initialize with default values
    numTrackedFeatures.clear();
    numLandmarks = 0;
    numObservations = 0;
    numActivePoints = 0;
    isTracking = false;
    numKeyframes = 0;
    numStates = 0;
    avgTrackingQuality = 0.0f;
    processingTimeMs = 0.0f;
}

}  // namespace dai 