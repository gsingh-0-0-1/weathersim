import numpy as np
import matplotlib.pyplot as plt
import itertools

class Matter:
	def __init__(self):
		self.heat = 0
		self.under = None
		self.ontopof = None
		self.conductable_heat = 0
		self.conduct_to = []
		self.dissipate = 0.05

		#this differentiation will help create the sphere structure
		self.links = {
			"lat" : [],
			"lon" : []
		}

	def calc_conductable(self):
		self.conductable_heat = self.heat * self.conduct
		self.conduct_to = self.links["lat"] + self.links["lon"]
		if self.under is not None:
			self.conduct_to = self.conduct_to + [self.under]

	def conduct_heat(self):
		for item in self.conduct_to:
			item.heat = item.heat + self.conductable_heat / len(self.conduct_to)
		self.heat = self.heat - self.conductable_heat

	def dissipate_heat(self):
		if self.under is None:
			self.heat = self.heat * (1 - self.dissipate)

class Terrain(Matter):
	def __init__(self, theta, phi, t = "land"):
		super().__init__()
		self.theta = theta
		self.phi = phi

		self.heat = 0

		if t == "land":
			self.reflect = 0.2
			self.conduct = 0.75
		if t == "water":
			self.reflect = 0.5
			self.conduct = 0.45

	def illuminate(self, heat):
		self.heat = self.heat + heat * (1 - self.reflect)


class Air(Matter):
	def __init__(self, ontopof):
		super().__init__()
		self.ontopof = ontopof
		self.ontopof.under = self

		self.theta = self.ontopof.theta
		self.phi = self.ontopof.phi

		self.heat = 0
		self.conduct = 0

	def link(self, airmass, d):
		if airmass not in self.links[d]:
			self.links[d].append(airmass)
		if self not in airmass.links[d]:
			airmass.links[d].append(self)


class Sun:
	def __init__(self):
		self.heat = 5
		self.time = 0

	def warm_ter(self, ter):
		target_ter = [t for t in ter if abs(t.theta - self.time) < np.pi / 2 or 
										abs(t.theta - self.time - 2 * np.pi) < np.pi / 2 or
										abs(t.theta - self.time + 2 * np.pi) < np.pi / 2]
		for t in target_ter:
			t.illuminate(self.heat * np.cos(t.theta - self.time) * np.sin(t.phi))
		self.time += 0.25
		self.time = self.time % (2 * np.pi)

#fig = plt.figure()
#ax = fig.add_subplot(projection='3d')

#keep track of the list of airmasses at each phi, or latitute,
#so that we can link them up "vertically"
lat_air_list = []
lat_ter_list = []

PHI_STEP = 0.05

#create the terrain
#we will add a water body centered on theta = 0, phi = pi / 2 -- near the equator
for phi in np.arange(0, np.pi + 0.001, PHI_STEP):
	#one point at the poles, i.e. where phi = 0 or phi = pi
	#and we will max out at, say, 20, at the equator
	npoints = round(1 + 99 * np.sin(phi))
	this_lat_ter_list = []
	this_lat_air_list = []
	print(npoints)
	for theta in np.linspace(0, 2 * np.pi, npoints):
		t = "land"
		#generate terrain here
		
		#if (theta < np.pi / 8 or theta > 15 * np.pi / 8) and (3 * np.pi / 8 < phi < 5 * np.pi / 8):
		#	t = "water"
		#	print("water")
		#else:
		#	t = "land"
		t = Terrain(theta, phi, t = t)
		a = Air(t)
		this_lat_ter_list.append(t)
		this_lat_air_list.append(a)

		#link to previous element
		if theta != 0:
			a.link(this_lat_air_list[-2], "lat")

	#connect first and last elements
	if phi != 0:
		this_lat_air_list[0].link(this_lat_air_list[-1], "lat")

	lat_air_list.append(this_lat_air_list)
	lat_ter_list.append(this_lat_ter_list)

	#now we link via longitude
	if phi != 0:
		l1 = lat_air_list[-1]
		l2 = lat_air_list[-2]
		n1 = len(l1)
		n2 = len(l2)

		for ind2 in range(n2):
			r_ind1 = [round((ind2 - 0.5) * n1 / n2), round((ind2 + 0.5) * n1 / n2)]
			for ind1 in range(r_ind1[0], r_ind1[1] + 1):
				l2[ind2 % n2].link(l1[ind1 % n1], "lon")


ALL_TER = [ter for subl in lat_ter_list for ter in subl]
ALL_AIR = [air for subl in lat_air_list for air in subl]

sun = Sun()


fig = plt.figure()
ax1 = fig.add_subplot(1, 2, 1, projection='3d')
ax2 = fig.add_subplot(1, 2, 2, projection='3d')

XS = []
YS = []
ZS = []

for air in ALL_AIR:
	x = np.cos(air.theta) * np.sin(air.phi)
	y = np.sin(air.theta) * np.sin(air.phi)
	z = np.cos(air.phi)
	XS.append(x)
	YS.append(y)
	ZS.append(z)

	#sc = ax.scatter(x, y, z, color = "blue")
	l = air.links["lat"] + air.links["lon"]

while True:

	AIR_HEATS = [air.heat for air in ALL_AIR]
	TER_HEATS = [ter.heat for ter in ALL_TER]


	ax1.clear()

	m_AIR_HEATS = AIR_HEATS / (np.amax(AIR_HEATS) if np.amax(AIR_HEATS) != 0 else np.array([1]))
	sc1 = ax1.scatter(XS, YS, ZS, c = m_AIR_HEATS, cmap = "coolwarm")
	ax1.set_title("Air Temp (Max " + str(round(np.amax(AIR_HEATS))) + ")")
	#colorbar(sc1, ax = ax1)

	plt.pause(0.01)

	ax2.clear()

	m_TER_HEATS = TER_HEATS / (np.amax(TER_HEATS) if np.amax(TER_HEATS) != 0 else np.array([1]))
	sc2 = ax2.scatter(XS, YS, ZS, c = m_TER_HEATS, cmap = "coolwarm")
	ax2.set_title("Ter Temp (Max " + str(round(np.amax(TER_HEATS))) + ")")
	#fig.colorbar(sc2, ax = ax2)

	plt.pause(0.01)

	
	for ter in ALL_TER:
		ter.calc_conductable()
		ter.conduct_heat()

	for air in ALL_AIR:
		air.calc_conductable()

	for air in ALL_AIR:
		air.conduct_heat()

	for air in ALL_AIR:
		air.dissipate_heat()


	sun.warm_ter(ALL_TER)

	'''
	for link in l:
		x1 = np.cos(link.theta) * np.sin(link.phi)
		y1 = np.sin(link.theta) * np.sin(link.phi)
		z1 = np.cos(link.phi)
		ax.plot([x, x1], [y, y1], [z, z1], color = "green")
	'''

plt.show()

