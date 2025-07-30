.. _more-on-events:

------------------------
Use of historical events
------------------------

In this section we provides some pointers on defining demographic models
involving past events using :ref:`coalesce <pycoalesce>`.

Bottlenecks
===========

EggLib supports changing the size of populations at any point in the history
of the sample. Thus, a bottleneck can straightforwardly implemented by
two consecutive population sizes (first reduction, and then restoration of the
same size). Assume the following model:

.. image:: /pict/model2.*
   :height: 200px
   :width: 200 px
   :align: center

The implementation would be::

    >>> c = egglib.coalesce.Simulator(num_pop=1, num_chrom=[50], theta=5.0)
    >>> c.params.add_event(cat='size', T=0.20, N=0.1)
    >>> c.params.add_event(cat='size', T=0.21, N=1.0)

This approach has the advantage of being easier to interpret, and
allowing independent population size before and after the bottleneck.

A second way to implement bottlenecks is the ``bottleneck`` event, which
has the advantage of saving one parameter. Instead of requiring both
duration and strength parameters, it requires only a strength parameter.
The code is of the type::

    >>> c.params.add_event(cat='bottleneck', T=0.2, S=0.5)

This model can be represented by:

.. image:: /pict/model3.*
   :height: 200px
   :width: 200 px
   :align: center

In the standard bottleneck (first model), the main consequence of the
bottleneck is an increase rate of coalescence events. This second
implementation assumes that the bottleneck is short enough so that its
duration can be neglected. Instead, a random number of coalescence events are
instantaneously performed at the time of the bottleneck. The number of
coalescence events is proportional to the ``S`` parameter and
is equivalent to what would be if the population would
have been allowed to evolved during a time given by ``S`` (as represented
by the insertion of a period of time equal to ``S`` in the picture above).

Merge, admixture, and split events
==================================

The principle of fixing once and for all the number of populations does not
impose any limitation in the implementation of complex models, which can all
be implemented by available historical events. In this
regard, the ``admixture`` event is essential.

Its definition is: at time ``T``, take a random number of lineages from
the population ``src`` (with probability ``proba``), and move them instantly
to the population ``dst``. See the example below along with its implementation:

.. image:: /pict/model4.*
   :height: 200px
   :width: 200 px
   :align: center

::

    >>> c = egglib.coalesce.Simulator(num_pop=2)
    >>> c.params.add_event(cat='admixture', T=0.5, src=0, dst=1, proba=0.5)

The parameter ``proba=5`` means that every lineage present at that point in the first
population will have a probability 0.5 to move to population 1. Obviously,
we would have to add samples to make a working example. In coalescent models,
admixture means that lineages move (in this case) from population ``src``
to population ``dst``, but it is important to realise that, biologically
speaking, this means that population ``dst`` has sent a bunch of migrants
to population ``src`` (everything is reverted since the model works
backward in time).

The population split event does not exist on its own, but can readily
implemented as an admixture. Again, remember that the term *split* must
be understood backward in time. To implement it, add one population with all
migration rates to it set to 0 (which is the default anyway), and without
samples. This is a "ghost" population with no effect on your sample since
no lineage can move to it. Program an admixture event to occur at the time
of the split, sending a given proportion of lineages to this ghost population
which, at this point, ceases to be ghost. Of course, the size of all
populations can be set freely at the start of the population, and changed
at any time by the historical event ``size``.

.. image:: /pict/model5.*
   :height: 200px
   :width: 200 px
   :align: center

::

    >>> c = egglib.coalesce.Simulator(num_pop=2, num_chrom=[50, 0])
    >>> c.params.add_event(cat='admixture', T=0.5, src=0, dst=1, proba=0.5)

The event ``merge`` is actually available, here we describe how it is
implemented in order to demonstrate the power of event management
in the :ref:`coalesce <pycoalesce>` module.

To perform a population merge, it is possible to define an admixture where
all samples from one of the populations are taken to the other one
(``proba=1``). To make it a proper merge event, the migration rate to the
merged (donor) population must be cancelled. So, if the migration rates
have not been set to a non-zero, value, the admixture event is enough to
implement a merge:

.. image:: /pict/model6.*
   :height: 200px
   :width: 200 px
   :align: center

::

    >>> c = egglib.coalesce.Simulator(num_pop=2, num_chrom=[20, 20])
    >>> c.params.add_event(cat='admixture', T=0.5, src=1, dst=0, proba=1)

But if the migration rate is non-zero it is also necessary to set all
migration rates to the donor population to 0.

As said above, there is a ``merge`` event that perform all required operations:

    >>> c = egglib.coalesce.Simulator(num_pop=2, num_chrom=[20, 20], migr=1)
    >>> c.params.add_event(cat='merge', T=0.5, src=1, dst=0)

Ghost populations and unsampled populations
===========================================

When considering complex models, it can be useful to make a clear distinction
between regular populations, ghost populations, and unsampled populations.

* Regular populations are populations where samples have been placed.
* Ghost populations are populations where there are no samples, and to
  which all migration rates from any non-ghost populations are null. The
  essential fact is that no lineages can ever go to this type of population so
  they don't have any effect on the final coalescent.
* Unsampled populations are populations where samples have not been placed,
  but where lineages can move by migration.

In the below example, population 0 is regular, population 1 is unsampled,
and population 2 is a ghost:

