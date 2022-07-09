from manim import *
from matplotlib.pyplot import text
from sympy import field
import time



grav_constant = -9.8

def parabola(initial_pos: np.ndarray, initial_vel: np.ndarray, t: float):
	return (
		initial_pos[0] + initial_vel[0] * t,
		initial_pos[1] + initial_vel[1] * t + 0.5 * grav_constant * t**2,
		initial_pos[2]
	)

def suborbital(initial_pos: np.ndarray, t: float):
	return(
		(1 - t**2) * (initial_pos[0] + 4 * t),
		initial_pos[1] + 5 * (1-np.abs(2*(t * 1.027)-1)**2.5),
		initial_pos[2]
	)

def calculate_g(y_cord: float):
	elevation = 400000 * (y_cord + 2.5) / 4
	
	return 6.67E-11 * (5.97E24) / (200 + elevation + 6.37E6) ** 2


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
			MoveAlongPath(projectile0, parabola0, run_time=parabola0.t_max * 2, rate_func=linear))
		self.wait(0.5)

		self.play(
			Rotate(cannon, 5 * DEGREES, rate_func=there_and_back, run_time=0.1),
			MoveAlongPath(projectile1, parabola1, run_time=parabola1.t_max * 2, rate_func=linear))
		self.wait(0.5)
		
		self.play(
			Rotate(cannon, 5 * DEGREES, rate_func=there_and_back, run_time=0.1),
			MoveAlongPath(projectile2, parabola2, run_time=parabola2.t_max * 2, rate_func=linear))
		self.play(FadeOut(intro_text), run_time=0.5)

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
		station.move_to(DOWN * 4.5)
		self.add(station)
		station.set_z_index(ground.z_index - 1)

		earth = Circle(radius=2).set_fill(opacity=1, color=DARK_BROWN)
		earth.shift(DOWN * 4.5)
		

		suborbital_tracker = ValueTracker(projectile4.radius)
		projectile4.add_updater(
			lambda x: x.scale_to_fit_width(suborbital_tracker.get_value() * 2))

		self.play(Rotate(cannon, 5 * DEGREES, rate_func=there_and_back, run_time=0.1))
		self.play(
			FadeOut(projectile0,projectile1,projectile2,projectile3,cannon, run_time=0.5),
			MoveAlongPath(projectile4, parabola4, run_time = 4, rate_func=linear),
			ReplacementTransform(ground, earth, run_time = 4),
			station.animate(run_time = 4).move_to(UP * 1.5),
			suborbital_tracker.animate(run_time = 4).set_value(0.03),)
		
		#Gravitational Field Strengths
		self.play(FadeOut(grav_text), run_time=0.5)

		field_text = Tex(
			"""\\raggedright {
				On the Earth objects fall at ${9.81 \\textrm{m/s}^{2}}$, which is only slightly\\\\
				more than the acceleration ${400\\textrm{km}}$ up, at the level of the ISS, so\\\\
				it seems like it should simply fall back to the ground.""")

		field_text.scale(0.7).shift(UP * 3)

		elevation_marker = Dot().scale(0.8).move_to(DOWN * 0.6)

		g_text = Tex("${"+"{0:.2f}".format(9.81)+"\\textrm{m/s}^{2}}$").scale(0.5)

		g_text.add_updater(
			lambda x: x.become(Tex("${"+"{0:.2f}".format(calculate_g(x.get_center()[1]))+"\\textrm{m/s}^{2}}$").scale(0.5)))
		g_text.add_updater(lambda x: x.next_to(elevation_marker, RIGHT))

		self.add(elevation_marker, g_text)		
		self.play(
			Write(field_text),
			FadeIn(elevation_marker, g_text))
		self.wait(2)
		self.play(elevation_marker.animate.shift(UP * 2.6), rate_func=wiggle, run_time=10)

		g_text.clear_updaters()
		self.play(FadeOut(field_text, elevation_marker, g_text), run_time=0.5)
		self.wait()

