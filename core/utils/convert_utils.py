import numpy as np
def float32_to_int16(audio_array):
    # Scale float32 array to int16
    return np.int16(audio_array * 32767)