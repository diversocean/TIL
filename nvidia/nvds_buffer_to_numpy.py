from diversocean import Engine
from diversocean.inputs import UriInput
from diversocean.outputs import FileOutput
from diversocean.filters import NvInfer, NvOverlay
import cv2
import pyds


def custom_callback_on_object(name, object_info):
    rect_params = object_info.rect_params
    text_params = object_info.text_params

    if object_info.class_id == 0:
        rect_params.border_color.set(0.0, 1.0, 0.0, 0.0)
        rect_params.border_width = 5
        text_params.font_params.font_size = 10
        object_info.text_params.text_bg_clr.set(0.0, 1.0, 0.0, 0.0)
        object_info.text_params.font_params.font_name = "Sans"
    else:
        rect_params.border_width = 0
        text_params.set_bg_clr = 0
        text_params.font_params.font_size = 0


# def custom_callback_on_frame(name, info, frame_info):
#     buffer = info.get_buffer()
#     batch_meta = pyds.gst_buffer_get_nvds_batch_meta(hash(buffer))
#     count = frame_info.num_obj_meta
#     print("count : {}\r".format(count), end='')
#     import pdb;pdb.set_trace()

def custom_callback_on_buffer_surface(name, info, frame_info):
    buffer = info.get_buffer()
    batch_meta = pyds.gst_buffer_get_nvds_batch_meta(hash(buffer))

    l_frame = batch_meta.frame_meta_list
    frame_meta = pyds.NvDsFrameMeta.cast(l_frame.data)
    import pdb;pdb.set_trace();
    n_frame = pyds.get_nvds_buf_surface(hash(buffer), frame_meta.batch_id)
    count = frame_info.num_obj_meta
    cv2.putText(n_frame, f'person:{count}', (30,30), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)


if __name__ == "__main__":

    engine = Engine(
        NvInfer(
            "nvinfer", "../models/yolov4/config.txt",
            callback_on_object=custom_callback_on_object,
            callback_on_surface=custom_callback_on_buffer_surface,
        ),
        UriInput(uid="input0", uri="../samples/ch05_raw.mp4"),
        NvOverlay(uid="nvoverlay0"),
        FileOutput(uid="output0", path="test.mp4"),
    )

    engine.link("input0", "nvinfer", "nvoverlay0", "output0")
    engine.start()
