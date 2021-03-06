```{include=partials/introduction/profile_project.md,L1}```

---

```{include=partials/introduction/phase_introduction/phase_introduction.md}```


### **Introduction / Phase Introduction / Phase Levels**

```{include=partials/introduction/phase_introduction/phase_levels__level1.md}```

---

### **Introduction / Phase Introduction / Initiation Phase**

The important elements of the Intiation Phase for Level 1 is the **Business Case**, followed by a **Project Charter**.

**Business Case**:

What are the benefits we are trying to get from the project and justification of the decision. It encapsulates the research done to see if the project is worth doing.

---

**Project Charter**:

What are the deliverables and the authorisation to do the project. It encapsulates the announcement to do the project.

---


*  **Initiation Phase** Components ∞0.001:
	
	1.  **Business Case**:
		*  Strategic case
		*  Commercial case
		*  Management case

	1.  **Project Charter**:
		*  Project Introduction
		*  Project Goal(s)
		*  Project Structure
		*  Deliverables
		*  Duration


---

### **Introduction / Phase Introduction / Initiation Phase / Business Case**

```{include=partials/introduction/phase_introduction/initiation_phase/business_case.md}```

---

### **Introduction / Phase Introduction / Initiation Phase / Business Case / Solution Options**

```{include=partials/introduction/phase_introduction/initiation_phase/business_case/solution_options.md}```

---

### **Introduction / Phase Introduction / Initiation Phase / Business Case / Strategic case**

```{include=partials/introduction/phase_introduction/initiation_phase/business_case/strategic_case/strategic_case.md}```

---

### **Introduction / Phase Introduction / Initiation Phase / Business Case / Strategic case / Contributions**

```{include=partials/introduction/phase_introduction/initiation_phase/business_case/strategic_case/contributions.md}```


---

### **Introduction / Phase Introduction / Initiation Phase / Business Case / Management case**

```{include=partials/introduction/phase_introduction/initiation_phase/business_case/management_case/management_case.md}```

---

### **Introduction / Phase Introduction / Initiation Phase / Business Case / Management case / Achievements Plan**

```{include=partials/introduction/phase_introduction/initiation_phase/business_case/management_case/achievements_plan.md}```

---

### **Introduction / Phase Introduction / Initiation Phase / Business Case / Management case / Timescales**

```{include=partials/introduction/phase_introduction/initiation_phase/business_case/management_case/timescales.md}```

---


### **Introduction / Phase Introduction / Initiation Phase / Project Charter**


*  **Project Charter** Components ∞0.002:
	*  Project Introduction
	*  Project Goals
	*  Project Structure
	*  Business Solution
	*  Deliverables
	*  Duration
	*  Benefits and Limitations

---

### **Introduction / Phase Introduction / Initiation Phase / Project Charter / Project Introduction**

*  **Project Introduction** Components ∞0.002:

	*  Project Name
	*  Project Statements
		*  Vision Statement
		*  Mission Statement
	*  Project Definition
		*  Problem 
		*  Opportunity

---

### **Introduction / Phase Introduction / Initiation Phase / Project Charter / Project Introduction / Project Name**

*  Suggested Names:
	*  Variomatic or Vmatic


---

### **Introduction / Phase Introduction / Initiation Phase / Project Charter / Project Introduction / Project Statements**

```{include=partials/introduction/phase_introduction/initiation_phase/project_charter/project_statements.md}```


---

### **Introduction / Phase Introduction / Initiation Phase / Project Charter / Project Introduction / Project Definition**

*  **Problem** Components ∞0.001:
	*  Making compatible variation instances requires tedious manual work.

*  **Opportunity** Components ∞0.001:
	*  Automatically Create compatible variation instances.
	*  Review incompatibilities.

---

### **Introduction / Phase Introduction / Initiation Phase / Project Charter / Project Goals**

Identified Goals:

*  Working on software to automatically take in a font family with a set of weights and put out a variable font with a weight axis. 
*  That software can depend on GlyphsApp or FontLab6 or RoboFont, although if it works only with fontTools that would be better, but increases the risk.
*  Create a interpolation layer that only cares about point numbers and contour direction.
*  Create a Plane that understands contour point warp or movement.
*  Recreate the contours according to the create layer.

---

### **Introduction / Phase Introduction / Initiation Phase / Project Charter / Project Structure**

*  **Project Structure** Components ∞0.001:
	*  Project Scope
	*  Project Team

---

#### Project Scope:

We have divided the project into the **Product Main** that is the **Variomatic**, and **Product Modules**. Each of those parts has its own set of development and design requirements. The project scope will be further updated during the LayerB.


