import numpy as np
import dectris.compression as deco

import os


image_pixel_format = {
    64: 'u1',
    65: '>u2',
    66: '>u4',
    67: '>u8',
    68: 'u1',
    69: '<u2',
    70: '<u4',
    71: "<u8",
    72: "i1",
    73: ">i2",
    74: ">i4",
    75: ">i8",
    77: "<i2",
    78: "<i4",
    79: "<i8",
    80: ">f2",
    81: ">f4",
    82: ">f8",
    83: ">f16",
    84: "<f2",
    85: "<f4",
    86: "<f8",
    87: "<f16",
}

def image_unpack(data, pixel_reshape_order="C"):
    '''
    Unpacks an Eiger-packed image and returns the Numpy array.
    
    `data` is the payload of the corresponding dectris "image"
    ZMQ event.

    Generally, the format is a stacked series of CBOR2 objects
    (CBORTag), roughly packed like this:

    ```
    CBORTag{
        "tag": 40, ## array of two arrays
        "value": [
            img_size,
            CBORTag{
                "tag": pixel_format_tag, ## 69, 70, ...
                "value": CBORTag{
                    "tag": 56500, ## dectris compressed buffer
                    "value": [algorithm_name, bytes_per_element, compressed_buffer]
                }
            }
        ]
    }
    ```

    Check Dectris docs for `pixel_reshape_order`. Apparently "C" gives
    the right result, but who knows...

    This is valid for Dectris API version 1.8.

    Returns a Numpy-array, the 2D Dectris image.
    '''

    if data.tag != 40:
        s = str(data)
        raise RuntimeError(f'Expected image data as CBORTag(tag=40), received: {s[0:30]}...{s[-10:]}')

    imgsize, data2 = data.value # two arrays

    pixfmt_tag = data2.tag
    data3 = data2.value

    if data3.tag != 56500:
        s = str(data3)
        raise RuntimeError(f'Expected Dectris compressed data as CBORTag(tag=56500), '
                           f'received {s[0:30]}...{s[-10:]}')

    cmp_alg, cmp_esize, cmp_buf = data3.value
    uncmp_buf = deco.decompress(cmp_buf, cmp_alg, elem_size=cmp_esize)

    return np.frombuffer(uncmp_buf, image_pixel_format[pixfmt_tag]).\
        reshape(imgsize, order=pixel_reshape_order)
