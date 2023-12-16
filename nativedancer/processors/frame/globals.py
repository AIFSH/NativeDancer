from typing import List, Optional

from nativedancer.processors.frame.typings import *

pose_frame_model : Optional[PoseFrameModel] = None
frame_pose_model : Optional[FramePoseModel] = None
frame_enhancer_model : Optional[FrameEnhancerModel] = None
frame_enhancer_blend : Optional[int] = None

random_seed : Optional[int] = None
guidance_scale : Optional[float] = None
step : Optional[int] = None

animate_path : Optional[str] = None
pose_path : Optional[str] = None

face_swapper_model : Optional[FaceSwapperModel] = None
face_enhancer_model : Optional[FaceEnhancerModel] = None
face_enhancer_blend : Optional[int] = None
face_debugger_items : Optional[List[FaceDebuggerItem]] = None