#### Project Team:

The initial team that will provide the deliverables:

*  Andreas Kalpakidis
*  Madina Akhmatova

---

### **Introduction / Phase Introduction / Initiation Phase / Project Charter / Business Solution**


*  **Business Solution** Components ∞0.001:
	*  Approach Options
	*  Possible Technical Solutions

---

### **Introduction / Phase Introduction / Initiation Phase / Project Charter / Deliverables**

This in overview of the deliverables that comprise the proposed solution to the problem of automatically interpolating contours and creating variation capable font instances.

#### Deliverable Overview:

We want to create initially a command line tool that will be able to get a set of fonts, may that be UFOs, create a compound path similarity index by gradually simplifying the contour, then use this Similarity Gradient or SGrad and update, remove, cleanup the original compound contour according to the most needed points identified, without losing curve precision.

We can start by providing .GLIF files directly to the SGRAD script and build the necessary component alphas, then proceed to integrating it to a library, and maybe move in accordance to the structure of VarLib so integration to it could be easier.

This will then allow us to successfully run the fontmake commands and receive the final interpolated variable font.

We want to create an interface, natively in the browser that will allow the user to review the script findings and accept alterations.

#### Deliverable Specification:

Further discussion and updates will be added to this section, that are related to the specifics of functions and features of the deliverables.

---

### **Introduction / Phase Introduction / Initiation Phase / Project Charter / Duration**

*  **Duration** Components ∞0.001:
	*  Timeframe
	*  Milestones

The Timeframe of this project has been set and the Milestones, will be elaborated on in further detail, they are a subject of constant update and will change before we progress further into the Planning Phase.

#### Timeframe:

This project will take place between **April 1st 2019** and until the end of **December 20th 2019**.
The duration is ≃10 months. There is a possibility not to be excluded that a further time frame will be required for a possible implementation of the program to the Google Fonts portfolio, or in case of possible unforeseen risks.

#### Milestones:

**Currently Identified Milestones** Components ∞0.001:

*  Create initial demos and tests for the solution of the given problem of automatic interpolation.
*  Functionality that understands the important contour points and maintains them while removing the excess ones.
*  Links the points that are related across instances
*  Use the similarity gradient points as a guide for original point cleanup.
*  Optimize the font compatible spline system equally across the instances.

---

### **Introduction / Phase Introduction / Initiation Phase / Project Charter / Benefits and Limitations**

Benefits:

*  SGRAD Straight contour matching allows for a relatively good match solving multiple stray points.
*  Reviewing the output SVGs allows for better understanding of what areas of a contour are problematic

Limitations:

*  SGRAD cannot always provide 100% results when the contours have major issues.

* the contour sorting fails for non line travel distance sortable, as it tries to calculate the travel distance, of each contour and sort. 	For example the inner part of the letter "O" from the outer, is a smaller travel distance in both instances. Where this is not true for glyphs like "=". A approximate position or centroid or barycentric of the contour points, in the glyphs will probably have to be taken into account.

* If end start is in the uncertain lines, final green matching line doesn't visually close.

* If triangle matching and inline check fails for uncertain lines... well there is no matching.
	
* At the moment there is no final line in a usable list, it is though plotted as green for certain and lime for uncertain basic_cleanup and match_uncertain_tris.
	
* This script doesn't do curved bezier contour analysis, it does straight point position comparison across simplification levels. In further iterations we will improve to do bezier contour comparison.

* As it doesn't do curved bezier contour analysis, there is a very small chance the certainty matching gives incorrect matching. But if this happens, there is a chance there are move issues than just that and those issues will be directly visible.

* Adding curved bezier contour analysis will result in 100% matching and cleanup. In respectfully similar contours. Do not expect this to work with two random letters, there is no morphing.

* The script solves only two instances against each other, there is no multiple instance support at this moment.

* The code needs a strong cleanup.

* Networkx should be removed.

---


### **Introduction / Phase Introduction / Planning Phase**

The Planning Phase, is where the project solution is further developed in as much detail as possible and the steps necessary to meet the project’s objectives.

The Planning Phase consists of:

1.  **Safe Planning**
1.  **Stakeholders**
1.  **Quality Plan (PQP)**


At this point, the project would have been planned in detail and is ready to be executed.

---

### **Introduction / Phase Introduction / Planning Phase / Safe Planning**

The project's **Project Plan** is created outlining the activities, tasks, dependencies, and timeframes. 


*  **Safe Planning** Components (Scope Management): 

	*  Project Plan:
		*  Activities
		*  Tasks
		*  Timeframes
	*  Work Planning:
		*  Dependencies
	*  Schedule Planning.

