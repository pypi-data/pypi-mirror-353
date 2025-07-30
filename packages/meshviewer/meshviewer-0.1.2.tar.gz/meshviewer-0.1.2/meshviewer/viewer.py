import moderngl
import glfw
import numpy as np
import sys
import os
from pathlib import Path
import trimesh
import glm

# Monkey patch trimesh.util.allclose to fix NumPy 2.0 compatibility
import trimesh.util
from .util import allclose
trimesh.util.allclose = allclose

WIDTH, HEIGHT = 1280, 720
TITLE = "ModernGL Mesh Viewer"



class MeshViewer:
    def __init__(self):
        # Initialize GLFW
        if not glfw.init():
            sys.exit("GLFW initialization failed")

        # Configure GLFW
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

        # Create window
        self.window = glfw.create_window(WIDTH, HEIGHT, TITLE, None, None)
        if not self.window:
            glfw.terminate()
            sys.exit("GLFW window creation failed")

        glfw.make_context_current(self.window)

        # Create ModernGL context
        self.ctx = moderngl.create_context()

        self.use_arcball = True

        if self.use_arcball:
            from .arcball_camera import ArcballCamera
            self.camera = ArcballCamera(WIDTH, HEIGHT)

        else:
            from .camera import Camera
            self.camera = Camera(WIDTH, HEIGHT)

        # Set callbacks
        glfw.set_cursor_pos_callback(self.window, self._mouse_callback)
        glfw.set_scroll_callback(self.window, self._scroll_callback)
        glfw.set_framebuffer_size_callback(self.window, self._resize_callback)
        glfw.set_mouse_button_callback(self.window, self._mouse_button_callback)

        # Mouse interaction state
        self.left_mouse_pressed = False
        self.right_mouse_pressed = False
        self.last_x = WIDTH / 2
        self.last_y = HEIGHT / 2

        # Mesh rotation state
        self.rotation_x = 0.0
        self.rotation_y = 0.0

        # Enable depth testing
        self.ctx.enable(moderngl.DEPTH_TEST)
        self.ctx.enable(moderngl.CULL_FACE)

        # Initialize mesh data
        self.meshes = []
        self.model_matrix = glm.mat4(1.0)
        self.axis_scale = 1.1

        # Load shaders
        self._load_shaders()

        self.axis_arrows = self.init_global_basis_axes(self.ctx, self.prog)
        
    def _load_shaders(self):
        shader_dir = Path(__file__).parent / "shaders"
        
        with open(shader_dir / "mesh.vert") as f:
            vertex_shader = f.read()
        
        with open(shader_dir / "mesh.frag") as f:
            fragment_shader = f.read()
        
        self.prog = self.ctx.program(
            vertex_shader=vertex_shader,
            fragment_shader=fragment_shader
        )
    
    
    def _fit_meshes_to_view(self):
        """Adjust camera position and center to fit all meshes in view."""
        if not self.meshes:
            return

        min_bounds = np.array([np.inf, np.inf, np.inf])
        max_bounds = np.array([-np.inf, -np.inf, -np.inf])

        for mesh_data in self.meshes:
            bounds = mesh_data['mesh'].bounds
            min_bounds = np.minimum(min_bounds, bounds[0])
            max_bounds = np.maximum(max_bounds, bounds[1])

        mesh_center = (min_bounds + max_bounds) / 2
        mesh_size = np.max(max_bounds - min_bounds)
        self.axis_scale = mesh_size * 1.2

        if self.use_arcball:
            self.camera.center = glm.vec3(*mesh_center)
            self.camera.zoom = mesh_size * 2.5
            self.camera._view_dirty = True  # mark view for recompute
        else:
            self.camera.target = glm.vec3(*mesh_center)
            self.camera.distance = mesh_size * 2.0
            self.camera.yaw = -135.0
            self.camera.pitch = 35.264
            self.camera._update_vectors()
    
    def load_mesh(self, filepath, color=(0.7, 0.7, 0.7)):
        mesh = trimesh.load(filepath)
        
        # Process mesh data
        vertices = mesh.vertices.astype('f4')
        indices = mesh.faces.flatten().astype('i4') if hasattr(mesh, 'faces') else np.arange(len(vertices)).astype('i4')
        normals = mesh.vertex_normals.astype('f4') if hasattr(mesh, 'vertex_normals') else np.zeros_like(vertices)
        
        # Create buffers
        vbo_vertices = self.ctx.buffer(vertices.tobytes())
        vbo_normals = self.ctx.buffer(normals.tobytes())
        ibo = self.ctx.buffer(indices.tobytes())
        
        # Create VAO
        mesh_vao = self.ctx.vertex_array(
            self.prog,
            [
                (vbo_vertices, '3f', 'in_position'),
                (vbo_normals, '3f', 'in_normal'),
            ],
            ibo
        )
        
        # Add mesh to list with ray intersector for picking
        intersector = trimesh.ray.ray_triangle.RayMeshIntersector(mesh)
        self.meshes.append({
            'vao': mesh_vao,
            'color': color,
            'mesh': mesh,
            'picker': intersector,
        })
        
        # Auto-fit meshes to view
        self._fit_meshes_to_view()
    
    def run(self):
        while not glfw.window_should_close(self.window):
            self._process_input()
            self._render()
            glfw.swap_buffers(self.window)
            glfw.poll_events()
        glfw.terminate()
    
    def _render(self):
        self.ctx.clear(0.15, 0.15, 0.15)
        self.ctx.enable(moderngl.DEPTH_TEST)

        # Get view and projection matrices from camera
        view = self.camera.get_view_matrix()
        projection = self.camera.get_projection_matrix()

        # Determine model matrix for rendering mesh
        if self.use_arcball:
            model = glm.mat4(1.0)  # Arcball rotation is already in view matrix
        else:
            model = glm.mat4(1.0)
            model = glm.rotate(model, glm.radians(self.rotation_x), glm.vec3(1, 0, 0))
            model = glm.rotate(model, glm.radians(self.rotation_y), glm.vec3(0, 1, 0))

        # Render meshes
        for mesh_data in self.meshes:
            self.prog['model'].write(model)
            self.prog['view'].write(view)
            self.prog['projection'].write(projection)
            self.prog['light_pos'].value = tuple(self.camera.position)  # Follow camera position
            self.prog['view_pos'].value = tuple(self.camera.position)
            self.prog['object_color'].value = mesh_data['color']
            mesh_data['vao'].render()

        # Scale for axis arrows
        scale = glm.scale(glm.mat4(1.0), glm.vec3(self.axis_scale * 1.1))

        # Render axis arrows
        for axis in self.axis_arrows:
            model_arrow = scale * axis['model']
            self.prog['model'].write(model_arrow)
            self.prog['view'].write(view)
            self.prog['projection'].write(projection)
            self.prog['light_pos'].value = tuple(self.camera.position)
            self.prog['view_pos'].value = tuple(self.camera.position)
            self.prog['object_color'].value = axis['color']
            axis['vao'].render()

    
    def _process_input(self):
        if glfw.get_key(self.window, glfw.KEY_ESCAPE) == glfw.PRESS:
            glfw.set_window_should_close(self.window, True)
    
    def _mouse_callback(self, window, xpos, ypos):
        if self.left_mouse_pressed:
            if self.use_arcball:
                self.camera.drag(xpos, ypos)
            else:
                self.camera.orbit(xpos, ypos)
                self.last_x = xpos
                self.last_y = ypos
        elif self.right_mouse_pressed:
            dx = xpos - self.last_x
            dy = ypos - self.last_y
            self.camera.pan(dx, dy)
            self.last_x = xpos
            self.last_y = ypos

    
    def _scroll_callback(self, window, xoffset, yoffset):
        if self.use_arcball:
            x, y = glfw.get_cursor_pos(self.window)
            width, height = glfw.get_window_size(self.window)
            ray = self.camera.screen_ray(x, y, width, height)
            self.camera.zoom_towards_cursor(yoffset, ray)
        else:
            x, y = glfw.get_cursor_pos(window)
            width, height = glfw.get_window_size(window)
            ray = self.camera.screen_ray(x, y, width, height)
            self.camera.zoom(yoffset, ray)
    
    def _resize_callback(self, window, width, height):
        self.ctx.viewport = (0, 0, width, height)
        self.camera.set_viewport(width, height)
    
    def _mouse_button_callback(self, window, button, action, mods):
        if button == glfw.MOUSE_BUTTON_LEFT:
            if action == glfw.PRESS and (mods & glfw.MOD_CONTROL):
                x, y = glfw.get_cursor_pos(window)
                self._pick(x, y)
                return

            self.left_mouse_pressed = (action == glfw.PRESS)

            if self.left_mouse_pressed:
                x, y = glfw.get_cursor_pos(window)
                if self.use_arcball:
                    self.camera.begin_drag(x, y)
                else:
                    self.last_x, self.last_y = x, y
            else:
                if self.use_arcball:
                    self.camera.end_drag()
                else:
                    self.camera._first_mouse = True

        elif button == glfw.MOUSE_BUTTON_RIGHT:
            self.right_mouse_pressed = (action == glfw.PRESS)
            if self.right_mouse_pressed:
                self.last_x, self.last_y = glfw.get_cursor_pos(window)


    def _pick(self, x: float, y: float) -> None:
        width, height = glfw.get_window_size(self.window)
        ray = self.camera.screen_ray(x, y, width, height)
        origin = self.camera.position

        # Inverse model matrix for current rotations
        model = glm.mat4(1.0)
        model = glm.rotate(model, glm.radians(self.rotation_x), glm.vec3(1, 0, 0))
        model = glm.rotate(model, glm.radians(self.rotation_y), glm.vec3(0, 1, 0))
        inv_model = glm.inverse(model)

        for mesh_data in self.meshes:
            o = glm.vec3(inv_model * glm.vec4(origin, 1.0))
            d = glm.normalize(glm.vec3(inv_model * glm.vec4(origin + ray, 1.0)) - o)
            locs, index_ray, index_tri = mesh_data['picker'].intersects_location([o], [d], multiple_hits=False)
            if len(locs):
                world_hit = glm.vec3(model * glm.vec4(*locs[0], 1.0))
                print(f"Picked point: {world_hit.x:.4f}, {world_hit.y:.4f}, {world_hit.z:.4f}")
                break


    def make_axis_arrow(self, axis: str) -> tuple[trimesh.Trimesh, glm.mat4, tuple[float, float, float]]:
        """Creates a cylinder + cone arrow along given axis."""
        shaft = trimesh.creation.cylinder(radius=0.01, height=0.9, sections=64)
        shaft.apply_translation([0, 0, 0.45])

        cone = trimesh.creation.cone(radius=0.03, height=0.1, sections=64)
        cone.apply_translation([0, 0, 0.9])

        color = {
            "X": (1.0, 0.0, 0.0),
            "Y": (0.0, 1.0, 0.0),
            "Z": (0.0, 0.0, 1.0),
        }[axis]

        if axis == "X":
            rot = glm.rotate(glm.mat4(1.0), glm.radians(90), glm.vec3(0, 1, 0))
        elif axis == "Y":
            rot = glm.rotate(glm.mat4(1.0), glm.radians(-90), glm.vec3(1, 0, 0))
        else:
            rot = glm.mat4(1.0)

        return shaft + cone, rot, color


    def init_global_basis_axes(self, ctx, shader_program) -> list[dict]:
        """
        Creates 3D axis arrows (X, Y, Z) using cylinders + cones,
        returns a list of renderable VAOs + transforms.
        """
        axis_vao_data = []

        for axis in ["X", "Y", "Z"]:
            mesh, model_matrix, color = self.make_axis_arrow(axis)

            vertices = mesh.vertices.astype("f4")
            normals = mesh.vertex_normals.astype("f4")
            indices = mesh.faces.flatten().astype("i4")

            vbo_vertices = ctx.buffer(vertices.tobytes())
            vbo_normals = ctx.buffer(normals.tobytes())
            ibo = ctx.buffer(indices.tobytes())

            vao = ctx.vertex_array(
                shader_program,
                [
                    (vbo_vertices, "3f", "in_position"),
                    (vbo_normals, "3f", "in_normal"),
                ],
                ibo
            )

            axis_vao_data.append({
                "vao": vao,
                "model": model_matrix,
                "color": color,
            })

        return axis_vao_data

