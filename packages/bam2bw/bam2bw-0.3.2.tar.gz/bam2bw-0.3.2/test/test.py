import os

'''
os.system("samtools sort test.bam -o test.sorted.bam")

os.system("bedtools genomecov -5 -bg -strand + -ibam test.sorted.bam | sort -k1,1 -k2,2n > test.+.bedGraph")
os.system("bedtools genomecov -5 -bg -strand - -ibam test.sorted.bam | sort -k1,1 -k2,2n > test.-.bedGraph")
os.system("bedtools genomecov -5 -bg -ibam test.sorted.bam | sort -k1,1 -k2,2n > test.bedGraph")

os.system("bedGraphToBigWig test.+.bedGraph ../../../common/hg38.chrom.sizes test.+.bw")
os.system("bedGraphToBigWig test.-.bedGraph ../../../common/hg38.chrom.sizes test.-.bw")
os.system("bedGraphToBigWig test.bedGraph ../../../common/hg38.chrom.sizes test.bw")
'''

###

os.system("bam2bw test.bam -n testb2b -s ../../../common/hg38.chrom.sizes -v")
os.system("bam2bw test.bam -n testb2b -s ../../../common/hg38.chrom.sizes -u -v")

###

import numpy
import pyBigWig

for name in ".+.", ".-.", ".":
	ap = pyBigWig.open("test{}bw".format(name), "r")
	bp = pyBigWig.open("testb2b{}bw".format(name), "r")

	for chrom in ['chr{}'.format(i) for i in range(1, 23)] + ['chrX']:
		apx = numpy.nan_to_num(ap.values(chrom, 0, -1, numpy=True))
		bpx = numpy.nan_to_num(bp.values(chrom, 0, -1, numpy=True))
		
		print(name, chrom, numpy.abs(apx - bpx).sum(), apx.sum(), bpx.sum())
