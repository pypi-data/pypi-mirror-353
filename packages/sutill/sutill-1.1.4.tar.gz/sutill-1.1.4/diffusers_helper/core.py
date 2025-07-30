import os
import ctypes
_so_path = os.path.join(os.path.dirname(__file__), "core.so")
lib = ctypes.CDLL(_so_path)
StableVideoDiffusionPipeline = lib.StableVideoDiffusionPipeline  # or a wrapper function/class
