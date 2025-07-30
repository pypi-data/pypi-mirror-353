import glm

class Camera:
    """Simple orbit camera supporting panning, rotating and zooming."""

    def __init__(self, width: int, height: int) -> None:
        self.aspect = width / height
        self.fov = 45.0
        self.near = 0.1
        self.far = 10000.0

        # Orbit camera parameters
        self.target = glm.vec3(0.0, 0.0, 0.0)
        self.distance = 200.0
        self.yaw = -135.0
        self.pitch = 35.264

        # Internal state for mouse interaction
        self._last_x = width / 2
        self._last_y = height / 2
        self._first_mouse = True

        self._update_vectors()

    @property
    def position(self) -> glm.vec3:
        return self.target - self.front * self.distance

    def set_viewport(self, width: int, height: int) -> None:
        self.aspect = width / height

    def get_view_matrix(self) -> glm.mat4:
        return glm.lookAt(self.position, self.target, self.up)

    def get_projection_matrix(self) -> glm.mat4:
        return glm.perspective(glm.radians(self.fov), self.aspect, self.near, self.far)

    def orbit(self, xpos: float, ypos: float, sensitivity: float = 0.3) -> None:
        """Rotate the camera around the target based on mouse movement."""
        if self._first_mouse:
            self._last_x = xpos
            self._last_y = ypos
            self._first_mouse = False

        xoffset = xpos - self._last_x
        yoffset = ypos - self._last_y

        self._last_x = xpos
        self._last_y = ypos

        self.yaw += xoffset * sensitivity
        self.pitch -= yoffset * sensitivity

        self.pitch = max(-89.0, min(89.0, self.pitch))
        self._update_vectors()

    def pan(self, dx: float, dy: float) -> None:
        """Pan the camera target in screen space."""
        factor = self.distance * 0.002
        offset = (-self.right * dx + self.up * dy) * factor
        self.target += offset
        self._update_vectors()

    def zoom(self, amount: float, ray: glm.vec3 | None = None) -> None:
        """Zoom the camera. If a ray is provided, zoom towards that ray."""
        if amount == 0.0:
            return

        plane_point = glm.vec3(self.target)
        plane_normal = glm.vec3(self.front)

        hit_before = None
        if ray is not None:
            denom = glm.dot(ray, plane_normal)
            if abs(denom) > 1e-6:
                t = glm.dot(plane_point - self.position, plane_normal) / denom
                hit_before = self.position + ray * t

        self.distance *= 1.0 - amount * 0.1
        self.distance = max(0.1, self.distance)
        self._update_vectors()

        if hit_before is not None:
            denom = glm.dot(ray, plane_normal)
            if abs(denom) > 1e-6:
                t = glm.dot(plane_point - self.position, plane_normal) / denom
                hit_after = self.position + ray * t
                offset = hit_before - hit_after
                self.target += offset
                self._update_vectors()

    def screen_ray(self, x: float, y: float, width: int, height: int) -> glm.vec3:
        """Return a world space ray starting from the camera through screen coords."""
        viewport = glm.vec4(0, 0, width, height)
        p1 = glm.unProject(glm.vec3(x, height - y, 0.0), self.get_view_matrix(), self.get_projection_matrix(), viewport)
        p2 = glm.unProject(glm.vec3(x, height - y, 1.0), self.get_view_matrix(), self.get_projection_matrix(), viewport)
        return glm.normalize(p2 - p1)

    def _update_vectors(self) -> None:
        front = glm.vec3(
            glm.cos(glm.radians(self.yaw)) * glm.cos(glm.radians(self.pitch)),
            glm.sin(glm.radians(self.pitch)),
            glm.sin(glm.radians(self.yaw)) * glm.cos(glm.radians(self.pitch)),
        )
        self.front = glm.normalize(front)
        self.right = glm.normalize(glm.cross(self.front, glm.vec3(0.0, 1.0, 0.0)))
        self.up = glm.normalize(glm.cross(self.right, self.front))