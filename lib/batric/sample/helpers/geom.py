import math

def area(corners):
	#
	n = len(corners) # of corners
	area = 0.0
	for i in range(n):
		j = (i + 1) % n
		area += corners[i][0] * corners[j][1]
		area -= corners[j][0] * corners[i][1]
	area = abs(area) / 2.0
	#
	return area
	#
#
def circle_point_distance( point1, point2):
	return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

#
def in_circle( point, circle):
	origin, radius = circle
	return radius >= circle_point_distance(point, origin)
#
def rotate_tri_match(x,y,xo,yo,degs): #rotate x,y around xo,yo by theta (rad)

	#
	x1 = x
	x2 = xo
	y1 = y
	y2 = yo
	#
	angle = math.atan2(y1 - y2, x1 - x2)
	#
	angle_ = angle * (180 / math.pi) % 360
	#
	theta = math.radians(degs)
	#
	if angle_ > 180:
		#
		theta = math.radians(-degs)
		#
	#
	xr=math.cos(theta)*(x-xo)-math.sin(theta)*(y-yo) + xo
	yr=math.sin(theta)*(x-xo)+math.cos(theta)*(y-yo) + yo
	return [xr,yr]
#
def getPerpCoord(aX, aY, bX, bY, length):
	vX = bX-aX
	vY = bY-aY
	#print(str(vX)+" "+str(vY))
	if(vX == 0 or vY == 0):
		return 0, 0, 0, 0
	mag = math.sqrt(vX*vX + vY*vY)
	vX = vX / mag
	vY = vY / mag
	temp = vX
	vX = 0-vY
	vY = temp
	cX = bX + vX * length
	cY = bY + vY * length
	dX = bX - vX * length
	dY = bY - vY * length
	return int(cX), int(cY), int(dX), int(dY)

def barycentric(tri):
	#
	centerX = (tri[0][0] + tri[1][0] + tri[2][0]) / 3;
	centerY = (tri[0][1] + tri[1][1] + tri[2][1]) / 3;
	#
	return [centerX,centerY]
	#
#

def value_mid(inputlist, pos):

	_mx = max([sublist[pos] for sublist in inputlist])
	_mn = min([sublist[pos] for sublist in inputlist])
	#
	mid = (_mx + _mn) / 2
	#
	return mid
#

# center of bounding box
def cntr(x1, y1, x2, y2):
	return x1+(x2-x1)/2, y1+(y2-y1)/2
#

def flipCoordPath(p, horizontal, vertical):
	#
	res = []
	#
	for x,y in p:
		#
		if horizontal:
			#
			pass
			#
		else:
			#
			if y < 0:
				#
				y = abs(y)
				#
			else:
				#
				if y == 0:
					y = y
				else:
					y = -abs(y)
				#
			#
		if vertical:
			#
			pass
			#
		else:
			#
			if x < 0:
				#
				x = abs(x)
				#
			else:
				#
				if x == 0:
					x = x
				else:
					x = -abs(x)
				#
			#
		#
		res.append([round(x,1),round(y,1)])
		#
	#
	return res
#
def midpoint(p1, p2):
	return [(p1[0]+p2[0])/2, (p1[1]+p2[1])/2]
#
def get_angle(p1, p2, rads=False):
	
	_rads = math.atan2(p1[1]-p2[1], p1[0]-p2[0])

	if rads == True:
		#
		_res = _rads
		#
	else:
		#
		_res = int(math.degrees(_rads))
		#
	return _res

def get_angle_b (p1,p2):
	#
	x1 = p1[0]
	x2 = p2[0]
	y1 = p1[1]
	y2 = p2[1]
	#
	angle = math.atan2(y1 - y2, x1 - x2)
	#
	angle_ = angle * (180 / math.pi) % 360
	#
	if angle_ > 180:
		#
		angle_ = angle_ - 360
		#
	#
	return angle_
	#

def get_angle_c (unit1, unit2):

	return unit1-unit2 % 360

	# phi = abs(unit2-unit1) % 360
	# sign = 1
	# # used to calculate sign
	# if not ((unit1-unit2 >= 0 and unit1-unit2 <= 180) or (
	# 		unit1-unit2 <= -180 and unit1-unit2 >= -360)):
	# 	sign = -1
	# if phi > 180:
	# 	result = 360-phi
	# else:
	# 	result = phi

	# return int(result*sign)
	
def drawLine2P(x,y,xlims,ax):
	_xrange = np.arange(xlims[0],xlims[1],0.1)
	A = np.vstack([x, np.ones(len(x))]).T
	k, b = np.linalg.lstsq(A, y)[0]
	ax.plot(_xrange, k*_xrange + b, 'k')


def angle_diff(a,b):
	#
	return (a-b) % 360
	#

def move_coord_by(coord, move_by):
	#
	c_x = coord[0] 
	c_y = coord[1]
	#
	moved = [c_x + move_by, c_y + move_by]
	#
	return moved
	#