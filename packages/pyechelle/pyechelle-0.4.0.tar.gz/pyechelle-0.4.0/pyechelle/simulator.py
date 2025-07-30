#!/usr/bin/env python
from __future__ import annotations

import argparse
import inspect
import logging
import pathlib
import random
import re
import sys
import time
from dataclasses import field, dataclass
from datetime import datetime, timezone

from pathlib import Path
from typing import Type

import numpy as np
from astropy.io import fits
from joblib import Parallel, delayed
from numba import cuda

import pyechelle
import pyechelle.slit
from pyechelle import sources
from pyechelle.CCD import CCD
from pyechelle.efficiency import Efficiency, CSVEfficiency, SystemEfficiency, Atmosphere
from pyechelle.raytrace_cuda import raytrace_order_cuda
from pyechelle.raytracing import raytrace_order_cpu
from pyechelle.sources import Phoenix, Source
from pyechelle.spectrograph import Spectrograph, ZEMAX
from pyechelle.telescope import Telescope

logger = logging.getLogger("Simulator")
logger.setLevel(level=logging.INFO)

# get list of available spectrograph models
dir_path = (
    Path(__file__).resolve().parent.joinpath("models").joinpath("available_models.txt")
)
with open(dir_path, "r") as am:
    available_models = [line.strip() for line in am.readlines() if line.strip() != ""]

# get list of available sources
available_sources = [
    m[0]
    for m in inspect.getmembers(pyechelle.sources, inspect.isclass)
    if issubclass(m[1], pyechelle.sources.Source) and m[0] != "Source"
]


def str2bool(v):
    """Converts string to boolean"""
    if isinstance(v, bool):
        return v
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean value expected.")


def parse_num_list(string_list: str) -> list:
    """
    Converts a string specifying a range of numbers (e.g. '1-3') into a list of these numbers ([1,2,3])
    Args:
        string_list: string like "[start value]-[end value]"

    Returns:
        List of integers
    """

    m = re.match(r"(\d+)(?:-(\d+))?$", string_list)
    if not m:
        raise argparse.ArgumentTypeError(
            "'"
            + string_list
            + "' is not a range of number. Expected forms like '0-5' or '2'."
        )
    start = m.group(1)
    end = m.group(2) or start
    return list(range(int(start, 10), int(end, 10) + 1))


def export_to_html(
    data,
    filename,
    include_plotlyjs=False,
    width=1000,
    height=300,
    y_range_min=2000,
    y_range_max=3000,
):
    """
    Exports a 2D image into a 'standalone' HTML file. This is used e.g. for some examples in the documentation.
    Args:
        data: 2d numpy array
        filename: output filename
        include_plotlyjs: whether plotlyjs is included in html file or not
        width: width of the plot in pixel
        height: height of the plot in pixel
        y_range_min: minimum y coordinate shown in image
        y_range_max: maximum y coordinate shown in image

    Returns:
        None
    """
    import plotly.express as px

    fig = px.imshow(data, binary_string=True, aspect="equal")

    fig.update_traces(hovertemplate=None, hoverinfo="skip")
    fig.update_layout(
        autosize=True, width=width, height=height, margin=dict(l=0, r=0, b=0, t=0)
    )
    fig.update_yaxes(range=[y_range_min, y_range_max])
    fig.write_html(filename, include_plotlyjs=include_plotlyjs)


def log_elapsed_time(msg: str, t0: float) -> float:
    t1 = time.time()
    logger.info(msg + f" (took {t1 - t0:2f} s )")
    return t1


