import numpy as np
import astropy.units as u
from lalsimulation.gwsignal.core.waveform import (
    CompactBinaryCoalescenceGenerator,
    GenerateTDWaveform,
)
from lalsimulation.gwsignal.core.waveform import LALCompactBinaryCoalescenceGenerator as _LALCompactBinaryCoalescenceGenerator
import lal
import lalsimulation as lalsim
from lalsimulation.gwsignal.core.waveform_conditioning import (
    check_pow_of_2,
)
from . import custom_conditioning as cond
from .custom_conditioning import fix_ref_frequency
from .waveform_utils import extract_some_waveform_parameters

# Default values
extra_time_fraction = 0.1  # fraction of waveform duration to add as extra time for tapering
extra_cycles = 3.0  # more extra time measured in cycles at the starting frequency

# Hotfix
from lalsimulation.gwsignal.core import utils as ut
from lalsimulation.gwsignal.core import parameter_conventions as pc
class LALCompactBinaryCoalescenceGenerator(_LALCompactBinaryCoalescenceGenerator):
    def parameter_check(self, units_sys='S.I.', extra_parameters=dict(), **parameters):
        """
        Perform checks on the various parameters and populate the different parameters not passed
        in the kwargs required for generating waveforms.

        Parameters
        ----------

            Python dictionary of parameters required for waveform generation
            of the form specified in `parameter_conventions.py`.

        Returns
        -------

            Populate self.waveform_dict with python dictionary and self.lal_dict with LALSuite dictionary structure.
        """
        default_dict = pc.default_dict.copy()
        # Need to add this line to take care of the extra parameters passed to ExternalPython LAL Generator
        ExternalPythonParameters=['object', 'module']

        for key, value in parameters.items():
            if key in ExternalPythonParameters:
                pass
            else:
                default_dict[key] = value

        if not 'deltaF' in default_dict:
            default_dict['deltaF'] = 1./16.*u.Hz
        if not 'deltaT' in default_dict:
            default_dict['deltaT'] = 1./512.*u.s
        if not 'f_max' in default_dict:
            default_dict['f_max'] = (0.5/default_dict['deltaT'].value)*u.Hz

        # Add units if indicated
        if units_sys is not None:
            self.waveform_dict = ut.add_params_units(default_dict, units_sys, generic_param_dict=extra_parameters)
        #This is a mandatory check that units are correctly used
        # Hotfix: however bypass this check for parameters starting with "PhenomX"
        _dict_to_check = default_dict.copy()
        for key in default_dict.keys():
            if "PhenomX" in key:
                del _dict_to_check[key]
        ut.check_dict_parameters(_dict_to_check, generic_param_dict=extra_parameters)

        self.lal_dict  = ut.to_lal_dict(default_dict)
        return default_dict


