import numpy as np

def load_obj(file_path):
    """
    Load an OBJ file and return vertices, indices, and normals
    """
    vertices = []
    normals = []
    faces = []
    
    with open(file_path, 'r') as f:
        for line in f:
            if line.startswith('#'):
                continue
                
            values = line.split()
            if not values:
                continue
                
            if values[0] == 'v':
                vertices.append([float(x) for x in values[1:4]])
            elif values[0] == 'vn':
                normals.append([float(x) for x in values[1:4]])
            elif values[0] == 'f':
                # Handle different face formats
                face_vertices = []
                face_normals = []
                
                for v in values[1:]:
                    w = v.split('/')
                    # OBJ indices start at 1
                    face_vertices.append(int(w[0]) - 1)
                    if len(w) >= 3 and w[2]:
                        face_normals.append(int(w[2]) - 1)
                
                # Triangulate if needed (for faces with more than 3 vertices)
                for i in range(1, len(face_vertices) - 1):
                    faces.append([
                        face_vertices[0],
                        face_vertices[i],
                        face_vertices[i + 1]
                    ])
    
    vertices = np.array(vertices, dtype=np.float32)
    
    # If no normals in file, calculate them
    if not normals:
        normals = np.zeros_like(vertices)
        
    # Convert faces to numpy array
    indices = np.array(faces, dtype=np.int32).flatten()
    
    # Map normals to vertices
    vertex_normals = np.zeros_like(vertices)
    if normals:
        normals = np.array(normals, dtype=np.float32)
        for i, face in enumerate(faces):
            for j, vertex_idx in enumerate(face):
                vertex_normals[vertex_idx] += normals[face[j]]
    
    # Normalize vertex normals
    lengths = np.sqrt(np.sum(vertex_normals**2, axis=1))
    non_zero = lengths > 0
    vertex_normals[non_zero] = vertex_normals[non_zero] / lengths[non_zero, np.newaxis]
    
    return vertices, indices, vertex_normals