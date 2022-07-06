from manim import *
from matplotlib.pyplot import text



grav_constant = -9.8

def parabola(initial_pos: np.ndarray, initial_vel: np.ndarray, t: float):
	return (
		initial_pos[0] + initial_vel[0] * t,
		initial_pos[1] + initial_vel[1] * t + 0.5 * grav_constant * t**2,
		initial_pos[2]
	)

def suborbital(initial_pos: np.ndarray, t: float):
	return(
		(1 - t**2) * (initial_pos[0] + 5 * t),
		initial_pos[1] + 5 * (1-np.abs(2*(t * 1.05)-1)**2.5),
		initial_pos[2]
	)

def calculate_g(y_cord: float):
	elevation = 400000 * (y_cord + 2.5) / 4
	
	return 6.67E-11 * (5.97E24) / (-250 + elevation + 6.37E6) ** 2


# Animation debunking the myth that launching into orbit is zero gravity 
class GravitationalField(Scene):
	def construct(self):
		ground = Square(side_length=16).set_fill(opacity=1, color=GREY)
		ground.shift(DOWN * 10.5)

		cannon = ImageMobject("res/orbital_mechanics/CannonClipArt.png").scale(0.5)
		cannon.shift(DOWN * 1.75 + LEFT * 5.5)

		projectile0 = Circle(radius=0.15).set_fill(opacity=1, color=PINK)
		projectile0.move_to(cannon.get_center() + LEFT * 0.1)
		path0 = TracedPath(projectile0.get_center, dissipating_time=0.2)
		parabola0 = ParametricFunction(
			lambda t: parabola(projectile0.get_center(), UP * 4 + RIGHT * 1, t),
			t_range=[0,0.95])

		projectile1 = projectile0.copy()
		path1 = TracedPath(projectile1.get_center, dissipating_time=0.4)
		parabola1 = ParametricFunction(
			lambda t: parabola(projectile1.get_center(), UP * 6 + RIGHT * 1.5, t),
			t_range=[0,1.32])
		
		projectile2 = projectile0.copy()
		path2 = TracedPath(projectile2.get_center, dissipating_time=0.4)
		parabola2 = ParametricFunction(
			lambda t: parabola(projectile2.get_center(), UP * 8 + RIGHT * 2, t),
			t_range=[0,1.707])
		
		projectile3 = projectile0.copy()
		path3 = TracedPath(projectile3.get_center, dissipating_time=0.4)
		parabola3 = ParametricFunction(
			lambda t: parabola(projectile3.get_center(), UP * 10 + RIGHT * 2.5, t),
			t_range=[0,2.1])

		projectile4 = projectile0.copy()
		path4 = TracedPath(projectile4.get_center, dissipating_time=0.75)
		parabola4 = ParametricFunction(
			lambda t: suborbital(projectile4.get_center(), t),
			t_range=[0,1])




		#Intro Scene

		self.add(projectile0, path0)
		self.add(projectile1, path1)
		self.add(projectile2, path2)
		self.add(projectile3, path3)
		self.add(projectile4, path4)
		
		self.add(ground, cannon)
		self.wait()

		intro_text = Tex(
			"""\\raggedright {
				As the saying goes, "What goes up \\\\
				must come down," so how do spacecraft \\\\
				stay in orbit near the Earth?}""")
		intro_text.scale(0.7).shift(RIGHT * 3.75 + UP * 3)
		self.play(
			Write(intro_text),
			Rotate(cannon, 5 * DEGREES, rate_func=there_and_back, run_time=0.1),
			MoveAlongPath(projectile0, parabola0, run_time=parabola0.t_max * 2, rate_func=linear)
		)
		self.wait(0.5)

		self.play(
			Rotate(cannon, 5 * DEGREES, rate_func=there_and_back, run_time=0.1),
			MoveAlongPath(projectile1, parabola1, run_time=parabola1.t_max * 2, rate_func=linear)
		)
		self.wait(0.5)
		
		self.play(
			Rotate(cannon, 5 * DEGREES, rate_func=there_and_back, run_time=0.1),
			MoveAlongPath(projectile2, parabola2, run_time=parabola2.t_max * 2, rate_func=linear)
		)
		self.wait(0.4)
		self.play(FadeOut(intro_text), run_time=0.1)

		grav_text = Tex(
			"""\\raggedright {
				If you launched a rocket straight up to the \\\\
				height of the space station, it would simply \\\\
				fall back down to Earth.""")

		grav_text.scale(0.7).shift(RIGHT * 3.75 + UP * 3)
		self.play(
			Write(grav_text),
			Rotate(cannon, 5 * DEGREES, rate_func=there_and_back, run_time=0.1),
			MoveAlongPath(projectile3, parabola3, run_time=parabola3.t_max * 2, rate_func=linear)
		)
		self.wait(0.5)



		#Transition to space view

		self.remove(path0,path1,path2,path3)

		station = ImageMobject("res/orbital_mechanics/SpaceStation.png").scale(0.3)
		station.move_to(DOWN * 8)
		self.add(station)
		station.set_z_index(ground.z_index - 1)

		earth = Circle(radius=2).set_fill(opacity=1, color=DARK_BROWN)
		earth.shift(DOWN * 4.5)
		

		suborbital_tracker = ValueTracker(projectile4.radius)
		projectile4.add_updater(
			lambda x: x.scale_to_fit_width(suborbital_tracker.get_value() * 2)
		)

		self.play(Rotate(cannon, 5 * DEGREES, rate_func=there_and_back, run_time=0.1))
		self.play(
			FadeOut(projectile0,projectile1,projectile2,projectile3,cannon, run_time=0.5),
			AnimationGroup(
			MoveAlongPath(projectile4, parabola4, rate_func=linear),
			ReplacementTransform(ground, earth),
			station.animate.move_to(UP * 1.5),
			suborbital_tracker.animate.set_value(0.03),
			run_time = 4)
		)
		self.wait(0.4)

		#Gravitational Field Strengths
		self.play(FadeOut(grav_text), run_time=0.1)

		field_text = Tex(
			"""\\raggedright {
				On the Earth objects fall at ${9.81 \\textrm{m/s}^{2}}$, which\\\\
				is only slightly more than the acceleration\\\\
				${400\\textrm{km}}$ up, at the level of the ISS""")
		field_text.scale(0.7).shift(RIGHT * 2.75 + UP * 3)

		elevation_marker = Dot().scale(0.8).move_to(DOWN * 0.6)

		g_text = Tex("${"+"{0:.2f}".format(9.81)+"\\textrm{m/s}^{2}}$").scale(0.5)

		g_text.add_updater(
			lambda x: x.become(Tex("${"+"{0:.2f}".format(calculate_g(x.get_center()[1]))+"\\textrm{m/s}^{2}}$").scale(0.5)))
		g_text.add_updater(lambda x: x.next_to(elevation_marker, RIGHT))

		self.add(elevation_marker, g_text)		
		self.play(
			Write(field_text),
			FadeIn(elevation_marker, g_text)
			)
		self.wait()
		self.play(elevation_marker.animate.shift(UP * 2.6), rate_func=wiggle, run_time=10)

class Orbits(Scene):
	def construct(self):
		return super().construct()