def write_to_fits(
    c: CCD,
    filename: str | Path,
    overwrite: bool = True,
    append: bool = False,
    dtype: Type | np.dtype = np.uint16,
    metadata: dict = None,
):
    """Saves CCD image to disk

    Args:
        c: CCD object
        filename: filepath
        overwrite: if True, file will be overwritten if existing
        append: if True, CCD data will be added to data in fits file
        dtype: numpy.dtype object defining the data type of the saved FITS file, defaulting to unsigned 16-bit integers
        metadata: dictionary with additional metadata that should be saved to the FITS header

    Returns:
        None
    """
    old_file_data = np.zeros_like(c.data)
    if append:
        if pathlib.Path(filename).is_file():
            old_file_data = fits.getdata(filename)
            assert old_file_data.shape == c.data.shape, (
                f"You tried to append data to {filename}, "
                f"but the fits file contains"
                f"data with a different shape ({old_file_data.shape})."
            )

    hdu = fits.PrimaryHDU(data=np.array(c.data + old_file_data, dtype=dtype))
    # unfortunately, long HIERARCH keywords and long values exclude each other:
    # see
    # https://stackoverflow.com/questions/29950918/astropy-io-fits-hierarch-keywords-dont-work-with-continue-cards-bug-or-feat
    # therefore, we add short meaningless keywords.
    if metadata is not None:
        for i, (key, value) in enumerate(metadata.items()):
            hdu.header.set(f"PYE{i}", f"{key}: {str(value)}")

    hdu_list = fits.HDUList([hdu])
    hdu_list.writeto(filename, overwrite=overwrite or append)


