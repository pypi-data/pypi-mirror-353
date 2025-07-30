# simulate_damage

`simulate_damage` is a command-line tool that simulates ancient DNA (aDNA) deamination damage in **paired-end FASTQ** files. It introduces realistic C→T and G→A transitions at read ends and internally, allowing researchers to test pipelines under damage conditions typical of ancient samples.

---

##  Features

-  Supports **.fastq** and **.fastq.gz**
-  Handles **paired-end reads** automatically
-  Allows **custom damage rates** for 5′ and internal C→T (R1) and G→A (R2)
-  Keeps **original read qualities** and structure
-  Fully scriptable or callable via CLI

---

## Installation

```bash
pip install simulate_damage

## Example usage

simulate_damage \
  --r1 sample_R1.fastq.gz \
  --r2 sample_R2.fastq.gz \
  --out_r1 damaged_R1.fastq.gz \
  --out_r2 damaged_R2.fastq.gz \
  --ct5 0.03 --ctint 0.4 --ga3 0.01 --gaint 0.7 --overhang 10

