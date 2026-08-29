# DASCore, xdas, DASPy, DAS4Whales, and Lightguide: a scientist-facing comparison

## Scope and method

This report compares released software, not unreleased default-branch features. The feature baselines are the latest published releases available on 29 August 2026: [DASCore 0.1.21](https://github.com/DASDAE/dascore/releases/tag/v0.1.21) (21 August 2026), [xdas 0.2.8](https://github.com/xdas-dev/xdas/releases/tag/0.2.8) (31 July 2026), [DASPy 1.2.6](https://github.com/HMZ-03/DASPy/releases/tag/v1.2.6) (26 June 2026), [DAS4Whales 0.2.2](https://github.com/DAS4Whales/DAS4Whales/releases/tag/0.2.2) (6 July 2026), and [Lightguide 0.4.0](https://github.com/pyrocko/lightguide/releases/tag/v0.4.0) (14 April 2023). Default branches were consulted only for maintenance signals and are identified as such.

“DasPi” is interpreted as **DASPy**, whose distribution is named `daspy-toolbox`. Searches found no DAS/DFOS project named DasPi; the similarly named [DaSPi](https://pypi.org/project/DaSPi/) is an unrelated process-analytics package.

The comparison uses official release source, documentation, packaging metadata, CI configuration, and canonical publications, cross-checked against this survey’s measured records as of 28–29 August 2026. Feature, test, and CI claims were checked at the named release tags. The linked `forge`, `registry`, `practices`, and similar survey records are default-branch snapshots; where a branch had moved beyond its release, those records are used only for explicitly dated maintenance, community, and packaging signals. Stars, downloads, commits, citations, and reverse-dependency counts are contextual signals rather than quality scores.

Conflict-of-interest disclosure: the author of this survey is a principal DASCore maintainer. The recommendation therefore deserves particular scrutiny. To reduce that risk, this report states its criteria, separates foundation suitability from domain-method maturity, pins every feature baseline to a release, links the underlying evidence, and reports material weaknesses in DASCore alongside the other packages.

This was a package-selection review rather than a complete numerical audit of every method in every release. The release source of all five packages was inspected for architecture, features, tests, and integration concerns; the two source-level correctness risks called out below are concrete issues encountered during that review, not evidence that the unflagged packages’ numerical methods have been validated more deeply.

## Bottom line

There is no universal winner because the packages occupy different layers.

| Scientific need | Strongest starting point | Why | Main condition |
|---|---|---|---|
| A general data model and foundation for new research packages | **DASCore** | Broadest versioned I/O, validated labeled data model, physical units, immutable processing style, explicit extension entry points, strongest downstream-package evidence | It remains pre-1.0/Beta; pin a compatible minor release and test the formats you use |
| Huge multi-file acquisitions, gaps/overlaps, chunk-continuous pipelines, or live streaming | **xdas** | Virtual arrays, compact coordinates, stateful `Atom` pipelines, optimized multi-file access, parallel signal processing, and ZeroMQ streaming | GPL-3.0 and a changing 0.2 API may be unacceptable for some downstream packages |
| Broad DAS seismology analysis in scripts and notebooks | **DASPy** | Richest seismology-specific algorithm set, simple `Section`/`Collection` workflow, broad read/write support, permissive MIT license | The 1.2.6 release has no test suite and CI builds packages without running scientific tests |
| Whale-call detection, association, and localization | **DAS4Whales** | Deepest end-to-end marine-bioacoustics workflow and domain-specific visualization | CC BY-NC-SA licensing, uneven interrogator support, and a procedural data model make it a poor general foundation |
| Pyrocko-based DAS forward modeling or the published AFK denoiser | **Lightguide** | Unique fiber-aware Green’s-function modeling and a Rust-backed adaptive frequency-wavenumber filter | The latest release is old, Beta, lightly maintained, GPL-licensed, and dependent on compiled native code |

For a new broadly reusable package, **DASCore is the best default foundation**. Choose **xdas instead when larger-than-memory or real-time processing is central rather than incidental**. DASPy, DAS4Whales, and Lightguide are better treated as processing or domain integrations unless their narrower data models exactly match the project.

## At-a-glance comparison

| Dimension | DASCore 0.1.21 | xdas 0.2.8 | DASPy 1.2.6 | DAS4Whales 0.2.2 | Lightguide 0.4.0 |
|---|---|---|---|---|---|
| Primary role | General DAS/DFOS framework | Scalable DAS array and pipeline framework | DAS seismology toolbox | Marine-bioacoustics workflow | Pyrocko-oriented processing and modeling |
| Main data model | Immutable N-D `Patch`; indexed/lazy-source `Spool` | N-D `DataArray`; hierarchical `DataCollection`; virtual arrays | Mutable, eager 2-D `Section`; file-oriented `Collection` | Mostly NumPy arrays, metadata dictionaries, and separate coordinate arrays | Mutable, eager 2-D `Blast`; thin `Pack`; separate modeling `Fiber` |
| Coordinate and metadata semantics | Named dimensions, several coordinate types, validated attributes, Pint units | Named dimensions and compact sampled/interpolated/dense coordinates; free-form attributes | Uniform scalar `dx`/`fs`, start values, optional geometry and headers | Caller-managed arrays/dicts; limited invariant enforcement | Uniform scalar sample rate/channel spacing and descriptive unit string |
| Scale model | A patch is generally in memory; `Spool` indexes, selects, chunks, and maps across files or sources | Native virtualization, multi-file views, Dask fallback, stateful chunk processing, multiprocessing/multithreading, streaming | Eager arrays; sequential continuous-file processing carries filter state | Mostly eager arrays; small Dask/xarray helpers do not define the main API | Eager arrays; Rust/Rayon accelerates AFK only |
| I/O breadth | Broadest: more than 20 DAS/vendor/standard families, versioned handlers, external I/O entry points | Roughly ten common DAS/standard engines, virtualization, custom callable/class engines | HDF5 across many vendors, TDMS, SEG-Y, pickle, NPY; read and write | Targeted OptaSense-family/ASN/Silixa workflows; derived association HDF5 | Direct `Blast` API is MiniSEED/Pyrocko; README claims TDMS and OptoDAS through Pyrocko |
| Distinctive science | General transforms, filters, units, coordinate-safe processing | Continuous massive-data processing, streaming, triggers and stateful pipelines | Curvelet/f-k denoising and decomposition, channel analysis, three strain-to-velocity methods | Whale templates, matched/spectral detection, association, localization, tracking, bathymetry/cable maps | Published AFK denoising, phase following, fiber Green’s-function forward modeling |
| Extension story | Package entry points for I/O and `Patch`/`Spool` namespaces | Custom reader callable or `Engine` subclass; custom `Atom`; NumPy/xarray conversion | Functions plus custom read callable; built-in ObsPy/DASCore/Lightguide conversions | No general plugin/data-model protocol | Ordinary subclassing and Pyrocko interop; no plugin protocol |
| License | LGPL-3.0-or-later | GPL-3.0-only | MIT | CC BY-NC-SA 4.0 | GPL-3.0-only |
| Best foundation? | Yes, for most reusable DAS packages | Yes, for scalable/streaming GPL-compatible packages | Possible with strong downstream regression tests | Usually no; use as a specialized optional integration | Usually no; use targeted methods in a Pyrocko/GPL stack |

## DASCore 0.1.21

### Where it is strongest

DASCore has the most deliberate foundation-layer design. A [`Patch`](https://dascore.org/tutorial/patch.html) combines an arbitrary-dimensional array with named coordinates and validated attributes. Coordinates and attributes are reconciled at construction, units are represented with Pint, and processing methods return new patches rather than mutating an existing one. This style is valuable in research code because a method chain is easier to reason about and accidental cross-step mutation is reduced.

A [`Spool`](https://dascore.org/tutorial/spool.html) is a common interface over in-memory patches, a file, a directory, or another data source. It supports metadata inspection, selection, chunking with overlap, concatenation, and mapping. A `DirectorySpool` indexes file metadata so a scientist can find the relevant time/distance interval without eagerly reading the full archive. This is source-level laziness and chunked iteration, not the same execution model as xdas virtual arrays or Dask.

Release 0.1.21 registers more than 30 version-specific handlers covering more than 20 format families, including AP Sensing, several Febus variants, OptoDAS versions 8–11, ProdML 2.0/2.1, SEG-Y variants, Silixa HDF5, Sintela binary, Terra15, TDMS, DASDAE, Neubrex DAS/RFS, Sentek, Uptech HDF5, GDR, and several standards or exchange formats. The [working-with-files guide](https://dascore.org/tutorial/file_io.html) demonstrates indexed directory access and writing. Read support is substantially broader than write support; DASDAE, Pickle, SEG-Y, RSF, and WAV are the released write targets, with Pickle explicitly discouraged for security and compatibility reasons.

The broad format list does not mean every path is available from the smallest base installation. Some handlers, conversions, or accelerated operations require the `extras` dependencies, including packages such as `segyio`, ObsPy, Numba, and xarray. A downstream package should declare the relevant DASCore extra or its own optional dependency group rather than assume every advertised integration is present.

The processing surface is broad enough for a framework: filtering and resampling, detrending/tapering, rolling and aggregation, correlation, whitening, Wiener/Hampel/slope filters, Fourier and short-time Fourier transforms, differentiation/integration, Hilbert/envelope, spectrogram, STA/LTA, tau-p and dispersion transforms, and strain-related conversions. It also includes basic waterfall, wiggle, spectral, and map visualization. The emphasis is coordinate and metadata preservation rather than providing every specialized DAS algorithm.

For downstream packages, DASCore has the clearest extension mechanism of the five. [External namespaces](https://dascore.org/contributing/extending_dascore.html) can add methods such as `patch.my_package.method()` or a spool namespace through Python package entry points. File readers also use an entry-point registry. This allows domain functionality and vendor readers to remain outside the core dependency set while presenting a coherent user API.

### Where it looks mature

The 0.1.21 release contains documentation, examples, a changelog, contribution guidance, a large test suite, coverage workflows, cross-platform/full and minimum-dependency test matrices, doctests, linting, and performance benchmarks. At the release tag, the tree contains about 100 Python test files and 2,428 named test functions. These counts do not prove scientific correctness, but the assurance structure is substantially deeper than in the other packages.

The survey snapshot records 160 stars, 41 forks, 18 linked human contributors, 35 GitHub releases, a release in August 2026, PyPI and conda-forge distribution, and 13 other catalogued DAS projects declaring some dependency relationship with DASCore. This last count includes optional or development relationships, not only required runtime dependencies. See the measured [forge](../data/measured/forge/dascore.md), [registry](../data/measured/registry/dascore.md), [practices](../data/measured/practices/dascore.md), and [publication](../data/measured/publications/dascore.md) records and the survey’s [dependency network](../figures/v160_network.svg). The canonical 2024 [Seismica paper](https://doi.org/10.26443/seismica.v3i2.1184) describes the data model and goals.

### Where it is less mature

DASCore still labels itself Beta and remains on a 0.1 series. Release 0.1.21 itself includes breaking visualization changes, so “well engineered” should not be confused with “API frozen.” A downstream package should constrain supported DASCore versions, follow the changelog, and test against the minimum and maximum supported versions.

Its `Patch` operations are generally eager. `Spool` makes large collections tractable through metadata indexing, selection, chunking, and mapping, but users seeking a single virtual array spanning thousands of files, persistent state across IIR-filter chunks, or network streaming will find xdas more purpose-built.

The validated model has a learning and dependency cost: coordinate managers, attributes, units, and immutable return semantics are more machinery than a simple NumPy wrapper. The LGPL is much friendlier to downstream reuse than GPL, but it is still copyleft and requires compliance when distributing the library or modifications.

### Selection judgment

Use DASCore when the new package needs a canonical, extensible representation of DAS/DFOS measurements; broad input support; unit- and coordinate-aware operations; or a public API intended to outlive a single project. It is the strongest choice for making another research package’s domain methods available without inventing another array container.

## xdas 0.2.8

### Where it is strongest

xdas is the strongest option when data volume and continuity dominate the design. Its [`DataArray`](https://xdas.readthedocs.io/en/stable/user-guide/data-structures/index.html) is an xarray-like labeled N-dimensional array with a deliberately smaller API and specialized coordinate implementations. Sampled and interpolated coordinates compactly represent regular blocks, jitter, gaps, and overlaps without materializing a timestamp for every sample. `DataCollection` can organize acquisitions hierarchically without requiring every array to share coordinates.

Its major differentiator is [virtual multi-file access](https://xdas.readthedocs.io/en/stable/user-guide/io/virtual-datasets.html). HDF5-backed formats can use HDF5 virtualization, other formats can use Dask-backed virtualization, and compatible files can appear as one array. Release 0.2.8 also formalizes regular coordinates with declared sampling interval and tolerance so chunked and unchunked processing can produce consistent coordinates.

For processing beyond memory, an [`Atom`](https://xdas.readthedocs.io/en/stable/getting-started.html) represents a processing unit; stateful atoms carry filter or resampler state across contiguous chunks, and `Sequential` composes a pipeline. Loaders and writers overlap I/O with processing. [ZeroMQ publishers and subscribers](https://xdas.readthedocs.io/en/stable/user-guide/pipeline/streaming.html) support self-describing streamed chunks, including a protocol for ASN OptoDAS streams. This is a real architectural advantage over file-by-file loops when filter transients and live operation matter.

Released I/O engines cover AP Sensing, ASN OptoDAS, Febus, OptaSense/ProdML/Sintela variants, Silixa, Terra15, xdas NetCDF/HDF5, ProdML, and MiniSEED. The [format guide](https://xdas.readthedocs.io/en/stable/user-guide/io/data-formats.html) documents virtualization type and known caveats, such as manually specified trimming for poorly documented Febus blocks. A callable reader can be passed for a lightweight extension, or an `Engine` subclass can implement a fuller backend.

Signal processing includes detrending, tapering, filtering, Hilbert transforms, resampling/decimation, integration/differentiation, median and mean removal, FFT/STFT, triggering and pick support, with parallel implementations for many array operations. NumPy operations are supported selectively, and conversion to and from xarray is built in.

### Where it looks mature

The 0.2.8 release has a substantial pytest/doctest suite, coverage configuration, release notes, contribution documentation, a detailed user guide, and CI across Python 3.10–3.14. At the release tag, the tree contains about 33 test files and 788 named test functions. The survey records 72 stars, 16 forks, 11 linked human contributors, 15 GitHub releases, a July 2026 release, and three included DAS projects declaring some dependency relationship with xdas. See the measured [forge](../data/measured/forge/xdas.md), [registry](../data/measured/registry/xdas.md), [practices](../data/measured/practices/xdas.md), and [publication](../data/measured/publications/xdas.md) records and the survey’s [dependency network](../figures/v160_network.svg). The framework has a peer-reviewed 2025 [Seismological Research Letters paper](https://doi.org/10.1785/0220240366).

### Where it is less mature

The 0.2 line is still changing. Release 0.2.8 removes internal-leaning APIs, reworks the coordinate hierarchy, and introduces a future transition from inferred to explicitly declared sampling intervals. These are defensible changes, but downstream packages should expect migration work and test coordinate edge cases. The hosted “stable” pages observed during this review still identified some pages as 0.2.7, so exact 0.2.8 behavior should be checked against the [release tag](https://github.com/xdas-dev/xdas/tree/0.2.8) and release notes.

Compared with xarray, xdas intentionally implements a limited subset. Conversion through xarray densifies compact coordinates, potentially losing the representation that made xdas attractive. Attributes are free-form rather than a validated physical metadata model, and units do not participate in operations as directly as DASCore’s Pint-backed model.

The dependency footprint is large and mostly mandatory: Dask, ObsPy, xarray, h5py/h5netcdf/hdf5plugin, Numba, SciPy, pandas, Plotly, ZeroMQ, watchdog, xinterp, and others. Release 0.2.8 pins Dask below 2025.4 and setuptools below 82, which can constrain integration into modern environments. CI at the release tests multiple Python versions on Ubuntu but not a cross-platform OS matrix.

GPL-3.0-only is the largest downstream-package constraint. A GPL-compatible open research package may be comfortable with it; a permissively licensed package, mixed institutional codebase, or commercial collaborator needs a deliberate licensing decision before making xdas a required dependency.

### Selection judgment

Use xdas when a project’s core abstraction should be a virtual acquisition rather than an in-memory segment, or when stateful chunk processing and streaming are first-class requirements. For smaller data and a broadly reusable third-party extension ecosystem, DASCore offers a lower-risk foundation.

## DASPy 1.2.6

### Where it is strongest

DASPy is a broad, practical seismology toolbox. A [`Section`](https://github.com/HMZ-03/DASPy/blob/v1.2.6/daspy/core/section.py) holds an eager two-dimensional channel-by-time NumPy array with required channel spacing and sample rate, plus start channel/distance/time and optional gauge length, data type, scale, geometry, source metadata, and headers. Most methods mutate the section and return it, which makes interactive workflows concise but requires care when reusing objects.

A [`Collection`](https://daspy-tutorial.readthedocs.io/en/latest/Handling%20Continuous%20Data.html) represents a time-ordered set of files from one acquisition. It can inspect continuity, select a time interval, read it as a section, and apply a sequence of operations across files while carrying filter, integration, or differentiation state over boundaries. That is scientifically preferable to naively filtering each file independently, although it remains a sequential eager workflow rather than a virtual or distributed array.

DASPy’s main advantage is algorithm breadth. The [tutorial index](https://daspy-tutorial.readthedocs.io/en/latest/) covers standard preprocessing, filters, spectra, spectrograms, f-k transforms, visualization, channel-quality and cable-geometry analysis, spike/common-mode/curvelet denoising, f-k and curvelet wavefield decomposition, and three strain-to-velocity approaches: f-k rescaling, curvelet conversion, and time-domain slowness/slant stacking. These methods make it the most immediately useful option for a seismologist who wants analysis results rather than framework infrastructure.

The [I/O guide](https://daspy-tutorial.readthedocs.io/en/latest/Reading%20DAS%20Data.html) documents read/write support for HDF5, TDMS, SEG-Y, pickle, and NPY, with HDF5 variants for numerous vendors and datasets. Readers support metadata-only access and spatial/temporal trimming. A custom reader callable is accepted, though this is an argument-level seam rather than a package-discoverable plugin system.

Release 1.2.6 includes conversions to and from ObsPy streams, DASCore patches, and Lightguide blasts. This is useful in mixed stacks, but fixed uniform axes and differing metadata models mean round trips should be tested with real project fixtures.

### Where it looks mature

DASPy is MIT-licensed, supports Python 3.9+, is released on both PyPI and conda-forge, has English and Chinese tutorials, includes an example notebook, and has an active 1.x release series. Its methods are described in a peer-reviewed 2024 [Seismological Research Letters paper](https://doi.org/10.1785/0220240124). The survey records 157 stars, 30 forks, three linked human contributors, 457 commits, and a June 2026 release. See the measured [forge](../data/measured/forge/daspy.md), [git](../data/measured/git/daspy.md), [registry](../data/measured/registry/daspy.md), [practices](../data/measured/practices/daspy.md), and [publication](../data/measured/publications/daspy.md) records.

### Where it is less mature

Scientific feature maturity is ahead of software-assurance maturity. The v1.2.6 tag contains no test files. Its only [GitHub Actions workflow](https://github.com/HMZ-03/DASPy/blob/v1.2.6/.github/workflows/workflow.yml) builds and releases distributions but does not run functional or numerical tests. There is no coverage configuration, changelog, release note for 1.2.6, typed-package marker, or supported-version test matrix. The separately hosted documentation still labels itself 1.0.0, making the release-specific API contract less clear than the package version suggests.

`Section` assumes a rectangular, uniformly sampled channel-by-time grid. This is convenient for most traditional DAS processing but a weak canonical representation for irregular coordinates, extra dimensions, multiple fibers, or metadata schemas that need machine validation. Mutation makes stepwise notebook use easy but can obscure provenance in a large package. `Collection` manages sequential files but does not provide xdas-style virtualization, distributed execution, or live streaming.

The required dependency set is moderate, but `segyio` and `nptdms` are unconditional. The v1.2.6 README warns that conda installation on Python 3.13 or newer may fail where `segyio` builds are unavailable.

### Selection judgment

Use DASPy for general DAS seismology, especially when its advanced algorithms avoid substantial new implementation. It can support downstream packages because its MIT license is permissive and its objects are straightforward, but pin 1.2.6 and add package-level regression tests for every relied-on operation, reader, and conversion. It is less compelling as the public data model of a long-lived ecosystem.

## DAS4Whales 0.2.2

### Where it is strongest

DAS4Whales is the deepest domain workflow in this comparison. Release 0.2.2 contains modules for interrogator-specific loading and calibration, filtering, whale-call templates, normalized/matched and spectrogram-domain correlation, time picking, association along one or two cable segments, least-squares localization, covariance and error ellipses, tracking, cable and bathymetry maps, and many domain-specific plots. For a marine bioacoustician, this can replace a large amount of bespoke workflow code.

The strongest documented path is the OptaSense HDF5/OOI workflow. The [tutorial](https://das4whales.readthedocs.io/en/latest/src/tutorial.html) walks through metadata, channel selection, strain loading, Butterworth and f-k filtering, time-distance and frequency-distance plots, spectrograms, and audio playback using a public OOI file. Release source goes substantially further into detection, association, localization, and tracking than this introductory documentation.

### Architecture and scale

The package is procedural. Most functions exchange NumPy arrays, metadata dictionaries, and separate time/distance arrays. Small `dask_wrap` and xarray-oriented helpers exist, but they do not create a consistent package-wide lazy data model. There is no central waveform object that enforces dimensions, units, calibration, or metadata preservation, and no general extension protocol.

This is productive for a known experiment and familiar notebooks, but it increases integration risk in reusable packages: callers must preserve array orientation, sampling rate, channel spacing, calibration, clock, and geometry conventions themselves. Many routines are also eager and have a heavy unconditional scientific/image dependency stack.

### I/O strengths and cautions

Release 0.2.2 has metadata or loading branches for OptaSense-family HDF5, Onyx, Fosina DxS, ASN OptoDAS, and Silixa TDMS, plus multi-file time-window loading, URL/file-list helpers, cable geometry, annotation CSV, and compressed HDF5 persistence for derived association results.

The support is not uniform. In the release [`data_handle.py`](https://github.com/DAS4Whales/DAS4Whales/blob/0.2.2/src/das4whales/data_handle.py#L337-L447), the Silixa metadata reader uses TDMS but `load_das_data(..., interrogator="silixa")` follows the HDF5 branch at lines 366–370; post-release branch commits later corrected Silixa loading, so that fix is not credited here. The [dispatcher accepts `mars`](https://github.com/DAS4Whales/DAS4Whales/blob/0.2.2/src/das4whales/data_handle.py#L63-L77) and calls `get_metadata_mars`, but that function is absent from the release. ASN data loading requires a manual GitHub installation of `simpledas`, which is not a declared runtime dependency. Scientists should therefore describe non-OptaSense support as sample-specific or partial until it passes against their own files.

### Where it looks mature

The package has a recent release, a real tutorial dataset, Colab onboarding, API documentation, PyPI distribution, Zenodo records, CI that builds the distribution and runs pytest, and a notably complete domain workflow. At 0.2.2, the tree has eight test modules and about 50 named test functions. The survey records 79 stars, 21 forks, four linked human contributors, four GitHub releases, and active work in 2026. See the measured [forge](../data/measured/forge/das4whales.md), [registry](../data/measured/registry/das4whales.md), [practices](../data/measured/practices/das4whales.md), and [publication](../data/measured/publications/das4whales.md) records.

### Where it is less mature

The project labels itself Beta. CI tests one Python version (3.10.12) on Ubuntu, with no coverage measurement or lint step. There is no changelog or contributing guide, type coverage is partial, newer domain modules are less completely explained than the original OptaSense tutorial, and many tests are smoke/shape/error-path checks rather than known-answer validation of calibrated scientific outputs.

Its runtime dependency list is unusually broad and includes `dask[complete]`, OpenCV, scikit-image, librosa, netCDF4, pandas, xarray, sparse, plotting packages, and even pytest. This increases environment conflicts and installation time for downstream users who need only one detection or localization routine.

The decisive package-foundation caveat is legal. The code is licensed [CC BY-NC-SA 4.0](https://github.com/DAS4Whales/DAS4Whales/blob/0.2.2/LICENSE), which prohibits commercial use and applies share-alike conditions to adaptations; Creative Commons [does not recommend its content licenses for software](https://creativecommons.org/faq/#can-i-apply-a-creative-commons-license-to-software). It is source-available but not OSI-approved open-source software. A package intended for broad reuse, industry collaboration, or a permissive license should not take DAS4Whales as a required dependency without explicit licensing review or permission.

### Selection judgment

Choose DAS4Whales when the scientific question is marine-mammal detection/localization and its domain methods are the point of the work. Pin the release, validate the exact interrogator files, and verify calibrated results. For a general package, keep it optional and isolate its array/metadata and licensing boundaries rather than adopting it as the core data layer.

## Lightguide 0.4.0

### Where it is strongest

Lightguide’s most defensible uses are narrow and scientifically interesting. Its adaptive frequency-wavenumber denoiser is backed by a peer-reviewed [Geophysical Journal International methods paper](https://doi.org/10.1093/gji/ggac229) and is implemented as a Rust/PyO3 extension with Rayon and FFTW. Its [`Fiber` and `LocalEngine.process_fiber()`](https://github.com/pyrocko/lightguide/blob/v0.4.0/lightguide/gf.py) integrate cable geometry with Pyrocko Green’s-function stores to synthesize displacement and derive DAS strain or strain rate. Scientists already using Pyrocko source models and Green’s functions will find this integration unique among the five.

The [`Blast`](https://github.com/pyrocko/lightguide/blob/v0.4.0/lightguide/blast.py) object wraps a two-dimensional channel-by-time NumPy array with timezone-aware start time, scalar sample rate, starting channel, uniform channel spacing, and a descriptive unit. It offers detrending, decimation, Butterworth filters, AFK filtering, phase following by neighbor-channel cross-correlation, tapering, one-bit normalization, median-level muting, trimming, conversions, plotting, and MiniSEED/Pyrocko conversion. Most filters mutate the blast; trimming and physical conversions return copies, so pipeline code must distinguish the two styles.

### Where it looks mature

The released project includes Sphinx documentation, four example notebooks, type stubs for the native extension, lint configuration, tests, packaging workflows, citation metadata, a software DOI, and a separately published AFK method. The Rust kernel targets a genuine DAS performance bottleneck rather than using native code decoratively.

### Where it is less mature

The [release README](https://github.com/pyrocko/lightguide/blob/v0.4.0/README.md) states that Lightguide is Beta and that functions may change. Version 0.4.0 was published in April 2023. The default branch has only two later commits, ending in October 2024; one added Wiener and median filters, but these remain unreleased and are not counted as features here. The survey’s August 2026 snapshot records 65 stars, 13 forks, one linked human contributor, six releases, and no release for more than three years. See the measured [forge](../data/measured/forge/lightguide.md), [registry](../data/measured/registry/lightguide.md), [practices](../data/measured/practices/lightguide.md), and [publication](../data/measured/publications/lightguide.md) records.

The data model is eager, fixed-grid, and narrow. `Pack` is a thin set of blasts rather than an indexed archive; its forwarded methods discard return values, which is awkward for methods that return a trimmed or converted copy. Cable geography is held in the separate modeling `Fiber`, and the initialized `processing_flow` is not populated by release methods. There are no labeled arbitrary dimensions, irregular coordinates, physical unit algebra, lazy arrays, or metadata validation comparable to DASCore or xdas.

The README claims Silixa TDMS, ASN OptoDAS, and MiniSEED through Pyrocko, but the direct `Blast` API implements MiniSEED and Pyrocko trace conversions only. TDMS/OptoDAS support is inherited and dependent on Pyrocko rather than a dedicated Lightguide reader. `save_mseed()` does not preserve all `Blast` metadata such as unit and channel spacing in a round trip.

The v0.4.0 [build workflow](https://github.com/pyrocko/lightguide/blob/v0.4.0/.github/workflows/build.yml), lint workflow, and documentation workflow build wheels, lint, and build documentation but do not invoke pytest. The release tree has seven test files and about 16 named test functions, yet the tests are not demonstrated as passing in CI. There is no coverage reporting, changelog, or dedicated contribution guide, and the single-contributor concentration is a major maintenance risk.

One scientific implementation deserves explicit validation: [`Blast.to_strain()`](https://github.com/pyrocko/lightguide/blob/v0.4.0/lightguide/blast.py#L489-L511) cumulatively sums strain-rate samples at line 509 without multiplying by the sampling interval. Unless the input values are already per-sample increments, the amplitude is sample-rate dependent. This is a source-based concern, not a claim that all Lightguide results are invalid; test the conversion against an analytical signal before relying on physical amplitudes.

Installation is easy when a [matching v0.4.0 wheel](https://pypi.org/project/lightguide/0.4.0/#files) exists, but the published wheels cover older CPython/platform combinations and not macOS. Other Python versions and architectures require Rust/Maturin and FFTW-related source builds. GPL-3.0 also constrains how a downstream package may be distributed.

### Selection judgment

Use Lightguide for its published AFK filter or Pyrocko fiber forward modeling when those methods are specifically required. Do not select it as a new general DAS data foundation in 2026 without a maintenance plan, release-fork strategy, numerical validation suite, and compatible GPL licensing.

## Cross-cutting conclusions for research-package authors

### Data semantics matter more than method count

DASCore provides the strongest guardrails for preserving named coordinates, metadata, and physical units through package boundaries. xdas provides the strongest representation of huge, gappy, multi-file acquisitions. DASPy and Lightguide provide simpler uniform 2-D objects, while DAS4Whales largely leaves the contract in the caller’s arrays and dictionaries.

If a downstream package exposes one of these objects in its public API, that choice becomes expensive to reverse. Prefer DASCore for semantic validation, xdas for virtual acquisition semantics, or keep the dependency behind conversion functions when using one of the narrower toolboxes.

### “Large data support” means different things

- DASCore indexes sources and lets callers select, chunk, and map over patches. It avoids loading irrelevant data but normally processes each patch eagerly.
- xdas creates virtual arrays across files and explicitly manages stateful, chunk-continuous pipelines and streams. It has the strongest end-to-end scale model.
- DASPy’s `Collection` sequentially processes continuous files and carries selected state across boundaries. It is useful and scientifically aware, but not distributed/lazy execution.
- DAS4Whales has selected Dask/xarray helpers, while much of the domain API still materializes NumPy arrays.
- Lightguide accelerates one important filter with native parallel code but otherwise operates in memory.

Benchmark the exact operation chain and representative channel/time dimensions. None of these architectural labels guarantees that a particular workflow is faster.

### I/O lists need release- and sample-level validation

“Supports HDF5” is not meaningful without an interrogator, firmware/schema version, read/write direction, partial-read behavior, and metadata round-trip test. DASCore is strongest at explicit versioned handlers; xdas documents engine and virtualization behavior; DASPy covers many variants but lacks release tests; DAS4Whales has known release inconsistencies outside its best-documented OptaSense path; Lightguide relies on Pyrocko for all but direct MiniSEED conversion.

Before committing to any package, retain representative files from every acquisition configuration and test metadata-only scan, spatial/time selection, calibration, clock, coordinate orientation, gauge length, units, and a write/read round trip where writing is required.

### Interoperability exists, but conversion is not lossless by default

DASPy directly converts among its `Section`, ObsPy streams, DASCore patches, and Lightguide blasts. xdas converts to/from xarray and MiniSEED/ObsPy-related representations. DASCore has optional integrations and a namespace/plugin design. The survey also catalogues [Unidas](../data/curated/unidas.md), a lightweight MIT-licensed adapter among DASCore, DASPy, Lightguide, and xdas. Unidas lowers the cost of calling an algorithm written for another container, but it does not make the underlying public models equivalent or eliminate their representational constraints.

Uniform-axis models cannot always represent irregular or auxiliary coordinates. xarray round trips densify xdas compact coordinates. MiniSEED cannot carry every DAS-specific metadata field. Build a small, explicit interoperability test matrix for units, axis order, start/end conventions, timezone, coordinate spacing, geometry, and missing values.

### Software and scientific maturity are separate axes

The following deployment/adoption snapshot provides additional context. PyPI values are downloads during the 30 days preceding the survey scan; conda totals are lifetime channel counters and are therefore not directly comparable to the PyPI window. Download events are not unique users, and dependency counts include required, optional, or development relationships among included catalogue projects.

| Package | PyPI downloads, 30 d | Conda-forge | Catalogued dependents |
|---|---:|---:|---:|
| DASCore | 7,139 | Yes; 49,007 total downloads | 13 |
| xdas | 770 | No measured package | 3 |
| DASPy | 340 | Yes; 7,168 total downloads | 2 |
| DAS4Whales | 52 | No measured package | 3 |
| Lightguide | 94 | No measured package | 2 |

- **DASCore** has the strongest overall engineering assurance and ecosystem foundation evidence, but its API is still Beta/pre-1.0.
- **xdas** has strong tests, documentation, active releases, and the most mature scale architecture, but its coordinate/API design is still evolving in the 0.2 series.
- **DASPy** has a mature scientific feature set, paper, tutorials, and 1.x release cadence, but essentially no upstream verification harness in 1.2.6.
- **DAS4Whales** has substantial domain maturity and some CI tests, but its core abstractions, I/O consistency, documentation coverage, and license are weaker foundations.
- **Lightguide** has mature individual scientific ideas, especially AFK and Pyrocko modeling, but the released software and maintenance process carry the highest sustainability risk.

### License and deployment constraints can decide the answer

| Package | Practical downstream implication |
|---|---|
| DASCore, LGPL-3.0-or-later | Generally usable by open or closed downstream software when LGPL obligations are respected; modifications to the library remain under LGPL |
| xdas, GPL-3.0-only | Best suited to GPL-compatible downstream distribution; obtain legal guidance before making it a required dependency of permissive/proprietary software |
| DASPy, MIT | Lowest licensing friction and easiest to incorporate into packages with different licenses |
| DAS4Whales, CC BY-NC-SA 4.0 | Noncommercial and share-alike restrictions are a major barrier to general-purpose dependency use; software-specific licensing review is warranted |
| Lightguide, GPL-3.0-only | Same copyleft concern as xdas, plus native-wheel/source-build deployment constraints |

This table describes each project’s stated top-level license, based on its release license file and package metadata; forge auto-detection did not identify every license. Downstream distributors must also review transitive dependencies. For example, DASPy’s required I/O stack includes LGPL-licensed libraries, while Lightguide depends on GPL-licensed Pyrocko. This is a technical selection warning, not legal advice.

## Recommended selection process

1. Decide whether the package will expose a third-party data object publicly. If yes, begin with DASCore, or xdas when virtualization/streaming is non-negotiable.
2. List the exact released readers and sample schemas required. Run them against retained fixture files before comparing algorithms.
3. Write known-answer tests for calibration, units, integration/differentiation, filter phase and state across chunk boundaries, f-k orientation, and coordinate round trips.
4. Prototype the largest realistic acquisition and measure memory, I/O throughput, and total wall time. Compare DASCore chunked spools, xdas virtual/atomic processing, and DASPy collections where relevant.
5. Review license compatibility before implementation, especially for xdas, DAS4Whales, and Lightguide.
6. Pin a tested version range. For pre-1.0 projects, read every release note before widening it.
7. Keep specialized algorithms behind a small adapter boundary. A robust common design is a DASCore or xdas core model with optional DASPy, DAS4Whales, or Lightguide integrations, subject to license compatibility. Evaluate Unidas where its four supported containers and conversion constraints fit the project.

## Overall recommendation

For a scientist writing research code today, choose by the center of gravity of the work: **DASPy for broad seismological analysis**, **DAS4Whales for whale bioacoustics**, **Lightguide for Pyrocko modeling/AFK**, **xdas for huge or live continuous acquisitions**, and **DASCore for general DAS data handling and package construction**.

For a scientist building software that other research packages will depend on, the order is clearer: start with **DASCore**, evaluate **xdas** if its scale model justifies GPL and API-migration costs, use **DASPy** behind well-tested adapters for advanced methods, and treat **DAS4Whales** and **Lightguide** as specialized optional integrations rather than foundational dependencies.
