import pyds
from .. import Gst
from ..helpers import link_many
from ._filter import Filter
from ..utils import ColorPicker


class GList(object):
    def __init__(self, glist, cast_func=None):
        self.glist = glist
        self.cast_func = cast_func

    def __iter__(self):
        while self.glist is not None:
            if self.cast_func is not None:
                yield self.cast_func(self.glist.data)
            else:
                yield self.glist.data
            try:
                self.glist = self.glist.next
            except StopIteration:
                break


class FrameInfo(GList):
    def __init__(self, frame_meta_list):
        super(FrameInfo, self).__init__(frame_meta_list, pyds.NvDsFrameMeta.cast)


class ObjectInfo(GList):
    def __init__(self, obj_meta_list):
        super(ObjectInfo, self).__init__(obj_meta_list, pyds.NvDsObjectMeta.cast)


class NvInfer(Filter):
    def __init__(
        self,
        uid,
        config_file,
        interval=0,
        width=1280,
        height=720,
        batch_size=1,
        callback_on_frame=None,
        callback_on_object=None,
        callback_on_surface=None,
    ):
        super(NvInfer, self).__init__(uid)
        streammux_bin = self.create_elements("nvstreammux")
        queue_before_infer = self.create_elements("queue")
        nvinfer = self.create_elements("nvinfer")
        queue_after_infer = self.create_elements("queue")
        streamdemux_bin = self.create_elements("nvstreamdemux")
        self._first_element = streammux_bin
        self._last_element = streamdemux_bin

        streammux_bin.set_property("width", width)
        streammux_bin.set_property("height", height)
        streammux_bin.set_property("batch-size", batch_size)
        streammux_bin.set_property("batched-push-timeout", 4000000)
        streammux_bin.set_property("enable-padding", True)
        nvinfer.set_property("config-file-path", config_file)
        nvinfer.set_property("interval", interval)

        with open(config_file, "r") as f:
            config_file = f.read()
        for line in config_file.split("\n"):
            if "num-detected-classes" in line:
                self.num_classes = int(line.split("=")[-1])

        link_many(
            streammux_bin,
            queue_before_infer,
            nvinfer,
            queue_after_infer,
            streamdemux_bin,
        )

        self.callback_on_frame = callback_on_frame
        self.callback_on_object = callback_on_object
        self.callback_on_surface = callback_on_surface
        if self.callback_on_object is None:
            self.colors = ColorPicker(self.num_classes)
        self.connect("pad-added", self._callback_on_pad_added)

        # if self.callback_on_surface is None:
        #     self.default_callback_on_buffer_surface

    def _callback_on_pad_added(self, block, pad):
        if pad.direction.value_nick == "src":
            pad.add_probe(Gst.PadProbeType.BUFFER, self.callback_on_batch)
            return Gst.PadProbeReturn.REMOVE

    def callback_on_batch(self, pad, info):
        buffer = info.get_buffer()
        batch_meta = pyds.gst_buffer_get_nvds_batch_meta(hash(buffer))
        for frame_info in FrameInfo(batch_meta.frame_meta_list):
            if self.callback_on_frame is not None:
                self.callback_on_frame(pad.name, frame_info)
            if self.callback_on_surface is not None:
                self.callback_on_surface(pad.name, info, frame_info)
            for object_info in ObjectInfo(frame_info.obj_meta_list):
                if self.callback_on_object is not None:
                    self.callback_on_object(pad.name, object_info)
                else:
                    self.default_callback_on_object(pad.name, object_info)
        return Gst.PadProbeReturn.OK

    def default_callback_on_object(self, name, object_info):
        color = self.colors[object_info.class_id] + [1.0]
        object_info.rect_params.border_color.set(*color)
        object_info.rect_params.border_width = 5
        object_info.text_params.set_bg_clr = 1
        object_info.text_params.text_bg_clr.set(*color)
        object_info.text_params.font_params.font_name = "Sans"
