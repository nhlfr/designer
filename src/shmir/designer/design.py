#!/usr/bin/env python

"""
.. module:: main
    :synopsis: provides the executable program
"""

import sys
from copy import deepcopy
from .validators import check_input
from .utils import (
    get_frames,
    reverse_complement,
)
from .score import (
    score_frame,
    score_homogeneity,
    score_two_same_strands,
)
from data.models import (
    Backbone,
    db_session,
)
from mfold import delegate_mfold


def fold_and_score(seq1, seq2, frame_tuple, original):
    score = 0
    frame, insert1, insert2 = frame_tuple
    mfold_data = delegate_mfold(frame.template(insert1, insert2))
    if 'error' in mfold_data:
        return mfold_data
    pdf, ss = mfold_data[0], mfold_data[1]
    score += score_frame(frame_tuple, ss, original)
    score += score_homogeneity(original)
    score += score_two_same_strands(seq1, original)
    return (score, frame.template(insert1, insert2), frame.name, pdf)


def design_and_score(input_str):
    """
    Main function takes string input and returns the best results depending
    on scoring. Single result include sh-miR sequence,
    score and link to 2D structure from mfold program
    """

    sequence = check_input(input_str)
    seq1, seq2, shift_left, shift_right = sequence
    if not seq2:
        seq2 = reverse_complement(seq1)

    original_frames = db_session.query(Backbone).all()

    frames = get_frames(seq1, seq2,
                        shift_left, shift_right,
                        deepcopy(original_frames))

    frames_with_score = []
    for frame_tuple, original in zip(frames, original_frames):
        frames_with_score.append(
            fold_and_score(seq1, seq2, frame_tuple, original)
        )
    sorted_frames = [elem for elem in sorted(frames_with_score,
                     key=lambda x: x[0], reverse=True) if elem[0] > 60]
    return {'result': sorted_frames[:3]}


if __name__ == '__main__':
    print(design_and_score(" ".join(sys.argv[1:])))