class Orbits(Scene):
	def construct(self):
		station = ImageMobject("res/orbital_mechanics/SpaceStation.png").scale(0.3)
		station.move_to(UP * 1.5)

		earth = Circle(radius=2).set_fill(opacity=1, color=DARK_BROWN)
		earth.shift(DOWN * 4.5)

		orbit_text0 = Tex(
			"""\\raggedright {
				However, an object with significant horizontal velocity \\\\
				will "miss" the Earth as it falls, allowing a stable orbit.""")
		orbit_text0.scale(0.7).shift(UP * 3)


		self.add(earth, station)
		self.play(Write(orbit_text0))
		self.play(Rotate(station, angle=-PI, about_point=earth.get_center(), rate_func=rush_into, run_time=5))

		#Scale Shift

		orbit_text1 = Tex(
			"""\\raggedright {
				First, let's shift things into the correct scale. Now we can try dropping\\\\
				some objects near the ISS with different horizontal velocities.""")
		orbit_text1.scale(0.7).shift(UP * 3)

		self.play(FadeOut(orbit_text0), run_time=0.5)
		self.play(
			Write(orbit_text1),	
			earth.animate.scale_to_fit_width(5.64 * 2))
		self.wait(0.5)


		#0 km/s
		vel_text = Tex("""${v_{h0} = 0.00 \\textrm{km/s}}$"""	)
		vel_text.scale(0.7).shift(LEFT * 1.5 + UP * 1.5)

		projectile0 = Circle(radius=0.15).set_fill(opacity=1, color=PINK).move_to(UP * 1.5)
		trace0 = TracedPath(projectile0.get_center, dissipating_time=1)
		curve0 = ParametricFunction(lambda t: (0,1.5 - 4*t,0), t_range=[0,0.09]).set_stroke(opacity=0)

		self.play(	
			FadeIn(projectile0, trace0),
			FadeIn(vel_text))

		self.wait()
		self.play(MoveAlongPath(projectile0, curve0), rate_func=rush_into, run_time=2)

		#1 km/s
		projectile1 = Circle(radius=0.15).set_fill(opacity=1, color=PINK).move_to(UP * 1.5)
		trace1 = TracedPath(projectile1.get_center, dissipating_time=1)
		curve1 = ParametricFunction(lambda t: (0.604 * np.sin(PI * t),-4.5 + 3.032 * (np.cos(PI * t) + 0.98),0), t_range=[0,0.159]).set_stroke(opacity=0)

		self.play(
			FadeIn(projectile1, trace1),
			vel_text.animate.become(Tex("""${v_{h0} = 1.00 \\textrm{km/s}}$"""	).scale(0.7).shift(LEFT * 1.5 + UP * 1.5)))
		
		self.wait()
		self.play(MoveAlongPath(projectile1, curve1), rate_func=rush_into, run_time=3)

		#3 km/s
		projectile2 = Circle(radius=0.15).set_fill(opacity=1, color=PINK).move_to(UP * 1.5)
		trace2 = TracedPath(projectile2.get_center, dissipating_time=1)
		curve2 = ParametricFunction(lambda t: (1.711 * np.sin(PI * t),-4.5 + 3.245 * (np.cos(PI * t) + 0.85),0), t_range=[0,0.165]).set_stroke(opacity=0)

		self.play(
			FadeIn(projectile2, trace2),
			vel_text.animate.become(Tex("""${v_{h0} = 3.00 \\textrm{km/s}}$"""	).scale(0.7).shift(LEFT * 1.5 + UP * 1.5)))
		
		self.wait()
		self.play(MoveAlongPath(projectile2, curve2), rate_func=rush_into, run_time=3)
		
		#6 km/s
		projectile3 = Circle(radius=0.15).set_fill(opacity=1, color=PINK).move_to(UP * 1.5)
		trace3 = TracedPath(projectile3.get_center, dissipating_time=1)
		curve3 = ParametricFunction(lambda t: (3.971 * np.sin(PI * t),-4.5 + 4.317 * (np.cos(PI * t) + 0.39),0), t_range=[0,0.212]).set_stroke(opacity=0)

		self.play(
			FadeIn(projectile3, trace3),
			vel_text.animate.become(Tex("""${v_{h0} = 6.00 \\textrm{km/s}}$"""	).scale(0.7).shift(LEFT * 1.5 + UP * 1.5)))
		
		self.wait()
		self.play(MoveAlongPath(projectile3, curve3), rate_func=rush_into, run_time=3)

		#7.67 km/s
		orbit_text2 = Tex(
			"""\\raggedright {
				We're getting close! Orbital velocity around the Earth is ${7.67\\textrm{km/s}}$.\\\\
				Let's see what happens at that speed.""")
		orbit_text2.scale(0.7).shift(UP * 3)

		projectile4 = Circle(radius=0.15).set_fill(opacity=1, color=PINK).move_to(UP * 1.5)
		trace4 = Arc(radius=6, angle=0, arc_center=earth.get_center())

		scale_tracker = ValueTracker(0)
		theta_tracker0 = ValueTracker(0)
		earth.add_updater(
			lambda x: x.scale_to_fit_width((1 - 0.8 * scale_tracker.get_value()) * 5.64 * 2))
		projectile4.add_updater(
			lambda x: x.move_to((
				earth.get_center()[0] + ((1-0.8 * scale_tracker.get_value()) * 6) * np.sin(PI * theta_tracker0.get_value()), 
				earth.get_center()[1] + ((1-0.8 * scale_tracker.get_value()) * 6) * np.cos(PI * theta_tracker0.get_value()),
				 0)))
		trace4.add_updater(
			lambda x: x.become(Arc(
				radius=(1-0.8 * scale_tracker.get_value()) * 6,
				arc_center=earth.get_center(),
				start_angle= PI / 2 - PI * theta_tracker0.get_value(),
				angle= min(PI * theta_tracker0.get_value() / 3, 1.5 * PI),
				stroke_width=2)))


		self.remove(trace0, trace1,trace2)
		self.play(FadeOut(orbit_text1, run_time=0.5))

		self.play(Write(orbit_text2))
		self.play(
			FadeIn(projectile4, trace4),
			vel_text.animate.become(Tex("""${v_{h0} = 7.67 \\textrm{km/s}}$"""	).scale(0.7).shift(LEFT * 1.5 + UP * 1.5)))
		self.wait()
		self.play(
			FadeOut(projectile0, projectile1, projectile2, projectile3, run_time=0.5),
			earth.animate(run_time=3).move_to(DOWN * 1),
			scale_tracker.animate(run_time=3).set_value(1),
			theta_tracker0.animate(run_time=3, rate_func=lambda t: (2 * t**2 - t**3)).set_value(1))


		orbit_text3 = Tex(
			"""\\raggedright {
				We have a stable circular orbit!\\\\
				Let's bump the speed up even more.""")
		orbit_text3.scale(0.7).shift(UP * 3)

		self.play(
				LaggedStart(FadeOut(orbit_text2, run_time=0.5), Write(orbit_text3), lag_ratio=1),
				theta_tracker0.animate(run_time=6, rate_func=linear).increment_value(2))


		#10 km/s
		projectile5 = Circle(radius=0.15).set_fill(opacity=1, color=PINK)
		trace5 = TracedPath(projectile5.get_center, dissipating_time=1)


		theta_tracker1 = ValueTracker(0)

		def pos5_function(t:float) -> np.ndarray:
				t *= 0.2 * PI
				scaled_time = t + 2 * (0.325 * np.sin(t) + 0.202 / 2 * np.sin(2*t) + 0.140 / 3 * np.sin(3*t))

				return (
					earth.get_center()[0] -  3.86 * (np.cos(scaled_time) - 0.69), 
					earth.get_center()[1] +  2.80 * np.sin(scaled_time),
					0)

		projectile5.add_updater(lambda x: x.move_to(pos5_function(theta_tracker1.get_value())))

		self.play(
			LaggedStart(
				AnimationGroup(
					vel_text.animate.become(Tex("""${v_{h0} = 10.0 \\textrm{km/s}}$"""	).scale(0.7).shift(LEFT * 5.5 + UP * 1.5)),
					earth.animate.move_to(DOWN * 1 + LEFT * 4), 
					run_time=0.5),
				FadeIn(projectile5, trace5, run_time=0.5),
				lag_ratio=1),
			theta_tracker0.animate(run_time=1, rate_func=linear).increment_value(0.333333))


		#Energy Conservation
		orbit_text4 = Tex(
			"""\\raggedright {
				At ${10 \\textrm{km/s}}$ we have a nice elliptical orbit! But, it's only going\\\\
				${10 \\textrm{km/s}}$ at the bottom of its orbit. Because of energy conservation, it\\\\
				is moving much slower at the peak of its orbit.""")
		orbit_text4.scale(0.7).shift(UP * 3)


		trace_fix = TracedPath(projectile5.get_center, dissipating_time=1.05)
		self.add(trace_fix)
		self.play(
				LaggedStart(
					Wait(2),
					FadeOut(orbit_text3, run_time=0.5),
					Write(orbit_text4),
					FadeOut(trace5),
					lag_ratio=1),
				theta_tracker0.animate(run_time=15, rate_func=linear).increment_value(5),
				theta_tracker1.animate(run_time=15, rate_func=linear).set_value(5))

		orbit_text5 = Tex(
			"""\\raggedright {
				We can add a velocity vector to visualize this.""")
		orbit_text5.scale(0.7).shift(UP * 3)

		vel_vector = Arrow(start=projectile5.get_center(), end=projectile5.get_center()+DOWN, color=ORANGE).set_stroke(color=ORANGE, width=2)

		def get_end_pos(t: float) -> np.ndarray:
			delta_pos = pos5_function(theta_tracker1.get_value()+0.1) - projectile5.get_center() 
			delta_pos_normalized = delta_pos / np.linalg.norm(delta_pos)

			orbit_radius = np.linalg.norm(projectile5.get_center() - earth.get_center())
			orbit_vel_len = 1.5/10000 * np.sqrt(2*5.369E7 - 2 * 3.99E14 * (1/6.37E6 - 1/ (5.56E6 * orbit_radius)))

			return projectile5.get_center() + delta_pos_normalized * orbit_vel_len

		vel_vector.add_updater(
			lambda x: x.put_start_and_end_on( 
				projectile5.get_center(),
				get_end_pos(theta_tracker1.get_value())).set_stroke(width=4))


		self.play(
			FadeOut(orbit_text4),
			theta_tracker0.animate(rate_func=linear).increment_value(0.16666),
			theta_tracker1.animate(rate_func=linear).increment_value(0.16666),
			run_time=0.5)
		self.play(
			FadeIn(vel_vector),
			Write(orbit_text5),
			theta_tracker0.animate(run_time=9, rate_func=linear).increment_value(3),
			theta_tracker1.animate(run_time=9, rate_func=linear).increment_value(3))


		orbit_text6 = Tex(
			"""\\raggedright {
				The smaller orbit with a slower initial velocity completes multiple orbits\\\\
				in the time it takes for the higher object to complete a single orbit.""")
		orbit_text6.scale(0.7).shift(UP * 3)
		
		self.play(
			FadeOut(orbit_text5),
			theta_tracker0.animate(rate_func=linear).increment_value(0.16666),
			theta_tracker1.animate(rate_func=linear).increment_value(0.16666),
			run_time=0.5)
		self.play(
			Write(orbit_text6),
			theta_tracker0.animate(run_time=6, rate_func=linear).increment_value(2),
			theta_tracker1.animate(run_time=6, rate_func=linear).increment_value(2))


		orbit_text7 = Tex(
			"""\\raggedright {
				It "wins the race" despite starting slower!""")
		orbit_text7.scale(0.7).shift(UP * 3)
		

		self.play(
			FadeOut(orbit_text6),
			theta_tracker0.animate(rate_func=linear).increment_value(0.16666),
			theta_tracker1.animate(rate_func=linear).increment_value(0.16666),
			run_time=0.5)
		self.play(
			Write(orbit_text7),
			theta_tracker0.animate(run_time=6, rate_func=linear).increment_value(2),
			theta_tracker1.animate(run_time=6, rate_func=linear).increment_value(2))
		
		orbit_text8 = Tex(
			"""\\raggedright {
				Thanks for watching!""")
		orbit_text8.scale(0.8).shift(UP * 3)
		
				
		self.play(
			FadeOut(orbit_text7, vel_text),
			theta_tracker0.animate(rate_func=linear).increment_value(0.16666),
			theta_tracker1.animate(rate_func=linear).increment_value(0.16666),
			run_time=0.5)
		self.play(
			Write(orbit_text8),
			theta_tracker0.animate(run_time=15, rate_func=linear).increment_value(5),
			theta_tracker1.animate(run_time=15, rate_func=linear).increment_value(5))
		self.wait()