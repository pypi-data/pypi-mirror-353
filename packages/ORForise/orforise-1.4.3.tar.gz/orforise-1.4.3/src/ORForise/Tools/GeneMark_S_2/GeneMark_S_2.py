import collections

try:
    from utils import revCompIterative
    from utils import sortORFs
except ImportError:
    from ORForise.utils import revCompIterative
    from ORForise.utils import sortORFs


def GeneMark_S_2(*args):
    tool_pred = args[0]
    genome = args[1]
    types = args[2]
    geneMark_S_2_ORFs = collections.defaultdict(list)
    genome_size = len(genome)
    genome_rev = revCompIterative(genome)
    with open(tool_pred, 'r') as GeneMark_S_2_input:
        for line in GeneMark_S_2_input:
            line = line.split('\t')
            if len(line) >= 9 and "CDS" in line[2]:
                start = int(line[3])
                stop = int(line[4])
                strand = line[6]
                info = line[8]
                if '-' in strand:  # Reverse Compliment starts and stops adjusted
                    r_start = genome_size - stop
                    r_stop = genome_size - start
                    startCodon = genome_rev[r_start:r_start + 3]
                    stopCodon = genome_rev[r_stop - 2:r_stop + 1]
                elif '+' in strand:
                    startCodon = genome[start - 1:start + 2]
                    stopCodon = genome[stop - 3:stop]
                po = str(start) + ',' + str(stop)
                orf = [strand, startCodon, stopCodon, 'CDS', 'GeneMark_S_2|'+info]
                geneMark_S_2_ORFs.update({po: orf})

    geneMark_S_2_ORFs = sortORFs(geneMark_S_2_ORFs)
    return geneMark_S_2_ORFs
