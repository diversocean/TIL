# TIL
Today I leaned

## [1. Deepstream](https://docs.nvidia.com/metropolis/deepstream/5.0DP/python-api/index.html)
[- Deepstream Python: nvds_buffer → Numpy format](https://docs.nvidia.com/metropolis/deepstream/5.0DP/python-api/Methods/methodsdoc.html)  
[- Deepstream Python_set capsfilter to convert the video format to RGBA](https://forums.developer.nvidia.com/t/deepstream-python-bindings-cannot-access-frame-from-deepstream-test-app3/153804/3)

## Error
`*** RuntimeError: get_nvds_buf_Surface: Currently we only support RGBA color Format ***`
  
In Deepstream,  
video format:RGBA → pyds.get_nvds_buf_surface(arg0: int, arg1: int) → numpy.ndarray[uint8]

define video format:RGBA = **capsfilter** plugin
