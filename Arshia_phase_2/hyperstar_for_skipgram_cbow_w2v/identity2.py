#!/usr/bin/env python

import argparse
import csv
import sys
import gensim
import numpy as np

parser = argparse.ArgumentParser(description='Identity Evaluation.')
parser.add_argument('--w2v',          default='all.norm-sz100-w10-cb0-it1-min100.w2v', nargs='?', help='Path to the word2vec model.')
parser.add_argument('--subsumptions', default='subsumptions-test.txt', nargs='?', help='Path to the test subsumptions.')
args = vars(parser.parse_args())

w2v = gensim.models.KeyedVectors.load(args['w2v'])
w2v.init_sims(replace=True)

subsumptions_test = []

with open(args['subsumptions']) as f:
    reader = csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE)
    for row in reader:
        subsumptions_test.append((row[0], row[1]))

def compute_ats(measures):
    return [sum(measures[j].values()) / len(subsumptions_test) for j in range(len(measures))]

def compute_auc(ats):
    return sum([ats[j] + ats[j + 1] for j in range(0, len(ats) - 1)]) / 2 / 10

measures = [{} for _ in range(0, 10)]
file_ptr_ms = open("i_test_candidates2",'w')
file_ptr_hypo = open("i_test_hypo2",'w')
file_ptr_gold = open("i_test_gold2",'w')
prev_hypo = ''
gold_list = ''
out_ms = ''
count = 0
temp_hyper_list = []
for i, (hyponym, hypernym) in enumerate(subsumptions_test):
    actual  = [w for w, _ in w2v.most_similar(positive=[w2v[hyponym]], topn=10)]
    if count==0 or prev_hypo == hyponym :
        gold_list = gold_list + hypernym + '\t'
        for word in actual:
		if word not in temp_hyper_list :
			temp_hyper_list.append(word)
        prev_hypo = hyponym
	count = 1
    elif prev_hypo != hyponym :
        gold_list = gold_list + '\n'
	for word in temp_hyper_list :
		out_ms = out_ms + str(word) + "\t"
	out_ms = out_ms + '\n'
        file_ptr_ms.write(out_ms)
        file_ptr_hypo.write(prev_hypo + '\n')
        file_ptr_gold.write(gold_list)
        
	gold_list = ''
        out_ms = ''
	temp_hyper_list = []
		
        prev_hypo = hyponym
        gold_list = gold_list + hypernym + '\t'
        for word in actual:
		if word not in temp_hyper_list :
			temp_hyper_list.append(word)
				
    for j in range(0, len(measures)):
        measures[j][(hyponym, hypernym)] = 1. if hypernym in actual[:j + 1] else 0.

    if (i + 1) % 100 == 0:
        ats = compute_ats(measures)
        auc = compute_auc(ats)
        ats_string = ', '.join(['A@%d=%.6f' % (j + 1, ats[j]) for j in range(len(ats))])
        print('%d examples out of %d done for identity: %s. AUC=%.6f.' % (
            i + 1,
            len(subsumptions_test),
            ats_string,
            auc))
file_ptr_ms.close()
file_ptr_hypo.close()
file_ptr_gold.close()
ats = [sum(measures[j].values()) / len(subsumptions_test) for j in range(len(measures))]
auc = sum([ats[j] + ats[j + 1] for j in range(0, len(ats) - 1)]) / 2 / 10
ats_string = ', '.join(['A@%d=%.4f' % (j + 1, ats[j]) for j in range(len(ats))])
print('For identity: overall %s. AUC=%.6f.' % (ats_string, auc))
