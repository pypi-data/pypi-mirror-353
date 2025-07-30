.. _manual-coal:

---------------------
Coalescent parameters
---------------------

The coalescent theory
======================

The coalescent theory is a statistical framework describing the 
property of the genealogy of a sample based on the population's 
properties. The coalescent only addresses the history of a given sample 
(backward in time, until the most recent common ancestor). By being 
sample-centered, and offering the possibility of ignoring, among the 
events having affected the population, all those that did not affect 
the sample, the coalescent theory is an efficient analytical and 
computational tool. The basic idea is to model simulated data sets 
based on a (potentially complex) population structure and history. There
are many computer programs performing coalescence simulations, offering
a wide array of functionalities. EggLib incorporates a coalescent
simulator, pursuing those particular aims:

* Integrate several tools within a single, consistent, piece of software
  (data management, diversity statistics, coalescent simulation) for
  improved efficiency when they are used together.
* Support features not available elsewhere, or not together (arbitrary
  mutation models, homoplasy, delayed samples, diploid model with partial
  self-fertilization).

There are various variants of coalescent models, differing in how many 
factors they implement regarding subpopulation, reproduction regime, 
recombination and gene conversion, and so on. In short, the coalescent 
simulator of EggLib assumes a model with :math:`N_0` diploid 
individuals (but it is straighforward to consider it as a model with 
:math:`2N_0` haploid individuals). This number of individuals is 
expressed per population when there are several. The size of 
populations can be set individually, and changed over time. Each 
population can have its own self-fertilization rate (which can be 
changed over time as well). All rates of the migration rate matrix can 
be set independently, and changed over time. There are instant events 
set at fixed point in time that can implement large-scale events 
(population extinction, founding events, and introgression). Finally, 
recombination and a wide array of mutation models are allowed, enabling 
the simulation of various types of genetic markers with or without 
homoplasy.

The basics
==========

The coalescent simulator lies in a module of its own, :ref:`coalesce 
<pycoalesce>`. The interface is the class :class:`.coalesce.Simulator`. 
To perform simulations, you need to create an instance of this class. 
There can be several instances at the same time if needed. If 
simulations must be run sequentially, even with different models, it is 
better to use the same instance to profit from the optimization system 
of EggLib. However, if the number of populations should change, it is 
required to create a new instance (see the next paragraph).

The constructor of :class:`!Simulator` instance takes one required 
argument, the number of populations. It is possible to pass almost all 
parameters as additional arguments (they must be passed in the 
``keyword=value`` format). See the example below::

    coal = egglib.coalesce.Simulator(1, num_chrom=[20], theta=4.0)

This line defines a model with a single population, with 20 samples and
a :math:`\theta` of 4.0. The created instance, here
named ``coal``, can directly be used to perform simulations and/or
setting parameter values (see below).

Note on the number of populations
=================================

A characteristic of EggLib's coalescent simulator is that the number of 
populations is fixed and immutable during the course of a simulation. 
This does not mean that classical features of population genetics 
features such as population extinction, fusion, and split cannot be 
implemented. All those events can be implemented in a way directly 
comparable to other pieces of software. A non-existent population is a 
population that does not contain any samples, and to which all pairwise 
migration rates are set to zero. Then populations can appear to go 
extinct or, on the contrary to be created using this combination of 
parameters. This can be understood as a fixed number of demes in an 
environment that provides a constant number of sites able to harbour a 
population. Populations are extinct when the demes does not contain
samples (and is not allowed to receive any). We stick however to the
term of *population*.

From a programming point of view, this means that the user of the 
:class:`!Simulator` class is required to set the number of 
populations to the total number of populations over the full history of 
the model. In practice, populations which will be created (or will be 
created by a split, thinking backward), must already be present since 
the start of the simulation (with zero samples and with all migration 
rates to them set to 0). Consider the following model:

.. image:: /pict/model1.*
   :height: 200px
   :width: 200 px
   :align: center

It should be noted that, in this kind of representation of coalescent 
models, the present is a the bottom but, since the coalescent is 
backward in time, those models must be read from bottom to top, as 
indicated by the arrow. Still, the "biological" course of time is from 
the top to the bottom.

