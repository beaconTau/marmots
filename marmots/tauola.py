"""
This module provides methods to randomly sample the included TAUOLA decay
file for various parameters including shower types, and fractional shower
energies.
"""
import os.path as path

import numpy as np

from poinsseta import ShowerType, data_directory

# the methods we export during an `import *`.
__all__ = ["sample_energy_fraction", "sample_shower_type", "sample_range"]

# and load the decay file on import
decays = np.loadtxt(
    path.join(data_directory, ("tauola_decay.dat")),
    skiprows=1,
    dtype=[
        ("nu_tau", float),
        ("nu_mu", float),
        ("nu_e", float),
        ("hadron", float),
        ("muon", float),
        ("electron", float),
    ],
)

# the number of electromagnetic or hadronic showers
Nem = np.sum(decays["electron"] > 0.0)
Nhad = np.sum(decays["hadron"] > 0.0)

# the total nmuber of EM or hadronic showers in the decay file
Nshowers = np.sum(np.logical_or(decays["electron"] > 0.0, decays["hadron"] > 0.0))

# the sorted fractional shower energies for hadronic and EM showers
Eem = np.sort(decays["electron"][decays["electron"] > 0.0])
Ehad = np.sort(decays["hadron"][decays["hadron"] > 0.0])


def sample_tau_energies(Enu: float, N: int = 1) -> np.ndarray:
    """
    Return `N` randomly sampled tau energies.

    Parameters
    ----------
    Enu: float
       The energy of the tau neutrino (eV).
    N: int
       The number of tau lepton energies to sample.

    Returns
    -------
    Etau: np.ndarray
        `N` randomly sampled tau energies (eV).
    """

    # random sample a set of shower types
    stypes = sample_shower_type(N)

    # and sample some corresponding energy fractions
    Efrac = sample_energy_fraction(stypes)

    # and return the corresponding energy of tau's
    return Enu * Efrac


def sample_energy_fraction(stypes: np.ndarray) -> np.ndarray:
    """
    For every provided shower type in `stypes`, randomly sample a fractional
    shower energy from the loaded TAUOLA decay file.

    See poinsseta/__init__.py for the definition of the ShowerType enum:
        (0 == Hadronic, 1 == Electromagnetic)

    `stypes` is most likely generated by `sample_shower_type`.

    Parameters
    ----------
    stypes: np.ndarray
        An (N,)-length ndarray containing integer
        representations of shower types.

    Returns
    -------
    fraction: np.ndarray
        The fraction of primary energy that is transferred into each shower.
    """

    # generate N uniform samples to sample our CDFs
    u = np.random.uniform(size=stypes.size)

    # create the array to store the energy fractions
    fractions = np.zeros_like(u)

    # the indices that correspond to electromagnetic and hadronic showers
    emshowers = stypes == ShowerType.Electromagnetic
    hadshowers = stypes == ShowerType.Hadronic

    # interpolate into the sorted shower energies for EM
    fractions[emshowers] = np.interp(Nem * u[emshowers], np.arange(Nem), Eem)
    fractions[hadshowers] = np.interp(Nhad * u[hadshowers], np.arange(Nhad), Ehad)

    # and we are done
    return fractions


def sample_shower_type(N: int = 1) -> np.ndarray:
    """
    Randomly sample a shower type from the tauola decay file.

    Parameters
    ----------
    N: int
        The number of random shower types to sample.

    Returns
    -------
    type: np.ndarray
        A np.ndarray instance indicating the shower type.
    """
    # draw a uniform random number
    u = np.random.uniform(0, 1, size=N)

    # and the probability that a shower is electromagnetic
    Pem = Nem / Nshowers

    # create the array to store each shower type
    stypes = np.zeros(N, dtype=int)

    # and fill in the electromagnetic (non-zero)
    stypes[u > Pem] = ShowerType.Electromagnetic

    # and we are done
    return stypes


def sample_range(Etau: np.ndarray) -> np.ndarray:
    """
    Sample a random set of tau decay ranges (in km) given the
    tau energy [in eV].

    If you want to get multiple ranges, provide an array as input i.e.
        sample_range(1e17*np.ones(100))

    This uses a linear approximation that:

        d(E) = (4.9 km)*(Etau / 1e17 eV)

    Parameter
    ---------
    Etau: np.ndarray
        An (N,)-length ndarray of tau energies in eV.

    Returns
    -------
    ranges: np.ndarray
        An (N,)-length ndarray containing random tau ranges in km.
    """
    return np.random.exponential(4.9e-17 * Etau)
