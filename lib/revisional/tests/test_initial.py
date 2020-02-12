# -*- coding: utf-8 -*-

from context import sample
from colors import tcolor
import pprint
import unittest
import itertools
import collections

class InitialTestSuite(unittest.TestCase):
	"""Initial test cases."""

	####
	# test_rotate_points
	####

	''' 
		We take that the contour direction is counter clockwise.
		and our set contains contour indexed points [1,21,22,23]
		
		The appropriate result after rotate_points() should be [21,22,23,1]
		as in circular counter clockwise fashion,
		point 1 goes after the last point 23 (length of points).
		
		Data in l_t items:

		[ Length from center, 
		  [x,y], 
		  Index sorted according to length from center,
		  Index on the glif line
		]

		We are trying to correct "Index on the glif line"

	'''

	#
	####
	# END test_rotate_points
	####

	def test_rotate_points_a(self):
		#
		print ('\n'+tcolor.WARNING + "TESTING: test_rotate_points_a" + tcolor.ENDC)
		#
		''' 
			"Point at start should be at end"

		'''
		#
		rotate_before = [
			[4, [193.5, -539.0], 19, 1 ],
			[3, [330.5, -421.0], 20, 21],
			[2, [329.5, -467.0], 21, 22],
			[1, [312.5, -496.0], 22, 23]
		]
		#
		rotate_after = [
			[3, [330.5, -421.0], 20, 21],
			[2, [329.5, -467.0], 21, 22],
			[1, [312.5, -496.0], 22, 23],
			[4, [193.5, -539.0], 19, 1 ]
		]
		#
		# The length of points in the glif
		len_points = 23
		#
		rotated_points = sample.rotate_points(rotate_before, len_points)
		#
		self.assertEqual(rotated_points, rotate_after)
		#
	#
	def test_rotate_points_b(self):
		#
		print ('\n'+tcolor.WARNING + "TESTING: test_rotate_points_b" + tcolor.ENDC)
		#
		''' 
			"Point 1 and 2 should be after 23"

		'''
		#
		rotate_before = [
			[1, [193.5, -539.0], 19,  1],
			[3, [110.5, -624.0], 6,   2],
			[2, [312.5, -496.0], 22, 23]
		]
		#
		rotate_after = [
			[2, [312.5, -496.0], 22, 23],
			[1, [193.5, -539.0], 19,  1],
			[3, [110.5, -624.0], 6,   2],
		]
		#
		# The length of points in the glif
		len_points = 23
		#
		rotated_points = sample.rotate_points(rotate_before, len_points)
		#
		self.assertEqual(rotated_points, rotate_after)
		#
	#
	####
	# test_lineate_points
	####
	#
	def test_lineate_points_a(self):
		#
		print ('\n'+tcolor.WARNING + "TESTING: test_lineate_points_a" + tcolor.ENDC)
		#
		'''
			See if sequence has start and end and rotate accordingly
		'''
		#
		#
		lineate_before = [[1, 2, 3, 4, 5, 6, 7], [9, 10, 11, 12, 13, 14, 15], [19, 20, 21, 22, 23]]
		#
		len_points = 23
		#
		lineate_after = [19, 20, 21, 22, 23, 1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15]
		#
		rot_seq = sample.rotate_points([],len_points,lineate_before)
		#
		self.assertEqual(rot_seq, lineate_after)
		#
	# #
	def test_lineate_points_b(self):
		#
		print ('\n'+tcolor.WARNING + "TESTING: test_lineate_points_b" + tcolor.ENDC)
		#
		''' 
			Line sequence preference according to center transfer psca matches on the target
			Trying to determine what is the most appropriate line from the sequence
			Keeping in mind that the most appropiate line may be between the end and start of the sequences.
			so we must first act on the sequences. We are not looking for precise match only for the line
			that can further be triangulated and matched.

		'''
		#
		len_points = 23
		#
		in_line_seq = [[6, 7], [9, 10, 11, 12, 13, 14, 15], [19, 20, 21, 22, 23]]
		#
		rot_seq = sample.rotate_points([],len_points,in_line_seq)
		#
		'''
			Since there is no start and end in the sequence, we recieve a joined result with no rotation.

			[6, 7, 9, 10, 11, 12, 13, 14, 15, 19, 20, 21, 22, 23]

		'''
		#
		#
		'''
			The contents of in_psca_t_m correspond to Pre, Search Center and Ante, matches on the target.
			The zero index is the distance from center index and the first is the index on the glif line.

		'''
		#
		#
		in_psca_t_m = [
			[(18, 13), (22, 23), (12, 7) ], 
			[(17, 14), (22, 23), (21, 22)], 
			[ (8, 15), (13, 20), (22, 23)]
		]
		#
		in_psca_t_m_ginx = sample.psca_glif_line_inx(in_psca_t_m)
		#
		#
		'''
			Just glif line index points according to center transfer matches
			[
				[13, 23, 7 ], 
				[14, 23, 22], 
				[15, 20, 23]
			]
		'''
		#
		#
		'''
			To determine the what will be the final line sequence we must find what points in_psca_t_m
			appear in what sequence and extract that sequence.

			According to the PSCA matches, the smaller the index the better the match.

				[6, 7, 9, 10, 11, 12, 13, 14, 15, 19, 20, 21, 22, 23]
			P       3                  1                           2
			SC                             1                   3   2
			A                                  1       2           3

			The real matches are

			P  = (18, 13)
			SC = (17, 14)
			A  = ( 8, 15)
			
			#
			
			We can see that the line can be cliped in a few locations that do not have linearity.
			What if we had circularity [23, 1] end and start? Could we still check for linearity?
			And how could we clip the appropriate line?

			Padded Line:

				[19, 20, 21, 22, 23, 1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15]
			P                     2                    3                  1
			SC                3   2                                           1
			A         2           3                                               1

			According to this we see that the best line option is 13,14,15
			and we should grab a few more points maybe from each side if the points exist in the list
		'''
		
		ag_prob = sample.line_agnostic_probable(rot_seq, in_psca_t_m_ginx)


		'''
			Padded Line

			Lets call this function line_agnostic_probable
			
				[19, 20, 21, 22, 23, 1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15]

			creates a list incrementing the index by index in PSCA

				[ 0,  2,  0,  3,  7, 0, 0, 0, 0, 0, 0, 3, 0,  0,  0,  0,  1,  1,  1]

			Avoiding zero the best matches from 1 to 3 are:

				[ -, 20,  -, 22,  -, -, -, -, -, -, -, 7, -,  -,  -,  -, 13, 14, 15]

			We can sequence this to:

				[[20],[22],[7],[13,14,15]]

			And just get the biggest sequence, that is our Target PSCA line:

				[13,14,15]

			for the non padded line:

				[6, 7, 9, 10, 11, 12, 13, 14, 15, 19, 20, 21, 22, 23]
				[0, 3, 0,  0,  0,  0,  1,  1,  1,  0,  2,  0,  3,  7]
				[-, 3, -,  -,  -,  -,  1,  1,  1,  -,  2,  -,  3,  7]
				[   3,                 1,  1,  1,      2,      3    ]
				[[7],[13,14,15],[20],[22]]
				[13,14,15]

		'''
		#

		#
	#
	def test_lineate_points_c(self):
		#
		print ('\n'+tcolor.WARNING + "TESTING: test_lineate_points_c" + tcolor.ENDC)
		#
		''' 
			Line sequence preference according to center transfer psca matches on the target
			Trying to determine what is the most appropriate line from the sequence
			Keeping in mind that the most appropiate line may be between the end and start of the sequences.
			so we must first act on the sequences. We are not looking for precise match only for the line
			that can further be triangulated and matched.

		'''
		#

		#
		len_points = 23
		best_match_for_sc = 23
		#
		
		#
		in_line_seq = [[18, 19, 20, 21, 22, 23], [1], [14, 15]]
		#
		rotated_seq = sample.rotate_points([],len_points,in_line_seq)
		#
		# [21, 22, 23, 1, 14, 15, 18, 19, 20]
		# Find 23,1
		#
		
		#
		rot_cent = sample.rotate_center_clip(rotated_seq, best_match_for_sc, len_points, 7)
		#
		#print("___>")
		#print(rot_cent)
		#
		rot_seq = sample.rotate_points([],len_points,in_line_seq)
		#
		'''
			[21, 22, 23, 1]
			[16, 17, 18, 19, 20, 21, 22, 23, 1, 2, 14]

		'''
		#
		#
		'''
			The contents of in_psca_t_m correspond to Pre, Search Center and Ante, matches on the target.
			The zero index is the distance from center index and the first is the index on the glif line.

		'''
		#
		#
		in_psca_t_m = [
			[(21, 22), (22, 23), (20, 21)], 
			[(22, 23), (19, 1),  (20, 21)], 
			[(19, 1),  (16, 18), (22, 23)]
		]

		#
		in_psca_t_m_ginx = sample.psca_glif_line_inx(in_psca_t_m)
		#
		#print(in_psca_t_m_ginx)
		#print(rotated_seq)
		#
		#
		'''
			Just glif line index points according to center transfer matches
			[
				[20, 15, 19], 
				[21, 18, 23], 
				[22, 23, 21]
			]
		'''
		#
		#
		'''
			To determine the what will be the final line sequence we must find what points in_psca_t_m
			appear in what sequence and extract that sequence.

			According to the PSCA matches, the smaller the index the better the match.

				[  1, 15, 16, 17, 18, 19, 20, 21 ]
			P              1   2   3
			SC                 3   1   2   
			A                      1   3   2

				[  0,  0,  1,  5,  5,  5,  2,  0 ]

			The real matches are

			P  = (10, 17)
			SC = (16, 18)
			A  = (15, 19)
			
			#
		'''
		
		ag_prob = sample.line_agnostic_probable(rot_seq, in_psca_t_m_ginx)

		#print(ag_prob)

		'''
			Padded Line

			Lets call this function line_agnostic_probable
			
				[19, 20, 21, 22, 23, 1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15]

			creates a list incrementing the index by index in PSCA

				[ 0,  2,  0,  3,  7, 0, 0, 0, 0, 0, 0, 3, 0,  0,  0,  0,  1,  1,  1]

			Avoiding zero the best matches from 1 to 3 are:

				[ -, 20,  -, 22,  -, -, -, -, -, -, -, 7, -,  -,  -,  -, 13, 14, 15]

			We can sequence this to:

				[[20],[22],[7],[13,14,15]]

			And just get the biggest sequence, that is our Target PSCA line:

				[13,14,15]

			for the non padded line:

				[6, 7, 9, 10, 11, 12, 13, 14, 15, 19, 20, 21, 22, 23]
				[0, 3, 0,  0,  0,  0,  1,  1,  1,  0,  2,  0,  3,  7]
				[-, 3, -,  -,  -,  -,  1,  1,  1,  -,  2,  -,  3,  7]
				[   3,                 1,  1,  1,      2,      3    ]
				[[7],[13,14,15],[20],[22]]
				[13,14,15]

		'''
		#
	#
	# def test_determine_missing(self):
	# 	#
	# 	print ('\n'+tcolor.WARNING + "TESTING: test_determine_missing" + tcolor.ENDC)
	# 	print ('\n\t'+tcolor.OKBLUE + "Best Matching Point for SC is 15, before triangulation" + tcolor.ENDC)
	# 	#
	# 	'''
	# 		Here we can see when PSCA have appropriate matches on the target

	# 		BEST LINE PRE
	# 		[5, 6, 7, 8, 9, 10, 11]
	# 		BEST LINE SC
	# 		[6, 7, 8, 9, 10, 11, 12]
	# 		BEST LINE ANTE
	# 		[7, 8, 9, 10, 11, 12, 13]
			
	# 		Here are examples where PSCA is failing because there is no point in the Pre

	# 		BEST LINE PRE
	# 		[22, 1, 2, 3, 4, 5, 6]
	# 		BEST LINE SC
	# 		[13, 14, 15, 16, 17, 18, 19]
	# 		BEST LINE ANTE
	# 		[13, 14, 15, 16, 17, 18, 19]
			
	# 		Failing PSCA no point in Search Center

	# 		BEST LINE SC
	# 		[12, 13, 14, 15, 16, 17, 18]
	# 		BEST LINE SC
	# 		[22, 1, 2, 3, 4, 5, 6]
	# 		BEST LINE ANTE
	# 		[13, 14, 15, 16, 17, 18, 19]
				
	# 		Failing PSCA no point in Ante

	# 		BEST LINE PRE
	# 		[11, 12, 13, 14, 15, 16, 17]
	# 		BEST LINE SC
	# 		[12, 13, 14, 15, 16, 17, 18]
	# 		BEST LINE ANTE
	# 		[22, 1, 2, 3, 4, 5, 6]

	# 		The Failing Best Lines (BL) can be compared with the Matching Best Lines.

	# 	'''

	# 	len_points = 22

	# 	blm_pre = [
	# 		[22, 1, 2, 3, 4, 5, 6],
	# 		[12, 13, 14, 15, 16, 17, 18],
	# 		[13, 14, 15, 16, 17, 18, 19]

	# 	]

	# 	blm_searchcenter = [
	# 		[12, 13, 14, 15, 16, 17, 18],
	# 		[22, 1, 2, 3, 4, 5, 6],
	# 		[13, 14, 15, 16, 17, 18, 19]

	# 	]

	# 	blm_ante = [
	# 		[12, 13, 14, 15, 16, 17, 18],
	# 		[22, 1, 2, 3, 4, 5, 6],
	# 		[13, 14, 15, 16, 17, 18, 19]

	# 	]
	# 	#
	# 	agregate_line_problem_p = sample.get_aggregate_line(blm_pre, len_points, 7)
	# 	agregate_line_problem_sc = sample.get_aggregate_line(blm_searchcenter, len_points, 7)
	# 	agregate_line_problem_a = sample.get_aggregate_line(blm_ante, len_points, 7)
	# 	#
	# 	test_should = [
	# 		[12, 13, 14, 15, 16, 17, 18],
	# 		[13, 14, 15, 16, 17, 18, 19],
	# 		[13, 14, 15, 16, 17, 18, 19],
	# 	]
	# 	#
	# 	test_res = [
	# 		agregate_line_problem_p,
	# 		agregate_line_problem_sc,
	# 		agregate_line_problem_a
	# 	]
	# 	#
	# 	self.assertEqual(test_should, test_res)
	# 	#
	def test_multiline_best(self):
		#
		#
		print ('\n'+tcolor.WARNING + "TESTING: test_multiline_best" + tcolor.ENDC)
		#
		'''#
		ct = [
				 [
				  [(10, 8),
				   (30.16080152706108, 37.0, (428.41421760122375, -371.4703535337667)),
				   323.2015403746773,
				   390.3623419017384,
				   [416.0, -354.0],
				   [453.0, -354.0],
				   30],
				  [(11, 14),
				   (17.84524341065403,
					73.7563556583431,
					(457.45332852132924, -412.3366852170857)),
				   638.5473015664902,
				   730.1489006354873,
				   [416.0, -354.0],
				   [472.0, -402.0],
				   17],
				  [(8, 13),
				   (72.25163430800929,
					75.6042326857432,
					(403.10358912514585, -335.8510626655843)),
				   804.3178849371689,
				   952.1737519309214,
				   [416.0, -354.0],
				   [462.0, -294.0],
				   72]],
				 [
				  [(2, 12),
				   (50.00131034530255,
					50.08991914547278,
					(381.40703880611, -264.5352419995925)),
				   74.45396486701065,
				   174.545194357786,
				   [384.0, -266.0],
				   [406.0, -221.0],
				   50],
				  [(6, 9),
				   (28.952127418870038,
					32.449961479175904,
					(396.76000226442557, -273.20809684544474)),
				   212.1493277933332,
				   273.5514166913792,
				   [384.0, -266.0],
				   [411.0, -248.0],
				   28],
				  [(3, 11),
				   (6.279591565389425,
					141.50971698084905,
					(260.91140590887153, -196.4675274821766)),
				   443.87392734790774,
				   591.6632358941462,
				   [384.0, -266.0],
				   [264.0, -191.0],
				   6]],
				 [
				  [(7, 10),
				   (23.828424398734406,
					24.020824298928627,
					(264.0232136089853, -233.74237595563295)),
				   36.14975128564038,
				   83.9989999833034,
				   [261.0, -234.0],
				   [262.0, -210.0],
				   23],
				  [(2, 12),
				   (0.6414571884576102,
					145.58159224297555,
					(406.05446457103244, -221.63914077880088)),
				   46.691726174773066,
				   192.9147756062062,
				   [261.0, -234.0],
				   [406.0, -221.0],
				   0],
				  [(3, 11),
				   (42.58999706750034,
					43.104524124504614,
					(267.61621315080447, -233.43619743400245)),
				   141.4028788932992,
				   227.09740008530417,
				   [261.0, -234.0],
				   [264.0, -191.0],
				   42]
				  ]
			]

		#'''
		_p = [(10, 8), (11, 14), (8, 13)]
		_c = [(2, 12), (6, 9),   (3, 11)]
		_a = [(7, 10), (2, 12),  (3, 11)]
		#
		__p = [10, 11, 8]
		__c = [2,  6,  3]
		__a = [7,  2,  3]
		
		#BEST LINE PRE
		l_p = [6, 7, 8, 9, 10], [12, 13, 14, 15, 1], [11, 12, 13, 14, 15]
		#BEST LINE SC
		l_c = [10, 11, 12, 13, 14], [7, 8, 9, 10, 11], [9, 10, 11, 12, 13]
		#BEST LINE ANTE
		l_a = [8, 9, 10, 11, 12],[10, 11, 12, 13, 14],[9, 10, 11, 12, 13]
		'''

		#
		_p = [(4, 3), (9, 4), (12, 5)]
		_c = [(9, 4), (4, 3), (12, 5)]
		_a = [(12, 5), (9, 4), (4, 3)]
		#
		__p = [4, 9, 12]
		__c = [9, 4, 12]
		__a = [12,9, 4]
		#
		l_p = [[1, 2, 3, 4, 5],[2, 3, 4, 5, 6],[3, 4, 5, 6, 7]]
		l_c = [[2, 3, 4, 5, 6],[1, 2, 3, 4, 5],[3, 4, 5, 6, 7]]
		l_a = [[3, 4, 5, 6, 7],[2, 3, 4, 5, 6],[1, 2, 3, 4, 5]]
		#
		'''
		#
		# _p = [(8, 15), (13, 20), (15, 19)]
		# _c = [(15, 19), (16, 18), (9, 16)]
		# _a = [(9, 16), (10, 17), (16, 18)]
		# #
		# __p = [8, 13, 15]
		# __c = [15, 16, 9]
		# __a = [9, 10, 16]
		# #
		# l_p = [[13, 14, 15, 16, 17],[18, 19, 20, 21, 22],[17, 18, 19, 20, 21]]
		# l_c = [[17, 18, 19, 20, 21],[16, 17, 18, 19, 20],[14, 15, 16, 17, 18]]
		# l_a = [[14, 15, 16, 17, 18],[15, 16, 17, 18, 19],[16, 17, 18, 19, 20]]
		#
		s = [l_p, l_c, l_a]
		#
		s_i = [[0,1,2], [0,1,2], [0,1,2]]
		#
		perm = list(itertools.product(*s))
		perm_i = list(itertools.product(*s_i))
		#
		pprint.pprint(perm)
		pprint.pprint(perm_i)
		#
		results = []
		#
		for p in perm:
			#
			#testdata = ([6, 7, 8, 9, 10], [10, 11, 12, 13, 14], [8, 9, 10, 11, 12])
			#
			unique_data = set(x for l in p for x in l)
			# 
			# {6, 7, 8, 9, 10, 11, 12, 13, 14}
			#
			#print(p)
			#print(unique_data)
			#
			result = []
			#
			print(unique_data)
			#
			for x in unique_data:
				#
				total = -1
				#
				z = 0
				#
				for y in p:
					#
					if x in y:
						#
						total = total + 1
						#
					#
					z = z + 1
					#

					#
				#
				#print(x, total)
				#
				result.append(total)
				#
			#
			results.append(result)
			#
		#
		pprint.pprint(results)
		#
		sum_results = []
		#
		o = 0
		#
		for u in results:
			#
			sum_results.append([o,sum(u),perm_i[o], sum(perm_i[o])])
			#
			o = o + 1
			#
		#
		pprint.pprint(sum_results)
		#
		sorted_sum_results = sorted(sum_results, key = lambda x: x[1] - sum(x[2]), reverse=True)
		#
		pprint.pprint(sorted_sum_results)
		#
		item = perm[sorted_sum_results[0][0]]
		#
		print('--')
		print(item)
		#
	#
	def test_combine_order(self):
		#
		print ('\n'+tcolor.WARNING + "TESTING: test_combine_order" + tcolor.ENDC)
		#

		#BEST TARGET CT AGGREGATE LINE
		a = [10, 11, 12, 13, 14]
		
		#BEST TARGET CT LINE
		b = [7, 8, 9, 10, 11]
		#
		m_a = min(a)
		m_b = min(b)
		#
		if m_a > m_b:
			#
			iter_l = b
			iter_m = a
			#
		else:
			#
			iter_l = a
			iter_m = b
			#
		#
		print( sample.merge_overlap(iter_l,iter_m) )
		#
	#

	def test_sgrad_certainty_b(self):
		#
		#
		print ('\n'+tcolor.WARNING + "TESTING: test_sgrad_certainty_b" + tcolor.ENDC)
		#
		''' 
	
		Compare SGRADs for certainty.

		We run instance a against instance b, and vice versa.
		We generate a sgrad and then compare the sgrad, gathering the most certain matching.

		The coordinates might differ during creation, but the point indexes remain standard.

		We can use those indexes after this function to match the coordinates of the original UFO glif.

		Some points have multiple matches that we should address.

		''' 
		# { source point index on the line (lower node number): [
		# 		[simplification_level, target point index on the line (lower node number), instance_a coordinate, instance_b coordinate ]
		# 	],
		# }
		#
		s_grad_rb = collections.OrderedDict({1: [[0, 1, [472.0, -700.0], [472.0, -699.5]],
     [1, 1, [472.0, -700.0], [472.0, -699.5]],
     [2, 1, [472.0, -700.0], [472.0, -699.5]],
     [3, 1, [472.0, -700.0], [472.0, -699.5]],
     [4, 1, [472.0, -700.0], [472.0, -699.5]],
     [5, 1, [472.0, -700.0], [472.0, -699.5]],
     [6, 1, [472.0, -700.0], [472.0, -699.5]]],
 2: [[0, 2, [316.0, -711.0], [316.0, -710.5]],
     [1, 2, [316.0, -711.0], [316.0, -710.5]],
     [2, 2, [316.0, -711.0], [316.0, -710.5]],
     [3, 2, [316.0, -711.0], [316.0, -710.5]],
     [4, 2, [316.0, -711.0], [316.0, -710.5]],
     [5, 2, [316.0, -711.0], [316.0, -710.5]],
     [6, 2, [316.0, -711.0], [316.0, -710.5]]],
 3: [[0, 3, [149.0, -672.0], [149.0, -671.5]],
     [1, 3, [149.0, -672.0], [149.0, -671.5]],
     [2, 3, [149.0, -672.0], [149.0, -671.5]],
     [3, 3, [149.0, -672.0], [149.0, -671.5]],
     [4, 3, [149.0, -672.0], [149.0, -671.5]],
     [5, 3, [149.0, -672.0], [149.0, -671.5]],
     [6, 3, [149.0, -672.0], [149.0, -671.5]],
     [10, 3, [149.0, -672.0], [149.0, -671.5]],
     [11, 3, [149.0, -672.0], [149.0, -671.5]],
     [12, 3, [149.0, -672.0], [149.0, -671.5]],
     [13, 3, [149.0, -672.0], [149.0, -671.5]],
     [14, 3, [149.0, -672.0], [149.0, -671.5]]],
 4: [[0, 4, [87.0, -531.0], [87.0, -530.5]],
     [1, 4, [87.0, -531.0], [87.0, -530.5]],
     [2, 4, [87.0, -531.0], [87.0, -530.5]],
     [3, 4, [87.0, -531.0], [87.0, -530.5]],
     [4, 4, [87.0, -531.0], [87.0, -530.5]],
     [5, 4, [87.0, -531.0], [87.0, -530.5]],
     [6, 4, [87.0, -531.0], [87.0, -530.5]],
     [10, 5, [87.0, -531.0], [87.0, -447.5]],
     [11, 5, [87.0, -531.0], [87.0, -447.5]],
     [12, 5, [87.0, -531.0], [87.0, -447.5]],
     [13, 5, [87.0, -531.0], [87.0, -447.5]],
     [14, 5, [87.0, -531.0], [87.0, -447.5]]],
 5: [[0, 5, [87.0, -490.0], [87.0, -447.5]]],
 6: [[0, 5, [87.0, -448.0], [87.0, -447.5]],
     [1, 5, [87.0, -448.0], [87.0, -447.5]],
     [2, 5, [87.0, -448.0], [87.0, -447.5]],
     [3, 5, [87.0, -448.0], [87.0, -447.5]],
     [4, 5, [87.0, -448.0], [87.0, -447.5]],
     [5, 5, [87.0, -448.0], [87.0, -447.5]],
     [6, 5, [87.0, -448.0], [87.0, -447.5]],
     [10, 5, [87.0, -448.0], [87.0, -447.5]]],
 7: [[0, 6, [160.0, -316.0], [156.0, -313.5]],
     [1, 6, [160.0, -316.0], [156.0, -313.5]],
     [2, 6, [160.0, -316.0], [156.0, -313.5]],
     [3, 6, [160.0, -316.0], [156.0, -313.5]],
     [4, 6, [160.0, -316.0], [156.0, -313.5]],
     [5, 6, [160.0, -316.0], [156.0, -313.5]],
     [6, 6, [160.0, -316.0], [156.0, -313.5]],
     [10, 6, [160.0, -316.0], [156.0, -313.5]],
     [11, 6, [160.0, -316.0], [156.0, -313.5]],
     [12, 6, [160.0, -316.0], [156.0, -313.5]],
     [13, 6, [160.0, -316.0], [156.0, -313.5]],
     [14, 6, [160.0, -316.0], [156.0, -313.5]]],
 8: [[0, 7, [253.0, -298.0], [240.0, -296.5]],
     [1, 7, [253.0, -298.0], [240.0, -296.5]],
     [2, 7, [253.0, -298.0], [240.0, -296.5]],
     [3, 7, [253.0, -298.0], [240.0, -296.5]],
     [4, 7, [253.0, -298.0], [240.0, -296.5]],
     [5, 7, [253.0, -298.0], [240.0, -296.5]],
     [6, 7, [253.0, -298.0], [240.0, -296.5]],
     [10, 7, [253.0, -298.0], [240.0, -296.5]],
     [11, 7, [253.0, -298.0], [240.0, -296.5]],
     [12, 9, [253.0, -298.0], [384.0, -264.5]]],
 9: [[0, 16, [453.0, -354.0], [472.0, -400.5]],
     [1, 16, [453.0, -354.0], [472.0, -400.5]],
     [2, 16, [453.0, -354.0], [472.0, -400.5]],
     [3, 16, [453.0, -354.0], [472.0, -400.5]],
     [4, 16, [453.0, -354.0], [472.0, -400.5]],
     [5, 8, [453.0, -354.0], [416.0, -352.5]],
     [6, 8, [453.0, -354.0], [416.0, -352.5]],
     [10, 8, [453.0, -354.0], [416.0, -352.5]],
     [11, 8, [453.0, -354.0], [416.0, -352.5]],
     [12, 8, [453.0, -354.0], [416.0, -352.5]],
     [13, 8, [453.0, -354.0], [416.0, -352.5]],
     [14, 8, [453.0, -354.0], [416.0, -352.5]]],
 10: [[0, 14, [411.0, -248.0], [406.0, -219.5]],
      [1, 14, [411.0, -248.0], [406.0, -219.5]],
      [2, 14, [411.0, -248.0], [406.0, -219.5]],
      [3, 14, [411.0, -248.0], [406.0, -219.5]],
      [4, 14, [411.0, -248.0], [406.0, -219.5]],
      [5, 14, [411.0, -248.0], [406.0, -219.5]],
      [6, 14, [411.0, -248.0], [406.0, -219.5]],
      [10, 9, [411.0, -248.0], [384.0, -264.5]],
      [11, 9, [411.0, -248.0], [384.0, -264.5]],
      [12, 9, [411.0, -248.0], [384.0, -264.5]],
      [13, 14, [411.0, -248.0], [406.0, -219.5]],
      [14, 14, [411.0, -248.0], [406.0, -219.5]]],
 11: [[0, 13, [310.0, -211.0], [345.0, -196.5]],
      [1, 13, [310.0, -211.0], [345.0, -196.5]],
      [2, 13, [310.0, -211.0], [345.0, -196.5]],
      [3, 13, [310.0, -211.0], [345.0, -196.5]],
      [4, 13, [310.0, -211.0], [345.0, -196.5]],
      [5, 13, [310.0, -211.0], [345.0, -196.5]],
      [6, 14, [310.0, -211.0], [406.0, -219.5]]],
 12: [[0, 11, [262.0, -210.0], [261.0, -232.5]],
      [1, 11, [262.0, -210.0], [261.0, -232.5]],
      [2, 11, [262.0, -210.0], [261.0, -232.5]],
      [3, 11, [262.0, -210.0], [261.0, -232.5]],
      [4, 11, [262.0, -210.0], [261.0, -232.5]],
      [5, 11, [262.0, -210.0], [261.0, -232.5]],
      [6, 11, [262.0, -210.0], [261.0, -232.5]]],
 13: [[0, 12, [264.0, -191.0], [264.0, -189.5]],
      [1, 12, [264.0, -191.0], [264.0, -189.5]],
      [2, 12, [264.0, -191.0], [264.0, -189.5]],
      [3, 12, [264.0, -191.0], [264.0, -189.5]],
      [4, 12, [264.0, -191.0], [264.0, -189.5]],
      [5, 12, [264.0, -191.0], [264.0, -189.5]],
      [6, 12, [264.0, -191.0], [264.0, -189.5]],
      [10, 12, [264.0, -191.0], [264.0, -189.5]],
      [11, 12, [264.0, -191.0], [264.0, -189.5]],
      [12, 12, [264.0, -191.0], [264.0, -189.5]],
      [13, 12, [264.0, -191.0], [264.0, -189.5]],
      [14, 12, [264.0, -191.0], [264.0, -189.5]]],
 14: [[0, 14, [406.0, -221.0], [406.0, -219.5]],
      [1, 14, [406.0, -221.0], [406.0, -219.5]],
      [2, 14, [406.0, -221.0], [406.0, -219.5]],
      [3, 14, [406.0, -221.0], [406.0, -219.5]],
      [4, 14, [406.0, -221.0], [406.0, -219.5]],
      [5, 14, [406.0, -221.0], [406.0, -219.5]],
      [6, 14, [406.0, -221.0], [406.0, -219.5]],
      [10, 14, [406.0, -221.0], [406.0, -219.5]],
      [11, 14, [406.0, -221.0], [406.0, -219.5]],
      [12, 14, [406.0, -221.0], [406.0, -219.5]],
      [13, 14, [406.0, -221.0], [406.0, -219.5]]],
 15: [[0, 15, [462.0, -294.0], [462.0, -292.5]],
      [1, 15, [462.0, -294.0], [462.0, -292.5]],
      [2, 15, [462.0, -294.0], [462.0, -292.5]],
      [3, 15, [462.0, -294.0], [462.0, -292.5]],
      [4, 15, [462.0, -294.0], [462.0, -292.5]],
      [5, 15, [462.0, -294.0], [462.0, -292.5]],
      [6, 15, [462.0, -294.0], [462.0, -292.5]],
      [10, 15, [462.0, -294.0], [462.0, -292.5]],
      [11, 15, [462.0, -294.0], [462.0, -292.5]],
      [12, 15, [462.0, -294.0], [462.0, -292.5]],
      [13, 15, [462.0, -294.0], [462.0, -292.5]],
      [14, 15, [462.0, -294.0], [462.0, -292.5]]],
 16: [[0, 16, [472.0, -402.0], [472.0, -400.5]],
      [1, 16, [472.0, -402.0], [472.0, -400.5]],
      [2, 16, [472.0, -402.0], [472.0, -400.5]],
      [3, 16, [472.0, -402.0], [472.0, -400.5]],
      [4, 16, [472.0, -402.0], [472.0, -400.5]],
      [5, 17, [472.0, -402.0], [472.0, -478.5]],
      [6, 17, [472.0, -402.0], [472.0, -478.5]]],
 17: [[0, 18, [472.0, -608.0], [472.0, -572.5]],
      [1, 18, [472.0, -608.0], [472.0, -572.5]],
      [2, 18, [472.0, -608.0], [472.0, -572.5]],
      [3, 18, [472.0, -608.0], [472.0, -572.5]],
      [4, 18, [472.0, -608.0], [472.0, -572.5]],
      [5, 18, [472.0, -608.0], [472.0, -572.5]],
      [6, 18, [472.0, -608.0], [472.0, -572.5]],
      [10, 18, [472.0, -608.0], [472.0, -572.5]],
      [11, 18, [472.0, -608.0], [472.0, -572.5]],
      [12, 18, [472.0, -608.0], [472.0, -572.5]],
      [13, 18, [472.0, -608.0], [472.0, -572.5]],
      [14, 18, [472.0, -608.0], [472.0, -572.5]]]}
)


		#
		s_grad_br = collections.OrderedDict({1: [[0, 1, [472.0, -700.0], [472.0, -700.5]],
     [1, 1, [472.0, -700.0], [472.0, -700.5]],
     [2, 1, [472.0, -700.0], [472.0, -700.5]],
     [3, 1, [472.0, -700.0], [472.0, -700.5]],
     [4, 1, [472.0, -700.0], [472.0, -700.5]],
     [5, 1, [472.0, -700.0], [472.0, -700.5]],
     [6, 1, [472.0, -700.0], [472.0, -700.5]]],
 2: [[0, 2, [316.0, -711.0], [316.0, -711.5]],
     [1, 2, [316.0, -711.0], [316.0, -711.5]],
     [2, 2, [316.0, -711.0], [316.0, -711.5]],
     [3, 2, [316.0, -711.0], [316.0, -711.5]],
     [4, 2, [316.0, -711.0], [316.0, -711.5]],
     [5, 2, [316.0, -711.0], [316.0, -711.5]],
     [6, 2, [316.0, -711.0], [316.0, -711.5]]],
 3: [[0, 3, [149.0, -672.0], [149.0, -672.5]],
     [1, 3, [149.0, -672.0], [149.0, -672.5]],
     [2, 3, [149.0, -672.0], [149.0, -672.5]],
     [3, 3, [149.0, -672.0], [149.0, -672.5]],
     [4, 3, [149.0, -672.0], [149.0, -672.5]],
     [5, 3, [149.0, -672.0], [149.0, -672.5]],
     [6, 3, [149.0, -672.0], [149.0, -672.5]],
     [10, 3, [149.0, -672.0], [149.0, -672.5]],
     [11, 3, [149.0, -672.0], [149.0, -672.5]],
     [12, 3, [149.0, -672.0], [149.0, -672.5]],
     [13, 3, [149.0, -672.0], [149.0, -672.5]],
     [14, 3, [149.0, -672.0], [149.0, -672.5]]],
 4: [[0, 4, [87.0, -531.0], [87.0, -531.5]],
     [1, 4, [87.0, -531.0], [87.0, -531.5]],
     [2, 4, [87.0, -531.0], [87.0, -531.5]],
     [3, 4, [87.0, -531.0], [87.0, -531.5]],
     [4, 4, [87.0, -531.0], [87.0, -531.5]],
     [5, 4, [87.0, -531.0], [87.0, -531.5]],
     [6, 4, [87.0, -531.0], [87.0, -531.5]]],
 5: [[0, 6, [87.0, -448.0], [87.0, -448.5]],
     [1, 6, [87.0, -448.0], [87.0, -448.5]],
     [2, 6, [87.0, -448.0], [87.0, -448.5]],
     [3, 6, [87.0, -448.0], [87.0, -448.5]],
     [4, 6, [87.0, -448.0], [87.0, -448.5]],
     [5, 6, [87.0, -448.0], [87.0, -448.5]],
     [6, 6, [87.0, -448.0], [87.0, -448.5]],
     [10, 6, [87.0, -448.0], [87.0, -448.5]],
     [11, 7, [87.0, -448.0], [160.0, -316.5]],
     [12, 7, [87.0, -448.0], [160.0, -316.5]],
     [13, 4, [87.0, -448.0], [87.0, -531.5]],
     [14, 4, [87.0, -448.0], [87.0, -531.5]]],
 6: [[0, 7, [156.0, -314.0], [160.0, -316.5]],
     [1, 7, [156.0, -314.0], [160.0, -316.5]],
     [2, 7, [156.0, -314.0], [160.0, -316.5]],
     [3, 7, [156.0, -314.0], [160.0, -316.5]],
     [4, 7, [156.0, -314.0], [160.0, -316.5]],
     [5, 7, [156.0, -314.0], [160.0, -316.5]],
     [6, 7, [156.0, -314.0], [160.0, -316.5]],
     [10, 7, [156.0, -314.0], [160.0, -316.5]],
     [11, 7, [156.0, -314.0], [160.0, -316.5]],
     [12, 7, [156.0, -314.0], [160.0, -316.5]],
     [13, 7, [156.0, -314.0], [160.0, -316.5]],
     [14, 7, [156.0, -314.0], [160.0, -316.5]]],
 7: [[0, 8, [240.0, -297.0], [253.0, -298.5]],
     [5, 8, [240.0, -297.0], [253.0, -298.5]],
     [6, 8, [240.0, -297.0], [253.0, -298.5]],
     [10, 8, [240.0, -297.0], [253.0, -298.5]],
     [11, 8, [240.0, -297.0], [253.0, -298.5]]],
 8: [[0, 9, [416.0, -353.0], [453.0, -354.5]],
     [1, 9, [416.0, -353.0], [453.0, -354.5]],
     [2, 9, [416.0, -353.0], [453.0, -354.5]],
     [3, 9, [416.0, -353.0], [453.0, -354.5]],
     [4, 9, [416.0, -353.0], [453.0, -354.5]],
     [5, 9, [416.0, -353.0], [453.0, -354.5]],
     [6, 9, [416.0, -353.0], [453.0, -354.5]],
     [10, 9, [416.0, -353.0], [453.0, -354.5]],
     [11, 9, [416.0, -353.0], [453.0, -354.5]],
     [12, 9, [416.0, -353.0], [453.0, -354.5]],
     [13, 9, [416.0, -353.0], [453.0, -354.5]],
     [14, 9, [416.0, -353.0], [453.0, -354.5]]],
 9: [[0, 10, [384.0, -265.0], [411.0, -248.5]],
     [1, 10, [384.0, -265.0], [411.0, -248.5]],
     [2, 10, [384.0, -265.0], [411.0, -248.5]],
     [3, 10, [384.0, -265.0], [411.0, -248.5]],
     [4, 10, [384.0, -265.0], [411.0, -248.5]],
     [5, 10, [384.0, -265.0], [411.0, -248.5]],
     [6, 14, [384.0, -265.0], [406.0, -221.5]],
     [10, 10, [384.0, -265.0], [411.0, -248.5]],
     [11, 10, [384.0, -265.0], [411.0, -248.5]],
     [12, 10, [384.0, -265.0], [411.0, -248.5]],
     [13, 10, [384.0, -265.0], [411.0, -248.5]]],
 10: [[0, 11, [332.0, -240.0], [310.0, -211.5]],
      [1, 11, [332.0, -240.0], [310.0, -211.5]],
      [2, 11, [332.0, -240.0], [310.0, -211.5]],
      [3, 11, [332.0, -240.0], [310.0, -211.5]],
      [4, 11, [332.0, -240.0], [310.0, -211.5]],
      [5, 11, [332.0, -240.0], [310.0, -211.5]]],
 11: [[0, 12, [261.0, -233.0], [262.0, -210.5]],
      [1, 12, [261.0, -233.0], [262.0, -210.5]],
      [2, 12, [261.0, -233.0], [262.0, -210.5]],
      [3, 12, [261.0, -233.0], [262.0, -210.5]],
      [4, 12, [261.0, -233.0], [262.0, -210.5]],
      [5, 12, [261.0, -233.0], [262.0, -210.5]],
      [6, 12, [261.0, -233.0], [262.0, -210.5]],
      [10, 14, [261.0, -233.0], [406.0, -221.5]],
      [11, 14, [261.0, -233.0], [406.0, -221.5]],
      [12, 14, [261.0, -233.0], [406.0, -221.5]]],
 12: [[0, 13, [264.0, -190.0], [264.0, -191.5]],
      [1, 13, [264.0, -190.0], [264.0, -191.5]],
      [2, 13, [264.0, -190.0], [264.0, -191.5]],
      [3, 13, [264.0, -190.0], [264.0, -191.5]],
      [4, 13, [264.0, -190.0], [264.0, -191.5]],
      [5, 13, [264.0, -190.0], [264.0, -191.5]],
      [6, 13, [264.0, -190.0], [264.0, -191.5]],
      [10, 13, [264.0, -190.0], [264.0, -191.5]],
      [11, 13, [264.0, -190.0], [264.0, -191.5]],
      [12, 13, [264.0, -190.0], [264.0, -191.5]],
      [13, 13, [264.0, -190.0], [264.0, -191.5]],
      [14, 13, [264.0, -190.0], [264.0, -191.5]]],
 13: [[0, 14, [345.0, -197.0], [406.0, -221.5]],
      [1, 14, [345.0, -197.0], [406.0, -221.5]],
      [2, 14, [345.0, -197.0], [406.0, -221.5]],
      [3, 14, [345.0, -197.0], [406.0, -221.5]],
      [4, 14, [345.0, -197.0], [406.0, -221.5]],
      [5, 14, [345.0, -197.0], [406.0, -221.5]]],
 14: [[0, 14, [406.0, -220.0], [406.0, -221.5]],
      [1, 14, [406.0, -220.0], [406.0, -221.5]],
      [2, 14, [406.0, -220.0], [406.0, -221.5]],
      [3, 14, [406.0, -220.0], [406.0, -221.5]],
      [4, 14, [406.0, -220.0], [406.0, -221.5]],
      [5, 14, [406.0, -220.0], [406.0, -221.5]],
      [6, 14, [406.0, -220.0], [406.0, -221.5]],
      [10, 14, [406.0, -220.0], [406.0, -221.5]],
      [11, 14, [406.0, -220.0], [406.0, -221.5]],
      [12, 14, [406.0, -220.0], [406.0, -221.5]],
      [13, 14, [406.0, -220.0], [406.0, -221.5]],
      [14, 10, [406.0, -220.0], [411.0, -248.5]]],
 15: [[0, 15, [462.0, -293.0], [462.0, -294.5]],
      [1, 15, [462.0, -293.0], [462.0, -294.5]],
      [2, 15, [462.0, -293.0], [462.0, -294.5]],
      [3, 15, [462.0, -293.0], [462.0, -294.5]],
      [4, 15, [462.0, -293.0], [462.0, -294.5]],
      [5, 15, [462.0, -293.0], [462.0, -294.5]],
      [6, 15, [462.0, -293.0], [462.0, -294.5]],
      [10, 15, [462.0, -293.0], [462.0, -294.5]],
      [11, 15, [462.0, -293.0], [462.0, -294.5]],
      [12, 15, [462.0, -293.0], [462.0, -294.5]],
      [13, 15, [462.0, -293.0], [462.0, -294.5]],
      [14, 15, [462.0, -293.0], [462.0, -294.5]]],
 16: [[0, 16, [472.0, -401.0], [472.0, -402.5]],
      [1, 16, [472.0, -401.0], [472.0, -402.5]],
      [2, 16, [472.0, -401.0], [472.0, -402.5]],
      [3, 16, [472.0, -401.0], [472.0, -402.5]],
      [4, 16, [472.0, -401.0], [472.0, -402.5]]],
 17: [[0, 16, [472.0, -479.0], [472.0, -402.5]],
      [1, 16, [472.0, -479.0], [472.0, -402.5]],
      [2, 16, [472.0, -479.0], [472.0, -402.5]],
      [3, 16, [472.0, -479.0], [472.0, -402.5]],
      [4, 16, [472.0, -479.0], [472.0, -402.5]],
      [5, 16, [472.0, -479.0], [472.0, -402.5]],
      [6, 16, [472.0, -479.0], [472.0, -402.5]]],
 18: [[0, 17, [472.0, -573.0], [472.0, -608.5]],
      [1, 17, [472.0, -573.0], [472.0, -608.5]],
      [2, 17, [472.0, -573.0], [472.0, -608.5]],
      [3, 17, [472.0, -573.0], [472.0, -608.5]],
      [4, 17, [472.0, -573.0], [472.0, -608.5]],
      [5, 17, [472.0, -573.0], [472.0, -608.5]],
      [6, 17, [472.0, -573.0], [472.0, -608.5]],
      [10, 17, [472.0, -573.0], [472.0, -608.5]],
      [11, 17, [472.0, -573.0], [472.0, -608.5]],
      [12, 17, [472.0, -573.0], [472.0, -608.5]],
      [13, 17, [472.0, -573.0], [472.0, -608.5]],
      [14, 17, [472.0, -573.0], [472.0, -608.5]]]}

)
		#
		# iterate point by point and count occurences for each sgrad
		#
		mo_a = []
		mo_b = []
		#
		for k,v in s_grad_br.items():
			#
			mst_occ = sample.most_occuring(v)
			#
			# 
			if len(mst_occ) > 0:
					
				for x in mst_occ:
					#
					count = x[1] - ((len(mst_occ[1:])) + 1) #devaluate diluted matches
					#
					x[1] = count
				#

			#
			t_m_o = [mst_occ[0]]
			#
			for x in t_m_o:
				#
				x.append("ba")
				#
			#
			mo_a.append([k,t_m_o])
			#
		#
		#pprint.pprint(mo_a)
		#
		for k,v in s_grad_rb.items():
			#
			mst_occ = sample.most_occuring(v)
			#
			# 
			if len(mst_occ) > 0:
					
				for x in mst_occ:
					#
					count = x[1] - ((len(mst_occ[1:])) + 1) #devaluate diluted matches
					#
					x[1] = count
				#

			#
			t_m_o = [mst_occ[0]]
			#
			for x in t_m_o:
				#
				x.append("ab")
				#
			#
			mo_b.append([k,t_m_o])
			#
		#
		# for k,v in s_grad_rb.items():
		# 	#
		# 	t_m_o = [sample.most_occuring(v)[0]]
		# 	# 
		# 	#
		# 	for x in t_m_o:
		# 		#
		# 		x.append("ab")
		# 		#
		# 	#
		# 	mo_b.append([k,t_m_o])
		# 	#
		# #
		print("A")
		pprint.pprint(mo_a)
		print("B")
		pprint.pprint(mo_b)
		#
		'''
		A
		[[1, [[1, 12, 'ba']]],
		 [2, [[2, 12, 'ba']]],
		 [3, [[4, 12, 'ba']]],
		 [4, [[5, 12, 'ba']]],
		 [5, [[6, 7, 'ba']]],
		 [6, [[7, 8, 'ba']]],
		 [7, [[8, 12, 'ba']]],
		 [8, [[9, 8, 'ba']]],
		 [9, [[10, 6, 'ba']]],
		 [10, [[11, 8, 'ba']]],
		 [11, [[12, 7, 'ba']]],
		 [12, [[13, 12, 'ba']]]]
		B
		[[1, [[1, 12, 'ab']]],
		 [2, [[2, 12, 'ab']]],
		 [3, [[3, 7, 'ab']]],
		 [4, [[3, 5, 'ab']]],
		 [5, [[4, 12, 'ab']]],
		 [6, [[5, 7, 'ab']]],
		 [7, [[6, 8, 'ab']]],
		 [8, [[7, 12, 'ab']]],
		 [9, [[8, 8, 'ab']]],
		 [10, [[9, 6, 'ab']]],
		 [11, [[10, 8, 'ab']]],
		 [12, [[11, 7, 'ab']]],
		 [13, [[12, 10, 'ab']]]]

		'''

		# compare most occuring
		#
		#
		m_lon = max([mo_a,mo_b], key=len)
		m_sho = min([mo_a,mo_b], key=len)
		#
		print("longest list")
		pprint.pprint(m_lon)
		#
		inxs_lon = [c[0] for c in m_lon]
		inxs_sho = [c[0] for c in m_sho]
		#
		missing_inx = []
		#
		all_mo = []
		#
		for x in range(len(m_lon)):
			#
			if x+1 in inxs_sho:
				#
				combined = m_lon[x][1] + m_sho[x][1]
				#
				dedupe_combined = []
				#
				# for match in combined:
				# 	#
				# 	#
				# 	if match not in dedupe_combined:
				# 		#
				# 		dedupe_combined.append(match)
				# 		#
				# 	#
				# #
				dedup_combined_sorted_count = sorted(combined,key = lambda x: x[1], reverse=True) 
				#
				all_mo.append([x+1,dedup_combined_sorted_count])
				#
			else:
				#
				missing_inx.append(x+1)
				#

		#
		pprint.pprint(all_mo)
		#
		'''
		[1, [[1, 12, 'ab'], [1, 12, 'ba']]]
		[2, [[2, 12, 'ab'], [2, 12, 'ba']]]
		[3, [[4, 12, 'ba'], [3, 7, 'ab']]]
		[4, [[5, 12, 'ba'], [3, 5, 'ab']]]
		[5, [[4, 12, 'ab'], [6, 7, 'ba']]]
		[6, [[7, 8, 'ba'], [5, 7, 'ab']]]
		[7, [[8, 12, 'ba'], [6, 8, 'ab']]]
		[8, [[7, 12, 'ab'], [9, 8, 'ba']]]
		[9, [[8, 8, 'ab'], [10, 6, 'ba']]]
		[10, [[11, 8, 'ba'], [9, 6, 'ab']]]
		[11, [[10, 8, 'ab'], [12, 7, 'ba']]]
		[12, [[13, 12, 'ba'], [11, 7, 'ab']]]


		'''
		#
		prop_match = []
		#
		for x in all_mo:
			#
			print(x)
			#
			dir_matches = x[1]
			#
			for z in dir_matches:
				#
				#
				#
				_dir = z[2]
				_len = z[1]
				_pnt = z[0]
				#
				if _dir == "ab":
					#
					to_app = [x[0],_pnt, _len]
					#
				else:
					#
					to_app = [_pnt, x[0], _len]
					#
				#
				if to_app not in prop_match:
					#
					prop_match.append(to_app)
					#
				#
		#
		print("redirected match")
		#
		pprint.pprint(prop_match)
		#
		'''
		[[1, 1, 12],
		 [2, 2, 12],
		 [4, 3, 12], // here we see 3 being a match of 4 with certainty 12, and of 3 with certainty 7
		 [3, 3, 7],
		 [5, 4, 12],
		 [4, 3, 5],
		 [6, 5, 7],
		 [7, 6, 8],
		 [8, 7, 12],
		 [9, 8, 8],
		 [10, 9, 6],
		 [11, 10, 8],
		 [12, 11, 7],
		 [13, 12, 12]]

		'''
		#
		# remove same match less certain
		#
		
		#
		print("missing")
		pprint.pprint(missing_inx)
		#
	def test_inxline(self):
		#
		#
		print ('\n'+tcolor.WARNING + "TESTING: test_inxline" + tcolor.ENDC)
		#	
		point_length = 6
		#
		points = [
			sample.get_point_inx_line(point_length,0,"p"),
			sample.get_point_inx_line(point_length,1,"p"),
			sample.get_point_inx_line(point_length,2,"p"),
			sample.get_point_inx_line(point_length,3,"p"),
			sample.get_point_inx_line(point_length,4,"p"),
			sample.get_point_inx_line(point_length,5,"p"),
			sample.get_point_inx_line(point_length,6,"p"),
			sample.get_point_inx_line(point_length,6,"a"),
			sample.get_point_inx_line(point_length,5,"a"),
			sample.get_point_inx_line(point_length,4,"a"),
			sample.get_point_inx_line(point_length,3,"a"),
			sample.get_point_inx_line(point_length,2,"a"),
			sample.get_point_inx_line(point_length,1,"a"),
			sample.get_point_inx_line(point_length,0,"a")
		]
		#
		points_b = [
			sample.get_point_inx_line_b(point_length,0,"p"),
			sample.get_point_inx_line_b(point_length,1,"p"),
			sample.get_point_inx_line_b(point_length,2,"p"),
			sample.get_point_inx_line_b(point_length,3,"p"),
			sample.get_point_inx_line_b(point_length,4,"p"),
			sample.get_point_inx_line_b(point_length,5,"p"),
			sample.get_point_inx_line_b(point_length,6,"p"),
			sample.get_point_inx_line_b(point_length,6,"a"),
			sample.get_point_inx_line_b(point_length,5,"a"),
			sample.get_point_inx_line_b(point_length,4,"a"),
			sample.get_point_inx_line_b(point_length,3,"a"),
			sample.get_point_inx_line_b(point_length,2,"a"),
			sample.get_point_inx_line_b(point_length,1,"a"),
			sample.get_point_inx_line_b(point_length,0,"a")
		]
		points_c = [
			sample.get_point_inx(point_length,0,"p"),
			sample.get_point_inx(point_length,1,"p"),
			sample.get_point_inx(point_length,2,"p"),
			sample.get_point_inx(point_length,3,"p"),
			sample.get_point_inx(point_length,4,"p"),
			sample.get_point_inx(point_length,5,"p"),
			sample.get_point_inx(point_length,6,"p"),
			sample.get_point_inx(point_length,6,"a"),
			sample.get_point_inx(point_length,5,"a"),
			sample.get_point_inx(point_length,4,"a"),
			sample.get_point_inx(point_length,3,"a"),
			sample.get_point_inx(point_length,2,"a"),
			sample.get_point_inx(point_length,1,"a"),
			sample.get_point_inx(point_length,0,"a")
		]
		#
		#
		print(points)
		print(points_b)
		print(points_c)
		#self.assertEqual(rotated_points, rotate_after)
		#

if __name__ == '__main__':
	unittest.main()