In this model we have two populations that merge at some point back in 
time. Based on EggLib's principle of constant population number, one 
population is assumed to merge into the other (here, the second 
population merges the first one), and will remain as some kind of empty 
slot. (It is possible to "reactivate" a population further back in time 
if needed by activating migration rates to this population and/or 
setting an instant introgression event.)

To implement this model, the following code will suffice::

    coal = egglib.coalesce.Simulator(2, num_chrom=[20, 20], theta=4.0)
    coal.params.add_event('merge', T=0.1, src=1, dst=0)

The parameters dictionary-like
==============================

You may have noticed that the last example used the attribute
:py:obj:`~.coalesce.Simulator.params` of the :class:`!Simulator` 
instance. This attribute is holding all simulation parameters and can be 
used to modify almost all parameters. Actually, most parameters can be 
both set either through the constructor or this property although there 
are several exceptions (see the review of parameters in the next 
section).

:py:obj:`!params` acts like a dictionary (actually it is a 
:class:`.coalesce.ParamDict` instance). Compared with normal 
:class:`dict`, it has additional methods and, most importantly, it 
won't let you add or remove keys (which would not have any meaning). 
There are also restrictions on the values parameters can take.

If one uses ``print(coal.params)``, it won't yield anything useful. 
However, it is possible to convert the parameters into a genuine 
:class:`!dict`, and display it::

    >>> coal = egglib.coalesce.Simulator(num_pop=1)
    >>> print(dict(coal.params))
    {'num_pop': 2, 'num_sites': 0, 'recomb': 0.0, 'theta': 4.0, 'num_mut': 0, 'mut_model': 'KAM', 'TPM_proba': 0.5, 'TPM_param': 0.5, 'num_alleles': 2, 'rand_start': False, 'num_chrom': [20, 20], 'num_indiv': [0, 0], 'N': [1.0, 1.0], 'G': [0.0, 0.0], 's': [0.0, 0.0], 'site_pos': [], 'site_weight': [], 'migr_matrix': [[None, 0.0], [0.0, None]], 'trans_matrix': [[None, 1.0], [1.0, None]], 'events': [<event_index=0;src=1;dst=0;cat=merge;T=0.1>], 'max_iter': 100000}

It is also possible to generate a string summary of the current value of parameters.
This is more readable, but the format might be changed (for example if new
parameters are added) so it should not be used in programs unless as
for information only (note that the parameter ``max_iter`` is not included)::

    >>> print(coal.params.summary())
    Number of populations: 2
        Population 1:
            Single samples: 20
            Double samples: 0
            Relative size: 1
            Growth rate: 0
            Selfing rate: 0
        Population 2:
            Single samples: 20
            Double samples: 0
            Relative size: 1
            Growth rate: 0
            Selfing rate: 0
    Recombination rate: 0
    Migration matrix:
        0        0
        0        0
    Mutation rate: 4
    Fixed number of alleles: 0
    Mutation model: KAM
    Number of alleles: 2
    Random start allele: 0
    Custom transition matrix: 0
        1        1
        1        1
    Number of mutable sites: 0
    Number of changes: 2
        Change 1: Admixture
            Date: 0.1
            Population: 1
            Other population: 0
            Probability: 1
        Change 2: Pairwise migration rate change
            Date: 0.1
            Source: 0
            Destination: 1
            Rate: 0

Below we list all parameters of the coalescent simulator, with useful details.

Number of populations and population properties
===============================================

The table below lists all parameters related to the population structure.
The temporal changes of this structure as described in :ref:`events-params`.

