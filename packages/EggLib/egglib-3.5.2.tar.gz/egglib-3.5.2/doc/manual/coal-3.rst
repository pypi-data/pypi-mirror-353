----------------------
Performing simulations
----------------------

Simplest case
=============

The most straighforward way to perform coalescent simulations is to run the
:meth:`~.Simulator.simul` method of :class:`~.coalesce.Simulator` instances.
This method uses the current value of parameters and returns a brand new
:class:`.Align` instance containing simulated data. This instance will always
have the desired number of samples. If the infinite site model of mutation
is used (``num_sites=0``, by default), then the number of sites can vary,
as shown by the two consecutive simulations with the same model below::

    >>> c = egglib.coalesce.Simulator(num_pop=1, num_chrom=[5], theta=5.0)
    >>> aln = c.simul()
    >>> print(aln.ns, aln.ls)
    5 27
    >>> print(aln.fasta(alphabet=egglib.alphabets.DNA))
    >
    ACCCCCCACAAAAAAAACCAAACCACC
    >
    ACCCACCACAAAAAAAACCAAACCCAC
    >
    CAAAAAACACCCCCCCCAACCCAAAAA
    >
    ACCCACCACAAAAAAAACCAAACCCAC
    >
    ACCCACCACAAAAAAAACCAAACCCAC
    >>> aln = c.simul()
    >>> print(aln.ns, aln.ls)
    5 2

Note that, to print sequences, we used the *alphabet* option of :meth:`~.Align.fasta`.
This is because simulated alleles are (in this case, with the number of alleles fixed to
2) the integers 0 and 1, which is not supported by default by :meth:`!fasta`.

If the number of sites is fixed by ``num_sites``, then the number of sites
will be fixed, but it will not be guaranteed that all sites will be variable.
Here is an example with a low :math:`\theta`, 4 alleles, and the number of
sites set to 50, to simulate a short fragment of DNA::

    c.params['theta'] = 1.0
    c.params['num_alleles'] = 4
    c.params['num_sites'] = 50
    aln = c.simul()
    print(aln.ns, aln.ls)
    5 50
    print(aln.fasta(alphabet=egglib.alphabets.DNA))
    >
    AACAAAAAAAAAAAAAAAAAAAAAACAAAAAAAAAAAGAAAAAAAAAAAA
    >
    TAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
    >
    AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
    >
    AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
    >
    AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA

Model with populations, individuals, and outgroup
*************************************************

You may have noticed that the resulting alignment has empty names. However it
has two levels of group labels (identifying respectively populations and individuals,
in that order). This is demonstrated below:

.. image:: /pict/model13.*
   :height: 200px
   :width: 200 px
   :align: center

::

    >>> c = egglib.coalesce.Simulator(num_pop=3, num_indiv=[4, 4, 1], theta=5.0)
    >>> c.params.add_event(cat='merge', T=0.5, src=0, dst=1)
    >>> c.params.add_event(cat='merge', T=3, src=2, dst=1)
    >>> aln = c.simul()
    >>> print(aln.ns, aln.ls)
    16 48
    >>> print(aln.fasta(alphabets=egglib.alphabets.DNA, labels=True))
    >@0,0
    CCAAACAAACAACAAAAAAAAAAAAAACCAACACCAAAAAAAAACAA
    >@0,0
    CCCAAAAAACAACAAAAAAAAAAAAACCCAACACCAAAAAAAAACAA
    >@0,1
    CCAAAACAACAACAAAAAAAAAAAAAACCAACACCAAAAAAAAACAA
    >@0,1
    CCCAAAAAACAACAAAAAAAAAAAAAACCAACACCAAAAAAAAACAA
    >@0,2
    CCCAAAAAACAACAAAAAAAAAAAAAACCAACACCAAAAAAAAACAA
    >@0,2
    CCCAAAAAACAACAAAAAAAAAAAAAACCAACACCAAAAAAAAACAA
    >@0,3
    CCCAAAAAACAACAAAAAAAAAAAAAACCAACACCAAAAAAAAACAA
    >@0,3
    CCCAAAAAACAACAAAAAAAAAAAAAACCAACACCAAAAAAAAACAA
    >@1,4
    CCAAAAAAACAACAAAAAAAAAACAAAACAAAAACCAAAAAACCCAA
    >@1,4
    CCAAAAAAACACCAAAAAAAAAACAAAACAAAAACCAAAAAACCCAA
    >@1,5
    CCAAAAAAACCACAAAAAAAAAAAAAAACAAAAACCAAAAACCACAA
    >@1,5
    CCAACAAAACAACACAAAAAACAAAAAACACAAACCAAAAAACACAA
    >@1,6
    CCAAAAAAACAACAAAAAAAAAACAAAACAAAAACCAAAAAACCCAA
    >@1,6
    CCAAAAAAACAACAAAAACAAAACAAAACAAAAACCAAAAAACCCAA
    >@1,7
    CCAAAAAAACAACAAAAAAAAAACAAAACAAAAACCAAAAAACCCAA
    >@1,7
    CCAAAAAAACAACCAAAAAAAAACAAAACAAAAACCAAAAAACCCAA
    >@2,8
    AAACAAACCAAAAAACCCACCACACCAAACAAAAAAACCCCAAAACC
    >@2,8
    AAACAAACCAAAAAACCAACCACACCAAACAACAAACCCCCAAAACC

