from .. import Gst
from ..helpers import link_many
from ._filter import Filter


class NvOverlay(Filter):
    def __init__(self, uid):
        super(NvOverlay, self).__init__(uid)

        self._first_element = self._create_default_first_element()
        self._last_element = self._create_default_last_element()
        convert_before_nvosd = self.create_elements("nvvideoconvert")
        capsfilter_before_nvosd = self.create_elements("capsfilter")
        capsfilter_before_nvosd.set_property(
            "caps",
            Gst.caps_from_string("video/x-raw(memory:NVMM), format=RGBA"),
        )
        osd = self.create_elements("nvdsosd")
        convert_after_nvosd = self.create_elements("nvvideoconvert")
        capsfilter_after_nvosd = self.create_elements("capsfilter")
        capsfilter_after_nvosd.set_property(
            "caps",
            Gst.caps_from_string("video/x-raw(memory:NVMM), format=NV12"),
        )

        link_many(
            self._first_element,
            convert_before_nvosd,
            capsfilter_before_nvosd,
            osd,
            convert_after_nvosd,
            capsfilter_after_nvosd,
            self._last_element,
        )
