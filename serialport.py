
# Handles serial communication

from re import S
import serial
import yaml



class SerialInput():
    """Serial creating serial structure"""
    
    def __init__(self) -> None:
        self.cfg = yaml.full_load(open('cfg.yaml', 'r'))




class SerialObj():
    """Serial object for communication"""
    
    def __init__(self) -> None:
        pass




if __name__ == '__main__':
    a = SerialInput()


    with serial.Serial('COM4', 115200) as ser:
        while True:        
            line = ser.readline().strip()
            s = line.decode('ascii')

            print(s)



# with serial.Serial('COM4', 115200, timeout = 1) as ser:
#             ser.reset_input_buffer()
#             while True:
#                 line = ser.readline().strip()
#                 s = line.decode('ascii')

#                 if s:
#                     curr_time = time.monotonic_ns()
#                     self.new_data.append(int(s))
#                     self.new_time.append((curr_time - prev_time)*1e-9)
#                     prev_time = curr_time