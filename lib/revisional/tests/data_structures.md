```
A = [([x, y], i, ...)...]
# A = [([x, y], 0, ...),([x, y], 1, ...)]
H = (V(A),E(A),B(A))

# Vertices of instace A
# V(A)
# Edges of instace A
# E(A)
# Barycentric Edges of instace A
# B(A)

```

---

### Parts

#### V(Instance)

Vertices of instace A

#### E(Instance)

Edges of instace A

#### B(Instance)

Barycentric Edges of instace A, Function B needs the rest of the instances for δ. Starts count from zero as Barycentric point.

---

### Mechanisms

#### Center Transfer Tree (κ, kappa):

Works only for **B** Barycentric Edges, ```κB(Vertice Index, Other Instance)```. Returns Center Transfer Tree of the provided instance against the other instance.

#### Tree (δ, delta):

On the Current Vertice (cV), we get the Barycentric Vertice it corresponds, we create a perpendicular infinite line (PIL) on that B. Then in the other instances we look for Vertices that are close to that line and create further perpendicular lines extending from those points to meet the PIL. 

The intersection point from the other Instances Vertice (oV) to the Current Vertice PIL is called P. The cV, P and oV create a triangle ```Δ = (cV,P,oV)``` and an area of the triangle ```A = (Δ)```, we store this for each point for each instance as AreaTriangle (ΔA) that includes ```ΔA = [ΔA, A(Δ)]```. **The ΔA best match is one from ΔA with the smallest Area**.

```δB(Vertice Index, Other Instance) = sort([ΔA(v23)[A],ΔA(v24)[A],ΔA(v25)[A]]```

---

### Complete Logic

```
i1 = ([x,y], ...)

Instances = (i1, i2, i3)

i1 = (V(i1), E(i1), B(i1, Instances))

for instance i1

	V(i1) = {v1, v2, ..., vn }
	E(i1) = {e1, e2, ..., en }
	B(i1, Instances) = {b0, b1, ..., bn}

provided B(i1) and V(i1) of instance.

	b0 = barycentric of Instance only no kappa.
	b1 = { κB(v1,i2), κB(v1,i3) }
	κB(v1,i2) = { δB(v1,i2),δB(v2,i2) }

```

---

### Preparatory Functions

These functions are used to create the numbers we need to run further comparison logic. We create the graphs and Center Transfer Trees for each Instance.

Prep Functions:

* make_graphs
	* make_v
	* make_e
	* make_b
* make_ctt
	* make_delta

---

#### Function make_graphs(Instances)

Creates Instance Graphs ```V,E,B(without κB)``` for provided Instances.

#### Permute CTT make_ctt(Instances)

Populates ```B``` in each Instance with ```κB``` against other Instances, by building ```δB``` for each Instance Vertice leveraging Barycentric Edges.
