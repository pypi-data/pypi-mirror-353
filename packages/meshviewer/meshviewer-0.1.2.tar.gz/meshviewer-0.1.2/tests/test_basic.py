import unittest
import os
import sys

# Add parent directory to path to import meshviewer
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from meshviewer.viewer import MeshViewer

class TestMeshViewer(unittest.TestCase):
    """Basic tests for MeshViewer functionality"""
    
    def test_initialization(self):
        """Test that MeshViewer can be initialized without errors"""
        try:
            # This will be skipped if GLFW can't initialize (e.g., in CI environments)
            import glfw
            if glfw.init():
                viewer = MeshViewer()
                self.assertIsNotNone(viewer)
                glfw.terminate()
            else:
                self.skipTest("GLFW initialization failed, skipping test")
        except ImportError:
            self.skipTest("GLFW not available, skipping test")

if __name__ == '__main__':
    unittest.main()