class EchoesWaveformGenerator(CompactBinaryCoalescenceGenerator):
    """
    Generator parent class for echoes waveform models implemented in this package for gwsignal

      - IMREPhenomAbediGenerator for IMREPhenomAbedi,
      - IMREPhenomBHPGenerator for IMREPhenomBHP
    
    """
    def __init__(
        self,
        EchoesIMRApproximant="IMRPhenomTPHM",
    ):
        """
        Initialize a EchoesWaveformGenerator object

        Parameters
        ----------
        EchoesIMRApproximant : str
            The approximant to use for the base IMR waveform

        Returns
        -------
        EchoesWaveformGenerator
            The EchoesWaveformGenerator instance

        """
        super().__init__()
        self.EchoesIMRApproximant = EchoesIMRApproximant
        # Initialize the base IMR wfm generator
        self.base_wfm_generator = LALCompactBinaryCoalescenceGenerator(self.EchoesIMRApproximant)

    def partition_parameters(self, **parameters):
        """
        Partition the parameters into base and echo parameters

        Parameters
        ----------
        parameters : dict
            The parameters for the waveform model
        
        Returns
        -------
        dict, dict
            The base and echo parameters

        """
        base_parameters = {k:v for k,v in parameters.items() if k not in list(self.metadata["extra_parameters"].keys())}
        # Or we can take a substraction, but whatever
        echo_parameters = {k:v for k,v in parameters.items() if k in list(self.metadata["extra_parameters"].keys())}

        return base_parameters, echo_parameters

    def generate_cbc_td_waveform(self, **parameters):
        """
        Generate the base IMR waveform in the time domain. 
        Note that we do not do conditioning here as we will add echoes to this waveform later on

        Parameters
        ----------
        parameters : dict
            The parameters for the waveform model
        
        Returns
        -------
        TimeSeries, TimeSeries
            The plus and cross polarizations of the base IMR waveform in the time domain

        """
        base_parameters, echo_parameters = self.partition_parameters(**parameters)

        # Turn OFF conditioning
        base_parameters["condition"] = 0 # OFF
        # Generate the base IMR waveform in time domain
        hp_IMR, hc_IMR = GenerateTDWaveform(
            base_parameters,
            self.base_wfm_generator,
        )

        return hp_IMR, hc_IMR

    def generate_td_waveform(self, **parameter_dict):
        """
        Generate the full waveform (IMR + echoes) in the time domain. 
        This function is called by the parent class to generate the waveform

        Parameters
        ----------
        parameter_dict : dict
            The parameters for the waveform model
        
        Returns
        -------
        TimeSeries, TimeSeries
            The plus and cross polarizations of the full waveform in the time domain

        """
        # This is identical to the one in gwsignal
        # https://git.ligo.org/lscsoft/lalsuite/-/blob/master/lalsimulation/
        # python/lalsimulation/gwsignal/core/waveform_conditioning.py?ref_type=heads#L34

        # Get some of the required parameters and get their values (so as not to have issues with units and LAL)
        f_min, f_ref, s1z, s2z, m1, m2 = extract_some_waveform_parameters(parameter_dict)

        # Fix reference frequency to fmin/ case by case for Python generators. It is set to zero for lalsim generators as LALSim has its
        # own checks.
        if np.isclose(f_ref, 0):
            f_ref = fix_ref_frequency(parameter_dict, self)


        # If the given f_min is higher than the 22-frequency corresponding to
        # the furthest possible r_isco, set fmin to that value.
        # This is achieved when r = 9M for a test mass in retrograde orbit with a Kerr BH.
        fisco_max = 1.0 / (np.power(9.0, 1.5) * np.pi * (m1 + m2) * lal.MTSUN_SI / lal.MSUN_SI)
        if (f_min > fisco_max):
            f_min = fisco_max


        # Upper chrip time bound
        tchirp = lalsim.SimInspiralChirpTimeBound(f_min, m1, m2, s1z, s2z)

        # Upper bound on the final black hole spin
        s = lalsim.SimInspiralFinalBlackHoleSpinBound(s1z, s2z)

        # Upper bound on the final plunge, merger, and ringdown time
        tmerge = lalsim.SimInspiralMergeTimeBound(m1, m2) + lalsim.SimInspiralRingdownTimeBound(m1 + m2, s)

        # extra time to include for all waveforms to take care of situations
        # where the frequency is close to merger (and is sweeping rapidly):
        # this is a few cycles at the low frequency
        textra = extra_cycles / f_min

        # For conditioning, start waveform at a lower frequency than f_min and then apply tapers between new low freq and f_min.
        fstart = lalsim.SimInspiralChirpStartFrequencyBound((1.0 + extra_time_fraction) * tchirp + tmerge + textra, m1, m2)

        # generate the waveform in the time domain starting at fstart. Add astropy units
        new_parameters = parameter_dict.copy()
        new_parameters['f22_ref'] = f_ref*parameter_dict['f22_start'].unit
        new_parameters['f22_start'] = fstart*parameter_dict['f22_start'].unit


        # Generate the new waveform
        new_parameters['condition']=0
        hp, hc = self._generate_td_waveform(**new_parameters)

        times = hp.times
        dt = hp.dt.value
        # Condition the time domain waveform by tapering in the extra time at the beginning
        # And perform the high-pass filtering
        hp, hc = cond.time_array_condition_stage1(hp, hc, dt, extra_time_fraction * tchirp + textra, parameter_dict['f22_start'].value)

        # The 22-frequency when a test particle is at r = 6M
        f_at_6M = 1.0 / (np.power(6.0, 1.5) * np.pi * (m1 + m2) * lal.MTSUN_SI / lal.MSUN_SI)
        hp, hc = cond.time_array_condition_stage2(hp, hc, dt, f_min, f_at_6M)

        return hp, hc

    def generate_fd_waveform(self, **parameter_dict):
        """
        Generate the full waveform (IMR + echoes) in the frequency domain.
        This function is called by the parent class to generate

        Parameters
        ----------
        parameter_dict : dict
            The parameters for the waveform model
        
        Returns
        -------
        FrequencySeries, FrequencySeries
            The plus and cross polarizations of the full waveform in the frequency domain

        """
        # This is identical to the one in gwsignal
        # https://git.ligo.org/lscsoft/lalsuite/-/blob/master/lalsimulation/
        # python/lalsimulation/gwsignal/core/waveform_conditioning.py?ref_type=heads#L376

        df    = parameter_dict['deltaF'].value
        f_max = parameter_dict['f_max'].value
        f_min, f_ref, s1z, s2z, m1, m2 = extract_some_waveform_parameters(parameter_dict)

        # Fix reference frequency to fmin/ case by case for Python generators. It is set to zero for lalsim generators as LALSim has its
        # own checks.
        if np.isclose(f_ref, 0):
            f_ref = fix_ref_frequency(parameter_dict, self)

        # Apply condition that f_max rounds to the next power-of-two multiple of deltaF.
        # Round f_max / deltaF to next power of two.
        # Set f_max to the new Nyquist frequency.
        # The length of the chirp signal is then 2 * f_nyquist / deltaF.
        # The time spacing is 1 / (2 * f_nyquist)
        f_nyquist = f_max

        # Check if n is power of 2
        if df!=0:
            n = np.round(f_max/df)
            truth, exponent = check_pow_of_2(n)
            if not truth:
                f_nyquist = 2**(exponent)*df

        deltaT = 0.5/f_nyquist

        # generate the waveform in the time domain starting at fstart. Add astropy units
        new_parameters = parameter_dict.copy()
        new_parameters['f22_ref'] = f_ref*u.Hz
        new_parameters['deltaT'] = deltaT*u.s

        # Generate the new waveform
        new_parameters['condition']=1
        hp, hc = self.generate_td_waveform(**new_parameters)

        if df==0:
            chirplen = len(hp)
            tt, chirplen_exp = check_pow_of_2(chirplen)
            chirplen = 2**(chirplen_exp)
            df = 1./(chirplen*hp.dt)
        else:
            chirplen=2*f_nyquist/df


        hp = cond.resize_gwpy_timeseries(hp, len(hp)-chirplen,chirplen)
        hc = cond.resize_gwpy_timeseries(hc,len(hc)-chirplen,chirplen)

        hpf = hp.fft()
        hcf = hc.fft()

        # NOTE This is a known issue in gwpy
        # See bug report here: https://github.com/gwpy/gwpy/issues/1739
        hpf.epoch = hp.t0
        hcf.epoch = hc.t0

        # Normalize to match lalsuite
        hpf = hpf/(2*hpf.df)
        hcf = hcf/(2*hpf.df)
        return hpf, hcf