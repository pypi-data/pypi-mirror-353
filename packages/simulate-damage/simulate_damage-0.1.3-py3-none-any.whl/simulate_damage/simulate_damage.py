#!/usr/bin/env python3

import argparse
import gzip
import random
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord


def open_maybe_gzip(file_path, mode='rt'):
    """Open file normally or via gzip depending on extension."""
    return gzip.open(file_path, mode) if file_path.endswith('.gz') else open(file_path, mode)


def damage_read(seq, is_r1, params, overhang):
    """Apply deamination-like damage to a read sequence."""
    seq = list(seq)
    length = len(seq)

    for i, base in enumerate(seq):
        if is_r1 and base == 'C':
            p = params['p_ct_5prime'] if i < overhang else params['p_ct_internal']
            if random.random() < p:
                seq[i] = 'T'
        elif not is_r1 and base == 'G':
            p = params['p_ga_3prime'] if i >= length - overhang else params['p_ga_internal']
            if random.random() < p:
                seq[i] = 'A'
    return ''.join(seq)


def simulate_deamination_pe(input_r1, input_r2, output_r1, output_r2, damage_params, overhang_length):
    """Simulate damage on paired-end reads."""
    with open_maybe_gzip(input_r1, 'rt') as in_r1, \
         open_maybe_gzip(input_r2, 'rt') as in_r2, \
         open_maybe_gzip(output_r1, 'wt') as out_r1, \
         open_maybe_gzip(output_r2, 'wt') as out_r2:

        r1_reads = SeqIO.parse(in_r1, "fastq")
        r2_reads = SeqIO.parse(in_r2, "fastq")

        for r1, r2 in zip(r1_reads, r2_reads):
            damaged_r1_seq = damage_read(str(r1.seq), is_r1=True, params=damage_params, overhang=overhang_length)
            damaged_r2_seq = damage_read(str(r2.seq), is_r1=False, params=damage_params, overhang=overhang_length)

            damaged_r1 = SeqRecord(Seq(damaged_r1_seq), id=r1.id, description="",
                                   letter_annotations={"phred_quality": r1.letter_annotations["phred_quality"]})
            damaged_r2 = SeqRecord(Seq(damaged_r2_seq), id=r2.id, description="",
                                   letter_annotations={"phred_quality": r2.letter_annotations["phred_quality"]})

            SeqIO.write(damaged_r1, out_r1, "fastq")
            SeqIO.write(damaged_r2, out_r2, "fastq")


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Simulate deamination damage on paired-end FASTQ files (gzipped or plain)."
    )
    parser.add_argument('--r1', required=True, help="Input FASTQ R1 (.fastq or .fastq.gz)")
    parser.add_argument('--r2', required=True, help="Input FASTQ R2 (.fastq or .fastq.gz)")
    parser.add_argument('--out_r1', required=True, help="Output damaged R1 FASTQ file")
    parser.add_argument('--out_r2', required=True, help="Output damaged R2 FASTQ file")
    parser.add_argument('--ct5', type=float, default=0.03, help="C→T damage at 5′ ends (R1)")
    parser.add_argument('--ctint', type=float, default=0.4, help="C→T internal damage (R1)")
    parser.add_argument('--ga3', type=float, default=0.01, help="G→A damage at 3′ ends (R2)")
    parser.add_argument('--gaint', type=float, default=0.7, help="G→A internal damage (R2)")
    parser.add_argument('--overhang', type=int, default=10, help="Length of terminal overhangs")

    return parser.parse_args()


def main():
    args = parse_args()
    damage_params = {
        'p_ct_5prime': args.ct5,
        'p_ct_internal': args.ctint,
        'p_ga_3prime': args.ga3,
        'p_ga_internal': args.gaint
    }

    simulate_deamination_pe(args.r1, args.r2, args.out_r1, args.out_r2,
                             damage_params, args.overhang)


# For pip entry-point
def run():
    main()