All :class:`!Align` instances returned by :class:`!Simulator` have these
two levels of structure.

The iterator
============

The :meth:`~.coalesce.Simulator.simul` method of :class:`!Simulator`
returns a brand new :class:`!Align` instance at
each call, which represents a significant computational burden when performing
a lot of simulations if each alignment only needs to be processed once
and does not need to be stored. :class:`!Simulator` instances have another
method, :meth:`~.coalesce.Simulator.iter_simul`, that is much more efficient since it
reuses constantly the same :class:`!Align` instance.

Currently, the expression::

    >>> for aln in c.iter_simuls(1000):
    ...

is above 50 times faster than::

    >>> for i in range(1000):
    ...     aln = c.simul()
    ...

But it should be kept in mind that the ``aln`` variable will actually
always point to the same instance (which is a static alignment stored in the
:class:`!Simulator` instance, and which is automatically reset at the end of
the loop). Printing alignments demonstrate it::

    >>> aln_list = []
    >>> for i in range(5):
    ...     aln = c.simul()
    ...     aln_list.append(aln)
    ...
    >>> print(map(hash, aln_list))
    [8733823164941, 8733823165037, 8733823165093, 8733823165109, 8733823165125]

    >>> del aln_list[:]
    >>> for aln in c.iter_simul(5):
    ...     aln_list.append(aln)
    ...
    >>> print(map(hash, aln_list))
    [8733823165089, 8733823165089, 8733823165089, 8733823165089, 8733823165089]

Coupling simulations and statistics
***********************************

:meth:`!iter_simul` can be used to chain diversity analysis with coalescent
simulations. You need to create your own :class:`~.stats.ComputeStats` instance
and specify what statistics you want to be computed, then pass it to
:meth:`!iter_simul` as the *cs* argument. Instead of the alignment, a
dictionary of statistics will be computed::

    >>> cs = egglib.stats.ComputeStats()
    >>> cs.add_stats('D', 'S')
    >>> for stats in c.iter_simul(10, cs=cs):
    ...     print(stats)
    ...
    {'S': 24, 'D': -0.20644191669019338}
    {'S': 26, 'D': 0.34339003894229597}
    {'S': 34, 'D': 0.3435768693207146}
    {'S': 15, 'D': 0.21333685716317954}
    {'S': 37, 'D': 1.065702801735725}
    {'S': 24, 'D': -0.2017428852888509}
    {'S': 23, 'D': 0.4068741818892754}
    {'S': 14, 'D': 0.9424874038796626}
    {'S': 34, 'D': -1.3365645916387778}
    {'S': 27, 'D': -1.3531206659089505}

Within the iteration loop, it is still possible to retrieve the static
alignment (even if the loop returns dictionaries of statistics), through
the instance property :py:obj:`~.Simulator.align`.

Varying parameters over simulations
***********************************

It is possible to perform coalescent simulations with variable parameters
(a different value for each replicate), using the ``feed_params``
feature of :meth:`!iter_simul`. To use it,
keyword arguments must be supplied with lists of parameter values matching
parameter names.

For example, to run the simplest model with one constant population with
a variable value for the ``theta`` parameter, this is how it would be
done (assuming the varying ``theta`` values have been drawn previously
randomly, or provided externally)::

    >>> c = egglib.coalesce.Simulator(num_pop=1, num_chrom=[20])
    >>> theta_values = [2.5645, 4.4111, 6.5677, 1.8904, 2.1915, 0.9696, 2.8418, 5.221, 4.9423, 9.0793]
    >>> for aln in c.iter_simul(10, theta=theta_values):
    ...     print(aln.ls)
    13
    13
    42
    8
    15
    1
    11
    12
    12
    32

Several parameters can be provided at once (just use as many keyword arguments
as needed). Unfortunately, it is currently not possible to set this way
population-specific parameters or arguments of historical events.

Accessing other data
====================

Getting simulated trees
***********************

The genealogical trees representing the history of sample can be retrieved for
all simulations. To do it, one must provide a :class:`list` to :meth:`~.coalesce.Simulator.iter_simul`
and the list will be filled by the genealogical trees of each replicate. The
trees are represented by instances of the class :class:`.Tree` which provides
an array of functionality (see the reference manual for details).

