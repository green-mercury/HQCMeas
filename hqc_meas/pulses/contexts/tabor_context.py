# -*- coding: utf-8 -*-
# =============================================================================
# module : tabor_context.py
# author : Pierre Heidmann and Matthieu Dartiailh and Nathanael Cottet
# license : MIT license
# =============================================================================
"""

"""
from atom.api import Float, observe, set_default
import numpy as np
from .base_context import BaseContext, TIME_CONVERSION


class TABORContext(BaseContext):
    """
    """

    channels = ('Ch1_A', 'Ch1_M1', 'Ch1_M2',
                'Ch2_A', 'Ch2_M1', 'Ch2_M2',
                'Ch3_A', 'Ch3_M1', 'Ch3_M2',
                'Ch4_A', 'Ch4_M1', 'Ch4_M2')

    # Sampling frequency in Hz
    sampling_frequency = Float(1e9)

    time_unit = set_default('mus')

    analogical_channels = set_default(('Ch1_A', 'Ch2_A', 'Ch3_A', 'Ch4_A'))

    logical_channels = set_default(('Ch1_M1', 'Ch2_M1', 'Ch3_M1', 'Ch4_M1',
                                    'Ch1_M2', 'Ch2_M2', 'Ch3_M2', 'Ch4_M2'))

    def compile_sequence(self, pulses, **kwargs):
        """ Transform a sequence of pulse to a dict of waveform.

        Parameters
        ----------
        pulses : list(Pulse)
            List of pulse generated by the compilation of a sequence.

        Returns
        -------
        result : bool
            Boolean indicating whether or not the compilation succeeded.

        to_send or traceback : dict
            Dict of {channel: bytearray} to send to the AWG in case of success
            or the traceback of the issues in case of failure.

        """
        sequence_duration = max([pulse.stop for pulse in pulses])
        # Total length of the sequence to send to the AWG
        if 'sequence_duration' in kwargs:
            if sequence_duration <= kwargs['sequence_duration']:
                sequence_duration = kwargs['sequence_duration']
                if sequence_duration%16 != 0:
                    return False, {'Sequence_duration':
                        'The sequence duration must be a multiple of 16'}
            else:
                return False, {'Sequence_duration':
                               'Not all pulses fit in given duration'}

        # Collect the channels used in the pulses' sequence
        used_channels = set([pulse.channel[:3] for pulse in pulses])

        # Coefficient to convert the start and stop of pulses in second and
        # then in index integer for array
        time_to_index = TIME_CONVERSION[self.time_unit]['s'] * \
            self.sampling_frequency

        # Length of the sequence
        sequence_length = int(round(sequence_duration * time_to_index))

        # create 3 array for each used_channels
        array_analog = {}
        array_M1 = {}
        array_M2 = {}
        for channel in used_channels:
            # numpy array for analog channels int16 init 2**13
            array_analog[channel] = np.ones(sequence_length,
                                            dtype=np.uint16)*(2**13)
            # numpy array for marker1 init False. For AWG M1 = 0 = off
            array_M1[channel] = np.zeros(sequence_length, dtype=np.int8)
            # numpy array for marker2 init False. For AWG M2 = 0 = off
            array_M2[channel] = np.zeros(sequence_length, dtype=np.int8)

        for pulse in pulses:

            waveform = pulse.waveform
            channel = pulse.channel[:3]
            channeltype = pulse.channel[4:]

            start_index = int(round(pulse.start*time_to_index))
            stop_index = start_index + len(waveform)

            if channeltype == 'A' and pulse.kind == 'Analogical':
                array_analog[channel][start_index:stop_index] +=\
                    np.rint(8191*waveform)
            elif channeltype == 'M1' and pulse.kind == 'Logical':
                array_M1[channel][start_index:stop_index] += waveform
            elif channeltype == 'M2' and pulse.kind == 'Logical':
                array_M2[channel][start_index:stop_index] += waveform
            else:
                msg = 'Selected channel does not match kind for pulse {} ({}).'
                return False, {'Kind issue':
                               msg.format(pulse.index,
                                          (pulse.kind, pulse.channel))}

        # Check the overflows
        traceback = {}
        for channel in used_channels:
            analog = array_analog[channel]
            if analog.max() > 16383 or analog.min() < 0:
                mes = 'Analogical values out of range.'
                traceback['{}_A'.format(channel)] = mes

            elif array_M1[channel].max() > 1 or array_M1[channel].min() < 0:
                mes = 'Overflow in marker 1.'
                traceback['{}_M1'.format(channel)] = mes

            elif array_M2[channel].max() > 1 or array_M2[channel].min() < 0:
                mes = 'Overflow in marker 2.'
                traceback['{}_M2'.format(channel)] = mes

        if traceback:
            return False, traceback

        # Invert marked logical channels.
        for i_ch in self.inverted_log_channels:
            ch, m = i_ch.split('_')
            if m == 'M1':
                np.logical_not(array_M1[ch], array_M1[ch])
            else:
                np.logical_not(array_M2[ch], array_M2[ch])

        # Byte arrays to send to the AWG
        to_send = {}
        for channel in used_channels:
            # Convert to sixteen bits integers
            array = array_analog[channel]+\
                array_M1[channel]*(2**14) + array_M2[channel]*(2**15)
            # Creating and filling a byte array for each channel.
            aux = np.empty(2*sequence_length, dtype=np.uint8)
            aux[::2] = array % 2**8
            aux[1::2] = array // 2**8

            to_send[int(channel[-1])] = bytearray(aux)
 #           print((array_analog[channel] + 2**13) % 2**14)

        return True, to_send

    def _get_sampling_time(self):
        """ Getter for the sampling time prop of BaseContext.

        """
        return 1/self.sampling_frequency*TIME_CONVERSION['s'][self.time_unit]

    @observe('sampling_frequency', 'time_unit')
    def _reset_sampling_time(self, change):
        """ Observer resetting the sampling_time property.

        """
        member = self.get_member('sampling_time')
        member.reset(self)

CONTEXTS = {'TaborAWG': TABORContext}
