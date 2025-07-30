*******
History
*******

Here is a complete history of EggLib tracing back to initial pure C++
version.

=============
Version 3.5.2
=============

Solves a bug occurring when the statistic ``Fs`` is computed on a data
set with a pattern of missing data such that ``Pi`` can be computed but
the number of samples without any missing data is exactly 1
(:issue:`307`).

=============
Version 3.5.1
=============

This version addresses problems with the management of positions
overlapping a previous deletion in VCF files (:issue:`306`). If such
position is harbouring a new indel, a bug could occur when exporting
data as a site.

* Change in :meth:`.io.VCF.get_alleles` and :meth:`.io.VCF.get_alternate`:
  the ``*`` allele is not included anymore.

* Change in alphabets created by :meth:`.io.VCF.as_site` and
  :meth:`.io.VCF.iter_sites` for indels (alphabets of type string): the
  ``-`` allele is always included as missing data.

=============
Version 3.5.0
=============

* Groups of statistics in :class:`.stats.ComputeStats` (:issue:`299`).
  Due to the implementation of this change, the required Python version
  is now 3.10.

* The class :class:`.io.CodonVCF` is added to analyse synonymous /
  non-synonymous variation from the VCF file (:issue:`298`).

* A bug appearing with large datasets in :func:`.wrappers.codeml` has
  been fixed (:issue:`303`). The NEB/BEB results failed to be processed
  properly due to a mistake in regular expression. To help fix this bug
  and potential future ones, a *debug* option has been added to the
  method to save intermediate files before attempting to extract results
  (see the same issue). Also in :func:`.wrappers.codeml`, a rarely
  occurring bug has been fixed. Specifically, a typo preventing proper
  reporting of errors when parsing PAML's output.

* The Poisson random number generator had a flaw that led to occasional
  invalid small values (:issue:`295`).

* Two problems were fixed with :meth:`.Tree.midroot`. A rare bug could
  cause a crash (:issue:`294`), and another error used to lead to an
  invalid partition of the branch where the root is placed
  (:issue:`301`).

* The GFF3 parser (:class:`.io.GFF3`) was modified to support missing
  ``gff-version`` directive and excess semicolon in attribute fields
  (:issue:`300`). In addition, :class:`ValueError` is raised instead of
  :class:`IOError` in case of formatting errors (:issue:`302`). 

=============
Version 3.4.0
=============

* New features

    * :meth:`.VCF.is_single`.
    * :meth:`.VCF.as_site`.
    * :meth:`.VCF.iter_sites`.
    * :class:`.io.VcfSlider` performing sliding windows on a VCF.
    * Dump mode in :class:`.VCF` allowing to export given parts of a
      VCF.
    * :class:`.VCF` class supports :class:`pathlib.Path` instances.
    * :attr:`.Site.chrom`.
    * Added statistics ``f2``, ``f3``, ``f4``, and ``Dp`` to
      :class:`.stats.ComputeStats`.
    * Added method :func:`.stats.SFS` computing the site frequency
      spectrum.

* Bugs

    * :meth:`.VCF.goto` used to raise an exception in cases where it
      should return ``False``, and used to return ``None`` instead of
      ``True`` upon success.
    * The flag ``HTSLIB=0`` was ignored.
    * :meth:`.VCF.is_snp` used to return ``False`` for SNPs overlapping
      an indel.


=============
Version 3.3.5
=============

* Legacy VCF parser (:class:`.io.VcfParser`): did not support missing
  data for PL and GL FORMAT fields.

=============
Version 3.3.4
=============

* codeml wrapper: extract and export list of positively selectively
  sites under the ``candidates`` key of the output dictionary.

* also codeml wrapper: fix a regression which caused that data were
  exported for only a fraction (namely, a third) of sites if the
  ``codons`` alphabet was used.

* :meth:`.io.from_fasta` supports string-compatible objects as file
  name.

* some housekeeping in test suite.

=============
Version 3.3.3
=============

* codeml wrapper: allow codon_freq values 4-7.

* codeml wrapper: fix error when reference sequence has gaps.

* test suite: fix loading error from scipy.

* VCF: support ``None`` as value for *index* and *subset*.

* coalesce documentation: fix erroneous mentions to deleted *outgroup*
  parameter.

=============
Version 3.3.2
=============