@dataclass
class Simulator:
    """PyEchelle simulator

    Simulator class that contains everything needed to generate spectra.

    Attributes:
        spectrograph (Spectrograph): spectrograph used for simulations
        fibers (list[int]): fiber / list of fibers to be simulated
        orders (list[int]): order / list of diffraction orders to be simulated
        sources (list[Source]): spectral source / list of spectral sources per fiber (same length as fibers)
        atmosphere (list[bool]): whether to include atmospheric transmission per fiber (same length as fibers)
        atmosphere_conditions (list[dict | None]): skycalc arguments for atmospheric conditions (same length as sources)
        rvs (list[float]): radial velocity shifts in [m/s] for sources (same length as fibers)
        telescope (Telescope): Telescope used for simulations (relevant for 'on-sky' sources)
        random_seed (int): random seed for the number generator
        cuda (bool): flag if CUDA is to be used (default: True if available)
        max_cpu (int): number of CPUs used for simulation (if -1, max_cpu is number of available cores)
        exp_time (float): exposure time to be simulated
        output (Path): path to output fits file
        append (bool): flag if simulated counts should be appended to existing image
        overwrite (bool): flat if output file should be overwritten if existing
        global_efficiency (Efficiency): overall efficiency curve to be considered
         (on top of spectrograph efficiency curve and potentially atmosphere)

    """

    spectrograph: Spectrograph
    fibers: list[int] | None = field(init=False, default=None)
    orders: list[int] | None = field(init=False, default=None)
    ccd: int = field(init=False, default=None)
    sources: list[Source] = field(init=False, default=None)
    atmosphere: list[bool] = field(init=False, default=None)
    atmosphere_conditions: list[dict | None] = field(init=False, default=None)
    rvs: list[float] = field(init=False, default=None)
    telescope: Telescope = field(init=False, default=None)
    random_seed: int = field(init=False, default=-1)
    cuda: bool = field(init=False, default=cuda.is_available())
    max_cpu: int = field(init=False, default=1)
    exp_time: float = field(init=False, default=1.0)
    output: Path = field(init=False, default=None)
    append: bool = field(init=False, default=False)
    overwrite: bool = field(init=False, default=False)
    bias: int = field(init=False, default=0)
    read_noise: float = field(init=False, default=0.0)
    global_efficiency: Efficiency = field(init=False, default=None)

    def __post_init__(self):
        # set default CCD to first CCD in spectrograph
        self.ccd = list(self.spectrograph.get_ccd().keys())[0]

    def set_sources(self, source: Source | list[Source]):
        assert self.fibers is not None, (
            "Please set first the fields that you want to simulate."
        )
        self.sources = (
            source if isinstance(source, list) else [source] * len(self.fibers)
        )
        assert len(self.fibers) == len(self.sources), (
            "Number of sources needs to match the number of fields/fibers (or be 1)"
        )

    def set_atmospheres(
        self, atmosphere: bool | list[bool], sky_calc_kwargs: dict | list[dict] = None
    ):
        assert self.sources is not None, (
            "Please set first the sources that you want to simulate."
        )
        self.atmosphere = (
            [atmosphere] * len(self.sources)
            if isinstance(atmosphere, bool)
            else atmosphere
        )
        self.atmosphere_conditions = (
            [sky_calc_kwargs] * len(self.sources)
            if (isinstance(sky_calc_kwargs, dict) or sky_calc_kwargs is None)
            else sky_calc_kwargs
        )
        assert len(self.atmosphere) == len(self.sources), (
            "Number of atmosphere flags needs to match the number of sources (or be 1)"
        )
        assert len(self.atmosphere_conditions) == len(self.sources), (
            "Number of atmosphere condition arguments needs to match the number of sources (or be 1)"
        )

    def set_radial_velocities(self, rvs: float | list[float]):
        assert self.sources is not None, (
            "Please set first the sources that you want to simulate."
        )
        self.rvs = [rvs] * len(self.sources) if isinstance(rvs, float) else rvs
        assert len(self.rvs) == len(self.sources), (
            "Number of radial velocity values needs to match the number of sources (or be 1)"
        )

    def set_telescope(self, telescope: Telescope | list[Telescope]):
        self.telescope = telescope

    def set_ccd(self, ccd: int):
        self.ccd = ccd
        assert self.ccd in self.spectrograph.get_ccd().keys(), (
            f"You requested simulation of CCD {ccd}, which is not available."
        )

    def set_efficiency(self, eff: Efficiency):
        assert isinstance(eff, Efficiency)
        self.global_efficiency = eff

    def set_bias(self, bias_value: int = 0):
        self.bias = bias_value

    def set_read_noise(self, read_noise: float = 0.0):
        if read_noise > 0.0:
            assert self.bias > 0, (
                "read noise was specified, but no bias value is set, yet. "
                "Do so before setting the read noise."
            )
        self.read_noise = read_noise

    def set_fibers(self, fiber: int | list[int] | None):
        assert self.ccd is not None, "Please set CCD index first."
        if fiber is None:
            self.fibers = self.spectrograph.get_fibers(self.ccd)
        else:
            self.fibers = [fiber] if isinstance(fiber, int) else fiber
        for f in self.fibers:
            assert f in self.spectrograph.get_fibers(self.ccd), (
                f"You requested simulation of fiber {f}, which is "
                f"not available for ccd with index {self.ccd}"
            )

    def set_cuda(self, activate: bool = True, seed: int = -1):
        if activate:
            assert cuda.is_available(), "CUDA is not available on this system."
        self.cuda = activate
        self.random_seed = seed

    def _get_valid_orders(self, fiber: int):
        valid_orders = []

        requested_orders = (
            self.spectrograph.get_orders(fiber, self.ccd)
            if self.orders is None
            else self.orders
        )
        for o in requested_orders:
            if o in self.spectrograph.get_orders(fiber, self.ccd):
                valid_orders.append(o)
            else:
                logger.warning(
                    f"Order {o} is requested, but it is not in the Spectrograph model."
                )
        return valid_orders

    def _get_slit_function(self, fiber: int):
        try:
            if self.cuda:
                slit_fun = getattr(
                    pyechelle.slit,
                    f"cuda_{self.spectrograph.get_field_shape(fiber, self.ccd)}",
                )
            else:
                slit_fun = getattr(
                    pyechelle.slit, self.spectrograph.get_field_shape(fiber, self.ccd)
                )
        except AttributeError:
            raise NotImplementedError(
                f"Field shape {self.spectrograph.get_field_shape(fiber, self.ccd)} is not implemented."
            )
        return slit_fun

    def _simulate_multi_cpu(
        self, orders, fiber, ccd_index, slit_fun, s, rv, integration_time, c, efficiency
    ):
        simulated_photons = []
        t0 = time.time()
        results = Parallel(n_jobs=min(self.max_cpu, len(orders)), backend="threading")(
            delayed(raytrace_order_cpu)(
                o,
                self.spectrograph,
                s,
                slit_fun,
                self.telescope,
                rv,
                integration_time,
                c,
                fiber,
                ccd_index,
                efficiency,
                self.max_cpu,
            )
            for o in np.sort(orders)
        )
        logger.info("Add up orders...")
        ccd_results = [r[0] for r in results]
        simulated_photons.extend([r[1] for r in results])
        c.data = np.sum(ccd_results, axis=0)
        log_elapsed_time("done.", t0)
        return simulated_photons

    def _simulate_single_cpu(
        self, orders, fiber, ccd_index, s, slit_fun, rv, integration_time, c, efficiency
    ):
        simulated_photons = []
        for o in np.sort(orders):
            n_phot = raytrace_order_cpu(
                o,
                self.spectrograph,
                s,
                slit_fun,
                self.telescope,
                rv,
                integration_time,
                c,
                fiber,
                ccd_index,
                efficiency,
                1,
            )
            simulated_photons.append(n_phot)
        return simulated_photons

    def _simulate_cuda(
        self,
        orders,
        slit_fun,
        rv,
        integration_time,
        dccd,
        efficiency,
        s,
        c,
        fiber,
        ccd_index,
    ):
        simulated_photons = []
        for o in np.sort(orders):
            if self.random_seed < 0:
                ii16 = np.iinfo(np.uint32)
                seed = random.randint(1, ii16.max - 1)
            else:
                seed = self.random_seed
            nphot = raytrace_order_cuda(
                o,
                self.spectrograph,
                s,
                self.telescope,
                rv,
                integration_time,
                dccd,
                float(c.pixelsize),
                fiber,
                ccd_index,
                efficiency,
                seed=seed,
            )
            simulated_photons.append(nphot)
        return simulated_photons

    def validate(self):
        assert self.fibers is not None, "Please set fibers for simulation"
        assert self.ccd is not None, "Please set ccd index/indices for simulation"
        assert self.output is not None, "Please set output path for simulation"
        if self.atmosphere is None:
            logger.info(
                "It was not explicitly specified whether to consider atmospheric transmission. "
                "It is set to False"
            )
            self.atmosphere = [False] * len(self.sources)

        if self.atmosphere_conditions is None:
            if self.atmosphere:
                logger.info(
                    "Atmospheric conditions were not specified. The default atmospheric conditions apply. "
                    "(e.g. airmass 1)"
                )
            self.atmosphere_conditions = [None] * len(self.sources)

        if self.rvs is None:
            logger.info(
                "Radial velocities are not specified explicitly. They are therefore set to 0.0"
            )
            self.rvs = [0.0] * len(self.sources)
        if self.output.is_file():
            assert self.overwrite or self.append, (
                f"You specified to save the simulation at {self.output}, "
                f"but this file exists. If you want to overwrite, "
                f"please set the overwrite flag. Or in case you want to append to "
                f"the file: please set the append flag"
            )
        return True

    def run(self) -> int:
        self.validate()
        c = self.spectrograph.get_ccd(self.ccd)
        total_simulated_photons = []
        t1 = time.time()
        # copy empty array to CUDA device
        if self.cuda:
            dccd = cuda.to_device(np.zeros_like(c.data, dtype=np.uint32))
        metadata = {
            "pyechelle.version": pyechelle.__version__,
            "pyechelle.spectrograph": self.spectrograph.name,
            "pyechelle.cuda": self.cuda,
            "pyechelle.seed": self.random_seed,
            "pyechelle.EXPTIME": self.exp_time,
            "pyechelle.CCD": self.ccd,
            "pyechelle.bias": self.bias,
            "pyechelle.readnoise": self.read_noise,
            "pyechelle.sim_start_utc": datetime.now(timezone.utc).isoformat(),
        }

        for f, s, atm, atm_cond, rv in zip(
            self.fibers,
            self.sources,
            self.atmosphere,
            self.atmosphere_conditions,
            self.rvs,
        ):
            orders = (
                self.orders if self.orders is not None else self._get_valid_orders(f)
            )
            slit_fun = self._get_slit_function(f)
            metadata.update(
                {
                    f"pyechelle.fiber{f}.orders": orders,
                    f"pyechelle.fiber{f}.source": str(s),
                    f"pyechelle.fiber{f}.rv": rv,
                    f"pyechelle.fiber{f}.atmosphere": atm,
                }
            )
            # TODO: add also atmospheric keywords to fits header

            e = SystemEfficiency(
                [
                    self.spectrograph.get_efficiency(f, self.ccd),
                    self.global_efficiency,
                    Atmosphere("Atmosphere", sky_calc_kwargs=atm_cond) if atm else None,
                ],
                "Combined Efficiency",
            )

            if not self.cuda:
                if self.max_cpu > 1:
                    total_simulated_photons.extend(
                        self._simulate_multi_cpu(
                            orders, f, self.ccd, slit_fun, s, rv, self.exp_time, c, e
                        )
                    )
                else:
                    total_simulated_photons.extend(
                        self._simulate_single_cpu(
                            orders, f, self.ccd, s, slit_fun, rv, self.exp_time, c, e
                        )
                    )
            else:
                total_simulated_photons.extend(
                    self._simulate_cuda(
                        orders, slit_fun, rv, self.exp_time, dccd, e, s, c, f, self.ccd
                    )
                )

        if self.cuda:
            dccd.copy_to_host(c.data)
        logger.info("Finish up simulation and save...")
        c.clip()

        # add bias / global ccd effects
        if self.bias > 0:
            c.add_bias(self.bias)
        if self.read_noise > 0.0:
            c.add_readnoise(self.read_noise)
        t2 = time.time()
        metadata.update(
            {"pyechelle.sim_end_utc": datetime.now(timezone.utc).isoformat()}
        )
        write_to_fits(
            c,
            self.output,
            self.overwrite,
            self.append,
            dtype=np.uint16,
            metadata=metadata,
        )
        logger.info(f"Total time for simulation: {t2 - t1:.3f}s.")
        logger.info(f"Total simulated photons: {sum(total_simulated_photons)}")
        return sum(total_simulated_photons)

    def set_exposure_time(self, exp_time: float = 1):
        self.exp_time = exp_time

    def set_output(
        self,
        path: str | Path = Path().cwd().joinpath("test.fits"),
        append: bool = False,
        overwrite: bool = False,
    ):
        self.output = path if isinstance(path, Path) else Path(path)
        self.append = append
        self.overwrite = overwrite
        if append and not self.output.is_file():
            logger.warning(
                f"You specified that the simulation should be appended to {self.output}, but there is no "
                f"such file. It will be created."
            )

    def set_orders(self, orders: int | list[int] | None):
        if orders is None:
            self.orders = None
        else:
            self.orders = [orders] if isinstance(orders, int) else orders

        if self.orders is not None:
            for f in self.fibers:
                valid_orders = self._get_valid_orders(f)
                for o in self.orders:
                    assert o in valid_orders, (
                        f"You requested to simulate order {o}, but this order is not available"
                        f"on CCD {self.ccd} and fiber/field {f}"
                    )


