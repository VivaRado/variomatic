from shapely.geometry import LineString

def simplif(points, simp_level):
    #
    line = LineString(points)
    #
    try:
        #
        linestring = line.simplify(simp_level, preserve_topology=True)
        #
        #
    except Exception as e:
        #
        fin_line = line
        #
    #
    fin_line = list(linestring.coords)
    #
    return fin_line
    #