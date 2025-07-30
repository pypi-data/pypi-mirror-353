import numpy as np
import struct

def load_stl(file_path):
    """
    Load an STL file and return vertices and normals
    """
    with open(file_path, 'rb') as f:
        header = f.read(80)
        
        # Check if binary STL
        if not header.startswith(b'solid'):
            # Binary STL
            num_triangles = struct.unpack('<I', f.read(4))[0]
            
            vertices = np.zeros((num_triangles * 3, 3), dtype=np.float32)
            normals = np.zeros((num_triangles * 3, 3), dtype=np.float32)
            
            for i in range(num_triangles):
                # Read normal
                nx, ny, nz = struct.unpack('<fff', f.read(12))
                
                # Read vertices
                for j in range(3):
                    vx, vy, vz = struct.unpack('<fff', f.read(12))
                    vertices[i * 3 + j] = [vx, vy, vz]
                    normals[i * 3 + j] = [nx, ny, nz]
                
                # Skip attribute byte count
                f.read(2)
            
            return vertices, normals
        else:
            # ASCII STL - use trimesh instead
            raise ValueError("ASCII STL detected. Please use trimesh for loading ASCII STL files.")