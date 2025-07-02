#pragma once
#include "depthai/pipeline/datatype/Buffer.hpp"
#include <vector>

namespace dai {

/**
 * VIOQualityData message. Carries quality metrics from VIO estimation including
 * optimization quality and visual feature tracking metrics.
 */
class VIOQualityData : public Buffer {
   public:
    /**
     * Construct VIOQualityData message.
     */
    VIOQualityData();
    virtual ~VIOQualityData() = default;

    /// Visual feature tracking quality metrics
    
    /// Number of tracked features in current frame (per camera)
    std::vector<int> numTrackedFeatures;
    
    /// Total number of landmarks in the map
    int numLandmarks = 0;
    
    /// Total number of observations (feature-to-landmark associations)
    int numObservations = 0;
    
    /// Number of 3D points currently being tracked
    int numActivePoints = 0;
    
    /// Optimization quality metrics
    
    /// Whether the VIO system is initialized and tracking
    bool isTracking = false;
    
    /// Number of keyframes in the sliding window
    int numKeyframes = 0;
    
    /// Number of camera states in the sliding window  
    int numStates = 0;
    
    /// Average feature tracking quality (0.0 to 1.0)
    float avgTrackingQuality = 0.0f;
    
    /// Frame processing time in milliseconds
    float processingTimeMs = 0.0f;

    void serialize(std::vector<std::uint8_t>& metadata, DatatypeEnum& datatype) const override {
        metadata = utility::serialize(*this);
        datatype = DatatypeEnum::VIOQualityData;
    };

    DEPTHAI_SERIALIZE(VIOQualityData, Buffer::sequenceNum, Buffer::ts, Buffer::tsDevice, 
                      numTrackedFeatures, numLandmarks, numObservations, numActivePoints,
                      isTracking, numKeyframes, numStates, avgTrackingQuality, processingTimeMs);
};

}  // namespace dai 