+-----------------+---------------------------------+-------------+---------------------+
| Parameter       | Meaning                         | Default     | Notes               |
+=================+=================================+=============+=====================+
| ``num_pop``     | Number of populations           | Required    | Required; fixed     |
+-----------------+---------------------------------+-------------+---------------------+
| ``num_chrom``   | Number of haploid samples       | 0           |                     |
+-----------------+---------------------------------+-------------+---------------------+
| ``num_indiv``   | Number of diploid samples       | 0           |                     |
+-----------------+---------------------------------+-------------+---------------------+
| ``N``           | Population sizes                | 1.0         |                     |
+-----------------+---------------------------------+-------------+---------------------+
| ``G``           | Population growth/decline rates | 0.0         |                     |
+-----------------+---------------------------------+-------------+---------------------+
| ``s``           | Population selfing rates        | 0.0         |                     |
+-----------------+---------------------------------+-------------+---------------------+
| ``migr``        | Global migration rate           | 0.0         | Only in constructor |
+-----------------+---------------------------------+-------------+---------------------+
| ``migr_matrix`` | Pairwise migration rates        | 0.0 for all |                     |
+-----------------+---------------------------------+-------------+---------------------+

.. _list-params:

List-like parameters
********************

Except ``num_pop``  and ``migr``, all parameters are lists
(``migr_matrix`` is a square matrix). Their dimension is determined by
the value of ``num_pop`` provided to the constructor.
These arguments must be provided as a list of length matching the number of
populations::

    >>> coal = egglib.coalesce.Simulator(num_pop=4, num_chrom=[20,20,20,20], N=[1,1,1,0.2])

When using the :class:`!dict`-like features of :py:obj:`!params`, it is possible
to get or set only one item using the bracket operator::

    >>> print coal.params['N'][3]
    0.2
    >>> coal.params['N'][2] = 0.5
    >>> print(coal.params['N'])
    [1.0, 1.0, 0.5, 0.2]

The whole list of values, or a slice of the list, can be set at once:

    >>> coal.params['G'] = 1, 2, 3, 4
    >>> coal.params['G'][2:4] = 2.5, 2.7
    >>> print(coal.params['G'])
    [1.0, 2.0, 2.5, 2.7]

The concerned parameters are:

* ``num_chrom`` and ``num_indiv`` -- EggLib's coalescent simulator uses
  a diploid model (assuming a reference population with :math:`N_0`
  diploid individuals), so it is possible to define samples as diploid
  (individuals for which both chromosomes are sampled) or haploid
  (individuals for which one random chromosome is sampled). If ``s`` is
  0 (see below), there is no difference between using ``num_indiv=x`` or
  ``num_chrom=2*x``, and the model is equivalent to a haploid model with
  :math:`2N_0` individuals. It is possible to mix haploid and diploid
  samples (the total sample size is always equal to ``num_chrom +
  2*num_indiv``).

* ``N`` -- The relative size of populations (expressed relatively to the
  standard, current, population size). The default, 1.0, means that all
  populations have the size of the reference population. Within the framework
  of the   coalescent theory, it is never needed to assume a value for :math:`N_0`
  and several other parameters a expressed relatively to it.

* ``G`` -- Exponential growth/decline rate. If the rate is larger than
  zero, the size of the population decreases exponentially backward in time
  (the population has been growing exponentially if we think forward). If
  the rate is smaller than zero, the size of the population increases
  exponentially (shrinking exponentially if we think forward). In the later
  case, past population size can become so large that it is not possible to
  complete the simulation due to computational limitations. Negative values
  of ``G`` should be used with caution and, probably, used with a past event
  stopping the growth. The size of the population at time :math:`t` in the
  passed is given by :math:`N_o \exp^{Gt}`, as in the ``ms`` `software
  <http://home.uchicago.edu/rhudson1/source/mksamples.html>`_.

* ``s`` - The self-fertilization rate. It is the probability (between 0 and 1,
  both included) that one individual is the offspring of an occurrence of selfing
  reproduction. Note that different populations can have different values. In
  this case, the user should be aware that individuals migrating between
  populations with varying values of ``s`` will assume the self-fertilization
  of the new population after migration.

.. _migr-matrix:

The migration matrix
********************

