def test_get_certain_lines(self):
	#
	print ('\n'+tcolor.WARNING + "TESTING: test_get_certain_lines" + tcolor.ENDC)
	#
	certain_before = [
		([132.0, -405.0], 2, 5.0),
		([72.0, -331.0], 3, 5.5),
		([52.0, -328.0], 4, 6.0),
		([55.0, -303.0], 5, 6.0),
		([149.0, -306.0], 6, 2.0),
		([230.0, -303.0], 7, 11.0),
		([231.0, -328.0], 8, 6.0),
		([219.0, -330.0], 9, 0.5),
		([364.0, -408.0], 14, 5.0),
		([382.0, -346.0], 15, 10.5),
		([364.0, -331.0], 16, 1.0),
		([341.0, -328.0], 17, 6.5),
		([343.0, -303.0], 18, 11.0),
		([418.0, -306.0], 19, 2.0),
		([488.0, -303.0], 20, 9.0),
		([490.0, -328.0], 21, 6.0),
		([475.0, -330.0], 22, 5.0),
		([402.0, -417.0], 23, 10.0),
		([277.0, -712.0], 25, 6.0),
		([267.0, -716.0], 26, 1.0)
	]
	'''
	1                            |                        -
	([132.0, -405.0], 2, 5.0),   | -----                  -
	([72.0, -331.0], 3, 5.5),    | -----.                 +  3
	([52.0, -328.0], 4, 6.0),    | ------                 +  4
	([55.0, -303.0], 5, 6.0),    | ------                 +  5
	([149.0, -306.0], 6, 2.0),   | --                     +  6
	([230.0, -303.0], 7, 11.0),  | -----------            +  7
	([231.0, -328.0], 8, 6.0),   | ------                 -
	([219.0, -330.0], 9, 0.5),   | .                      -
	10                           |                        - 
	11                           |                        -
	12                           |                        -
	13                           |                        -
	([364.0, -408.0], 14, 5.0),  | -----                  -
	([382.0, -346.0], 15, 10.5), | ----------.            +  15
	([364.0, -331.0], 16, 1.0),  | -                      +  16
	([341.0, -328.0], 17, 6.5),  | -----.                 +  17
	([343.0, -303.0], 18, 11.0), | -----------            +  18
	([418.0, -306.0], 19, 2.0),  | --                     +  19
	([488.0, -303.0], 20, 9.0),  | ---------              +  20
	([490.0, -328.0], 21, 6.0),  | ------                 +  21
	([475.0, -330.0], 22, 5.0),  | -----                  +  22
	([402.0, -417.0], 23, 10.0), | ----------             -
	24                           |                        -
	([277.0, -712.0], 25, 6.0),  | ------                 -
	([267.0, -716.0], 26, 1.0)   | -                      -
	27                           |                        -

	get the highest
	travel towards each side, cw and ccw
	add to list if not low threshhold
	clip by one from each side

	'''
	#
	
	i = 0
	len_points = 26
	#
	crd_s = [item[0] for item in certain_before]
	inx_s = [item[1] for item in certain_before]
	crt_s = [item[2] for item in certain_before]
	#
	l = 5
	r = 15 
	#
	l_inxcrt = list(zip(inx_s,crt_s))
	#
	l_inxcrt_m = sample.add_missing(len_points, inx_s,crt_s)
	#
	l_inxcrt_lm = sample.certainty_limit(l_inxcrt_m, len_points)
	#
	seq_points = []
	#
	#
	for x in l_inxcrt_lm:
		#
		point_num = x[0]
		#
		seq_points.append(point_num)
		#
	#
	seq_lists = sample.get_seq(seq_points)
	#
	#
	print("ADD")
	pprint.pprint (l_inxcrt_m)
	#
	print("LIMIT")
	pprint.pprint (l_inxcrt_lm)
	#
	print("SEQ")
	pprint.pprint (seq_lists)
	#
	crt_s_lm = [item[0] for item in l_inxcrt_lm]
	l_inxcrt_lm_seq = []
	#
	for x in seq_lists:
		#
		lm_seq = []
		#
		for y in x:
			#
			if y in crt_s_lm:
				#
				for z in certain_before:
					#
					if z[1] == y:
						#
						lm_seq.append(z)
						#
					#
				#
			#
		#
		l_inxcrt_lm_seq.append(lm_seq)
		#
	#
	print("SEQ LM")
	pprint.pprint (l_inxcrt_lm_seq)
	#
	#
	#self.assertEqual(rotated_points, rotate_after)
		#