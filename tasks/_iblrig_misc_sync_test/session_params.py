#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Niccolò Bonacchi
# @Date:   2018-02-02 17:19:09
import logging
from sys import platform

from pythonosc import udp_client

import iblrig.bonsai as bonsai
import iblrig.iotasks as iotasks
import iblrig.sound as sound
from iblrig.path_helper import SessionPathCreator
from iblrig.rotary_encoder import MyRotaryEncoder

log = logging.getLogger('iblrig')


class SessionParamHandler(object):
    """Session object imports user_settings and task_settings
    will and calculates other secondary session parameters,
    runs Bonsai and saves all params in a settings file.json"""

    def __init__(self, task_settings, user_settings):
        # =====================================================================
        # IMPORT task_settings, user_settings, and SessionPathCreator params
        # =====================================================================
        ts = {i: task_settings.__dict__[i]
              for i in [x for x in dir(task_settings) if '__' not in x]}
        self.__dict__.update(ts)
        us = {i: user_settings.__dict__[i]
              for i in [x for x in dir(user_settings) if '__' not in x]}
        self.__dict__.update(us)
        self = iotasks.deserialize_pybpod_user_settings(self)
        spc = SessionPathCreator(self.IBLRIG_FOLDER, self.IBLRIG_DATA_FOLDER,
                                 self.PYBPOD_SUBJECTS[0],
                                 protocol=self.PYBPOD_PROTOCOL,
                                 board=self.PYBPOD_BOARD, make=True)
        self.__dict__.update(spc.__dict__)
        # =====================================================================
        # OSC CLIENT
        # =====================================================================
        self.OSC_CLIENT_PORT = 7110
        self.OSC_CLIENT_IP = '127.0.0.1'
        self.OSC_CLIENT = udp_client.SimpleUDPClient(self.OSC_CLIENT_IP,
                                                     self.OSC_CLIENT_PORT)
        # =====================================================================
        # ROTARY ENCODER
        # =====================================================================
        self.ALL_THRESHOLDS = self.STIM_POSITIONS
        self.ROTARY_ENCODER = MyRotaryEncoder(self.ALL_THRESHOLDS,
                                              self.STIM_GAIN,
                                              self.COM['ROTARY_ENCODER'])
        # =====================================================================
        # SOUNDS
        # =====================================================================
        self.SOUND_SAMPLE_FREQ = sound.sound_sample_freq(self.SOFT_SOUND)

        self.GO_TONE_DURATION = float(self.GO_TONE_DURATION)
        self.GO_TONE_FREQUENCY = int(self.GO_TONE_FREQUENCY)
        self.GO_TONE_AMPLITUDE = float(self.GO_TONE_AMPLITUDE)

        self.SD = sound.configure_sounddevice(
            output=self.SOFT_SOUND, samplerate=self.SOUND_SAMPLE_FREQ)

        self.SOUND_BOARD_BPOD_PORT = 'Serial3'
        self.GO_TONE_IDX = 2
        self.GO_TONE = None
        self = sound.init_sounds(self, noise=False)
        if self.SOFT_SOUND is None:
            sound.configure_sound_card(
                sounds=[self.GO_TONE],
                indexes=[self.GO_TONE_IDX],
                sample_rate=self.SOUND_SAMPLE_FREQ)
        self.OUT_STOP_SOUND = (
            'SoftCode', 0) if self.SOFT_SOUND else ('Serial3', ord('X'))
        self.OUT_TONE = ('SoftCode', 1) if self.SOFT_SOUND else ('Serial3', 5)
        # =====================================================================
        # RUN VISUAL STIM
        # =====================================================================
        bonsai.start_visual_stim(self)
        # =====================================================================
        # SAVE SETTINGS FILE AND TASK CODE
        # =====================================================================
        iotasks.save_session_settings(self)
        iotasks.copy_task_code(self)
        iotasks.save_task_code(self)

    # =========================================================================
    # SOUND INTERFACE FOR STATE MACHINE
    # =========================================================================
    def play_tone(self):
        self.SD.play(self.GO_TONE, self.SOUND_SAMPLE_FREQ)

    def stop_sound(self):
        self.SD.stop()

    # =========================================================================
    # JSON ENCODER PATCHES
    # =========================================================================
    def reprJSON(self):
        def remove_from_dict(sx):
            if "weighings" in sx.keys():
                sx["weighings"] = None
            if "water_administration" in sx.keys():
                sx["water_administration"] = None
            return sx

        d = self.__dict__.copy()
        d['GO_TONE'] = 'go_tone(freq={}, dur={}, amp={})'.format(
            self.GO_TONE_FREQUENCY, self.GO_TONE_DURATION,
            self.GO_TONE_AMPLITUDE)
        d['SD'] = str(d['SD'])
        d['OSC_CLIENT'] = str(d['OSC_CLIENT'])
        if isinstance(d['PYBPOD_SUBJECT_EXTRA'], list):
            sub = []
            for sx in d['PYBPOD_SUBJECT_EXTRA']:
                sub.append(remove_from_dict(sx))
            d['PYBPOD_SUBJECT_EXTRA'] = sub
        elif isinstance(d['PYBPOD_SUBJECT_EXTRA'], dict):
            d['PYBPOD_SUBJECT_EXTRA'] = remove_from_dict(
                d['PYBPOD_SUBJECT_EXTRA'])

        return d


if __name__ == '__main__':
    """
    SessionParamHandler fmake flag=False disables:
        making folders/files;
    SessionParamHandler debug flag disables:
        running auto calib;
        calling bonsai
        turning off lights of bpod board
    """
    import task_settings as _task_settings
    import scratch._user_settings as _user_settings
    if platform == 'linux':
        r = "/home/nico/Projects/IBL/github/iblrig"
        _task_settings.IBLRIG_FOLDER = r
        d = "/home/nico/Projects/IBL/github/iblrig/scratch/test_iblrig_data"  # noqa
        _task_settings.IBLRIG_DATA_FOLDER = d
        _task_settings.AUTOMATIC_CALIBRATION = False
        _task_settings.USE_VISUAL_STIMULUS = False

    sph = SessionParamHandler(_task_settings, _user_settings, debug=True,
                              fmake=False)
    # for k in sph.__dict__:
    #     print(f"{k}: {sph.__dict__[k]}")
    self = sph
    print("Done!")
