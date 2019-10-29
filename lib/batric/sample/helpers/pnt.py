import math

def dot(v,w):
	x,y = v
	X,Y = w
	return x*X + y*Y# + z*Z

def length(v):
	x,y = v
	return math.sqrt(x*x + y*y)

def vector(b,e):
	x,y = b
	X,Y = e
	return (X-x, Y-y)

def unit(v):
	x,y = v
	mag = length(v)

	if mag != 0:
		dev = (x/mag, y/mag)
	else:
		dev = (0,0)

	return dev

def distance(p0,p1):
	return length(vector(p0,p1))

def scale(v,sc):
	x,y = v
	return (x * sc, y * sc)

def add(v,w):
	x,y = v
	X,Y = w
	return (x+X, y+Y)

# Malcolm Kesson 16 Dec 2012

def pnt2line(pnt, start, end):
	line_vec = vector(start, end)
	pnt_vec = vector(start, pnt)
	line_len = length(line_vec)
	line_unitvec = unit(line_vec)

	if line_len != 0:
		#
		pnt_vec_scaled = scale(pnt_vec, 1.0/line_len)
		t = dot(line_unitvec, pnt_vec_scaled)    
		if t < 0.0:
			t = 0.0
		elif t > 1.0:
			t = 1.0
		nearest = scale(line_vec, t)
		dist = distance(nearest, pnt_vec)
		nearest = add(nearest, start)
		#
		return (dist, nearest)

	else:

		return (0, (0, 0))