* Fixed a single bug: the method :meth:`Align.del_columns` resulted in
  invalid outcome (issue #268).

=============
Version 3.3.1
=============

* Fixed the following bugs:

  * Bug in :func:`.tools.backalign` with the ``fix_stop`` option,
    resulting in an exception (issue #266).
  * Bug in helper methods of :func:`.wrappers.codeml` resuling in an
    exception when attempting to import the rst output file  (issue
    #267).
  * Regression of the test utility appearing with Python 3.12 while 
    generating the list of test components.

* Updated the test suite to prevent regression on fixed bugs.

* The star topology feature of :func:`.wrappers.codeml` doesn't work with
  later versions of PAML. Added a warning when this feature is used and
  warn about the problem in the documentation (the option might be
  removed at some point in the furture). Removed star topologies from
  tests.

=============
Version 3.3.0
=============

Added ``triconfig`` statistic (specifically for cases with three
populations).

=============
Version 3.2.1
=============

In this release, the test for executability of files passed as paths to
external application is dropped, because it was performed by the package
``click`` but requiring a recent version, thereby blocking the
generation of a ``conda`` package. Non-executable files will still cause
an error, although the type of exception and error message might be
different. This release supports any fairly recent version of ``click``.
Otherwise there are no changes.

=============
Version 3.2.0
=============

This new release addresses very few bugs but introduces a couple of
significant improvements.

-------------
New VCF class
-------------

The new :class:`.io.VCF` classes aims to replace :class:`.io.VcfParser`.
The old class is neither moved nor removed so backward compatibility is 
maintained. It is also maintained to provide a fallback solution in 
case the new class is not available, because it relies on the external 
C library ``htslib`` for better standardization and performance. The class 
is provided by a pure-C extension (without Python glue code). The new 
class is more efficient and is able to read compressed VCF and BCF
files. It has also a somewhat more intuitive API. For the moment, 
sliding windows are not available with the new class. Direct site 
extraction isn't either but since native lists are generated it should 
be efficient enough to use :func:`.site_from_list`. There is a function
for indexing BCF files, but it is not possible to index VCF files (VCF
indexes generated by :class:`~.io.VcfParser` are not compatible).
The class constructor and the indexing function ares replaced by a
function raising a :class:`NotImplementedError` if ``htslib`` is not
available at the moment of installation. A flag
:data:`egglib.config.htslib` tells if these tools are available.

---------
Packaging
---------

Although this is largely transparent to the user, the installation
procedure has been revised. EggLib now acknowledges new packaging
standards in Python by including a ``pyproject.toml`` file containing
most configuration. ``setuptools`` is still used as packaging and
installation backend, and calling directly the ``setup.py`` file is now
discouraged.

Dependencies
------------

In addition to the optional dependency to ``htslib``, EggLib depends on the
Python package ``click`` (for the new command-line interface tools). The
dependency should be automatically resolved by the installer (``pip``,
or possibly other) whenever installing EggLib.

There are additional dependencies for generating documentation and
testing, respectively. These can be automatically installed at the
user's request by requesting "extra" features (respectively ``doc`` and
``test``).

Package cleaning
----------------

A large number of items are removed from the package source. In
particular, compiled documentation which is currently generated
automatically upon pushing to the master branch (see below for
generating your copy). The test package is now included as a subpackage
of EggLib (see further down).

Options
-------

If needed, options are passed through environment variables
``HTSLIB`` and ``DEBUG`` (although this should be needed at all). In
addition to the aforementioned :data:`egglib.config.htslib` flag,
:data:`egglib.config.debug` tells if EggLib was compiled in debug mode.
Note that the ``-g`` option, which doesn't compromise performance, is
always passed to the compiler. The debug mode essentially consists in
dropping optimization, essentially for memory profiling.

Documentation
-------------

The commands generating documentation are dropped from setup.py which
should not be executed directly anymore. To generate the documentation,
run ``$ sphinx-build -a doc/ path/to/dest`` (where ``path/to/dest`` is
the location where you want the documentation to be generated). To
install needed dependencies, run ``pip install egglib[doc]``.

--------------
Muscle wrapper
--------------

A wrapper for MUSCLE version 5 is introduced. As a backup, the previous
wrapper is still maintained. There are now two separate functions,
:func:`.wrappers.muscle3` and :func:`.wrappers.muscle5` to explictly
use either version. The generic function :func:`.wrappers.muscle` calls
the appropriate one, based on which version has been detected when
configuring the muscle application path.

--------------------------
External application paths
--------------------------

To use tools of the :ref:`wrappers <wrappers>` module, it is still 
needed to pass command names or paths to the relevant programs. Now 
EggLib looks first within a user-specific configuration file for those 
paths and, if the configuration file does not exist there, falls back 
to the file in the EggLib installation location (which is still empty 
by default). The user-specific configuration file is only generated at 
the user request. More details with command-line tools.

------------------
Command-line tools
------------------

Two command-line tools are added for tackling auxiliary tasks. They
are automatically installed along with the EggLib package.

* ``egglib-config`` for configuration of the EggLib installation.

  * ``egglib-config version`` displays the version number
  * ``egglib-config infos`` displays more information (in addition to
    the version number, installation path, location of the external
    applications configuration file and the values of debug and htslib
    flags.
  * ``egglib-config apps [OPTIONS]`` can be used to set, reset and
    display external applications configuration for using tools of the
    :ref:`wrappers <wrappers>` module.

* ``egglib-test`` for running all or part of the test suite which is
  now included in the installed package. The test module has been
  updated with the addition of tests of the new :class:`.VCF` class, an
  update of the command-line interface for this command and a cleaning
  of the test files.

------------
New features
------------

* :class:`.Structure` now has a :meth:`~.Structure.subset` method
  allowing to spawn a new object representing a single or several
  populations or clusters.

* Added :meth:`~.Structure.get_populations` and
  :meth:`~.Structure.get_clusters` methods to :class:`.Structure`.

* New statistics are included. ``nall``, ``frq`` and ``frqp`` are lists
  giving, for each polymorphic site, the number of ingroup alleles, the
  allele frequencies and the allele frequencies per population,
  respectively.

------------------------------------
Implementation details and bug fixes
------------------------------------

* The output file is now closed explicitly at the end of
  :class:`.Align`'s and :class:`.Container`'s :meth:`~.Align.fasta`,
  avoiding a possible delay in flushing the file depending on the
  garbage collector.

* A bug has been found and fixed in :meth:`.Container.del_sample`
  affecting also expressions such as ``del cnt[idx]``: the length of all
  sequences (starting at the index of the deleted samples) could be
  incorrect, causing cropping of sequences or incorporation of undefined
  data in the sequence.

* The clustal format parser was a bit restrictive.

* :class:`.io.VcfParser` now tests type of *fname* argument.

* Default value of ``lseffo`` set to 0 rather than ``None``.

* There was a problem in the calculation of the ``rD`` statistic such
  that the statistic was not computed (and reported as ``None``) when
  there were outgroup samples. On a related note, the meaning of the
  attribute :attr:`.Structure.req_ns` is changed and
  :attr:`.Structure.req_no` is dropped. This is done without deprecation
  because these members are of limited use at the API level.

* A problem of the GFF3 was fixed: GFF3 files which had `start_codon`
  and `stop_codon` qualifiers with a phase, and `codon_id` or
  `codon_number` qualifiers (all of these at the level of a segment)
  were reported as a formatting error. Incidentally, the line number of
  error messages of the GFF3 parser has been fixed (there was an offset
  of 1).

* New tests found that the iterator :func:`.tools.orf_iter` was not
  working properly, so it has been fully reimplemented. Results of this
  tool and other ORF tools might differ but now they should be more
  reliable. The order of ORFs is also modified.

------------------------------
Changes in makeblastdb wrapper
------------------------------

Due to the evolution of underlying software, we do not enforce backward
compatibility of wrapper tools. The :func:`.wrappers.makeblastdb` is
changed:

* removal of the *gi_mask* and *gi_mask_name* option because, once
  triggered, they caused a difficult to fix error of ``makeblastdb``.

* default of *blastdb_version* upgraded from 4 to 5.

=============
Version 3.1.0
=============

Fixed bugs:

* :func:`.random.normal_bounded` did not process its arguments.

* Relative paths passed as BLAST database were not working.

* If an exception occurred in :meth:`.Align.add_sample` (or :meth:`.Container.add_sample`),
  the instance was left in an inconsistent state.

* There was a bug in the :func:`.wrappers.codeml` function, which did not
  use the :class:`.Tree` class with correct arguments.

Additions:

* Added the helper function :func:`.struct_from_iterable`.

* Added a way to use :meth:`.Align.extract`
  (using a :class:`.ReadingFrame`).

* Added :py:obj:`~.alphabets.binary` alphabet.

Improvements:

* Optimization of genotypes identification if ploidy is 1 (skipping
  unnecessary processing).

* Fasta exporting raises an exception when group labels contain the
  character used as label separator.

* Clustal wrapper supports protein sequences.

For the test suite:

* An excessively stringent condition in unit tests (causing occasional
  hanging) was lifted in ``test_bernoulli_T`` and ``test_binomial_T``.

* Compatibility with Python 3.10.

===========================
From version 2 to version 3
===========================


A large number of changes have been introduced when moving from version
2 to version 3. While functionalities have been extended, a lot of
changes aim to improve efficiency.

* EggLib ported to Python 3.

* The **C++ library** has been extensively rewritten, essentially to
  improve efficency.

  * There is no longer any out of bound checking at any place (with very
    few exceptions), meaning that the library is not safe anymore to use
    for C++ applications. The reason is that out of bound checking are
    done for arguments to the Python layer.

  * The pseudorandom number generator has been replaced by the
    Mersenne Twister algorithm. This algorithm has sufficient complexity
    for research purposes (but not for critical applications such as
    cryptography), and it is faster.

  * The old :class:`Container`, :class:`Align`, :class:`CharMatrix`, and
    :class:`DataMatrix` classes are replaced by a single
    :class:`DataMatrix` class that holds integer values only.

  * Several levels of structure. They are not required to be nested.

  * The Fasta parser does not allow any characters before the first >
    character. Empty files are no longer silently supported. There is
    no checking at reading time. The Fasta formatter has additional
    options.

  * Added classes to read VCF and GFF3 files.

  * Some changes in exceptions (:class:`EggInvalidCharacterError` is
    replaced by :class:`EggInvalidAlleleError`, among others).

  * A :class:`GeneticCode` class is added.

  * Main changes in the coalescence simulator are: changed interface,
    continuous segment for recombination, delayed samples, recombination
    rate changes, possibility to change parameters without building new
    instances.

  * Diversity statistics utils went through many changes: a
    :class:`Filter` class controls the list of valid allelic values.
    The analysis of data goes through site-based classes (:class:`Site`
    and :class:`SiteDiversity`, but there is also a class
    :class:`CodingSite` managing a codon-encoding triplet of sites),
    new statistics are added (Weir and Cockerham analysis of genetic
    variance with 1, 2 or 3 levels), Jost's D, allelic richness and
    the linkage disequilibrium statistic rD for microsatellites, Fis
    based on the observed heterozygosity, Fu and Li's statistics, Fu's
    F, ZnS, Wall's B and Q, Ramos-Onsins and Rozas's statistics, Rozas's
    Za and ZZ, EHH statistics.

  * Coding diversity analysis is reimplemented to remove the dependency
    on Bio++ and improve efficiency and consistency.

    * Random using Mersenne Twister algorithm.

* Create of a :class:`.Site` class and alphabets (instead of filters
  which were used during polymorphism analysis). A :class:`.Structure`
  class is introduced to manage explicitly sample structure (and allow
  using of alternate structures).

* The :class:`.Align` and :class:`.Container` classes are kept as
  constant as possible, but several significant changes have been done.

    * It is not possible to pass a file name to the constructor to
      initialize the object from a Fasta file. One must now use the
      function :func:`.io.from_fasta`.

    * The interface classes that manage access to data are extended to
      manage sequences and list of group labels. They are named
      :class:`.SampleView`, :class:`.SequenceView`, and :class:`.GroupView`.

    * Data items are always integers, but input as ASCII strings is
      allowed, and some methods are designed to export strings.

    * There is nore a direct :meth:`polymorphism` or :meth:`polymorphismBPP`
      method. One must use the :mod:`stats` module.

    * There is a single :meth:`~.Align.fasta` method allows to
      either generate a Fasta-formatted string or write it to a file.

    * A bunch of new methods are added, adding functionality and
      user-friendly access and edition tools using proxy classes. The
      underlying implementation of data is hidden and the polymorphism of
      data types (numerical, characters or strings) is transparent.
      
* In :mod:`!tools`, added a class handling all genetic codes.

* The :class:`.Tree` is improved: improved iterators (two different
  iterators are provided: :meth:`.Tree.breadth_iter` and
  :meth:`.Tree.depth_iter`, possibility to extract a subtree.

* A :mod:`!io` module is created with Fasta parsing methods, and new
  :class:`.VcfParser` and :class:`.GFF3` classes. Sequence-by-sequence
  parsing iterator; no data allowed before first >. The labelling system
  for groups is modified and extended. Labels are treated as strings.

* Diversity statistics are included in a new :mod:`stats` module which is
  designed to maximize object reuse (therefore improving efficiency). At
  the moment, a class named :class:`.ComputeStats` manages most
  statistics. Another class :class:`.CodingSite` is added, which allows
  to extract synonymous and non-synonymous and compute all available
  statistics on either of them. Many statistics
  are added, including Weir and Cockerham statistics, ``A``, ``He``
  (for sites), ``D`` of Jost``, allele status, site variance, ``R``, ``r_D``,
  statistics from Zeng *et al.* 2006, Fu and Li, ZnS, Li 2011,
  Ramos-Onsins and Rozas 2002, Wall's ``B`` and ``Q``, Rozas's Za and
  ZZ, Kelly’s test of neutrality, EHH. Ti and Tv. For Fay and Wu's H,
  changes of sample size due to missing data is taken into account when
  possible. Conversion to genotypes is supported.

* All wrappers are designed as function (but for the moment, only a few
  are implemented). The paths are managed by a dedicated class behaving
  like a dictionnary that supports both runtime and permanent
  specification of paths to run external paths.

* The coalescence simulator is also extensively changed.

    * A single class is proposed to manage all parameters and
      simulations (:class:`.ComputeStats`).

    * Replications are now more efficient, especially if the method
      :meth:`.ComputeStats.iter_simul` is used. It is also possible
      to compute statistics automatically from simulated datasets and
      to change parameters between repetitions.

    * New features are included (such as delayed samples and change of
      recombination rate during simulations).

    * Some historical events are removed and the number of populations
      is required to be constant during a simulation (making indexing of
      populations more logical if events occur), but all models that
      could be implemented before can still be implemented using given
      combinations of currently available features.

* In the :mod:`!wrappers` module, a few functions are exposed to manage
  application paths. All wrappers are updated to latest versions of the
  programs (and in some case extended to accomodate all options).

* Removed the modules :mod:`fitmodel` (ABC tools) and :mod:`utils`
  (directly executable commands).

* A unit test package has been included.

=====================================
Early version 3 intermediate versions
=====================================

**3.0.0b8** -- 2016-07-17

    Changes:

    * :data:`.stats.filter_nucl` is renamed :data:`.stats.filter_dna`.

    * Refactoring of the :mod:`.stats` module:

        * The class :class:`.SiteFrequency` was inherently ambiguous, so
          it is replaced by :class:`.Site` and :class:`.Freq` which help
          clarify the design. The `stats` module provides methods to
          instanciate both directly from user-provided data, :class:`.Align`,
          or each other.

        * The interface of :class:`.Structure` is modified. The previous
          design was also exceedingly flexible, thereby confusing. Now
          `Structure` is required to have all levels defined (clusters,
          populations, and individuals) but it is possible to bypass them
          (place all populations in a single cluster, all individuals in
          a single population, or, to make haploid data, make individuals
          with a single item each). To method used to create a `Structure`
          are moved to the level of the `egglib.stats` module (:func:`.egglib.stats.struct_from_dict`
          and :func:`.egglib.stats.struct_from_labels`). The former is equivalent to
          :meth:`.Structure.from_dict` but you need to specify a single dictionary
          for all data. Created more convenient :func:`.egglib.stats.struct_from_samplesizes`.

        * :class:`.ComputeStats` is also modified accordingly. The changes should
          be less significant but they can be still annoying if you have code
          running. :meth:`.ComputeStats.add_stat` is renamed as
          :meth:`.ComputeStats.add_stats` (and it allows you to pass several
          statistics names). The structure and the filter must be passed
          as argument to :meth:`.ComputeStats.process_align` and not
          :meth:`.ComputeStats.configure`. This method now always compute
          average of statistics. To get per-site statistics, you must call
          :meth:`.ComputeStats.process_site` for all sites. This method
          :meth:`.ComputeStats.process_site` and :meth:`.ComputeStats.process_freq`
          can compute statistics from individual sites, and there is also
          :meth:`.ComputeStats.process_sites` that can process a list of sites.
          All of those methods take a *no_return* argument that allows you to
          process several sites/alignments before computing statistics over all of
          them.

**3.0.0b7** -- 2016-05-11

    Bug fixes:

    * The method :meth:`.ComputeStats.process_site` was ignoring allele
      status (number of fixed alleles, etc.) when requested. Thanks to
      Tatum Mortimer for reporting this bug.

    * The "number of fixed differences" statistic was incorrectly named.
      It actually corresponded to the number of fixed alleles. A fixed
      difference between a pair of populations is when population 1 is
      fixed for allele A and population 2 is fixed for allele B, and this
      accounts for two fixed alleles. Now there are two statistics:
      ``numF`` (number of fixed differences, that is when one allele is
      fixed in one population and another allele is fixed in the other
      population), and ``numFA`` (number of fixed alleles, which counts
      all cases when one allele is fixed in a population but absent in
      the other, regardless of whether the other population is
      polymorphic).

    * The method :meth:`.Simulator.simul` was not actually making a deep
      copy of the simulated data object, causing an error if the
      simulator was deleted and the :class:`.Align` deleted (the data
      could be overwritten), or if new simulations were run. Now a deep
      copy is made as described in the documentation.

    * The :meth:`create` method of :class:`.Align` and :class:`.Container`
      did not get outgroup samples.

    Changes:

    * The method :meth:`.ComputeStats.process_site` now silently accepts
      empty lists of arguments. Before, an error was caused.

    * The :meth:`iter` method of :class:`.Align` and :class:`.Container`
      is renamed :meth:`iter_samples`.

**3.0.0b6** -- 2016-05-04

    Bug fixes:

    * The bug :meth:`.ComputeStats.process_align` in the previous
      version is fixed.

    * The value of ``Gst``, ``Gste``, and ``Hst`` was incorrect. In fact,
      the correct value could be computed as one minus the reported
      values for all three statistics in the previous version.

    * The PhyML wrapper was not compatible with earlier versions of
      PhyML (starting from 3.2). The wrapper is now tolerant regarding
      the .txt extension of output file of the program.

    * Installation method for MacOSX is updated. The previous method
      would overwrite permissions and owner of previously existing
      directory (which is a problem since the full path of the EggLib
      module was included in this archive). A, probably, worse problem
      is that this method made assumptions over the location of the
      Python installation. The new method is an *ad hoc* script which
      manually installs the module in a hopefully appropriate site-package
      directory. Feedback is welcome.

    Changes:

    * Both :meth:`.Align.encode` and :meth:`.Align.rename` (applies also
      to the equivalent methods of :class:`.Container`) support an
      argument to include the outgroup samples.

    * :meth:`.Align.rename` and :meth:`.Container.rename` return the
      number of rename operations.

    * Added an ``outgroup`` option to :class:`.coalesce.Simulator`
      to automatically move a given population to the outgroup.

    * Added :meth:`.stats.ParamList.mk_structure` method.

    * Few corrections in the documentation of options to the
      :mod:`.coalesce` module.

    * Removed the population-to-individuals flag of :class:`.Structure`
      (now it is as if it were always ``True`` when appropriate).

**3.0.0b5** -- 2016-04-20

    It is now possible to pass :class:`.SiteArray` instances to
    :meth:`.ComputeStats.process_align`. However this caused a bug that
    prevents :meth:`.ComputeStats.process_align` to work
    properly if a :class:`.Structure` is passed. To work around, first
    call :meth:`.ComputeStats.set_structure` with the :class:`.Structure`
    object than then :meth:`.ComputeStats.process_align` without the
    alignment only.

**3.0.0b4** -- 2016-04-13

**3.0.0b3** -- 2016-03-22

**3.0.0b2** -- 2016-03-18

**3.0.0b1** -- 2016-03-18

    The Python module is completed. EggLib 3 is now in beta mode and
    bugs are being fixed while missing functionalities are being
    implemented.

**3.0.0a** -- 2014-09-23

    Preliminary (alpha, for testing purpose only) release of the version
    3. This package contains the C++ new library and a stub Python
    package providing the updated ``Align`` and ``Container`` classes
    and an executable module implementing the coalescence simulator
    ``coalesce``.

================
Earlier versions
================

**2.1.11.** 2016-03-04

    Fixed a bug in eggcoal that caused an exception, with error messages
    stating that EggLib was unable to open (actually, in that case,
    create) a file.

**2.1.10.** 2015-03-23

    Ported to Bio++ 2.2.0. The new version is not compatible with
    previous versions of Bio++: the management of alphabets and genetic
    codes is modified.

    In :class:`ParamSet` (of the C++ library): the method :meth:`reset()`
    previously restored objects to 0 population (instead of 1).

**2.1.9.** 2014-10-04

    Bug fix: the ``staden()`` parser (and consequently the
    ``staden2fasta`` command) had an error that shifted sequences that
    would start *after* the first sequence finished.

**2.1.8.** 2014-09-23

    This is bug fix release fixing the following major problem that
    affected everyone using the summary statistics sets TPS, TPF and TPK
    (chiefly using ``abc_sample``). The error was that the program used
    population Pi for the last locus only (ignoring all previous ones).
    The three summary statistics sets are fixed.

**2.1.7.** 2013-11-07

    This version fixes the following minor problems:

        - eggstats: fixed two missing colons in program output (for Bio++ stats).
        - The archive egglib-htmldoc-2.1.6.tar.gz was actually a bzip2 archive.
        - egglib-cpp's configure script has been modified to detect more consistently the GSL library. If you have trouble to get it detected, please contact us. (Thanks to Jérôme Gouzy.)
        - The setup.py script takes clags=X and lflags=Y arguments to add X and Y as extra compile and link flags to compilation command lines.

    There was a more serious problem in tools and polymorphism analysis: there was a problem with genetic code specification--the code argument was ignored in some cases.

**2.1.6.** 2013-04-22

    egglib.cpp is modified to support Bio++ version 2.1.0.

**2.1.5.** 2013-09-20

    This version makes the following minor changes:

        - [backalign] tools.backalign() does not crop stop codons out of coding sequences any more.
        - [codalign] the codalign command takes a flag to prevent cropping stop codons out of coding sequences.
        - [fitmodel] the demographic models all accept a random object in order to control the random number chain (in the generate function)

    This version also corrects the following bugs or errors: 

        - [fitmodel] the documentation of the ABC model SM had incorrect parameter order THETA, DATE, MIGR, [RHO] (correct is THETA, MIGR, DATE, RHO)
        - [utils] the seeds argument of ABC simulation commands did not control the random generator objects used by demographic models

**2.1.4.** 2013-09-04

    This version fixes the following serious bug:

        - [diversity] the Fst/Kst/Gst/Hst/Snn statistics might be computed incorrectly if outgroup sequence were not placed at the end of the file (thanks to Emmanuel Reclus).

    This version fixes the following minor bugs:

        - [Codeml] the wrapper was failing to import site probability for models M1a, M2a, M8a and M8 if the reference was a gap (if the first position reference was a gap, a crash occurred; otherwise, the site probability table was truncated from the first gap position and on) (thanks to Nathalie Chantret).
        - [matcher] a ValueError was fixed.

    This version makes the following minor changes:

        - [Random] the seed1 and seed2 getters become const.
        - [Codeml] the wrapper now exports a `np` key (the number of parameters).
        - [fitmodel] a new prior type is added (PriorParser).


**2.1.3.** 10/02/12

   This version fixes the following bugs:

        - [fitmodel, abc_sample] the statistics set TPF was repaired (it is also modified compared to its previous definition).
        - [Align.phylip, wrappers.nj] the phylip converter of Align had a bug and has been repaired and rewritten.
        - [tools] a non-ASCII character was accidentally inserted in a comment in tools.py, preventing the package to load on at least some systems.


**2.1.2.** 08/02/12

   This version fixes the following bugs:

        - [eggstats] the option ``groups`` was ignored (the default value was always used).
        - [SitePolymorphism, data.Align.polymorphism, eggstats, etc.] non polymorphic sites were not considered as orientable: as a result, the number of orientable sites was always incorrectly reported as <= S.
        - [fitmodel, abc_sample] model AM was incorrectly implemented, leading to invalid results.

    This version incorporates the following improvements:

        - [eggstats] the option ``outgroup`` is added, as well as a few statistics.
        - [fitmodel, abc_sample] added summary statistics set SDZ

    Note on interface changes:

        - [eggstats] one additional option.
        - [eggstats] if you parse eggstats's output, beware that statistics have been added, the order is changed and some statistics might be skipped if you set the ``groups`` option to ``no``.


**2.1.1.** 26/01/12

   This version fixes a single bug: in eggcoal, the default number of threads could be smaller than the number of CPUs under some conditions. The links are updated following the move from the seqlib to egglib sourceforge project.

**2.1.0.** 24/01/12

    Version 2.1.0 is a preliminary version of the 2.1 release that will include an additional round of interface-changing changes. The changes listed below are mostly bug-fixes.

    - :class:`~egglib.Align` and :class:`~egglib.Container` method :meth:`find` now returns ``None`` instead of -1 when the specified name is not found.
    - There were a few mistakes in the documentation included in the file apps.conf.ini.
    - In the documentation of the command *ungap*, the word "newick" was incorrectly used instead of "fasta" (when specifying the format of the input file).
    - Some other minor documentation fixes.
    - The documentation of the :class:`~egglib.Align` method :meth:`~egglib.Align.matrixLD` has been completed.
    - The method :class:`~egglib.simul.coalesce` now returns `~egglib.SSR` instances instead of `~egglib.Align` if the number of alleles specified in the mutator if above 4.
    - A flag *forceSSR* is added to the method :class:`~egglib.simul.coalesce`.
    - All classes of the *data* module are converted to new-style classes.
    - In `~egglib.SSR`, when using the load method, population labels were not changed to strings.
    - `~egglib.SSR` improvements: addition of a ``str()`` method and ``str()`` support (string formatting), and addition of the :attr:`~egglib.SSR.indiv2pop` mapping data member.
    - When :meth:`egglib.Align.polymorphism` and :meth:`egglib.Align.polymorphismBPP` are unable to compute a statistics, the corresponding key in the returned dictionary is given a ``None`` value (rather than not reporting the statistic at all).
    - A check is added in ABC regression method to prevent attempting to fit data files containing model labels.
    - :meth:`Align.remove` in egglib-cpp was returning the length of the alignment instead of the new number of sequences.
    - An error lied in the low-level Edge class of the coalescent simulator, potentially generating errors when formatting newick string from ancestral recombination graphs and, potentially, skipping some mutations.
    - A tiny change is made to the error message shown by :class:`EggInvalidCharacterError`.
    - In the C++ library, :meth:`HaplotypeDiversity.haplotypeIndex` nows performs out of bound checking.
    - :meth:`LinkageDisequilibrium.correl` generated invalid results due to a bug.
    - tMRCA values obtained by the :class:`Ms` class of *egglib-cpp* are changed to double type (previously, they were float, what could cause rounding shifts when accessing them from Python).
    - :meth:`~egglib.Align.shuffle` had a bug.
    - :meth:`~egglib.Align.simErrors` is not available for :class:`~egglib.Container` instances anymore (for which it was not working).
    - The stability of :class:`~egglib.SSR` is improved in case of empty data sets and when importing haploid data sets.
    - The stability of the parser and extractor of :class:`~egglib.TIGR` has been improved.
    - The stability of the parser of :class:`~egglib.GenBank` was improved.
    - The meaning of :meth:`~egglib.GenBankFeature.qualifiers` of :class:`egglib.GenBankFeature` is changed (the previous version was incorrect).
    - :meth:`~egglib.GenBankFeature.rc` of :class:`egglib.GenBankFeature.rc` doesn't require an argument anymore.
    - Errors corrected in :class:`~egglib.GenBankFeatureLocation` methods to add sub-locations.
    - Fixed a bug in :class:`~egglib.Tree` method to set branch lengths.
    - Error fixed in :class:~egglib.Tree.frequency_nodes`.
    - :class:`~egglib.wrappers.BLAST` doesn't accept containers with duplicated names anymore.
    - Errors have been fixed in :meth:`egglib.Tree.get_nodes_re`, :meth:`egglib.TreeNode.set_branch_from` and :meth:`egglib.TreeNode.set_branch_to`.
    - The Clustal alignment format parser in :meth:`~egglib.tools.aln2fas` has been fixed and improved.
    - The :meth:`~egglib.tools.staden` was interpreting the fname as a Staden string. It is now possible to use both mode (read from file or from a string).
    - An error was fixed in :meth:`~egglib.tools.get_fgenesh`.
    - In :class:`~egglib.tools.Mase`, only ingroup sequences are imported (previously, outgroup sequences were imported at the instance level but not in the internal :class:`~egglib.Align` instance. The species name (*species* attribute) is stripped.
    - :meth:`~egglib.tools.longest_orf` now takes an option to specifies the minimal length of the returned ORFs. The default value is 1 codon, meaning that single stop codons are no longer returned by default.
    - Error management in :meth:`~egglib.tools.rc` is slightly modified.
    - :meth:`~egglib.tools.ungap` now takes an option for ignoring gaps in the outgroup sequence(s).
    - Bug fixed in :meth:`~egglib.tools.GeneticCodes.index`.
    - There was a bug in :meth:`~egglib.tools.motifs`: the position of reverse hits was incorrect.
    - :meth:`~egglib.tools.locate` returns ``None`` (instead of -1) for motifs not found.
    - :meth:`~egglib.tools.ReadingFrame.exon` of :class:`~egglib.tools.ReadingFrame` now returns ``None`` if the position is not in an exon.
    - :class:`~egglib.tools.Updater` now always shows null remaining time when "done" gets larger than "expected".
    - :meth:`~egglib.tools.wrap` is slightly improved.
    - The ms wrapper support the "prob" line that appears in ms output when both theta and the number of segregating sites have been specified.
    - The ms wrapper support the tree line(s) that appear in ms output when it has been requested, and adds a list of :class;`~egglib.Tree` instances to the returned instances under the name ``trees``.
    - BLAST wrappers are slightly improved.
    - The clustalw wrapper and parser have been improved to support the current version of the program.
    - :meth:`~egglib.wrappers.clustal` and :meth:`~egglib.wrappers.muscle` now attempt to preserve group labels and as a result no longer support duplicates in continers. They now take a *nogroup* flap to disable this feature.
    - The following stability issues have been fixed in :class:`~egglib.wrappers.Codeml`: regular expressions sometimes failed to catch some beta parameters; the number of classes of M8a/M8 models was incorrectly reporter as incorect when the number of categories was not default; and, for models A0, A and nW, the class did not checked that the tree has labels beforehand.
    - The following stability issues have been fixed in :class:`~egglib.wrappers.Primer3`: "primer not found" messages could occur when lower-case sequences were passed (the comparison are case-dependent - now the sequence is automatically converted to upper case), and when modifying the primer3 parameter relative to the primer first base index (previously, the class did not take this into account when locating the primer).
    - The member *nMutations* was missing from :class:`~egglib.egglib_binding.DataMatrix` instances returned by :meth:`~egglib.simul.coalesce`.
    - The option *randomAncestralState* of mutators of the :mod:`~egglib.simul` module was broken.
    - Modification in eggcoal: the program takes a "suffix" option and the "prefix" option can be skipped using a backlash character. The underlying variable _fastaPath becomes _fastaPrefix for clarity.
    - eggcoal is also parallelized an accept a max_threads option.
    - The command `abc_sample` now supports parallel computing. See the `max_threads` option. The `step` option is removed.
    - phyml (both function and utils command) allows to set the starting tree without fixing the topology.
    - small bugs fixed in IMn, IMG, IMiG, IMiGn and DOM (with recombination) demographic models.
    - The ABC summary statistics stats JFS yielded invalid results.
    - The `command` abc_psimuls now manages simulations without mutations (they previously caused an error). Missing statistics (such as those that are undefined when no polymorphism, or those that are not available) are now replaced by "None".
    - The function :meth:`~egglib.utils.execute` of the :mod:`~egglib.utils` module can be run directly to execute utils commands from python (as normal functions).
    - There was a bug in command `concatgb`'s default value for option "spacer".
    - Command `consensus` did not accept separator of length 1 (the separator must be a single character).
    - The :meth:`~egglib.Align.consensus` method of :meth:`~egglib.Align` is made more restrictive: only IUPAC characters are accepted. It returns an alignment gaps only if the gap is fixed (previously it returned a gap when there was at least one gap in the column).
    - In `extract_clade` command, nodes that have a support value equal to the threshold were rejected instead of accepted.
    - In `extract_clade` command, nodes that did not have labels were not supported when the threshold option is used.
    - In the `family` command, BLAST failed when the source sequences were proteins (because the data were cleaned assuming they were nucleotides).
    - In the `interLD` command, the output file had "file 1" twice.
    - :meth:`~egglib.tools.locate` is changed. Ambiguity characters are now allowed in the target sequence and, importantly, exact matches are found in priority (in order to fasten searches).
    - Command `staden2fasta` had a bug that prevented it from reading any file.
    - In the coalescence simulator, if the length of the tree is 0 (no samples), there will be no mutations regardless of the fixed number of mutations (previously, a bug occurred when a fixed number of mutations was requested with no samples).
    - A copy constructor is added to Mutator (in egglib-cpp).
    - A test subpackage is added to the Python package. It is included in the distributed version although it has not be designed to be routinely used by end-users (it has minimal documentation, a crude reporting system and generates local temporary files in the current directory, so it might deletes user's files if they happen to have the same name as one of the temporary file names used). This test package helped detect most of the bugs listed above.

**2.0.3.** 07/10/11

    This version incorporates a number of minor changes:

        - Small changes:
            - The utils command phyml accepted an option ``add_model`` that was meaningless (and ignored). It is now removed.
            - eggstats and the egglib script (or ``python -m egglib.utils``) now reports the version number in the default manual page.
            - eggcoal takes a --version or -v option to print out the version number.

        - Implementation changes:
            - The C++ Fasta parser now provides methods that append
              sequences to an existing :class:`~data.Container`.

        - Fixed bugs:
            - :class:`~data.Container` could not instanciate from strings.
            - The *clean* command of egglib-py setup.py was broken and
              caused an error.
            - The method :meth:`Convert.Align` and the program *eggcoal*, when running with a fixed alignment length and 
              using default mutation positions, failed to sort the mutation positions leading to either incorrect positions
              (they were clustered to the right-hand end of the alignment) or an error.


**2.0.2.** 16/09/11

    The change below fixes an error in the calculation of a statistic:

    - Fixed an error in the calculation of ``triConfigurations`` (some patterns were counted several times).
    - ``triConfigurations`` now ignores sites that have 0 sequence in either of the populations.

    The changes below are fixes corresponding to crashes or errors:

    - Fixed an error that prevented data.Align.polymorphismBPP from running.
    - Added an inclusion to the SWIG interface that was necessary for compiling the Python module on a least one system.
    - :class:`tools.Primer3` (and consequently the utils command sprimers) was broken with recent versions of the program. Now updated to primer3 version 2.2.3.
    - Fixed an error that resulted in a crash when displaying help for utils commands (under Windows and source version only).
    - The ABC class and the abc_fit commande were unable to compute threshold/perform rejection when at least one statistic was not variable; now they still are unable to do so, but report an informative message error.
    - abc_sample (linked to a method of both Prior type) now takes an argument "force_positive" that enforces that drawn parameter values are >=0 (an error is thrown if no positive value is found after a fixed number of tries).
    - Documentation of executable commands (``python -m egglib.utils concat`` for example) caused a crash on Windows installations.
    - In the coalescent simulator, the case when M=0 preventing simulations to complete was not handled properly (an incorrect error message was issued).
    - The stability of :meth:`wrappers.Primer3.find_primers` was improved (some errors occurred, typically with repetitive sequences where primers could be found at multiple positions in sequences).
 
    The changes below are minor improvements:

    - The function for adding models to the ABC analysis is modified.
      Now the model must be specified as a class with the same name as the module.

    The changes below are corrections to the names of statistics reported by :meth:`~Align.polymorphism()`:

    - ``Polymorphisms`` is renamed ``pop_Polymorphisms``.
    - The following statistics are reported: ``pair_CommonAlleles``, ``pair_FixedDifferences``, ``pair_SharedAlleles``, ``pop_SpecificAlleles``, ``pop_SpecificDerivedAlleles``.
    
    Some statistics are now no longer returned by both :meth:`~Align.polymorphism()` and :meth:`~Align.polymorphismBPP()`
    depending on the values of other statistics. For example ``thetaW`` and ``Pi`` are no longer returned if ``lseff`` is 0
    and ``D`` if ``S`` is 0. This is clearly documented in the documentation of both methods.
    
    In addition, several typos were corrected in the documentation.
    
**2.0.1. Windows pre-compiled modules** - 11/04/11

    - The code from the egglib script is moved to egglib.utils.execute.
    - egglib.utils is executable (as an alias for the egglib script).
    - egglib.utils.commands is created to hold all executable command
      classes.

**2.0.1** - 26/04/11

New major release. The interface is modified in depth. A few of the
many changes are higlighted below:

    - The name of the package is changed from SeqLib to EggLib to
      avoid confusion with other seqlib packages in the same field.
    - The C++ library is formally distinct (``egglib-cpp``).
    - Two separate C++ programs (``eggstats`` and ``eggcoal``) are
      also separated from the rest.
    - The remainder is the Python module, ``egglib-py``, whose structure
      is slightly modified: ``toolkit`` becomes ``tools`` and ``utils``
      functions cannot be called anymore from Python code (not easily
      at least).
    - Classes ``Container``, ``Align``, ``Tree`` and ``GenBank`` are
      extended and improved (and their names take capitals). In
      particular, polymorphism analysis is performed though ``Align``
      methods. They all have more powerful iteration methods. A ``SSR``
      class is added.
    - Additional genetic code are supported for translations.
    - Ported to Bio++ version 2.
    - The ABC module was rewritten, and made more easy to extend. The
      regression steps are performed at the C++ level and is more
      efficient (supports very large data files).
    - Interactive commands are standardized under a common interface
      controlling parameter input and documentation.
    - The C++ coalescent simulator is rewritten and now includes
      recombination, microsatellite and finite site mutation models.
    - The Python interface to the C++ coalescent simulator is
      redesigned to make it more easy to handle.
    - The extension module (binding to ``egglib-cpp``) now uses SWIG and
      doesn't require any external dynamic library.
    - The building process is based on autotools for the C++ packages
      and on distutils for the Python package.
    - Documentation using sphinx.
    - Many more changes not documented: please refer to the
      documentation when migrating from seqlib to EggLib.

**1.6** - 02/07/10

This version cumulates several bug fixes and additions. Rule H is
modified (single backward compatibility change) and rule I is added.
(These rules use the frequency spectrum; type
``$python -m seqlib.run abc_stats`` to know more. Note that rule I
automatically implies a missing data threshold of 0.70.). Among bug
fixes, a problem occurred with haplotype analysis when the outgroup was
not at the last position (resulting in memory crashes and possibly in
erroneous computation of statistics K, Hd and Fst estimators based on
haplotypes).

**1.5** - 26/11/09

More minor improvements and bug fixed. The change log is, unfortunately
unavailable but notable changes are the addition of stat rule H to the
ABC scheme (using the allele frequency spectrum as rejection/regression
criteria) and the removal of a bug in the coalescent simulator (that led
to the duplication of simulations without polymorphism under a certain
combination of options).

**1.4** - 24/10/09

Few minor improvements: The command ``abc_psimuls`` accepts an option
"excludefixed" that allows discarding simulations with S=0 for computing
the P-values of D, H and Z statistics. The rule G is changed.

**1.3** - 23/10/09

One important bug fix and one addition.

BUG FIX: Migration times were incorrectly drawn in the coalescent
simulator. The source code line doing that was accidently deleted!

ADDITION: addition of one set of statistics to the ABC system, allowing
to use thetaW, Pi, Snn and their respective coefficient of variation in
order to fit structure population models.

**1.2** - 06/10/09

With respect to version 1.0, this version fixes bugs and introduces
candidate features. The first bug listed led seqlib to output incorrect
results. Thanks to Sonja Kujala and Thomas Källman for helping solving
these problems.

BUG FIXES:

    - The statistics H, thetaH and Z (Fay and Wu's test) were incorrect.
      H was incorrect since version 1.0 and Z was incorrect since the
      beginning. The error was causing a deviation or an order of ~0.1
      of statistics H and Z that was consistent between simulations and
      computations from real data.

    - The method ``rempos`` (of Align and align) did not terminate
      correctly sequence strings.

    - The coalescent simulator used population indices starting at 0
      when S was 0 and from 1 otherwise. Now indices always start at 0.

    - ``abc_stats`` didn't support fixed parameters (when min=max).

    - a 'collinear matrix' error message was returned by ``abc_fit``
      when one (or more) of the statistics where not variable within the
      local region. Now, abc_fit takes an argument force that forces it
      to proceeds to the analysis in such case (as long as at least one
      statistic is variable), although it is always preferable that at
      least as many independent statistics as the number of parameters
      to estimate are available.

    - the pyinter class container had a method ``column()`` whose use
      led to a bug.

ADDITIONS

    - class ``tree`` (of toolkit) enhanced with new methods, including
      ``midroot()`` that performs automatic rooting using the midpoint
      method.
    - creation of class ``codeml``.
    - creation of function ``phyml3`` (planned to replace the class phyml
      and using PHYML v. 3).
    - creation of command ``picker`` to replace ``family`` (it is strongly
      advised to keep using ``family``).
    - new statistics in ``Polymorphism`` and ``polymorphism()``,
      including singletons.
    - member ``shuffle()`` in class ``container``.
    - argument "strict" of ````container```` classes' method ``find()``.
    - ``clustal()`` uses temporary files, allowing its use in several
      parallel instances of Python.
    - creation of the command ``interLD``, allowing computing linkage
      disequilibrium between two loci (based on haplotypes, considering
      all alleles), and test it by random permutations.

**1.1** 

No information available.

**1.0** - 07/06/09

The changes from version 0.8 are listed below. The list is unfortunately
non-exhaustive. In particular, many small interface changes and bug
fixes are not listed. The changes are grouped by subpackage:

    - ``seqlib`` (top-level)
        - A user manual is now included.
        - The utils commands must be launched through the had-oc module
          ``seqlib.run``.
        - The presence of external applications is monitored by the file
          ``config.py`` created by ``setup.py`` at installation.
        - Ported to Python 2.6 (this is now the primary target).
        - The structure is changed: the library is split into ``core``,
          ``pyinter``, ``toolkit``, and ``utils``.
        - The contents of ``pyinter`` and ``toolkit`` are both loaded
          both in the top ``seqlib`` namespace.
        - The doxygen documentation is fixed (but some formatting
          troubles remain).
        - The package is reorganized to fit to a correct Python module.

    - ``core``
        - Errors generated in seqlib.core's code systematically raise
          ``SeqlibException``.
        -  The previous ``error()`` flag system is removed.
        - ``Container``/``Align``:
            - All sequences have an integer label (supposed to indicate
              population membership).
              This modification is supported by ``IO``, ``Polymorphism``
              and ``Coalesce``.
            - The internals of both classes are reimplemented, allowing
              better performance for data access.
            - ``vslice(a,b)`` supports b>a (returns an empty alignment)
              & fixed bug : the groups were dismissed in all slices.
            - The underlying class Sequence is removed.
            - Accessors ``set()`` and ``get()`` for nucleotides.
            - An undue error was raised when the last sequence was removed.
            - ``Align::Align(unsigned int, unsigned int, char**)``: this
              function was not implemented
            - ``fget()`` replaces ``get()``.
            - ``hlice()``: the interface is changed to fix the one
              ``vslice()``.

        - Added reading modes "e" and "a".
        - ``Site``:
            - is completely rewritten, with minor interface changes.
            - The class reads the group information from the ``Align``
              objects (passed by address).
            - The header is now in ``Polymorphism.h``.
            - Did not compute ``pread()`` correctly.

        - ``Polymorphism``:
            - ``pairwise()`` is removed; one now needs to use
              ``analyze()`` with group labels.
              a bunch of group label stats (Fst, Kst, Hst, Gst, Snn and
              site pattern counters) are added.
            - analyze's option outgroup removed; one needs to specify an
              outgrup sequence using group label 999.
            - Si is removed.
            - as a general rule, stats that cannot be computed and stats
              are set to default values (0).
              That concerns per-site statistics (when no analyzable
              sites are available), stats that require an outgroup.
            - Added ``haplotype()``, ``LD()``.

        - ``VAlign``: ``clear()`` function added to ``VAlign``.
        - ``Coalesce``:
            - Options ``skipStatistics`` and ``saveAlignments``. Storage
              of ``Align`` objects.
            - Support for null mutation rate or FSS.
            - Supports simulations with only 1 sample.
            - Intercept null migraton rates as an error.
            - By default, K is 1.
            - Using "fusion" generated a bug.
            - The generator of newick trees was unstable.

        - ``Vdouble``: added.
        - ``IO``:  
            - Supports empty fasta files.
            - ``toPhyml()``: the names are limited to 30 characters.
            - Parser supports and ignores ``\r`` characters (in both
              sequences and names).
            - Added flag delete_consensus.
            - Possible to import termination (*) for proteins.

        - ``Container``/``Align``: ``ns()`` is reimplemented (using a
          class member) to speed up repetitive calls.
        - in polymorphism analysis, a conceptual error led to
          inappropriate results of He when an outgroup or missing data
          were present.
        - A couple of compilation errors are fixed (use of _N and _S symbols).
        - ``BppWrapper``: Ts/Tv is arbitrarily set to 0. if Tv=0.
        - Added class ``LDContainer``.
        - ``Staden``: supports for ``\r`` characters.
        
    - ``pyinter``
        - ``container``/``align``:
            - All sequences have an integer label (supposed to indicate
              population membership).
            - The sequence readers, writers, simulators and analyzers
              are modified accordingly.
            - Added methods ``str()``, ``missing()``.
            - added ``filter()`` method to ``align``.
            - An undue error was raised when the last sequence was removed.
            - Long integers are supported for group labels.

        - ``polymorphism()``: interface change:
            - no outgroup option anymore (the outrgroup should be one
              of the sequences of the ``align`` object, with group label
              999).
            - interpop stats are automatically computed when several
              pops are defined in the object.
            - added "haplotypes" key.
            - (BPP) Ts/Tv is arbitrarily set to 0. if Tv=0.

        - ``pairwise()`` is removed.
        - ``consensus()`` is moved to ``utils``.
        - in polymorphism analysis, a conceptual error led to
          inappropriate results of He when an outgroup or missing data
          were present.
        - ``dist()`` is removed.
        - ``interface()`` is removed.
        - ``align``:
        - ``simfasta()``:
            - added argument simErrors.
            - fasdir can be None/False.
            - returns a list.

        - ``xml``: raises exceptions in case of error.
        - ``xml`` ignore ``\r`` characters.
        - Simulators had a conflict with the name He (used for both Hd and He).
        - ``CoalesceSimulator`` renamed ``coalesceSimulator``.
        - ``msSimulator``: can compute orientation-based statistics.
        - Added ``SkipStats`` to simulators.
        - ``rlen()`` moved to pyinter.
        - Additions: ``nj()``, ``staden_consensus()``, ``muscle()``.
        - ``newick()``: supports ``\r``.
        
    - ``toolkit``
        - ``phyml``: debugged.
        - ``longest_orf()`` has been reimplemented - the external
          application getorf is no longer required. Faster.
        - The function ``rlen()`` is moved from the module seqtools.py
          to tools.py.
        - ``tree``: bug fixed in ``frequency_nodes()``.
        - ``gb``:
            - was sometimes unable to import TITLE.
            - supports any carriage return.

        - Added functions ``stats()`` and ``correl()``, and classes
          ``paml``, ``updater`` and ``timer``.
        - distribution.py is deleted.
        - ``cprimers()``, sprimers(): bug fixes and minor improvement of
          usability.
        - ``rc()``: faster implementation.
        - ``backalign()``: added option ``name_table``.
        - ``flocate()`` replaces ``locate()``. Use ``locate()`` for the
          fast (and only available) implementation.
        - ``ranges()``: supports unsorted data.
        - ``primer3``: the fixed parameters are put into string_init and
          string is reinitialized at each call to ``find()``.
        - ``isstream``: broken method ``read()``.
        - ``chisquare()``: the function was broken, and returns the
          critical value for (n+1) ddl instead of n.
            
    - ``utils``
        - The module ``tools`` is removed. The classes implementing abc
          commands are now directly in the seqlib.utils namespace.
        - ``rs`` (and other rs* commands) are removed and replaced by
          abc_* commands and a set of classes. Note that the behaviour
          of ``rs`` can be reproduced by ``abc_sample`` and ``abc_fit``
          (with regress=False).
        - Approximate Bayesian Computation: The commands ``abc_sample``,
          ``abc_fit``, ``abc_stats`` and ``abc_psimuls`` are introduced.
          ``rs`` and associated commands (``rsplot``, etc.) are removed
          and replaced by commands names ``abc_sample``, ``abc_fit``,
          etc. the abc family of commands extends the features
          previously incorporated in ``rs``, but also incorporates a
          number of modifications from version 0.8.
        - Faster implementation of the ABC discretization method.
        - Added commands: ``fasta2phyml()``, ``winphyml()``,
          ``translate()``, ``instruct()``, ``extract_clade()``,
          ``extract_nclade()``, ``infos()``.
        - ``sprimers``: significantly improved, with option additions
          and behavior change. In particular the blast check step was
          refined (with significantly improved stringency). The position
          score (3' preference) was wrong (reverted because of BLAST).
          Bug fixed (gaps were allowed in blast searches).
        - ``analyser()`` and ``stats()`` outputs Gst (and so on) -
          ``stats()`` supports group labels in input fasta file.
        - ``codalign()``: changed to support longer file names, and
          doesn't alter names anymore (spaces replaced by underscores).
          Added option "software" (can use ``muscle`` rather than
          ``clustalw``).
        - ``fasta2nexus()``: generates valid protein nexus files.
        - ``analyzer()`` becomes ``analyser()``.
        - input/output arguments syntax extended or modified for:
          ``clean_seq()``, ``clean_tree()``, ``codalign()``,
          ``concat()``, ``concatgb()``, ``extract()``, ``extract_clade()``,
          ``fasta2nexus()``, ``fasta2phyml()``, ``fg2gb()``, ``matcher()``,
          ``rename()``, ``select()`` (and others).
        - ``select()``:
            - removes the "*" wild-card.
            - the list file must use newlines as item separators.

**0.8**- 22.10.08

    - ``core`` now compiles successfully with GCC 4
    - ``tree``:
        - fixed: when several trees where imported, they were all
          accidentally merged (problem with superficial copy).
        - added: ``rename_leaves``, ``clades``, ``frequency_nodes`` methods.

    - ``Polymorphism`` and ``polymorphism`` provide the list of
      polymorphic sites
    - ``discret`` becomes ``rs_analyse`` and now produces an output
      with stats.
    - ``stats`` function added to ``utils``.
    - ``coalesce`` output was crappy (ie not supported by function ms)
      for simulations without polymorphic sites.

**(4.)0.7.2** - 16.10.08

A few improvments and bug fixes.

**(4.)0.7.1** - 16.09.08

    - pylab import generated crash when matplotlib was absent (fixed:
      the presence of matplotlib is no longer enforced)
    - useless params output by sprimers was fixed
    - Hnew of polymorphism renamed to Z
    - default values of simulators changed
    - added a trim option to discret
    - sprimers has been improved:
        - filter replaced by filter1 and filter2 (filter1 occurring before the blast step)
        - both sorting steps (before and after the blast step) were wrong

    - additions:
        - ranges, ungap, names and rename as utils commands
        - names, duplicates, contains_duplicates  and no_duplicates as fasta methods
        - translation in toolkit
        - nexus method in fasta.align and fasta2nexus command

**(4.)0.7.0** - 12.09.08

    - fasta string import extended to containers.
    - plot is depreciated replaced by
        - discret (doesn't clean up empty classes any more)
        - plot

    - align is fixed to support alignments with length = 0
    - Random seeds are now static: that means that seeds are set by the complete program.
      Previously (since 4.0.4), different objets created with less than 1 second of delay had the same seeds.
      As a result, rs simulated identical loci, resulting in increased variance of statistics and a very poor estimation.
    - rs:
        - error in time formatting after more than one day (fixed).
        - incremental counting of time (a priori, transparent change)
        - trims 0-frquency classes out of prior
        - fixed bug cause by Random error (above)
        - fixed error in SPM (M was ignored and errorly fixed at simul's default value!)
        - uses a harcoded (not in a separated file) very large prior distribution.

    - the setup.py script is radically modified:
        clean: removes object files and cleans sip
        configure: only creates a Makefile
        sip: compiles sip
        install: same as before
        The installation process should go::

            > python setup.py sip
            > python setup.py configure
            > make
            > python setup.py install

        setup also accepts some arguments to modify a few system options
    - sprimers check was so stringent that the step was completely removed
    - gb: added method rc (reverse-complement)
    - utils: added commands extractgb and gb2fas (no doc written yet)

        
**(4.)0.6** - 27.08.08

    - added composition() method to fasta base class.
    - additions to Toolkit:
        - genalys2fasta()
            - this function is directly imported from a script "Genalys2Fasta" (version 05/07/06).
            - the function has not been tested at all (more than the previous script).
              there may be a problem if initial files were not named .ab1.

    - blast hits are sorted according to e-values.
    - codalign(): cds argument may be a container instance.
    - primer3: check() is made a different function from pair() and find_and_pair() (both lose the argument check)
    - created a function flocate() in Toolkit (faster implementation on the basis of a regular expression search).
    - blast: inclusion of query-from, query-to and midline in hits entries.
    - added fasta string import to IO (core) and to align (pyinter) constructor.
    - ms parser draws nucleotides randomly.
    
**(4.)0.5** - 19.08.08

    - additions to Utils:
        - extract
        - fasta2mase
        - cprimers
        - matcher
        - staden2fasta
          This function re-implements part of the program tofasta. As
          of version 2.5 tofasta is now deprecated. Changes: (1) the
          interface changes, (2) CONSENSUS is always deleted, (3) dot
          ('.') characters are supported and resolved using CONSENSUS
          (before deletion), (4) no generation of consensus sequences.

    - bug fixed in mase parser.
    - mase extended: copy from align instances, and writer function.
        
**(4.)0.4** - 18.08.08

    - created help page for utils direct calls.
    - io.ms() IO.ms() both use (by default) standard input.
    - Align and Container had a problem in copy constructors: an empty sequence (instead of no sequences at all) was added when copying from an empty object.
    - Ms (and therefore IO.ms() and io.ms()) did not support an trailing empty null simulation.
    - dist() function (in pyinter, manips) was fixed and the order of parameters in the output tuple was changed (to be compatible with polymorphism::pairwise())
    - dist(): argument type added.
    - slider() added to toolkit.
    - introduced mode debug for running utils function through seqlib (shows full error message).
    - extensions of rs: introduction of option rule and addition of model 6 (using ms).
    - ms incorporated in the package.
    - Random used to take its address on memory as second seed.
      This seemed to cause problems depending on the system and was changed to a constant second seed (0.).
      The first seed is still the system time, and it's still possible to set arbitrary seeds.
    - added import_posterior, clean_tree, clean_seq concatgb and concat functions to Utils.
    - non-keyword arguments are passed to Utils functions (they may be ignored, as well as unknown keywords.
    - primer3 default Tm range was much narrower than claimed (61-65 instead of 55-65).
    - a problem with the function ranges of prior was fixed (appeared when using priors with more than 1 class).
    - rs accepts a maxsim argument to stop simulations after a givennumber of simulations (by default, 1000000000).


**(4.)0.3** - 07.08.08

    - SIP is now included in the distribution.
    - setup.py changes:
        - options removed: pyinc, pylib, cpath and compiler
        - compiles SIP
        - enforces the use of g++

    - Toolkit/blast: each hit entry contains:
        - 'pos', the positions of the first Hsp (individual hit fragment),
        - the e-value ('e'),
        - 'identity', the identity rate

**(4.)0.2** - 05.08.08

    - Polymorphism: Possible bug: count of segregating sites when MULTIPLE is true (sites may be missed).
    - the names of some private members (such as _A) in Changes, Coalesce and Polymorphism have been changed to make Xcode compiler happy.
    - two memory leaks have been fixed in Sequence and one in Site (causing problems to Polymorphism and Coalesce).
  
**(4.)0.1** - 04.08.08
  - Coalesce: a significant memory leak was fixed (in the top-level class Coalesce).
  - The version includes all changes of alpha versions of 4.0.0 (and possible bugs).

**(4.)0.0.4**

    - change in setup.py: now uses the sipconfig module to finds Python installation paths

**(4.)0** - 28.July.08 (alpha4)

    - utils::rs::rs finished (not tested)

**(4.)0** - 24.July.2008 (alpha3)

   - SeqLib is released publicly and numbering is reset to 0.
   - bugs fixed in setup.py:
        - option BPP not processed correctly.
        - inclusion not system independent.
        - flush output during compilation (not a bug).
        - determines itself python installation details.

   - incorportation of utils (preliminary)
        - codalign
        - rs (on-going)

   - misc.:
        - gb parser temporarilly failed if >1 '=' sign in feature (bug fixed)
        - in seqtools, locate() used amb_compare instead of compare (bug fixed)
        - addition of lfimport function in fasta
        - compilation in optimization mode 3 (hopefully faster)
        - missing imports in dataset and tools
        - dataset's select method extended and modified
   
**(4.)0** - 08.July.208 (alpha2)

   - formatting the release (license, readme, setup script).
   - Bio++ is made optional
   - toolkit is completely incorporated
   - doxygen documentation

**(4.)0** - 23.May.2008 (alpha1)

   KNOWN ISSUES
      - IO/MS:
         - mingw support is removed (has to be added in skip_line and next_line functions!)

      - Consensus/Polymorphism/Staden/IO:
         - noted a possible problem(in consensus generation): example A+T+A (rigorous) ->W+A -> A ( = problem)

      - newick is not stable, apparently (TODO: use standard libraries for XML and tree)
      - reprogram XML using default python modules
      - reprogram tree and newick
      - memory leak in rs
   
   CHANGES
      - Lots of changes in the interface and the implementation.
      - Not all changes are listed below.
      - creation of the seqlib namespace
      - added a simplified wrapper of vector for Align (VAlign) and unsigned int (Vuint) with no checking
          these classes provide a SIP interface and are designed for being used by a Python wrapper (never directly)
      - incorporation of the module coalesce
         - deletion of BaseCoalesce (classes are integrated in the Seqlib hierarchy)
         - other classes are just ported with minor compatibility changes
         - Coalesce:
            - pi attribute of Coalesce changed to Pi
            - uses new version of Polymorphism
            - removed clear_error
            - statistics of irrelavant data type are initialyzed
            - in case of error: sets everything to 0/default
            - apparently its impossible to set alpha<0. the blocking is maintained.
            - blank line added after header in data file, plus between simulations for microsats
            - added tMRCA statistic

      - other former classes of the BaseCoalesce hierarchy are in a "coalesce" namespace
      - creation of BppWrapper:
            - available only with mode dna at the moment (translated as DNA for bpp)

      - Pairwise: deleted and transfered to Polymorphism
      - ReadingFrame:
         - compatibility changes
         - the constructor closes the input file after use
         - return Vuint objects

      - Consensus (incorporated in Polymorphism):
         - doesn't write anything anywhere, except a report in an internal string
         - note: some use of vector (check whether any other container may be better)
         - missing: missing code in input (?)
         - disagrement: code for disagreemnt in output (non rigorous mode) (Z)

      - Polymorphism:
         - constructor calling directly analyze
         - both take more arguments
         - the same object can be used several times
         - analyze returns the number of polymorphic sites or -1 in case of error
         - site accessors are deleted (sites are not stored any more)
         - sites with more than 2 alleles are accepted: always: eta
         - consensus() function
         - pairwise() function collecting Pairwise functionalities
         - wrong data type leads to 0 polymorphism, not error (false characters are taken as missing)
      - Site:
         - don't store actual data anymore (no more get() accesser)
         - carriers reimplemented as a pointer, and initialized at construction
         - minor change in interface
         - no destruction of the data pointer
         - automatic conversion to upper case
         - possible to set an outgroup with mode b - otherwise, 0 are taken to be ancestral
         - the linked list feature is DELETED

      - ReadingFrame:
         - observations (these  are no change):
            - the usage of newlines for separating exons is enforced in constructor but no in method import()
            - the format is very sensitive to spaces, don't add any other positions than specified 
            - the numbering of the input is not converted

      - GetMS:
         - renamed to Ms and linked to from IO
         - copy is implicitely allowed
         - the class manages a pointer to the stream
         - size limits are removed

      - GetStadenAlign:
         - renamed as Staden
         - simplified interface: only import which returns an Align
         - import uses CONSENSUS to resolve . characters
         - import deletes CONSENSUS

      - SequenceContainerIO:
         - renamed as IO
         - significant changes of the interface: reading functions return an object and writing functions take an object as argument
         - no longer length limit (use of queues)
         - incorporates a call to Staden::convert (less efficient because of an additional object copy)
         - incorporates Ms call

      - Seqlib:
         - removed DATA_TYPE, MINIMUM_READ, SKIP_RM, SMALL_DIFF and MULTIPLE_HITS_ACCEPTED
         - change interface of isValid() to accept type character
         - isValid() is made case-insensitive

      - Sequence:
         - add constructor Sequence(number, char) to initialize an empty sequence
         - concatenating sequences with different names is no longer fatal
         - oor errors for get(), set(), rem()
         - suppress build_helper() helper function and lname, lseq members
         - pname(), psequence() become name() and sequence()
         - copy constructor supports overwriting

      - SequenceContainer:
         - remSeq() now checks
         - equalize() takes an optional padding character as argument
         - pname, psequence, psequence2 renamed to name, sequence and getSequence (respectively)
         - slice() becomes hslice()
         - still doesn't perform any test

      - SequenceAlignment:
         - get() checks
         - binSwitch() checks p and binary data
         - subset() becomes vslice() (with an overloaded function vslice(a,b)
         - vslice(vector<>) re-implemented (a bit) more efficiently, but now the order in the vector is strictly followed

**3.2.8** - 28.04.08

   - 28/04/08: SequenceAlignment::getColumn returns NULL in case of invalid index (and error statements)
   - 13/03/08: slice now accepts a=b arguments

**3.2.7** - 12/03/08

   - Pairwise: dist() was wrongly divided by the number of (overall) polymorphic sites

**3.2.6** - 04/03/08

   - GetMs: reading buffer increase to 500000 (instead of 50000): support larger lines (ie simulations with many more sites)
   - ReadingFrame: added function last()
   - Polymorphism: change in D(): in case the variance is close to zero (compared to SMALL_DIFF) is catched and its set to zero
     this avoids taking the square root of a (slightly) negative number and having an indefinite #IND D (although it will stay infinite #INF)
   - Added field SMALL_DIFF in Seqlib (used by Polymorphism:D() as stated above)

**3.2.5** - 28/02/08

   - Changes in SequenceContainer::slice()
       both arguments are made int, no default value
       checks are now performed and an error is set in case of any problem with indices
       upon such case, an empty container is return

   - Bug in SequenceContainer - SequenceAlignment:
     error generated when the last sequence was removed in SequenceAlignment, 
     lseq was not set to 0 because of missing virtual linking

**3.2.4** - 25/02/08

   - Bug fixed in GetStadenAlign: in getshift(), the rewind loop did not seem to work properly
     it has been replaced by a simple close+open operation
     required storage of the file name

**3.2.3** - 23/02/08

   - Bug fixed in SequenceContainer::remseq(): the loop for renumbering did not consider the last step
   - Iterators of SequenceAlignment are converted in SequenceAlignment*
   - SequenceContainer::build_helper() is deleted and replaced by its actual loop in SequenceContainer and descendants

**3.2.2** - 14/02/08

   - GetStadenAlign: bug fixed, a bug was generated by constructor GetStadenAlign(const char*)

**3.2.1** - 11/01/08

   - The SeqlibException's have been abandonned for the moment.
      Check ::error() instead (should be an empty string)
   - Changes in GetMS() (public functions added)
   - void close():
        - destroy the input stream
        - good() will return false
        - calls to import(bool) will generate errors
   - SequenceAlignment simul(bool binary = false):
        - wraps import(bool) (useful for Python where import is reserved)
        - its adviced to use import(bool) in C++

**3.2.0** -27/10/07

   - Each class has its own header file
   - The library is compiled as a static archive
   - All output goes through Seqlib::error( ) and generates a SeqlibException
   - typedef uint removed
   - Several bug fixes and changes (including in the interface)
   
Polymorphism changes:
   - site(int) returns the position of the site (no longer the Site object itself)
   - getsite(int) returns the Site object
   - sites( ) is removed
   - Pi( ), tW( ), tH( ) and tHnew( ) return 0 if lseff is zero

**3.1.1** - 18/08/07

   - Frame.h added with ReadingFrame and CodingSite (they are not incorporated in the Seqlib hierarchy)

**3.1.0** - 02/08/07

   - GetStadenAlign.h becomes Import.h
   - creation of GetMS added to Import.h

**Unnumbered** - 01/AUG/2007

   Polymorphism:
   - added access method site(int)
   - bug fixed in Site (see documentation of Site)
   - outgroup value checked
   
**3.0** - 31/07/07

   - SequenceAlignment splitted into SequenceContainer (just a list of sequences) and SequenceAlignment (forced to be equalized)
   - SequenceContainerIO replaces (with no notable changes) SequenceAlignmentI and O (note that it is a SequenceContainer)
   - Creation of Pairwise comparing to SequenceAlignment (divergence-like class)
   - GetStadenAlign is updated (more changes in header files)
   - Classes are grouped following kinda logic
        - Seqlib.h: Seqlib, Sequence, SequenceContainer, SequenceAlignment, SequenceContainerIO
        - Polymorphism.h: Site, Polymorphism, Pairwise
        - GetStadenAlign.h: GetStadenAlign

   - Bug fixed in SequenceAlignment::build_helper(): initialization of rank

   **Class hierarchy**
      - Seqlib
            - Sequence
            - SequenceContainer (has Sequence)
                - SequenceContainerIO
                - SequenceAlignment

            - Site
            - Polymorphism (has Site, SequenceAlignment)
            - GetStadenAlign (has Site, SequenceAlignment)

**2.2** - 25/MAY/07

   ReadingFrame: constructor accepts the index of an outgroup that will not be included 

**2.1** - 23/FEB/2007

   Polymorphism:
   - Create from a combination of code from previous classes Analyser and SequencePolymorphism (from Seqlib 1).
   
**2** - 23/02/07

   - The library is written on a c-like fashion, data storage is malloc (for sequences) and linked list (new) for sequence alignments
   - Input and output are interfaced by two classes, SequenceAlignmentI and SequenceAlignmentO
   - Seqlib is introduced as a general base class containing DATA_TYPE, MINIMUM_READ, SKIP_RM and FORCE_ALIGNMENT

**1.2** - 10/JUN/2006

   Changes in ReadingFrame:
   - allowing different codon start
   - good( ) function removed
   - reads into an open stream
   - frameQ created

**1.1** - 16/MAY/2006
   
   ReadingFrame: corrected error in NS/S sites per codon: mutations to stops were not excluded, now they are   
   
**1**
   
   - SequenceContainer class hierarchy, data storage as vectors

**0**
   
   - no information
