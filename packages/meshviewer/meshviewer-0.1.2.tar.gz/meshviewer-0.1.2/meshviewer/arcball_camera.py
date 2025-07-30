import glm
import numpy as np

class ArcballCamera:
    """
    Arcball-style camera using quaternion rotation for smooth object-centric control.
    Supports left-drag for rotation, right-drag for pan, and scroll for zoom.
    """

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.center = glm.vec3(0.0, 0.0, 0.0)
        self.zoom = 2.5

        rot_x = glm.angleAxis(glm.radians(-35.264), glm.vec3(1, 0, 0))
        rot_y = glm.angleAxis(glm.radians(45.0), glm.vec3(0, 1, 0))
        self.rotation = rot_y * rot_x
        self._last = None
        self._view_dirty = True
        self._view = glm.mat4(1.0)
        self._projection = glm.mat4(1.0)

        self.set_viewport(width, height)

    def set_viewport(self, width, height):
        self.width = width
        self.height = height
        aspect = width / height
        self._projection = glm.perspective(glm.radians(45.0), aspect, 0.01, 10000.0)

    def _screen_to_arcball(self, x, y):
        px = (2.0 * x - self.width) / self.width
        py = (self.height - 2.0 * y) / self.height
        d = px * px + py * py
        if d > 1.0:
            v = glm.normalize(glm.vec3(px, py, 0.0))
        else:
            z = np.sqrt(1.0 - d)
            v = glm.vec3(px, py, z)
        return glm.normalize(v)

    def begin_drag(self, x, y):
        # print("Begin drag")
        self._last = self._screen_to_arcball(x, y)

    def drag(self, x, y):
        if self._last is None:
            return

        curr = self._screen_to_arcball(x, y)
        dot = glm.dot(self._last, curr)
        dot = np.clip(dot, -1.0, 1.0)

        # print(f"Dragging - curr: {curr}, last: {self._last}, dot: {dot}")

        if dot < 0.999999:
            axis = glm.cross(self._last, curr)
            angle = np.arccos(dot) * 1.5

            if angle < 1e-4:
                angle = 1e-4

            if glm.length(axis) > 1e-6:
                rot_quat = glm.angleAxis(-angle, glm.normalize(axis))
                self.rotation = self.rotation * rot_quat 
                self._view_dirty = True

                # print(f"Arcball Rotation - angle: {angle:.4f}, axis: {axis}")
                # print(f"Updated quaternion: {self.rotation}")

        self._last = curr

    def end_drag(self):
        # print("End drag")
        self._last = None

    def zoom_delta(self, delta):
        self.zoom *= 1.0 - delta * 0.1
        self.zoom = max(0.1, min(self.zoom, 1000.0))
        self._view_dirty = True
        print(f"Zoom updated to: {self.zoom}")

    def get_view_matrix(self):
        if self._view_dirty:
            eye = glm.vec3(0.0, 0.0, self.zoom)
            rot_mat = glm.mat4_cast(self.rotation)
            eye = glm.vec3(rot_mat * glm.vec4(eye, 1.0))
            up = glm.vec3(rot_mat * glm.vec4(0, 1, 0, 0))
            self._view = glm.lookAt(eye + self.center, self.center, up)
            self._view_dirty = False
            # print(f"View matrix recomputed.")
        return self._view

    def get_projection_matrix(self):
        return self._projection

    @property
    def position(self):
        eye = glm.vec3(0.0, 0.0, self.zoom)
        rot_mat = glm.mat4_cast(self.rotation)
        eye = glm.vec3(rot_mat * glm.vec4(eye, 1.0))
        return eye + self.center


    def zoom_towards_cursor(self, amount: float, ray: glm.vec3):
        """Zoom towards point under the mouse cursor using a screen ray."""
        if amount == 0.0:
            return

        plane_point = glm.vec3(self.center)
        plane_normal = self.view_direction()

        denom = glm.dot(ray, plane_normal)
        if abs(denom) < 1e-6:
            return  # ray nearly parallel to view plane

        hit_before = self.position - ray * glm.dot(self.position - plane_point, plane_normal) / denom

        self.zoom *= 1.0 - amount * 0.1
        self.zoom = max(0.1, min(self.zoom, 1000.0))
        self._view_dirty = True

        # Recalculate hit point after zoom
        denom = glm.dot(ray, plane_normal)
        if abs(denom) < 1e-6:
            return
        hit_after = self.position - ray * glm.dot(self.position - plane_point, plane_normal) / denom

        offset = hit_before - hit_after
        self.center += offset
        self._view_dirty = True


    def view_direction(self) -> glm.vec3:
        view = self.get_view_matrix()
        inv_view = glm.inverse(view)
        eye = glm.vec3(inv_view[3])
        forward = glm.normalize(self.center - eye)
        return forward


    def pan(self, dx: float, dy: float):
        factor = self.zoom * 0.002
        rot_mat = glm.mat4_cast(self.rotation)
        right = glm.vec3(rot_mat * glm.vec4(1, 0, 0, 0))
        up = glm.vec3(rot_mat * glm.vec4(0, 1, 0, 0))
        self.center += -right * dx * factor + up * dy * factor
        self._view_dirty = True
        print(f"Pan - center updated to: {self.center}")

    def screen_ray(self, x: float, y: float, width: int, height: int) -> glm.vec3:
        view = self.get_view_matrix()
        proj = self.get_projection_matrix()
        viewport = glm.vec4(0, 0, width, height)

        p0 = glm.unProject(glm.vec3(x, height - y, 0.0), view, proj, viewport)
        p1 = glm.unProject(glm.vec3(x, height - y, 1.0), view, proj, viewport)
        return glm.normalize(p1 - p0)
