"""
    Copyright 2009-2023 Stephane De Mita, Mathieu Siol

    This file is part of EggLib.

    EggLib is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    EggLib is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with EggLib.  If not, see <http://www.gnu.org/licenses/>.
"""

import subprocess, re, os
from .. import eggwrapper as _eggwrapper
from .. import alphabets
from .. import _interface
from ..io import _fasta
from . import _utils

class _Clustal(_utils._App):

    @_utils._protect_run
    def _check_path(self, path, cfg):
        cmd = (path, '--version')
        try:
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            stdout, stderr = p.communicate()
            if len(stderr): return stderr
        except OSError as e:
            return e.strerror
        mo = re.search(r'(\d+)\.(\d+)\.(\d+)', stdout)
        M = int(mo.group(1))
        m = int(mo.group(2))
        if not mo: return 'cannot read version number from Clustal Omega'
        if M >= 2 or m >= 1: return None
        else: return 'Clustal Omega version 1.1.0 or higher is required'

_app = _Clustal(key='clustal', default='clustalo')
_utils.paths._add(_app)

@_utils._protect_run
def clustal(source, ref=None,
            full=False, full_iter=False, cluster_size=100,
            use_kimura=False, num_iter=1, threads=1, keep_order=False,
            verbose=False):

    """ clustal(source, ref=None, \
                full=False, full_iter=False, cluster_size=100, \
                use_kimura=True,  num_iter=1, threads=1, keep_order=False, \
                verbose=False)

    Multiple sequence alignment using `Clustal Omega <http://www.clustal.org/omega/>`_.

    :param source: a :class:`.Container` or :class:`.Align` containing
        the sequences to align. If a :class:`!Container` is provided,
        sequences are assumed to be unaligned, and, if a :class:`!Align`
        is provided, sequences are assumed to be aligned. The list below
        explains what is done based on the type of *source* and whether
        a value is provided for *ref*:

        * If *source* is a :class:`!Container` and *ref* is ``None``,
          the sequences in *source* are aligned.

        * If *source* is an :class:`!Align` and *ref* is ``None``, a
          hidden Markov model is built from the alignment, then the
          alignment is reset and sequences are realigned.

        * If *source* is an :class:`!Align` and an alignment is
          provided as  *ref*, the two alignments are preserved (their
          columns are left unchanged), and they aligned with respect to
          each other.

        * If *source* is a :class:`!Container` and an alignment is
          provided as *ref*, a hidden Markov model is built from *ref*,
          then *source* is aligned using it, and finally the resulting
          alignment is aligned with respect to *ref* as described for
          the previous case.

        *source* must contain at least two sequences unless it is an
        :class:`!Align` and a value is provided for *ref* (in that case,
        it must contain at least one sequence).

    :param ref: an :class:`!Align` instance providing an external
        alignment. See above for more details. *ref* must contain at
        least one sequence. Sequences must be aligned.

    :param full: use full distance matrix to determine guide tree (the
        default is using the faster and less memory-intensive mBed
        approximation).

    :param full_iter: use full distance matrix to determine guide tree
        during iterations.

    :param cluster_size: size of clusters (as a number of sequences)
        used in the mBed algorithm.

    :param use_kimura: use Kimura correction for estimating
        whole-alignment distance (only available if a protein alignment
        has been provided as *source*).

    :param num_iter: number of iterations allowing to improve the
        quality of the alignment. Must be a number :math:`\geq 1` or a pair
        of numbers :math:`\geq 1`. If the value is a pair of numbers, they
        specify the number of guide tree iterations and hidden Markov
        model iterations, respectively. If a single value is provided,
        iterations couple guide tree and hidden Markov model.

    :param threads: number of threads for parallelization (available for
        parts of the program).

    :param keep_order: return the sequences in the same order as they
        were loaded.

    :param verbose: display Clustal Omega's console output.

    :return: An :class:`.Align` instance containing aligned sequences.

    .. versionchanged:: 3.0.0

        Ported to Clustal Omega and added support for more options.

    .. versionchanged:: 3.1.0

        Support protein sequences.
    """

    # check that program is available
    path = _app.get_path()
    if path is None:
        raise RuntimeError('Clustal Omega program not available -- please configure path')
    command_line = [path, '--infmt=fa', '-o', 'o']

    # mapping for sample reference
    mapping = {}

    # check that source has valid alphabet and write it down
    if source._alphabet == alphabets.DNA: command_line.append('--seqtype=DNA')
    elif source._alphabet == alphabets.protein: command_line.append('--seqtype=Protein')
    else: raise ValueError('alphabet must be DNA or protein')
    _utils._write(source, 'i', mapping)

    # if ref is loaded, write it down
    if ref != None:
        if not isinstance(ref, _interface.Align): raise TypeError('invalid type for `ref` argument')
        if ref._alphabet != source._alphabet: raise ValueError('alphabet of `source` and `ref` must match')
        if len(ref) < 1: raise ValueError('not enough sequences loaded to perform alignment')
        _utils._write(ref, 'p', mapping)
        command_line.append('--profile1=p')

    # if source is a Container, write it as -i argument
    if isinstance(source, _interface.Container):
        if len(source) < 2: raise ValueError('not enough sequences loaded to perform alignment')
        command_line.append('--infile=i')

        # if all sequences have the same length, ensure it is treated as non-aligned sequences
        for sam in source:
            if len(sam.sequence) != source.ls(0): break
        else: command_line.append('--dealign')

    # if an alignment is loaded
    elif isinstance(source, _interface.Align):

        # ensure it is treated as a profile
        command_line.append('--is-profile')

        # if the source is a single Align, write it as -i argument also
        if ref is None:
            if len(source) < 2: raise ValueError('not enough sequences loaded to perform alignment')
            command_line.append('--infile=i')

        # if two Align, write this one as profile2 (2!)
        else:
            if len(source) < 1: raise ValueError('not enough sequences loaded to perform alignment')
            command_line.append('--profile2=i')

    # catch type error
    else: raise TypeError('invalid type for `source` argument')

    # other options
    if verbose: command_line.append('-v')
    if full: command_line.append('--full')
    if full_iter: command_line.append('--full-iter')
    if use_kimura:
        if isinstance(source, _interface.Container):
            raise ValueError('Kimura correction requires aligned sequences')
        if source.alphabet != alphabets.protein:
            raise ValueError('Kimura correction requires protein sequences')
        command_line.append('--use-kimura')
    if cluster_size < 1: raise ValueError('invalid value for `cluster_size` argument')
    command_line.append('--cluster-size={0}'.format(cluster_size))
    if isinstance(num_iter, int):
        if num_iter < 1: raise ValueError('invalid value for `num_iter` argument')
        command_line.append('--iter={0}'.format(num_iter))
    else:
        try:
            n1, n2 = num_iter
            n1 = int(n1)
            n2 = int(n2)
        except (ValueError, TypeError): raise ValueError('invalid value for `num_iter` argument')
        command_line.append('--iter={0}'.format(n1))
        command_line.append('--max-hmm-iterations={0}'.format(n2))
    if threads < 1: raise ValueError('invalid value for `threads` argument')
    command_line.append('--threads={0}'.format(threads))
    if keep_order: command_line.append('--output-order=input-order')
    else: command_line.append('--output-order=tree-order')

    # run the program
    p = subprocess.Popen(command_line, stdin=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        stdout=(None if verbose else subprocess.PIPE), universal_newlines=True) # add universal_newlines to support type `str` as stdin in python3
    stdout, stderr = p.communicate('Y\n')

    # check error
    stderr = stderr.strip()
    if len(stderr):
        raise RuntimeError('error while running Clustal Omega: {0}'.format(stderr))
    if not os.path.isfile('o'):
        raise RuntimeError('unknown error while running Clustal Omega (try verbose mode)')

    # get alignment
    aln = _fasta.from_fasta('o', source.alphabet, labels=False, cls=_interface.Align)

    # set proper names and groups
    for sam in aln:
        ref = mapping[sam.name]
        sam.name = ref.name
        sam.labels = ref.labels

    # return
    return aln