def generate_parser():
    parser = argparse.ArgumentParser(
        description="PyEchelle Simulator",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-s",
        "--spectrograph",
        choices=available_models,
        type=str,
        default="MaroonX",
        required=True,
        help="Filename of spectrograph model. Model file needs to be located in models/ folder. ",
    )
    parser.add_argument(
        "--ccd",
        type=int,
        default=1,
        required=False,
        help="Sets CCD index to be simulated.",
    )
    parser.add_argument(
        "-t",
        "--integration_time",
        type=float,
        default=1.0,
        required=False,
        help="Integration time for the simulation in seconds [s].",
    )
    parser.add_argument(
        "--fiber",
        type=parse_num_list,
        required=False,
        help="Fiber/Field number(s) to be simulated. Can either be a single integer, or an integer"
        "range (e.g. 1-3) ",
    )
    parser.add_argument(
        "--no_blaze",
        action="store_true",
        help="If set, the blaze efficiency per order will be ignored.",
    )
    parser.add_argument(
        "--no_efficiency",
        action="store_true",
        help="If set, all instrument/atmosphere efficiencies will be ignored.",
    )

    parser.add_argument(
        "--cuda",
        action="store_true",
        default=False,  # cuda.is_available(),
        help="If set, CUDA will be used for raytracing. Note: the max_cpu flag is then obsolete. Default: "
        "True if available.",
    )

    parser.add_argument(
        "--cuda_seed",
        type=int,
        default=-1,
        help="Random seed for generating CUDA RNG states. If <0, then the seed is chosen randomly.",
    )

    parser.add_argument(
        "--max_cpu",
        type=int,
        default=1,
        help="Maximum number of CPU cores used. Note: The parallelization happens 'per order'."
        " Order-wise images are added up. This requires a large amount of memory at the moment."
        "If planning on simulating multiple images, consider using only 1 CPU per simulation "
        "and starting multiple simulations instead.",
    )

    atmosphere_group = parser.add_argument_group("Atmosphere")
    atmosphere_group.add_argument(
        "--atmosphere",
        nargs="+",
        required=False,
        help="Add telluric lines to spectrum. For adding tellurics to all spectra just use"
        "--atmosphere Y, for specifying per fiber user e.g. --atmosphere Y N Y",
        type=lambda x: str2bool(x),
        default=[False],
    )

    atmosphere_group.add_argument(
        "--airmass",
        default=1.0,
        type=float,
        required=False,
        help="airmass for atmospheric model",
    )

    telescope_group = parser.add_argument_group("Telescope settings")
    telescope_group.add_argument(
        "--d_primary",
        type=float,
        required=False,
        default=1.0,
        help="Diameter of the primary telescope mirror.",
    )
    telescope_group.add_argument(
        "--d_secondary",
        type=float,
        required=False,
        default=0,
        help="Diameter of the secondary telescope mirror.",
    )

    parser.add_argument(
        "--orders",
        type=parse_num_list,
        nargs="+",
        required=False,
        help="Echelle/Grating order numbers to simulate... "
        "if not specified, all orders of the spectrograph are simulated."
        "Can either be a single integer, or a range (e.g. 80-90)",
    )

    parser.add_argument(
        "--sources",
        nargs="+",
        choices=available_sources,
        required=True,
        help='Spectral source for the simulation. Can either be a single string, e.g. "Etalon",'
        ' or a comma separated list of sources (e.g. "Etalon, Constant, Etalon") which length must'
        "match the number of fields/fibers.",
    )
    parser.add_argument(
        "--rv",
        nargs="+",
        type=float,
        required=False,
        default=[0.0],
        help="radial velocity shift of source",
    )
    const_source_group = parser.add_argument_group("ConstantFlux source")
    const_source_group.add_argument(
        "--constantflux_flux",
        type=float,
        default=0.0001,
        required=False,
        help="Flux in microWatts / nanometer for constant flux spectral source",
    )

    const_photons_group = parser.add_argument_group("ConstantPhotonFlux source")
    const_photons_group.add_argument(
        "--constantphotons_flux",
        type=float,
        default=1000,
        required=False,
        help="Flux in photons/s for constant photon flux spectral source",
    )

    arclamps_group = parser.add_argument_group("Arc Lamps")
    arclamps_group.add_argument(
        "--scale",
        default=10.0,
        required=False,
        help="Intensity scale of gas lines (e.g. Ag or Ne) vs metal (Th)",
    )

    csv_group = parser.add_argument_group("CSV")
    csv_group.add_argument(
        "--csv_filepath",
        type=argparse.FileType("r"),
        required=False,
        help="Path to .csv file that contains two columns: wavelength and flux. The flux is expected"
        "to be in ergs/s/cm^2/cm (like Phoenix spectra) or photons (then set it via "
        "--csv_flux_in_photons). The wavelength unit is expected to "
        "be angstroms, but it can be changed via --csv_wavelength_unit",
    )
    csv_group.add_argument(
        "--csv_wavelength_unit",
        default="AA",
        type=str,
        help="Unit of the wavelength column in the .csv file. Unit names are taken from astropy.units",
    )
    csv_group.add_argument(
        "--csv_list_like",
        type=bool,
        default=False,
        help="Set to True if spectrum is discrete.",
    )
    csv_group.add_argument(
        "--csv_flux_in_photons",
        type=bool,
        default=False,
        help="Set to True if flux is given in Photons/s rather than ergs",
    )
    csv_group.add_argument(
        "--csv_stellar_target",
        type=bool,
        default=True,
        help="Set to True if Source is a stellar target.",
    )
    csv_group.add_argument(
        "--csv_magnitude",
        type=float,
        default=10.0,
        required=False,
        help="If stellar target, the magnitude value i considered as V magnitude of the object and "
        "the flux is scaled accordingly. Ignored if --flux_in_photons is true.",
    )
    csv_group.add_argument(
        "--csv_delimiter",
        type=str,
        required=False,
        default=",",
        help="Delimiter of the CSV file",
    )

    csv_eff_group = parser.add_argument_group("CSVEfficiency")
    csv_eff_group.add_argument(
        "--eff_csv_filepath",
        type=argparse.FileType("r"),
        required=False,
        help="Path to .csv file that contains two columns: wavelength and efficiency."
        "The wavelength is expected to be in microns, "
        "the efficiency is a real number in [0,1]."
        "PyEchelle will interpolate the given values "
        "for intermediate wavelength positions.",
    )
    csv_eff_group.add_argument(
        "--eff_csv_delimiter",
        type=str,
        required=False,
        default=",",
        help="Delimiter of the CSV file",
    )

    phoenix_group = parser.add_argument_group("Phoenix")
    phoenix_group.add_argument(
        "--phoenix_t_eff",
        default=3600,
        choices=Phoenix.valid_t,
        type=int,
        required=False,
        help="Effective temperature in Kelvins [K].",
    )
    phoenix_group.add_argument(
        "--phoenix_log_g",
        default=5.0,
        choices=Phoenix.valid_g,
        type=float,
        required=False,
        help="Surface gravity log g.",
    )
    phoenix_group.add_argument(
        "--phoenix_z",
        choices=Phoenix.valid_z,
        type=float,
        required=False,
        default=0.0,
        help="Overall metallicity.",
    )
    phoenix_group.add_argument(
        "--phoenix_alpha",
        choices=Phoenix.valid_a,
        type=float,
        required=False,
        default=0.0,
        help="Alpha element abundance.",
    )
    phoenix_group.add_argument(
        "--phoenix_magnitude",
        default=10.0,
        required=False,
        type=float,
        help="V Magnitude of stellar object.",
    )

    etalon_group = parser.add_argument_group("Etalon")
    etalon_group.add_argument(
        "--etalon_d",
        type=float,
        default=5.0,
        required=False,
        help="Mirror distance of Fabry Perot etalon in [mm].",
    )
    etalon_group.add_argument(
        "--etalon_n",
        type=float,
        default=1.0,
        required=False,
        help="Refractive index of medium between etalon mirrors.",
    )
    etalon_group.add_argument(
        "--etalon_theta",
        type=float,
        default=0.0,
        required=False,
        help="angle of incidence of light in radians.",
    )
    etalon_group.add_argument(
        "--etalon_n_photons",
        default=1000,
        required=False,
        help="Number of photons per seconds per peak of the etalon spectrum.",
    )

    ccd_group = parser.add_argument_group("CCD")
    ccd_group.add_argument("--bias", type=int, required=False, default=0)
    ccd_group.add_argument("--read_noise", type=float, required=False, default=0.0)

    parser.add_argument(
        "--show",
        default=False,
        action="store_true",
        help="If set, the simulated frame will be shown in a matplotlib imshow frame at the end.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=lambda p: Path(p).absolute(),
        required=False,
        default=Path(__file__).absolute().parent / "test.fits",
        help="A .fits file where the simulation is saved.",
    )
    parser.add_argument(
        "--overwrite",
        default=False,
        action="store_true",
        help="If set, the output file will be overwritten if it exists already.",
    )
    parser.add_argument(
        "--append",
        default=False,
        action="store_true",
        help="If set, the simulated photons will be added to the output file rather than overwriting "
        "the content of the output file. If the output file does not exist yet, "
        "it will be created.This flag can be used to do more complex multi-fiber simulations as a"
        " sequential manner of simpler simulations.",
    )

    parser.add_argument(
        "--html_export",
        type=str,
        default="",
        help="If given, the spectrum will be exported to an interactive image using plotly. It's not a"
        "standalone html file, but requires plotly.js to be loaded.",
    )
    return parser