---

### **Introduction / Phase Introduction / Planning Phase / Safe Planning / Project Plan**


During our initial research we have identified one possible solution that if implemented will successfully produce the required interpolation capable contours. More solutions would be researched.

*  Current Plans in Development:

	*  Simplification Gradient (SGRAD)

*  Future Plans:

	*  Bezier Curve Analysis
	*  Dynamic Point Repositioning

---

### **Introduction / Phase Introduction / Planning Phase / Safe Planning / Project Plan / Simplification Gradient / Excessive Points Problem**

#### Provided Instances

We are given two instances, one is a Regular and the other is a Bold.
From those for the sake of this example we use a Compound Section.

![IMG](assets/media/PIP_a_001.svg)

image: #001, 0.001, svg, compound section of "&" for regular and bold instances.

#### Enumerated Matching

Enumeration over the point array fails, as there are excessive points and the matching proceeds inconsistently. This results to a failed match and a failed font variation.

![IMG](assets/media/PIP_a_002.svg)

image: #002, 0.001, svg, enumerated matching between given instance compound sections.

---

### **Introduction / Phase Introduction / Planning Phase / Safe Planning / Project Plan / Simplification Gradient / Method Implementation**

We present an example of implementing the Simplification Gradient (SGRAD) method over a compound section of a complete glyph.

---

### **Introduction / Phase Introduction / Planning Phase / Safe Planning / Project Plan / Simplification Gradient / Method Implementation / Simplification**


#### Simplification Gradient on Instance, value Max Error

We produce a simplification for each compound, iterating the Max Error by 10%.

![IMG](assets/media/PIP_a_003.svg)

image: #003, 0.001, svg, Simplification Gradient - Simplification Gradient.

---

#### Point Importance Index. Survival across simplification gradient

This method due to the results, works on geometric forms, and even then it performs poorly. There is heavy reliance on a simplification algorithm that "prefers" straight lines.
And a possible need of a Curve Fitting algorythm. Tests have been made on rasterizing, then vectorizing and simplifying, a method that might be used to counter very dirty contours that cannot be matched.

Points that we dont need tend to remain longer during simplification. This gives them higher score compared to points that we really need to remain.

<small>
**SCHEDULE:** ```VRM-1001```
</small>

---

#### Product

Here we can see the SGRAD with the evaluated points from the Simplification Gradient, and how they overlay the original provided compound. Allowing points that are at a minimum of 40% threshold, we can see that there is a matching candidate we can use as a guide. The simplification iteration could be even more granular.

![IMG](assets/media/PIP_a_006.svg)

image: #006, 0.001, svg, Simplification Gradient - Evaluated Overlay SGRAD and Original.

---

![IMG](assets/media/PIP_a_007.svg)

image: #007, 0.001, svg, Simplification Gradient - Cross instance SGRAD Matching.

---

### **Introduction / Phase Introduction / Planning Phase / Safe Planning / Project Plan / Simplification Gradient / Method Implementation / Graph Search**

We are creating a positioned graph. Then we can compare the instance graphs since we can create a center node and then see what points are the relatives, judging by the edge and not only by the coordinate similarity. That means that the letters between instance could virtually be located at different coordinates, but still have the same, similar shape, we could still locate them. Since we are evaluating according to graph center.

![IMG](assets/media/PIP_a_010.svg)

image: #010, 0.001, svg, Simplification Gradient - SGrad Graph Comparison.

This logic so far has been proven to work in tests. The logic behind this approach, without the need of SGrad.

**Graph Zoom Search**:

*  Parse points across two GLIF instances.
*  Create a topological graph.
*  Get center of all coordinates for each instance.
*  Align instances based on that center.
*  Create a sorted dictionary with the most distant to the closest, from the center points.
*  Perform Radius Search for each point, to find the closest point that belongs in the opposite instance.

This method works without simplification (^1). Working from the outside towards the inside. We have seen that even complex letters result in a proper match.
This method fails if implemented from the inside towards the outside. So sorting according to most distant to the center is important.
The graph logic so far proves to be appropriate for the solution of the autovariation.

<small>
^1: Although RAVS (rasterize-vectorize-simplify) could work if there would be later on comparison of the RAVS instances with the original ones and evaluation of what points we keep and remove.
</small>

---

#### Finding the Unmatched Points:

In the image #011, we can see in the produced result of Graph Zoom Search, that there are two points that do not correspond to each instance, marked in red. Those points will be dealt with in Naturalization. But let's see how we got this result.

