from typing import Dict

from new_extrinsic_calibration_manager.calibrator_base import CalibratorBase
from new_extrinsic_calibration_manager.calibrator_registry import CalibratorRegistry
from new_extrinsic_calibration_manager.ros_interface import RosInterface
from new_extrinsic_calibration_manager.types import FramePair
import numpy as np


@CalibratorRegistry.register_calibrator(
    project_name="x2", calibrator_name="mapping_based_base_lidar_calibrator"
)
class MappingBasedBaseLidarCalibrator(CalibratorBase):
    required_frames = []

    def __init__(self, ros_interface: RosInterface, **kwargs):
        super().__init__(ros_interface)

        self.base_frame = "base_link"
        self.top_sensor_kit_frame = "top_unit_base_link"

        self.mapping_lidar_frame = "pandar_40p_left"

        self.required_frames.extend(
            [self.base_frame, self.top_sensor_kit_frame, self.mapping_lidar_frame]
        )

        print("X2_MappingBasedBaseLidarCalibrator")

        self.add_calibrator(
            service_name="calibrate_base_lidar",
            expected_calibration_frames=[
                FramePair(parent=self.mapping_lidar_frame, child=self.base_frame)
            ],
        )

    def post_process(self, calibration_transforms: Dict[str, Dict[str, np.array]]):
        top_sensor_kit_to_mapping_lidar_transform = self.get_transform_matrix(
            self.top_sensor_kit_frame, self.mapping_lidar_frame
        )

        base_to_top_sensor_kit_transform = np.linalg.inv(
            top_sensor_kit_to_mapping_lidar_transform
            @ calibration_transforms[self.mapping_lidar_frame][self.base_frame]
        )
        results = {self.base_frame: {self.top_sensor_kit_frame: base_to_top_sensor_kit_transform}}

        return results