The ``migr`` argument of the :class:`!Simulator` constructor allows to 
avoid setting the whole matrix if all pairwise rates are identical. The 
value that must be provided as ``migr`` value is per-population overall 
emigration rate, such that each pairwise migration rate will be set to 
``migr/(num_pop-1)``::

    >>> coal = egglib.coalesce.Simulator(num_pop=4, migr=6.0)
    >>> print(coal.params['migr_matrix'])
    [[None, 2.0, 2.0, 2.0], [2.0, None, 2.0, 2.0], [2.0, 2.0, None, 2.0], [2.0, 2.0, 2.0, None]]

It is also possible to use the method :meth:`~.coalesce.ParamDict.set_migr`
of :attr:`!params`::

    >>> coal.params.set_migr(1.5)
    >>> print(coal.params['migr_matrix'])
    [[None, 0.5, 0.5, 0.5], [0.5, None, 0.5, 0.5], [0.5, 0.5, None, 0.5], [0.5, 0.5, 0.5, None]]

The argument ``migr_matrix`` represents the full matrix of pairwise rates.
The matrix above reads as:

+---------+----------+----------+----------+
|``None`` | 0.5      | 0.5      | 0.5      |
+---------+----------+----------+----------+
| 0.5     | ``None`` | 0.5      | 0.5      |
+---------+----------+----------+----------+
| 0.5     | 0.5      | ``None`` | 0.5      |
+---------+----------+----------+----------+
| 0.5     | 0.5      | 0.5      | ``None`` |
+---------+----------+----------+----------+

Note that diagonal value are set to ``None``.

Using :py:attr:`!params`, it is possible to set individual pairwise
rates within the migration matrix,
using the ``[from, to]`` operator, where ``from`` is the index of the source
population, and ``to`` is the index of the destination population::

    >>> coal.params['migr_matrix'][0, 1] = 4.0
    >>> print(coal.params['migr_matrix'])
    [[None, 4.0, 0.5, 0.5], [0.5, None, 0.5, 0.5], [0.5, 0.5, None, 0.5], [0.5, 0.5, 0.5, None]]

This operator can also be used to read values.

Alternatively, it is also possible to set the whole matrix in one call::

    >>> coal.params['migr_matrix'] = [[None, 1.0, 0.1, 0.1],
    ...                               [1.0, None, 1.0, 0.1],
    ...                               [0.1, 1.0, None, 1.0],
    ...                               [0.1, 0.1, 1.0, None]]

The argument must be a ``num_pop * num_pop`` nested list. Therefore,
the diagonal must be included in the provided value, all diagonal values
are explicitly required to be ``None``. It is possible to set the full
matrix as a constructor argument (using the keyword argument
``migr_matrix``).

Mutation models
===============

EggLib's :ref:`coalesce <pycoalesce>` module provides a flexible mutation model supporting
the standard two-allele model without homoplasy (infinite site model; ISM)
or realistic nucleotide mutation models (four alleles with homoplasy and
transition/transversion substitution bias), or microsatellite models. The
available parameters allow to extend the range of models that can be implemented.
The table below presents the parameters that can be set:

+------------------+----------------------------------+----------------+---------------------------------------+
| Parameter        | Meaning                          | Default        | Notes                                 |
+==================+==================================+================+=======================================+
| ``theta``        | :math:`\theta=4N_0\mu` parameter | 0              |                                       |
+------------------+----------------------------------+----------------+ Cannot be set together                +
| ``num_mut``      | Fixed number of mutations        | 0              |                                       |
+------------------+----------------------------------+----------------+---------------------------------------+
| ``mut_model``    | Mutation model                   | ``KAM``        | ``KAM`` -- fixed number of alleles    |
+                  |                                  |                +---------------------------------------+
|                  |                                  |                | ``IAM`` -- infinite number of alleles |
+                  |                                  |                +---------------------------------------+
|                  |                                  |                | ``SMM`` -- stepwise mutation model    |
+                  |                                  |                +---------------------------------------+
|                  |                                  |                | ``TPM`` -- two-phase mutation model   |
+------------------+----------------------------------+----------------+---------------------------------------+
| ``num_alleles``  | Number of possible alleles       | 2              | Only for ``KAM`` model                |
+------------------+----------------------------------+----------------+---------------------------------------+
| ``rand_start``   | Pick start allele randomly       | ``false``      | Only for ``KAM`` model                |
+------------------+----------------------------------+----------------+---------------------------------------+
| ``trans_matrix`` | Allele substitution rates        | All equal      | Only for ``KAM`` model                |
+------------------+----------------------------------+----------------+---------------------------------------+
| ``TPM_proba``    | Non-stepwise probability         | 0.5            | Only for ``TPM`` model                |
+------------------+----------------------------------+----------------+---------------------------------------+
| ``TPM_param``    | Non-stepwise parameter           | 0.5            | Only for ``TPM`` model                |
+------------------+----------------------------------+----------------+---------------------------------------+
| ``num_sites``    | Number of mutation sites         | 0              | 0 stands for ISM                      |
+------------------+----------------------------------+----------------+---------------------------------------+
| ``site_pos``     | Position of sites                | Evenly spread  | If ``num_sites`` is not 0             |
+------------------+----------------------------------+----------------+---------------------------------------+
| ``site_weight``  | Mutation weight of sites         | All equal to 1 | If ``num_sites`` is not 0             |
+------------------+----------------------------------+----------------+---------------------------------------+

