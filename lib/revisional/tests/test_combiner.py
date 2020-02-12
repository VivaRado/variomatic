# -*- coding: utf-8 -*-

from context import sample
from colors import tcolor
import pprint
import unittest
import itertools
import collections

class CombinerTestSuite(unittest.TestCase):
	"""Combiner test cases."""

	
	def test_seq_gap_of_one(self):
		#
		pass
		#
		'''
		seq_lists = [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13], [15, 16, 17, 18, 19, 20, 21], [23]]
		
		#
		new_seq_list_gap_one = []
		#
		#
		sl_c = seq_lists.copy()
		#
		bypass_ix = []
		#
		def run_seq(sq_l, bp_inx):
			
			sq = 0	

			for idx,item in enumerate(sq_l):
				#
				if sq+1 != len(sq_l):
					#
					last_sq = sl_c[idx][-1]
					first_next_sq = sl_c[idx+1][0]
					#
					if last_sq + 1 == first_next_sq - 1: # gap of one
						#
						print("gap one")
						#
						print(last_sq, first_next_sq)
						#
						bp_inx.append(idx)
						#

						#
						new_seq_list_gap_one.append(sl_c[idx]+sl_c[idx+1])
						#
						# has been updated, rerun
						#
						return new_seq_list_gap_one, bp_inx
						#
					#if not idx or item-1 != seq_lists[-1][-1]:
						
						#seq_lists.append([item])
					#else:

						#seq_lists[-1].append(item)
					#
				sq += 1
				#
		#
		#print(new_seq_list_gap_one)
		#
		for x in len(seq_lists):
			#
			i = 0
			#
			sl_c_b = seq_lists.copy()
			#
			if x in bypass_ix:
				#
				del sl_c_b[x]
				#
			#
			r_ = run_seq(sl_c_b,bypass_ix)
			#
			#
			print(r_[0], r_[1])
		#
		'''

	def test_seq_gap_of_one_a(self):
		#
		seq_lists = [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13], [15, 16, 17, 18, 19, 20, 21], [23,24], [26,27,28], [30,31], [34,35,36]]
		#
		n = len(seq_lists)
		#
		test_list = [seq_lists[i] + (seq_lists[i+1] if i+1 < n else []) for i in range(0, n, 2)]

		n = len(test_list)

		test_list_b = [test_list[i] + (test_list[i+1] if i+1 < n else []) for i in range(0, n, 2)]
		#
		#
		#needs repetition
		#

	def test_seq_gap_of_one_b(self):
		#
		#
		print ('\n'+tcolor.WARNING + "TESTING: test_seq_gap_of_one_b" + tcolor.ENDC)
		#
		#
		seq_lists =        [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13], [15, 16, 17, 18, 19, 20, 21], [23]]#[[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13], [15, 16, 17, 18, 19, 20, 21], [23, 24], [26, 27, 28], [30, 31], [34, 35, 36]]
		seq_lists_should = [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13,   15, 16, 17, 18, 19, 20, 21,   23]]#[[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13,   15, 16, 17, 18, 19, 20, 21,   23, 24,   26, 27, 28,   30, 31], [34, 35, 36]]
		#
		'''
		
		iterate seq_lists

		look for gaps

		record in between inx [0,1]

		if its end exists in start of las in combine list, append next inx to it
	
		result of combination list [[0, 1, 2, 3], [4]]

		result of combination list [[0,3], [4]]


		'''
		#
		comb_list = []
		#
		sl_c = seq_lists.copy()
		#
		for idx,item in enumerate(seq_lists):
			#
			if idx+1 != len(seq_lists):
				#
				last_sq = sl_c[idx][-1]
				first_next_sq = sl_c[idx+1][0]
				#
				if last_sq + 1 == first_next_sq - 1: # gap of one
					#
					if len(comb_list)>0:
						#
						if idx == comb_list[-1][-1]:
							#
							comb_list[-1].append(idx+1)
							#
						else:
							#
							comb_list.append( [idx,idx+1])
							#
						#
					else:
						#
						comb_list.append( [idx,idx+1])
						#
				else:
					#
					comb_list.append([idx+1])
					#
				#
			#
		#
		comb_range = []
		#
		for x in comb_list:
			#
			if len(x) > 1:
				#
				comb_range.append([x[0],x[-1]])
				#
			else:
				#
				comb_range.append(x)
				#
			#
		#
		merge = comb_range
		#
		sl_c_new = []
		#
		for t in merge:
			#
			if len(t)>1:
				#
				merged = sl_c[t[0]:t[1]+1]  # merging values within a range
				#
				sl_c_new.append(sum(merged, []))         # slice replacement
				#
			else:
				#
				sl_c_new.append(sl_c[t[0]])
				#
		#
		print("Initial")
		print(seq_lists)
		print("slc")
		print(sl_c_new)
		#
		self.assertEqual(sl_c_new, seq_lists_should)
		#

if __name__ == '__main__':
	unittest.main()