.. image:: /pict/model7.*
   :height: 200px
   :width: 200 px
   :align: center

::

    >>> c = egglib.coalesce.Simulator(num_pop=3, num_chrom=[20, 0, 0])
    >>> c.params['migr_matrix'] = [[None, 1, 0],
    ...                            [1, None, 0],
    ...                            [0, 0, None]]

Regular and unsampled populations are actually the same because the
important fact is that they are allowed to contain lineage at any time.

.. _coalescent-complete:

Completing simulations
**********************

An important point while designing a model is to prevent any situation
where the coalescent process will not be able to complete. Such situation
occurs if a population is experiencing exponential decline (as mentioned
when describing the parameter ``G``) or in any case when samples are
allowed to end up trapped in different populations with no chance to
ever coalesce. In either case, the simulator will not be able to complete
the tree and a :exc:`RuntimeError` will occur. The example below shows
the most simple case where this error is bound to occur:

.. image:: /pict/model8.*
   :height: 200px
   :width: 200 px
   :align: center

::

    >>> c = egglib.coalesce.Simulator(num_pop=2, num_chrom=[1, 1])
    >>> c.simul()
    [traceback omitted]
    RuntimeError: infinite coalescent time (unconnected populations or excessive ancestral population size)

It is important to note that the problem might not be systematic. For
example, in the example below, there is a degree of freedom that makes
that the error will occur randomly:

.. image:: /pict/model10.*
   :height: 200px
   :width: 200 px
   :align: center

::

    >>> c = egglib.coalesce.Simulator(num_pop=3, num_chrom=[20, 0, 0])
    >>> c.params['migr_matrix'] = [[None, 1, 0],
                                   [1, None, 0],
                                   [0, 0, None]]
    >>> c.params.add_event(cat='admixture', T=0.3, src=1, dst=2, proba=0.2)
    >>> c.params.add_event(cat='merge', T=0.5, src=0, dst=1)
    >>> for x in c.iter_simul(1000):
    ...     print('done')
    ...
    done
    done
    done
    done
    [traceback omitted]
    RuntimeError: infinite coalescent time (unconnected populations or excessive ancestral population size)

Here the error occurs at the fifth repetition (but this is random). It
is caused as soon as two different lineages end up trapped in, respectively,
the two last populations. Since the migration rate between them is null
and there is no additional historical even planned, they can never coalesce
(but this is not required to happen each time).

To prevent this error, it is required to allow the complete coalescence
of the sample at some point of the past, either by allowing migration
(setting non-null migration rates) or merging populations (and also by
preventing any population to increase in size indefinitely due to the
``G`` option).

Occasionally, you might meet another error message:

.. image:: /pict/model9.*
   :height: 200px
   :width: 200 px
   :align: center

::

    >>> c = egglib.coalesce.Simulator(num_pop=3, num_chrom=[20, 0, 0])
    >>> c.params['migr_matrix'] = [[None, 1, 0],
    ...                            [1, None, 0],
    ...                            [0, 0, None]]
    >>> c.params.add_event(cat='admixture', T=0.5, src=1, dst=2, proba=0.2)
    >>> for x in c.iter_simul(1000):
    ...     print('done')
    ...
    done
    done
    done
    done
    done
    done
    done
    done
    done
    done
    done
    done
    [traceback omitted]
    RuntimeError: failed to complete coalescent tree: two lineages might be trapped to unconnected populations (if you are sure your model is correct, increase the parameter `max_iter`)

In this case, two lineages are again trapped because the last population
is not connected with the others, but the one lineage which is not in the
last population can still migrate between the first two. As a result, there
is still always an event to be applied by the coalescent algorithm, but this
can never complete the coalescent. To prevent this, a bound is included,
stopping the algorithm after a large number of iterations.

It is possible to increase this bound in case of models taking very long
(that is, a very large number of iteration steps) but still ensuring
completion of the coalescent (see :ref:`max-iter-param`).

.. _delayed:

Delayed samples
===============

EggLib's coalescent simulator supports historical (delayed) sample, that is
samples that have been collected at some known point in the past and
would be analysed along with contemporary samples. The sampling date must be
known and expressed in units of :math:`4N_0` generations as all other dates.
Delayed samples must be taken from one of the populations declared at
the instance construction, whether or not this population has an initial
sample. It is thus possible to simulate the temporal evolution of a
population through consecutive samplings:

.. image:: /pict/model11.*
   :height: 200px
   :width: 200 px
   :align: center

::

    >>> c = egglib.coalesce.Simulator(num_pop=1, num_chrom=[20])
    >>> c.params.add_event(cat='sample', T=0.5, idx=0, label='1', num_chrom=20, num_indiv=0)

It is also possible to sample a previously unsampled population:

.. image:: /pict/model12.*
   :height: 200px
   :width: 200 px
   :align: center

::

    >>> c = egglib.coalesce.Simulator(num_pop=2, num_chrom=[20, 0])
    >>> c.params.add_event(cat='sample', T=0.2, idx=1, label='1', num_chrom=20, num_indiv=0)
    >>> c.params.add_event(cat='merge', T=1.0, src=1, dst=0)

Note that the ``label`` option can help discriminate the different
sampling in the downstream analyses. Like initial samples, it is possible
to specify both haploid (individuals for which only one chromosome has been
sampled) and diploid (individuals with both chromosomes sampled) samples.
