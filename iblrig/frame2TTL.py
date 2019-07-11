import serial
import numpy as np
import struct
import logging

log = logging.getLogger('iblrig')


class Frame2TTL(object):
    def __init__(self, serial_port):
        self.serial_port = serial_port
        self.connected = False
        self.ser = self.connect(serial_port)
        self.light_threshold = 40
        self.dark_threshold = 80
        self.streaming = False
        self.measured_black = None
        self.measured_white = None
        self.recomend_dark = None
        self.recomend_light = None

    def connect(self, serial_port) -> serial.Serial:
        """Create connection to serial_port"""
        ser = serial.Serial(port=serial_port, baudrate=115200, timeout=1)
        self.connected = True
        return ser

    def close(self) -> None:
        """Close connection to serial port"""
        self.ser.close()

    def start_stream(self) -> None:
        """Enable streaming to USB (stream rate 100Hz)
        response = int.from_bytes(self.ser.read(4), byteorder='little')"""
        self.ser.write(struct.pack('cB', b'S', 1))
        self.streaming = True

    def stop_stream(self) -> None:
        """Disable streaming to USB"""
        self.ser.write(struct.pack('cB', b'S', 0))
        self.streaming = False

    def read_value(self) -> int:
        """Read one value from sensor (current)"""
        self.ser.write(b'V')
        response = self.ser.read(4)
        # print(np.frombuffer(response, dtype=np.uint32))
        response = int.from_bytes(response, byteorder='little')
        return response

    def measure_photons(self, num_samples: int = 250) -> dict:
        """Measure <num_samples> values from the sensor and return basic stats.
        Mean, Std, SEM, Nsamples
        """
        import time
        sample_sum = []
        for i in range(num_samples):
            sample_sum.append(self.read_value())
            time.sleep(0.001)

        out = {
            'mean_value': np.array(sample_sum).mean(),
            'max_value': np.array(sample_sum).max(),
            'min_value': np.array(sample_sum).min(),
            'std_value': np.array(sample_sum).std(),
            'sem_value': np.array(sample_sum).std() / np.sqrt(num_samples),
            'nsamples': num_samples
        }
        return out

    def set_thresholds(self, dark=None, light=None) -> None:
        """Set light, dark, or both thresholds for the device"""
        if dark is None:
            dark = self.dark_threshold
        if light is None:
            light = self.light_threshold

        self.ser.write(b'C')
        response = self.ser.read(1)
        if response[0] != 218:
            raise(ConnectionError)

        # Device wants light threshold before dark
        self.ser.write(struct.pack('<BHH', ord('T'), int(light), int(dark)))
        if light != self.light_threshold:
            log.info(f"Light threshold set to {light}")
        if dark != self.dark_threshold:
            log.info(f"Dark threshold set to {dark}")
        if light == 40 and dark == 80:
            log.info(f"Resetted to default values: light={light} - dark={dark}")
        self.dark_threshold = dark
        self.light_threshold = light

    def measure_white(self):
        log.info("Measuring white...")
        self.measured_white = self.measure_photons(10000)
        return self.measured_white

    def measure_black(self):
        log.info("Measuring black...")
        self.measured_black = self.measure_photons(10000)
        return self.measured_black

    def calc_recomend_thresholds(self):
        if (self.measured_black is None) or (self.measured_white is None):
            log.error("No mesures exist")
            return -1
        self.recomend_light = self.measured_white.get('max_value')
        if self.measured_black['min_value'] - self.recomend_light > 40:
            self.recomend_dark = self.recomend_light + 40
        else:
            self.recomend_dark = round(self.recomend_light + (
                (self.measured_black['min_value'] - self.recomend_light) / 3))
        if self.recomend_dark - self.recomend_light < 5:
            log.error('Cannot recommend thresholds:'),
            log.error('Black and White measurements may be too close for accurate frame detection')
            log.error(f'Light = {self.recomend_light}, Dark = {self.recomend_dark}')
            return -1
        else:
            log.info('Recommended thresholds:')
            log.info(f'Light ={self.recomend_light}, Dark = {self.recomend_dark}.')
            log.info(f'Sending thresholds to device...')
            print('Done')
            return self.recomend_dark, self.recomend_light

    def set_recommendations(self):
        self.set_thresholds(dark=self.recomend_dark, light=self.recomend_light)

    def suggest_thresholds(self) -> None:
        input("Set pixels under Frame2TTL to white (rgb 255,255,255) and press enter >")
        print(" ")
        print("Measuring white...")
        white_data = self.measure_photons(10000)

        input("Set pixels under Frame2TTL to black (rgb 0,0,0) and press enter >")
        print(" ")
        print("Measuring black...")
        dark_data = self.measure_photons(10000)
        print(" ")
        light_max = white_data.get('max_value')
        dark_min = dark_data.get('min_value')
        print(f"Max sensor reading for white (lower is brighter) = {light_max}.")
        print(f"Min sensor reading for black = {dark_min}.")
        recomend_light = light_max
        if dark_min - recomend_light > 40:
            recomend_dark = recomend_light + 40
        else:
            recomend_dark = round(
                recomend_light + ((dark_min - recomend_light) / 3))
        if recomend_dark - recomend_light < 5:
            print('Error: Cannot recommend thresholds:',
                  'light and dark measurements may be too close for accurate frame detection')
        else:
            log.info(f"Recommended thresholds: Light = {recomend_light}, Dark = {recomend_dark}.")
            log.info(f"Sending thresholds to device...")
            self.recomend_dark = recomend_dark
            self.recomend_light = recomend_light
            self.set_thresholds(light=recomend_light, dark=recomend_dark)
            print('Done')


if __name__ == "__main__":
    com_port = 'COM6'
    f = Frame2TTL(com_port)
    print(f.read_value())
    print(f.measure_photons())
    f.set_thresholds()
    f.set_thresholds(light=41, dark=81)
    f.set_thresholds(light=41)
    f.set_thresholds(dark=81)
    f.suggest_thresholds()
    print('.')