def main():
    """
    Main entry point for the mesh viewer application.
    Handles command line arguments and launches the viewer.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="ModernGL Mesh Viewer")
    parser.add_argument("mesh_files", nargs="+", help="Path to mesh file(s) (.obj or .stl)")
    parser.add_argument("--width", type=int, default=1280, help="Window width (default: 1280)")
    parser.add_argument("--height", type=int, default=720, help="Window height (default: 720)")
    
    args = parser.parse_args()
    
    # Override global constants if provided
    global WIDTH, HEIGHT
    WIDTH, HEIGHT = args.width, args.height
    
    viewer = MeshViewer()
    
    # Load meshes with distinct colors
    colors = [
        (0.3, 0.6, 0.9),  # Light blue
        (0.9, 0.3, 0.6),  # Pink
        (0.6, 0.9, 0.3),  # Light green
        (0.65, 0.65, 0.75),  # Gray
        (0.9, 0.6, 0.3),  # Orange
    ]
    
    valid_files = 0
    for i, mesh_path in enumerate(args.mesh_files):
        if os.path.exists(mesh_path):
            viewer.load_mesh(mesh_path, colors[i % len(colors)])
            valid_files += 1
        else:
            print(f"Warning: File not found: {mesh_path}")
    
    if valid_files == 0:
        print("Error: No valid mesh files provided")
        sys.exit(1)
        
    print(f"Loaded {valid_files} mesh file(s)")
    print("Controls:")
    print("  Left mouse button: Rotate view")
    print("  Right mouse button: Pan view")
    print("  Mouse wheel: Zoom in/out")
    print("  Ctrl + Left click: Pick point on mesh")
    print("  ESC: Exit")
    
    viewer.run()

if __name__ == "__main__":
    main()