def main(args=None):
    if not args:
        args = sys.argv[1:]
    parser = generate_parser()
    args = parser.parse_args(args)
    t1 = time.time()
    sim = Simulator(ZEMAX(args.spectrograph))
    sim.set_ccd(args.ccd)

    # generate flat list for all fields to simulate
    if args.fiber is not None:
        if any(isinstance(el, list) for el in args.fiber):
            fibers = [item for sublist in args.fiber for item in sublist]
        else:
            fibers = args.fiber
    else:
        fibers = sim.spectrograph.get_fibers(args.ccd)
    sim.set_fibers(fibers)

    if args.orders is not None:
        if any(isinstance(el, list) for el in args.orders):
            requested_orders = [item for sublist in args.orders for item in sublist]
        else:
            requested_orders = args.orders
        sim.set_orders(requested_orders)
    # generate flat list of all sources to simulate
    source_names = args.sources
    if len(source_names) == 1:
        source_names = [source_names[0]] * len(
            fibers
        )  # generate list of same length as 'fields' if only one source given

    source_kwargs = []
    # extract kwords specific to selected source
    for s in source_names:
        source_args = [ss for ss in vars(args) if ss.startswith(s.lower())]
        # create dict consisting of kword arguments and values specific to selected source
        source_kwargs.append(
            dict(
                zip(
                    [ss.replace(f"{s.lower()}_", "") for ss in source_args],
                    [getattr(args, ss) for ss in source_args],
                )
            )
        )

    sim.set_sources(
        [
            getattr(sources, source)(
                **s_args, telescope=Telescope(args.d_primary, args.d_secondary)
            )
            if "telescope" in inspect.signature(getattr(sources, source)).parameters
            else getattr(sources, source)(**s_args)
            for source, s_args in zip(source_names, source_kwargs)
        ]
    )

    if args.eff_csv_filepath:
        sim.set_efficiency(
            CSVEfficiency("global", args.eff_csv_filepath, args.eff_csv_delimiter)
        )
    # generate flat list of whether atmosphere is added
    sim.set_atmospheres(
        args.atmosphere[0] if len(args.atmosphere) == 1 else args.atmosphere
    )
    sim.set_radial_velocities(args.rv[0] if len(args.rv) == 1 else args.rv)
    sim.set_cuda(args.cuda, args.cuda_seed)
    sim.set_exposure_time(args.integration_time)
    sim.set_telescope(Telescope(args.d_primary, args.d_secondary))
    sim.set_output(args.output, args.append, args.overwrite)
    sim.set_bias(args.bias)
    sim.set_read_noise(args.read_noise)
    nphot = sim.run()
    t2 = time.time()
    print(f"Simulation took {t2 - t1:.3f} s")
    return nphot


if __name__ == "__main__":
    main()