![IMG](assets/media/PIP_a_011.svg)

image: #011, 0.001, svg, Simplification Gradient - Graph Zoom Search - Unmatched Points.

---

#### Radius Match on Graph Zoom Search:

In the image #012, we can see in the Radius Search looking for nearby points from the opposite instance.

![IMG](assets/media/PIP_a_012.svg)

image: #012, 0.001, svg, Simplification Gradient - Radius Match.

---

#### The whole picture:

![IMG](assets/media/PIP_a_013.svg)

image: #013, 0.001, svg, Simplification Gradient - Graph Zoom Search and Radius Match


---

#### Graph Zoom Search:

In the demo function we have maintained the functionality of simplification as it might later on be required. The given method does not require simplification by what we have seen so far. We can see that the nodes have been sorted according to the distance from the center. Now we will move forward to producing the Radius Match functionality.

We identified a labeling bug in image #014. Where the old version was labeling incorectly. We can see that in comparison to image #015 where the labeling is according to length.

---

#### Single Search

Demo Function Here: ```python3 lib/graph_search/demo_graph_search.py```

![IMG](assets/media/PIP_a_014.svg)

image: #014, 0.001, svg, Simplification Gradient - Graph Search actual script product.

Here we can see the Radius Match finding the demo green point, any point above a specific Max Radius is not considered a match.
This will be extended to search points in between instances, by removing matched points from the agreed match array.

![IMG](assets/media/PIP_a_015.svg)

image: #015, 0.001, svg, Simplification Gradient - Graph Search and Radius Match actual script product.

---

#### Multiple Search

Demo Function Here: ```python3 lib/graph_search/demo_graph_search_multi.py```

Here we can see RadiusMatch finding the points that match between instances. It has no memory of best match that is why it might match the same points. If it had memory it would know the best matches for each point have been met, depending on distance, and so there would be no matching errors. Other than that the matching is successful, the next step is to implement memory.

*  Identified Memory Logic Rules:

	*  If a point from instance A has been matched with a point from instance B, which has a match with a closer point of instance A, prefer the closer distance point. 
		*  Avoids points that exist in one but not the other instance.

	*  If a point has been matched but is out of serial order or line (2,6,4), prefer the point that is in serial order or line (2,3,4). 
		*  Avoids points to be matched, that even though are in close proximity are not on the same line.
		*  Avoids points that exist in one but not the other instance.

	*  There are things we could do with simplification aswell but we have not yet identified issues that lead us to use additional matching rules.

![IMG](assets/media/PIP_a_016.svg)

image: #016, 0.001, svg, Simplification Gradient - Graph Search and Radius Match actual script product matching best candidate between regular and light.

