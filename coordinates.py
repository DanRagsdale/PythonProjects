from typing import Callable
from manim import *

r = 3

def patch_boundary(t):
	if t < 1:
		return(-1 + t * 2, -3, 0)
	elif t < 2:
		return (1, -3 + 6 * (t-1), 0)
	elif t < 3:
		return (1- 2*(t-2), 3, 0)
	else:
		return (-1, 3 - 6 *(t-3),0)

def dot_curve_function(t):
	return 0.75 * np.array([np.cos(3.5 * PI * t),2 - 4 * (t)**4,0])

def curve_function(t):
	return 0.75 * np.array([0.75 * np.sin(10 * t),1 * t + 2.5 * np.cos(5 * t),0])

def line_function(start, end, t):
	return (
		start[0] + t * (end[0]-start[0]),
		start[1] + t * (end[1]-start[1]),
		start[2] + t * (end[2]-start[2]),
		)

def homotopy_function(x, y, z, t):
	return (1-0.3 * np.sin(PI * t)) * np.array((
		x+t*np.sin(y) + 8*t,
		y + np.sin(PI * t),
		z))


class ChangeCoordinates(Scene):
	def construct(self):
		start_axes = Axes(
			tips=False
		)
		end_axes = start_axes.copy()


		start_boundary = ParametricFunction(
			lambda t: start_axes.c2p(*patch_boundary(t)),
			t_range=[0,4],
		)
		start_boundary.set_stroke(color=YELLOW)

		end_boundary = start_boundary.copy()


		start_grid = VGroup()
		for i in range(-5,5+1):
			h = ParametricFunction(
				lambda t: line_function(
					start_axes.c2p(*(-1,0.5*i,0)),
					start_axes.c2p(*( 1,0.5*i,0)),
					t)).set_stroke(color=BLUE, opacity=0.7, width=2)
			start_grid.add(h)
		for i in range (-1, 1+1):
			v = ParametricFunction(
				lambda t: line_function(
					start_axes.c2p(*(0.5*i,-3,0)),
					start_axes.c2p(*(0.5*i, 3,0)),
					t)).set_stroke(color=BLUE, opacity=0.7, width=2)
			start_grid.add(v)

		end_grid = start_grid.copy()


		start_curve = ParametricFunction(
			lambda t: start_axes.c2p(*curve_function(t)),
			t_range=[0,1.3]
		)
		start_curve.set_stroke(color=RED)

		end_curve = start_curve.copy()


		dot_path = ParametricFunction(
			lambda t: start_axes.c2p(*dot_curve_function(t)),
			t_range=[0,1]
		)
		dot_path.set_opacity(0)


		#Begin actual animations

		start_patch = VGroup(start_boundary, start_grid)
		end_patch = VGroup(end_boundary, end_grid)


		start_space = VGroup(start_axes, start_patch, dot_path, start_curve)
		start_space.shift(LEFT * 4)

		end_space = VGroup(end_axes, end_patch, end_curve)
		end_space.move_to(start_space.get_center())


		arrow = CurvedArrow(2*LEFT + UP, 2*RIGHT + UP, color=RED)
		arrow.set_stroke(width=7,color=RED)
		arrow.flip(RIGHT).stretch_to_fit_height(0.7)

		function_label=Tex(r"F(U)", font_size = 80)


		#Prevent these objects from appearing during animations
		start_axes.set_opacity(0)
		start_curve.set_opacity(0)

		end_axes.set_opacity(0)
		end_curve.set_opacity(0)


	#Intro scene

		intro_text = Tex(
			"""\\raggedright {Let ${U}$ and ${G}$ be topological sets, and let ${F}$ be a homeomorphism ${F:U \\longrightarrow G}$.\\\\
			This means that ${U}$ and ${G}$ will have similar properties.\\\\
			Anything that can be done in ${U}$ can also be done in ${G}$}""")
		intro_text.scale(0.5).shift(RIGHT * 2)

		self.play(Write(intro_text))
		self.wait(2)

		big_u = Tex("U").move_to(start_space.get_center())
		self.play(FadeIn(big_u), run_time=2)
		self.play(Transform(big_u,start_patch), run_time=2)

		self.wait(1.5)

	#Homeomorphism scene

		self.remove(big_u)
		self.add(start_patch)
		self.add(end_patch)

		self.play(
			FadeOut(intro_text, run_time=0.6), 
			LaggedStart(
				Homotopy(homotopy_function, end_space, run_time=4),
				AnimationGroup(Create(arrow),Write(function_label), run_time=1.5), lag_ratio=0.6))

		self.wait(1.5)
	#Points scene

		start_point = Dot().set_color(RED)
		end_point = Dot().set_color(RED)

		end_point.add_updater(
			lambda point: point.move_to(homotopy_function(*start_point.get_center(),1))
		)	
		points_text = Tex("\\text {Every point in ${U}$ corresponds to a point in the image ${F(U) = G}$ }")
		points_text.scale(0.8).shift(DOWN * 3)

		self.play(Write(points_text))
		self.wait()
		
		self.add(start_point)
		self.add(end_point)

		self.play(MoveAlongPath(start_point, dot_path), run_time=4)
		self.play(FadeOut(start_point, end_point, points_text), run_time=0.5)

		self.wait(1.5)

	#Curve scene

		curves_text = Tex("\\text {Likewise, every curve in ${U}$ corresponds to a curve in ${G}$")
		curves_text.scale(0.8).shift(DOWN * 3)
		
		self.play(Write(curves_text))
		self.wait()

		start_curve.set_stroke(opacity=1)
		end_curve.set_stroke(opacity=1)

		self.play(Create(start_curve), Create(end_curve),rate_func=linear, run_time=4)
		#start_grid.apply_function(lambda p: homotopy_function(*p,1))
		self.play(FadeOut(curves_text))

		self.wait(1.5)

	#Outro scene

		outro_text = Tex("\\text {From a topological perspective, ${U}$ and ${G}$ are the same space!")
		outro_text.scale(0.8).shift(DOWN * 3)

		self.play(Write(outro_text))
		self.wait(5)