The parameters ``theta`` and ``num_mut`` control the number of mutations
occurring in simulations. If the later option is used, the number of
mutations is fixed. In the other case, the number of mutations is drawn
randomly based on the statistical parameter.

Description of models
*********************

The different models are listed below:

* ``KAM`` (K-allele model) is a model where alleles can take a finite
  number of values. The number of alleles is given by ``num_alleles``
  (default: 2, which is the minimum allowed). The allelic values are
  in the range ``[0, num_alleles-1]``. This model can be configured with
  the following options:

  * ``num_alleles``, as stated already. Use 2 for standard diallelic
    markers. To simulate DNA sequence, use ``num_alleles=4``. The identity
    of the four bases is a matter of convention.
  * ``rand_start`` tells if the start (ancestral) allele should be
    drawn randomly among the available values. By default, the start
    allele is 0.
  * ``trans_matrix`` gives the matrix of transition weights among alleles.
    The usage of this matrix is identical to the one for the
    :ref:`migration matrix <migr-matrix>`.
    The matrix has dimension ``num_alleles*num_alleles``, with non-diagonal
    values giving the relative weights of each transition. The entry
    ``[i,j]`` gives the relative weight of the substitution from allele
    ``i`` to allele ``j``. For example, for setting DNA sequence with
    a transition/transversion rate ratio of 4, one can use::

        num_allele=4, trans_matrix=[[None, 2, 1, 1],
                                    [2, None, 1, 1],
                                    [1, 1, None, 2],
                                    [1, 1, 2, None]]

    The structure of the matrix in the above example is conditioned on
    the order of alleles. Here we assumed that the bases are sorted in
    the order: T, C, A, and G.

* In the ``IAM`` (infinite allele model), all mutations create a new
  allele. In this model, it is guaranteed that all identical alleles are
  identical by descent. The allelic value are arbitrary and should not
  be considered as allele size.

* In the ``SMM`` (stepwise mutation model), allelic values are meant to
  represent sizes and each mutation step increments or decrements the
  value by one unit. The start value is 0, and, therefore, positive
  and negative values are equally possible. Note that, to implement
  microsatellite data, it can be necessary to multiply the allelic values
  by the assumed repeat size and shift them to the reference locus size
  (in order to avoid negative value) before processing data in other
  software.

* The ``TPM`` (two-phase model) is a generalisation of the ``SMM``. In
  this model, mutation steps can be either of one unit, or drawn from a
  geometric distribution (in either case they can be either positive or
  negative). This model has two parameters:

  * ``TPM_proba``, the probability that a mutation step is drawn from the
    geometric distribution.

  * ``TPM_param``, the parameter of the geometric distribution.

  The generalized stepwise mutation model (a model where all steps are drawn
  from the geometric distribution) can be implemented by using
  this combination of parameters: ``mut_model=TPM, TPM_proba=1, TPM_param=a``
  with ``a`` the desired distribution parameter.

