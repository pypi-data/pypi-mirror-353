# MeshViewer

A modern 3D mesh viewer built with ModernGL and GLFW for visualizing STL and OBJ files.

![MeshViewer](https://via.placeholder.com/800x450.png?text=MeshViewer+Screenshot)

## Features

- Load and visualize STL and OBJ 3D mesh files
- Interactive camera controls:
  - Left-click drag: Rotate view (arcball rotation)
  - Right-click drag: Pan view
  - Scroll wheel: Zoom in/out
  - Ctrl+Left-click: Pick point on mesh (prints coordinates to console)
- Shader-based rendering with proper lighting
- 3D axis visualization
- Support for multiple meshes with different colors

## Installation

### Prerequisites

- Python 3.8+
- OpenGL 3.3+ compatible graphics hardware and drivers

### Install from source

```bash
# Clone the repository
git clone https://github.com/yourusername/meshviewer.git
cd meshviewer

# Install the package and dependencies
pip install -e .
```

Or install directly using pip:

```bash
pip install meshviewer
```

## Usage

### Command Line

```bash
# View a single mesh file
meshviewer path/to/your/mesh.stl

# View multiple mesh files at once
meshviewer path/to/mesh1.stl path/to/mesh2.obj
```

### As a Python Module

```python
from meshviewer.viewer import MeshViewer

# Create a viewer instance
viewer = MeshViewer()

# Load one or more mesh files
viewer.load_mesh("path/to/mesh.stl", color=(0.7, 0.7, 0.7))
viewer.load_mesh("path/to/another_mesh.obj", color=(0.3, 0.6, 0.9))

# Start the viewer
viewer.run()
```

## Controls

- **Left Mouse Button**: Rotate the view
- **Right Mouse Button**: Pan the view
- **Mouse Wheel**: Zoom in/out
- **Ctrl + Left Click**: Pick a point on the mesh (coordinates printed to console)
- **ESC**: Exit the viewer

## Dependencies

- moderngl: OpenGL wrapper
- glfw: Window and input management
- numpy: Numerical operations
- pyglm: Math library for 3D operations
- trimesh: Mesh processing

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.