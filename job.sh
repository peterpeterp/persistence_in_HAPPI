#!/bin/bash -l

#SBATCH --nodes=2
#SBATCH --time=00:30:00
#SBATCH --qos=regular
#SBATCH --license=SCRATCH   #note: specify license need for the file systems your job needs, such as SCRATCH,project
#SBATCH --constraint=haswell
srun -n 32 -c 4 $1 $2 $3 $4