.. note::

    The default is equivalent to ``model=KAM, num_alleles=2, num_sites=0`` (see
    below for the number of sites). The other mutation models are designed
    *a priori* to represent microsatellite markers and, most likely,
    they should be used with a fixed number of sites. If one wants to emulate
    realistic DNA sequences with homoplasy, the number of sites should also
    be set to a finite value.

.. _sites-params:

Number of sites
***************

The parameter ``num_sites`` determines the number of sites of the simulated
genetic segment. There are two main situations:

* ``num_sites=0`` (the default) corresponds to the infinitely-many site
  model. In this model, the number of sites is assumed to be large enough
  (compared to the mutation rate) so that each mutation necessarily hits
  a new site. In this case, a site is generated for each mutation. Only
  sites with a mutation are exported, and thereby all exported sites
  are polymorphic with exactly two alleles. This is the most time-efficient
  option.

* ``num_sites=L`` with ``L`` larger than 0. In this case, there are a finite
  number of sites and each mutation hits randomly one of the sites. As a result,
  there can be sites without mutation, others with one mutation exactly,
  and some with more than one mutation. In the latter case, unless the model is
  ``IAM``, there can be homoplasy (identity by state but not by descent).
  If the simulated segment is supposed to represent a stretch of DNA sequence,
  ``num_sites`` is the length of the region, in base pairs. To simulate a
  single microsatellite marker, use ``num_sites=1``. It is possible to
  simulate several microsatellite markers, or other type of individual markers (such
  as individuals SNPs).

  In this case, it is possible to use two additional options: ``site_pos``
  and ``site_weight``. These two options are lists of length matching the
  value of ``num_sites``, that can be used the same way as the lists
  describing population properties (:ref:`list-params`).

  * ``site_pos`` gives the position of all sites (in the range ``[0,1]``).
    The more distant two sites are, the more recombination is likely to occur
    between them (if ``recomb`` is more than 0 of course). By default,
    the sites are spread evenly along the interval. The first site
    will always be at position 0 and the last one at position 1 (if there
    is one site, it will be placed at position 0.5 although this has
    little relevance regarding recombination).

  * ``site_weight`` gives the relative probability that mutation hits each
    site. To be used if the mutation rate varies over sites. By default,
    all weights are equal to 1 (note that the absolute value is irrelevant,
    what matters is the ratio of the weights between sites). For example,
    to implement three linked microsatellite markers with
    respective per-site :math:`\theta` values of 1.4, 2.4, and 1.9, it is
    possible to use ``num_sites=3, theta=5.7, site_weight=[1.4, 2.4, 1.9]``
    (5.7 being the total mutation rate).
    Unlinked markers must be simulated independently.

.. _events-params:

Other parameters
================

The other parameters are listed in the table below. They are detailed
in the following paragraphs.

+--------------+-----------------------------------------+----------------+
| Parameter    | Meaning                                 | Default        |
+==============+=========================================+================+
| ``events``   | List of historical events               | Empty          |
+--------------+-----------------------------------------+----------------+
| ``recomb``   | :math:`\rho=4N_0c` parameter            | 0              |
+--------------+-----------------------------------------+----------------+
| ``max_iter`` | Maximum number of coalescent iterations | 100,000        |
+--------------+-----------------------------------------+----------------+

Historical events
*****************

The coalescent simulator support historical changes of most parameters.
The change specifications are held in a specific entry of the parameter
dictionary-like, at the key ``events``.

By default, the list of events is empty::

    >>> coal = egglib.coalesce.Simulator(num_pop=4, num_chrom=[10, 10, 10, 10], theta=1)
    >>> print(coal.params['events'])
    []

Events can be created using the method
:meth:`~.coalesce.ParamDict.add_event`.
This method takes as arguments a string identifying the type of
event, the date of the event (in the past, in units of :math:`4N_0` generations),
and parameters depending on the type of event. Here are two examples
using ``size``, the event allowing to implement past changes of
population size::

    >>> coal.params.add_event(cat='size', T=0.4, idx=0, N=0.1)
    >>> coal.params.add_event(cat='size', T=0.5, idx=0, N=1.0)
    >>> print(coal.params['events'])
    [<event_index=0;idx=0;N=0.1;cat=size;T=0.4>, <event_index=1;idx=0;N=1.0;cat=size;T=0.5>]