In case recombination occurs, there can be multiple trees for a given simulation: one
tree for each non-recombination segment. For this reason, each simulation is
represented by a :class:`!list` of ``(tree, start, stop)`` :class:`tuple` instances in the resulting list
(start and stop positions are bounded by 0 and 1). This will be probably clearer with an example::

    >>> c = egglib.coalesce.Simulator(num_pop=1, num_chrom=[10], recomb=1.0, theta=0.0)
    >>> trees = []
    >>> for aln in c.iter_simul(100, dest_trees=trees):
    ...     pass

    >>> print(len(trees[0]))
    3
    >>> for tree, start, stop in trees[0]:
    ...     print('segment')
    ...     print('  ', start)
    ...     print('  ', stop)
    ...     print('  ', tree.newick())
    ...
    segment
       0.0
       0.140169298276
       (((((2:0.0180097202807,8:0.0180097202807):0.0215616741102,5:0.0395713943908):0.0724922358078,1:0.112063630199):0.0558628762791,((3:0.0495320422666,(7:0.00261506458809,6:0.00261506458809):0.0469169776785):0.00203223981633,4:0.0515642820829):0.116362224395):0.188555286584,(9:0.0369467779977,0:0.0369467779977):0.319535015065);
    segment
       0.936298474669
       1.0
       (((((2:0.0180097202807,8:0.0180097202807):0.0215616741102,5:0.0395713943908):0.128355112087,(3:0.0515642820829,4:0.0515642820829):0.116362224395):0.0797638476642,(1:0.0470800821279,(7:0.00261506458809,6:0.00261506458809):0.0444650175398):0.200610272014):0.10879143892,(9:0.0369467779977,0:0.0369467779977):0.319535015065);
    segment
       0.140169298276
       0.936298474669
       (((((2:0.0180097202807,8:0.0180097202807):0.0215616741102,5:0.0395713943908):0.128355112087,((3:0.0495320422666,(7:0.00261506458809,6:0.00261506458809):0.0469169776785):0.00203223981633,4:0.0515642820829):0.116362224395):0.0797638476642,1:0.247690354142):0.10879143892,(9:0.0369467779977,0:0.0369467779977):0.319535015065);

In this example, the first simulation went through two events of
recombination, yielding three segments with breakpoints at approximate positions
0.1402 and 0.9363. The Newick representation of each of the three
trees for the first simulation are displayed. Notice that the trees are
not sorted within the per-simulation list (the order is defined by the
order of the recombination events in the simulation).

If recombination is null, then each simulation is a one-item :class:`!list` with
a single :class:`!tuple` with ``start`` equal to 0 and ``stop`` equal to 1.

.. _coalesce-structure:

Getting the structure of the model
**********************************

It can be useful to have the :class:`.Structure` instance describing the
population and individual structure of the alignments that will be generated
by simulations (in order to compute diversity statistics). It is possible
to do it using any :class:`!Align` instance, but this is not necessarily
convenient (in particular if you plan to use the *cs* option of
:meth:`!iter_simul`). The attribute :attr:`!params` provides a method to
generate the :class:`!Structure` describing the population and individual
structure based on model parameters::

    >>> c = egglib.coalesce.Simulator(num_pop=3, num_indiv=[4, 4, 1], theta=5.0)
    >>> c.params.add_event(cat='merge', T=0.5, src=0, dst=1)
    >>> c.params.add_event(cat='merge', T=3, src=2, dst=1)
    >>> struct = c.params.mk_structure(outgroup_label='2')
    >>> print(struct.as_dict())
    ({None: {'0': {'0': [0, 1], '1': [2, 3], '2': [4, 5], '3': [6, 7]}, '1': {'4': [8, 9], '5': [10, 11], '6': [12, 13], '7': [14, 15]}}}, {'8': [16, 17]})

    >>> cs = egglib.stats.ComputeStats()
    >>> cs.add_stats('FstWC', 'Fis')
    >>> cs.set_structure(struct)
    >>> for stats in c.iter_simul(10, cs=cs):
    ...     print(stats)
    {'FstWC': 0.4208284939992256, 'Fis': 0.20152091254752857}
    {'FstWC': 0.5204081632653061, 'Fis': 0.40327868852459026}
    {'FstWC': 0.7218045112781954, 'Fis': 0.5672727272727273}
    {'FstWC': 0.5411255411255411, 'Fis': 0.4494382022471909}
    {'FstWC': 0.6054421768707483, 'Fis': 0.6181818181818182}
    {'FstWC': 0.4155844155844157, 'Fis': 0.39607843137254906}
    {'FstWC': 0.7689594356261023, 'Fis': 0.762402088772846}
    {'FstWC': 0.6802721088435374, 'Fis': 0.5980861244019139}
    {'FstWC': 0.34833659491193747, 'Fis': 0.378132118451025}
    {'FstWC': 0.2332361516034986, 'Fis': 0.11363636363636342}

The fact that both :math:`F_{IS}` and Weir and Cockerham's :math:`\hat{\theta}`
(labelled ``FstWC``) can be computed shows that the two individual and
population levels have been properly described.

If you want to add a cluster level, or, for example, want to analyse the
data using a different structure than the one used for simulations, you
need to create your own :class:`!Structure` instance.

.. note::

    If you mix sampled individuals and sampled chromosomes (non-zero
    values for any ``num_chrom`` and any ``num_indiv`` items), it will not
    be possible to process the individual level due to non-constant
    ploidy. In this case (to process the population level anyway), use
    the *skip_indiv* option of :meth:`~.coalesce.ParamDict.mk_structure`.