[Variomatic TopoGraph RadiusMatch](https://www.youtube.com/watch?v=UWCHRD1Fp2k&feature=youtu.be)

video: #001, 0.001, youtube, Simplification Gradient - Graph Search and Radius Match - screencap.

---

#### Ignore Better Matched

Demo Function Here: ```python3 lib/graph_search/demo_graph_search_multi.py```

Here we can see Radius match with one rule added. The rule iterates each instance to instance agreed list, see if match exists in the other instances agreed list and compares the distance, if the distance in the other instances agreed is smaller, it adds that point to ignore. That makes the search leave the smallest distance, and ignore remove the other. We can also see that the points that do not exist in the other instance have no match. Making them removal candidates. Since the removal candidates are now defined and found, we can proceed with the removal and heal of the curves. We noticed that the circles created during the search, where centered on the found node whereas they should be on the node that initiates the search, like a cartoon sonar... During the integration we found that there was a problem with simplification not being drawn, that is now fixed.

![IMG](assets/media/PIP_a_017.svg)

image: #017, 0.001, svg, Simplification Gradient - Graph Search and Radius Match actual script product matching best candidate between regular and light, and ignoring points that do not exist.

[Variomatic TopoGraph RadiusMatch with Ignore Rule](https://youtu.be/L_xM--f-Lj0)

video: #002, 0.001, youtube, Simplification Gradient - Graph Search and Radius Match - Point Ignore Rule - screencap.

<small>
**SCHEDULE:** ```VRM-1003, VRM-1004```
</small>

---

### **Introduction / Phase Introduction / Planning Phase / Safe Planning / Project Plan / Simplification Gradient / Method Implementation / Graph Matching**

#### Tests and emerging requirements

During testing we identified a set of additional requirements:

*  The more similarly positioned the instances compared, by applying scale or move, the better the matching.
*  Simplification and the SGrad will probably be used, as selection of the wrong - easily disgarded paths, by simplification - leads to eroneus matching.
*  Matching should probably begin at a high simplification level, and gradually add detail, by reducing simplification, while evaluating path matching according to persistance of paths, in addition to cross instance, better-closer distance match.
*  There is a concept of segmentation of paths. Then comparison of matches to the position.

#### Example of shape similarity before match

An example of garamond where we can see the matching difference when some transforms are applied to the shapes before matching. The Radius Search being agnostic in terms of graph cluster comparison, results in wrong matching. But the best results come from just centering the differences of the total coordinate extent, the coordinate centers in both axes.

![IMG](assets/media/PIP_a_018.svg)

image: #018, 0.001, svg, Matching Garamond with shape transforms.

#### Cluster Matching

What the Radius Match is good at finding the clusters, or regions. Even if the point by point results sometimes is matching incorectly, there is a visible similarity in the clusters found for each point. There is also a preset function for rule checking and ignoring paths based on some criteria. The criteria we have tested before is distance based, per point.

Now we will need to go deeper than the ```letter / contour```. We will have to do radius matching on ```letter / contour / region```. Let's see then how we can obtain the clusters or regions. Here we have radius match for Blue instance point 0, that returns a cluster for instance Red. Then we can ask for points from Blue that are in the circle of the most distant match. This provides us with the clusters we need to start our comparison.

![IMG](assets/media/PIP_a_019.svg)

image: #019, 0.001, svg, Obtaining the clusters.

---

![IMG](assets/media/PIP_a_020.svg)

image: #020, 0.001, svg, Red and Blue Clusters for point 0.

---

#### Cluster Direction

![IMG](assets/media/PIP_a_021.svg)

image: #021, 0.001, svg, Determine Cluster Direction and Start Point.

---

Here we are running a direction finding function:

A reminder here that the numbers of the nodes are based on the distance from the center.

*  split everything before the search center.
*  split the list where there is a smaller number following a larger one.

```
If we are matching for point 0 and the obtained cluster would be:

[3,0,1,2,5,12,11]

The first split would result to:

[0,1,2,5,12,11]

The second split would result to:

[0,1,2,5,12]

Providing us with a list that every value after each value is larger.

```

---

#### Cluster Matching

After we overlay the coordinates on the search centers, we can run the same functions Radius Match Search (RMS) with Ignore Better Matched Rule(RIBM), and this will provide us with the correct matches. Onward to integrating this.

![IMG](assets/media/PIP_a_022.svg)

image: #022, 0.001, svg, Cluster center to Start Point and Radius Match with Ignore Better Matched.

---

Here we have the lines being drawn, now we will have to match them (probably by edge angle), then overlay them on the same coordinates, and then run radius match.

Demo Function Here: ```python3 lib/graph_search/demo_graph_search_lines.py```

![IMG](assets/media/PIP_a_023.svg)

image: #023, 0.001, svg, Lines created for graph matching.

![IMG](assets/media/PIP_a_024.svg)

image: #024, 0.001, svg, closeup of the lines.

---

Relevant Algorithms:

*  Locality-sensitive hashing
*  Map Matching
*  Fréchet distance
*  Dynamic time warping

<small>
**SCHEDULE:** ```VRM-1005, VRM-1006```
</small>

---

### **Introduction / Phase Introduction / Planning Phase / Safe Planning / Project Plan / Simplification Gradient / Method Implementation / Line Matching**


#### Line Matching Pre and Ante

From the points that create the line, we designate two observers, before and after the Search Center (SC). One point is pre-SC and the other point is ante-SC. When both observers of the Search Center (SC) verify the same point then have a true Match. From the matching scenarios that are incorrect. We have deducted a methond to fix the matching by using the Ante-Pre method.

![IMG](assets/media/PIP_a_025.svg)

image: #025, 0.001, svg, Pre Ante Rule diagram.

Here are some images from the breakdown of the rule on some cases non the less..

![IMG](assets/media/PIP_a_026.svg)

image: #026, 0.001, svg, Pre Ante Rule example case diagram.

---

![IMG](assets/media/PIP_a_027.svg)

image: #027, 0.001, svg, Pre Ante Rule example case diagram.

---

![IMG](assets/media/PIP_a_028.svg)

image: #028, 0.001, svg, Pre Ante Rule example case diagram.

---

#### Line Matching Degree and Distance Based

The point match is the one that is closest and has the less degree diff between the edge to the current search node and itself. This method was not effective.

![IMG](assets/media/PIP_a_029.svg)

image: #029, 0.001, svg, Degree and Distance based matching

---

![IMG](assets/media/PIP_a_030.svg)

image: #030, 0.001, svg, Degree and Distance example case diagram.

---

#### Line Matching Center Transfer Method

After overview of quite a few methods we have finally founda candidate that is in our opinion the most appropriate. Testing the Center Transfer method proves to work over the scenarios that previous methods failed.

Center Transfer Method Logic:

*  Each instance has a center, both of the centers are at the same coordinates.
*  For the point that we are running as Search Center (SC).
	*  For the point that we are running as Search Center (SC). 
		*  Take a line that connects to the center of the instance.
		*  At the point where that line meets the Search Center, create a perpendicular at 90deg to that line (Center Transfer, dashed line)
        *  Locate points from the target instance that are close to the Center Transfer (dashed line) by adding 90deg lines extending to them.
        *  Calculate the distance of those and prefer the smallest distance in terms of drive on the CT line (x axis) and drive on the perpendicular of the CT (y axis) that meets the target point.

---

![IMG](assets/media/PIP_a_031.svg)

image: #031, 0.001, svg, Center Transfer method running for both instances.

---

From the matching results we can see that the previously mismatched points:

*  Red 11 now matches Blue 12
*  Blue 4 now doesn't match any of the red points as Blue 7 and Blue 2 have better matches.

Demo Function Here: ```python3 lib/graph_search/demo_graph_search_center_transfer.py```

---

#### Line Matching Center Transfer Surface Method

We now calculate the surface of the center transfer point and we match all the points successfully BUT 9... Trying to see why that one fails.

![IMG](assets/media/PIP_a_032.svg)

Demo Function Here: ```python3 lib/graph_search/demo_graph_search_center_transfer_surface.py```

<small>
**SCHEDULE:** ```VRM-1007-0001```
</small>

---

#### PSCA (Pre, Search Center, Ante) Brokerage

```
Target PSCA Match Product 

PRE MATCHES:
[[(8, 15),
 [(13, 20),
 [(20, 21)]
]

SC MATCHES:
[[(15, 19),
 [(16, 18),
 [(9, 16)]
]

ANTE MATCHES:
[[(9, 16),
 [(10, 17),
 [(16, 18)]
]

```

We are now tasked with identifying the procedures that will broker the points across the observers (Pre and Ante). One of the methods we will most likely use is to look for series to identify firstly if the source instance Search Center exists at all in the target instance.

If we take a look at the code above we can see lists that refer to the Pre point, that is the point before the given Search Center (the point we are looking to match), and the Ante is the point after the SC. Each match has a tuple with two numbers in it. The first number represents the index based on the distance from the center - graph edge length, and the second number represents the index on the line, of that anchor.

For each of those lists we have 3 matches, this specific piece of matching result is when we are trying to match a point that doesn't exist in the target instance.
By this example we can see that any point in Pre doesn't have a sequence that increments by one point, through the SC until it reaches the Ante, we can see though that Pre(8,15) and Ante(9,16), have an increment of 1, that is proof that the SC doesn't exist at all as a match in the Target Instance.

Expanding on the logic on how to broker those points will provide a solution on matching with precision.

Further on we will use the points in the Match Product to create triangles that we can compare against the Source PSCA triangle and determine what triangle is the best fit for out current SC.

---

#### PSCA Triangle Comparison Barymetric Center Extension Angle


![IMG](assets/media/PIP_a_033.svg)

image: #033, 0.001, svg, Barymetric Center Extension Angle comparisson against triangles


We construct the matching triangles and find the barymetric center, we move the source triangle over the target triangle based on the barymetric centers, then we compare the angles in radians, of the source and target triangle lines, by extending from the barymetric center towards the nodes and comparing SC lines.

We can see that all the points match, and points that don't exist in the target the match returns nothing (red circle).

The more functions we use to compare the triangles the better. In case we see that some results are failing we can devise more triangle comparison functions.


Demo Function Here: ```python3 lib/graph_search/demo_gscts_psca_tcbcea_a.py```

[YouTube Video Here](https://youtu.be/X_bwzci6Ktg)

---

#### SGRAD Travel Distance Comparisson.

There are occasions where we get a line that is not correct, for that we implement travel distance comparisson.

We pass the results of the Center Transfer, that carries matches for each of the PSCA points. Then for every of the three matches contained in those three CT items (P, SC, A), we run a get distance from trace.

For each of those points inside each of PSCA we ger a coordinate range of two steps forward and two steps backward for P and A. And for those points we get the most occuring matches according to SGRAD. Then we trace the travel distance for each of those points (get_coord_range_finder).

We calculate if the point we are traveling is forward in glyph index or backward and assign a penalty if the traveling is going against the stream. On each direction as Pre points are supposed to travel counter clockwise and Ante points Clockwise.

We then evaluate the record and resort the CT results according to that.
This has been found to have a corrective results to lines and later produce better items for the triangle matching.

---

#### Results

After we have run each instance against each other. We have two SGRAD results. We can now use a combiner function to attempt and make the final combinations.

Here we show some of the results that we have gathered. Keep in mind that these pictures are without a combiner function and what we do is get the largest contour , not all the contours, run the variomatic and get the SGRADs that we then connect each points to each other according to SGRAD. Blue letter extends a blue line to the red letter and vice versa. There is also a thinner straight line connecting each point, this is the simlification line.

We can see that when there is a equilibrium in point count, the script returns appropriately matched letters where each SGRAD point looks at the appropriate point on the other instance. Just as you would have if the points where starting from the same location and just iterate each, combining with each, while what we do is completely different we get the same result.

We can also see that when the points are excess or misplaced, there are attempts of connecting to other points across the glyph points.

Because there is a rating for each of those points according to how many times they attempt a connection with the other instance, we can have useful data for the evaluation that we will need in the final combiner function.

I want to stress once more, that there is no attempt to remove or add points at the moment, all the images bellow are from the same run of the script on Garamond Pro Bold and Regular. The lines created are from each SGRAD and the thickness and radius of point circles corresponds to the value of attempts to connect with those points.

We could then get the uncertain areas between high certainty areas, and run an initial triangle matching.
From the points we gather we can then run triangle matching further on points we didn't match, with spamming triangles in intermediate points. We gradually gather the points we need and comprise a line.

---

Review the whole set of initial data at the repository here: 


```lib/batric/output_data/```


---

### **Introduction / Phase Introduction / Planning Phase / Safe Planning / Project Plan / Simplification Gradient / Method Implementation / Naturalisation**


#### Instance Original Point Naturalisation

Not implemented yet, but it will be based on remove and heal using fontparts after all the matching rules and quality checks run. Either Keep only overlapping points between the original instances and SGRAD. Or proceed to further Enhancing additional points to the final product. The curve difference must be in accordance to the Curve Difference Quality Target.

![IMG](assets/media/PIP_a_008.svg)

image: #008, 0.001, svg, Simplification Gradient - Cross instance SGRAD Matching.

---

![IMG](assets/media/PIP_a_009.svg)

image: #009, 0.001, svg, Simplification Gradient - Just SGRAD-abduct points from original instances.

---

#### Conclusion

SGRAD if not the easiest method is definitely a promising one. Given that the Max Error can be adjusted to be more granular, this only gives a more precise measurement for what are the points that keep persisting across. Those points are the most important ones and the ones we eventually keep for the final variable interpolation. We think that it provides good enough certainty by using straight no curve lines, and then we can step in and do bezier curve analysis, maybe with dynamic re-positioning.

---

### **Introduction / Phase Introduction / Planning Phase / Safe Planning / Project Plan / Simplification Gradient / Usage**

Run ```python3 lib/batric/sample/main.py``` with arguments:


```

Source UFO Instance Files:

	-a, "--instance_a"
	-b, "--instance_b"

	-a "/font_regular.ufo -b "/font_bold.ufo"

Log Directory for Output:

	-l, "--log_output"
	
	-l "/log_output"

Run Specific Glyph:

	-g, "--specific_glyph"

Or provide start and end number of glyphs to run:

	-s, "--start_glyph_num"
	-e, "--end_glyph_num"

	Start Glyph Number and End Glyph Number (-s from, -e to): -s 17 -e 117

```

For example run:

```
python3 lib/batric/sample/main.py -a "provide_ufo_a" -b "provide_ufo_b" -l "provide_directory_for_log_output" -g "A"
```

---

### **Introduction / Phase Introduction / Planning Phase / Safe Planning / Project Plan / Secondary Review**

<p>
Mathjax test:
When \(a \ne 0\), there are two solutions to \(ax^2 + bx + c = 0\) and they are
\[x = {-b \pm \sqrt{b^2-4ac} \over 2a}.\]
</p>

---

### **Introduction / Phase Introduction / Planning Phase / Safe Planning / Work Planning / Task Assignments**

We have identified a possible solution, and we are waiting for plan approval by Stakeholders.

---

### **Introduction / Phase Introduction / Planning Phase / Safe Planning / Work Planning / Dependencies**

*  SGRAD Components ∞0.001:
	*  Simplification Gradient:
		*  Path, Contour Simplification.
			*  According to Threshold Angle.
		*  Combiner
	*  SGradient to Instance:
		*  Method to transfer the SGradient Guide to the final compounds of each glyph.
			*  Point Match according to coordinates.
			*  Method to maintain curve when points are removed.
	*  Network X (To be removed)
	*  Plotlib


---


### **Introduction / Phase Introduction / Planning Phase / Safe Planning / Schedule Planning**

```{include=partials/introduction/phase_introduction/planning_phase/safe_planning/schedule_planning.md}```


---

### **Introduction / Phase Introduction / Planning Phase / Stakeholders**

We identify the **Stakeholders** by a **Personnel Plan** and create a **Communication Plan** to keep the **Stakeholders** informed.


*  **Stakeholders** Components:

	*  Applicable Stakeholders (Conscious and Unconscious Entities):
		*  clients
		*  personnel
		*  funders
		*  suppliers
		*  equipment
	*  Groups
		*  Development Group
		*  Organisation Documents Group
		*  Testing Team (TeT)
	*  Personnel Plan
	*  Communication Plan
		*  Stakeholder Feedback Mechanisms
		*  Required notifications

---

### **Introduction / Phase Introduction / Planning Phase / Stakeholders / Personnel Plan**

*  **Personnel Plan** Components ∞0.001:
	*  Organizational Structure
		*  team members
			*  internal
				*  Andreas Kalpakidis
				*  Madina Akhmatova
			*  external
				*  Dave Crossland
	*  Responsibilities and Qualifications
		*  Project Management and Accounting: Madina Akhmatova
		*  Planning and Design: Andreas Kalpakidis
		*  Review and Acceptance: Dave Crossland


---

### **Introduction / Phase Introduction / Planning Phase / Stakeholders / Communication Plan**

*  **Communication Plan** Components:
	*  Stakeholder Feedback Mechanisms
	*  Required notifications

#### Stakeholder Feedback Mechanisms

Currently the Stakeholders are notified by the README.md and README.html and README.pdf. Stakeholders can be notified by mail or in a forum to be presented soon. Github is also a viable method.

---

### **Introduction / Phase Introduction / Planning Phase / Quality Plan**

A **Quality Plan** describes the activities, standards, tools and processes necessary to achieve quality in the delivery of a project.

We can now create a **Quality Plan** by identifying the valid **Quality Targets** we want to achieve. Identify the **Quality Policies** that will be required to achieve them. Identify how to do **Quality Measurement**. Lastly identify how to maintain quality with **Quality Management**.


*  **Quality Plan (PQP)** Components:
	
	1.  Quality Targets
		*  Curve Difference.
	1.  Quality Measurement
		*  Combiner and Cross Matching.
	1.  Quality Management

---

### **Introduction / Phase Introduction / Planning Phase / Quality Plan / Quality Targets**

**Quality Targets** we want to achieve and what are their **Acceptance Criteria**, **Testing Parameters** and **Quality Management Procedures**, for each **Applicable Category**

1.  Quality Targets Components:
	*  Acceptance criteria
		*  Identify an acceptable curve difference threshold.
	*  Testing parameters
		*  Applicable Stakeholders
	*  Quality Management procedures
		*  Identify a Curve Precision Difference Calculation procedure.

---

### **Introduction / Phase Introduction / Planning Phase / Quality Plan / Quality Measurement**

Identify how to do **Quality Measurement** to see if we meet **Performance Standards** and **Acceptance criteria** and how those get collected by our **Performance Documentation Method**.

1.  Quality Measurement
	*  Performance Standards
		*  Performance Documentation Method

After each instance runs for each level of the simplification seed, creating the SGRAD, we pass the data to the combiner function, we gather point to point cross matching and measure how many times points match each other. This allows for us to understand the quality of matching. Points that do not have cross matching will be lower in quality. While creating the SVG we assign a larger radius to the points that have cross matched more times.

More on this subject and specifics will be presented here in the nearby future. For the moment after we run the function we end up with matching quality levels.

Currently we have 3 quality levels based on uncertainty:
	
* Low Uncertainty 
* Mid Uncertainty 
* High Uncertainty 

---


### **Introduction / Phase Introduction / Planning Phase / Quality Plan / Quality Management**

**Quality Management**, the nature of the **Audits**, **Work Verification** by assigning responsible personnel for **Task Fulfillment** and **Task Checking**.

1.  Quality Management
	*  Audits
	*  Tool Scheduling
	*  Work Verification
		*  Task fulfillment responsible personnel
		*  Task checking responsible personnel


---