The events can be added in any order: they will be sorted automatically
based on their date. If their date changes, the sorting will be updated
appropriately and automatically.

As you can see, when printed, events show a string presenting their parameters,
but the string should not be used to extract information in programs. Rather,
a dictionary can be obtained using the syntax below::

    >>> print(coal.params['events'][0])
    {'idx': 0, 'N': 0.1, 'cat': 'size', 'T': 0.4}

To modify the content of an event, one must used a method named :meth:`~.EventList.update`::

    >>> coal.params['events'].update(0, N=0.05)
    >>> print(coal.params['events'])
    [<event_index=0;T=0.4;idx=0;N=0.05;cat=size>, <event_index=1;T=0.5;idx=0;N=1.0;cat=size>]

The list below presents the list of available events and the list of their
parameters. Note that arguments ``cat`` (event code) and ``T`` (time of
the event) are always required. More details (in particular for complex
types of events) are given in :ref:`more-on-events`.

* ``size`` -- change size of a population.

  * ``idx`` -- population index (if omitted, all populations).
  * ``N`` -- new population size, expressed relatively to ``N_0``.

* ``migr`` -- change all migration rates.

  * ``M`` -- new migration rate, such that all pairwise migration rates will
    be equal to ``M/(num_pop-1)``.

* ``pair_migr`` -- change a pairwise migration rate.

  * ``src`` -- source population index.
  * ``dst`` -- destination population index.
  * ``M`` -- new pairwise migration rate.

* ``growth`` -- change exponential growth/decline rate of a population.

  * ``idx`` -- population index (if omitted, all populations).
  * ``G`` -- new exponential growth/decline rate.

* ``selfing`` -- change selfing rate for a population.

  * ``idx`` -- population index (if omitted, all populations).
  * ``s`` -- new selfing rate.

* ``bottleneck`` -- apply a bottleneck. In this implementation, bottlenecks
  are assumed to be short enough to have negligible length (such that,
  in particular, no mutations can occur within this time frame). Therefore,
  such bottlenecks are implemented as a random amount of coalescence events
  (excluding all other events), controlled by the parameter ``S``.

  * ``idx`` -- population index (if omitted, all populations).
  * ``S`` -- bottleneck strength.

* ``recombination`` -- change recombination rate.

  * ``R`` -- new recombination rate.

* ``admixture`` -- move random lineages from one population to another.

  * ``src`` -- source population.
  * ``dst`` -- destination population.
  * ``proba`` -- instant migration probability (not related to migration rates)

* ``merge`` -- move all lineages from a population to another, then
  set all migration rates to the first population to 0.

  * ``src`` -- source population index (the one that will be virtually
    removed).
  * ``dst`` -- destination population.

* ``sample`` -- perform a delayed sampling.

  * ``idx`` -- population index.
  * ``label`` -- group label to apply to samples belonging to this
    sampling (this allows to treat the sampling as an independent
    population in the generated data).
  * ``num_chrom`` -- number of haploid samples.
  * ``num_indiv`` -- number of diploid samples.

Recombination
*************

Recombination is implemented over a continuous interval, controlled by
a single parameter. The continuous interval means
that each occurrence of recombination yields a breakpoint randomly placed on the
interval ``[0,1]`` representing the simulated chromosome, thus
generating a new segment (which is represented by a genealogical tree of its own).

The recombination rate is not allowed to vary along the simulated genetic segment
(although it is allowed to vary discretely over time, see the historical events above),
but one can control the amount of recombination between sites by adjusting
their positions (see :ref:`sites-params`).

.. _max-iter-param:

Maximum number of iterations
****************************

The number of iterations in the coalescent process is bounded, in order to prevent
an infinite loop in situations where the final coalescence can never be
concluded (see :ref:`coalescent-complete`).
If this limit is reached by error (perhaps with extreme values of some
parameters), the bound can be lifted using the ``max_iter`` parameter.
