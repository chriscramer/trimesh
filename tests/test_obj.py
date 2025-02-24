try:
    from . import generic as g
except BaseException:
    import generic as g


class OBJTest(g.unittest.TestCase):

    def test_rabbit(self):
        # A BSD-licensed test model from pyglet
        # it has mixed triangles, quads, and 16 element faces -_-
        # this should test the non-vectorized load path
        m = g.get_mesh('rabbit.obj')
        assert len(m.faces) == 1252
        rec = g.wrapload(
            m.export(file_type='obj'), file_type='obj')
        assert g.np.isclose(m.area, rec.area)

    def test_no_img(self):
        # sometimes people use the `vt` parameter for arbitrary
        # vertex attributes and thus want UV coordinates even
        # if there is no texture image
        m = g.get_mesh('noimg.obj')
        assert m.visual.uv.shape == (len(m.vertices), 2)
        # make sure UV coordinates are in range 0.0 - 1.0
        assert m.visual.uv.max() < (1 + 1e-5)
        assert m.visual.uv.min() > -1e-5
        # check to make sure it's not all zeros
        assert m.visual.uv.ptp() > 0.5
        rec = g.wrapload(
            m.export(file_type='obj'), file_type='obj')
        assert g.np.isclose(m.area, rec.area)

    def test_trailing(self):
        # test files with texture and trailing slashes
        m = g.get_mesh('jacked.obj')
        assert len(m.visual.uv) == len(m.vertices)
        rec = g.wrapload(
            m.export(file_type='obj'), file_type='obj')
        assert g.np.isclose(m.area, rec.area)

    def test_obj_groups(self):
        # a wavefront file with groups defined
        mesh = g.get_mesh('groups.obj')

        # make sure some data got loaded
        assert g.trimesh.util.is_shape(mesh.faces, (-1, 3))
        assert g.trimesh.util.is_shape(mesh.vertices, (-1, 3))

        # make sure groups are the right length
        # TODO: we do not support face groups now
        # assert len(mesh.metadata['face_groups']) == len(mesh.faces)

        # check to make sure there is signal not just zeros
        # assert mesh.metadata['face_groups'].ptp() > 0

    def test_obj_negative_indices(self):
        # a wavefront file with negative indices
        mesh = g.get_mesh('negative_indices.obj')

        # make sure some data got loaded
        assert g.trimesh.util.is_shape(mesh.faces, (12, 3))
        assert g.trimesh.util.is_shape(mesh.vertices, (8, 3))

    def test_obj_quad(self):
        mesh = g.get_mesh('quadknot.obj')
        # make sure some data got loaded
        assert g.trimesh.util.is_shape(mesh.faces, (-1, 3))
        assert g.trimesh.util.is_shape(mesh.vertices, (-1, 3))

        assert mesh.is_watertight
        assert mesh.is_winding_consistent
        rec = g.wrapload(
            mesh.export(file_type='obj'), file_type='obj')
        assert g.np.isclose(mesh.area, rec.area)

    def test_obj_multiobj(self):
        # test a wavefront file with multiple objects in the same file
        scene = g.get_mesh('two_objects.obj',
                           split_object=True,
                           group_material=False)
        assert len(scene.geometry) == 2

        for mesh in scene.geometry.values():
            # make sure some data got loaded
            assert g.trimesh.util.is_shape(mesh.faces, (-1, 3))
            assert g.trimesh.util.is_shape(mesh.vertices, (-1, 3))

            assert mesh.is_watertight
            assert mesh.is_winding_consistent

    def test_obj_split_attributes(self):
        # test a wavefront file where pos/uv/norm have different indices
        # and where multiple objects share vertices
        # Note 'process=False' to avoid merging vertices
        scene = g.get_mesh('joined_tetrahedra.obj',
                           process=False,
                           split_object=True,
                           group_material=False)

        assert len(scene.geometry) == 2

        geom = list(scene.geometry.values())

        assert g.trimesh.util.is_shape(geom[0].faces, (4, 3))
        assert g.trimesh.util.is_shape(geom[0].vertices, (9, 3))
        assert g.trimesh.util.is_shape(geom[1].faces, (4, 3))
        assert g.trimesh.util.is_shape(geom[1].vertices, (9, 3))

    def test_obj_simple_order(self):

        # test a simple wavefront model without split indexes
        # and make sure we don't reorder vertices unnecessarily
        file_name = g.os.path.join(g.dir_models, 'cube.OBJ')
        # load a simple OBJ file without merging vertices
        m = g.trimesh.load(file_name, process=False)
        # use trivial loading to compare with fancy performant one
        with open(file_name, 'r') as f:
            f, v, vt = simple_load(f.read())
        # trimesh loader should return the same face order
        assert g.np.allclose(f, m.faces)
        assert g.np.allclose(v, m.vertices)

    def test_order_tex(self):

        # test a simple wavefront model without split indexes
        # and make sure we don't reorder vertices unnecessarily
        file_name = g.os.path.join(g.dir_models, 'fuze.obj')
        # load a simple OBJ file without merging vertices
        m = g.trimesh.load(
            file_name,
            process=False,
            maintain_order=True)
        # use trivial loading to compare with fancy performant one
        with open(file_name, 'r') as f:
            f, v, vt = simple_load(f.read())
        # trimesh loader should return the same face order
        assert g.np.allclose(f, m.faces)
        assert g.np.allclose(v, m.vertices)

    def test_obj_compressed(self):
        mesh = g.get_mesh('cube_compressed.obj', process=False)
        assert g.np.allclose(
            g.np.abs(mesh.vertex_normals).sum(axis=1), 1.0)

    def test_vertex_color(self):
        # get a box mesh
        mesh = g.trimesh.creation.box()
        # set each vertex to a unique random color
        mesh.visual.vertex_colors = [
            g.trimesh.visual.random_color()
            for _ in range(len(mesh.vertices))]
        # export and then reload the file as OBJ
        rec = g.trimesh.load(
            g.trimesh.util.wrap_as_stream(
                mesh.export(file_type='obj')),
            file_type='obj')
        # assert colors have survived the export cycle
        assert (mesh.visual.vertex_colors ==
                rec.visual.vertex_colors).all()

    def test_single_vn(self):
        """
        Make sure files with a single VN load.
        """
        m = g.get_mesh('singlevn.obj')
        assert len(m.vertices) > 0
        assert len(m.faces) > 0

    def test_polygon_faces(self):
        m = g.get_mesh('polygonfaces.obj')
        assert len(m.vertices) > 0
        assert len(m.faces) > 0

    def test_faces_not_enough_indices(self):
        m = g.get_mesh('notenoughindices.obj')
        assert len(m.vertices) > 0
        assert len(m.faces) == 1

    def test_export_path(self):
        m = g.get_mesh('fuze.obj')
        g.check_fuze(m)
        with g.TemporaryDirectory() as d:
            file_path = g.os.path.join(d, 'fz.obj')
            m.export(file_path)

            r = g.trimesh.load(file_path)
            g.check_fuze(r)

    def test_mtl(self):
        # get a mesh with texture
        m = g.get_mesh('fuze.obj')
        # export the mesh including data
        obj, data = g.trimesh.exchange.export.export_obj(
            m, return_texture=True)
        with g.trimesh.util.TemporaryDirectory() as path:
            # where is the OBJ file going to be saved
            obj_path = g.os.path.join(path, 'test.obj')
            with open(obj_path, 'w') as f:
                f.write(obj)
            # save the MTL and images
            for k, v in data.items():
                with open(g.os.path.join(path, k), 'wb') as f:
                    f.write(v)
            # reload the mesh from the export
            rec = g.trimesh.load(obj_path)
        # make sure loaded image is the same size as the original
        assert (rec.visual.material.image.size ==
                m.visual.material.image.size)
        # make sure the faces are the same size
        assert rec.faces.shape == m.faces.shape

    def test_scene(self):
        s = g.get_mesh('cycloidal.3DXML')

        e = g.trimesh.load(
            g.io_wrap(s.export(file_type='obj')),
            file_type='obj',
            split_object=True,
            group_materials=False)

        assert g.np.isclose(e.area, s.area, rtol=.01)

    def test_edge_cases(self):
        # a mesh with some NaN colors
        n = g.get_mesh('nancolor.obj')
        assert n.faces.shape == (12, 3)

        v = g.get_mesh('cubevt.obj')
        assert v.faces.shape == (12, 3)

    def test_empty_or_pointcloud(self):
        # demo files to check
        empty_files = ['obj_empty.obj',
                       'obj_points.obj',
                       'obj_wireframe.obj']

        for empty_file in empty_files:
            e = g.get_mesh('emptyIO/' + empty_file)

            # create export
            if 'empty' in empty_file:
                try:
                    export = e.export(file_type='ply')
                except BaseException:
                    continue
                raise ValueError('cannot export empty')
            elif 'points' in empty_file:
                export = e.export(file_type='ply')
                reconstructed = g.wrapload(export, file_type='ply')

                # result should be a point cloud instance
                assert isinstance(e, g.trimesh.PointCloud)
                assert hasattr(e, 'vertices')
                # point cloud export should contain vertices
                assert isinstance(reconstructed, g.trimesh.PointCloud)
                assert hasattr(reconstructed, 'vertices')

    def test_backslash_continuation_character(self):
        # an obj file with \ (backslash) line continuation characters
        m = g.get_mesh('wallhole.obj')
        assert m.faces.shape == (66, 3)

    def test_no_uv(self):
        mesh = g.get_mesh('box.obj')
        rec = g.wrapload(
            mesh.export(file_type='obj'), file_type='obj')
        assert g.np.isclose(mesh.area, rec.area)

    def test_no_uv_but_mtl(self):
        sphere = g.trimesh.creation.uv_sphere()
        sphere.visual = g.trimesh.visual.TextureVisuals(
            uv=None,
            material=g.trimesh.visual.material.empty_material())
        output = sphere.export('sphere.obj')
        assert 'usemtl' in output

    def test_chair(self):
        mesh = next(iter(g.get_mesh('chair.zip').geometry.values()))

        # this model comes with vertex normals
        assert 'vertex_normals' in mesh._cache
        assert g.np.allclose(
            1.0, g.np.linalg.norm(mesh.vertex_normals, axis=1))
        mesh.apply_scale(0.46377314288075433)
        assert 'vertex_normals' in mesh._cache
        assert g.np.allclose(
            1.0, g.np.linalg.norm(mesh.vertex_normals, axis=1))
        assert 'vertex_normals' in mesh._cache
        mesh._cache.clear()
        assert 'vertex_normals' not in mesh._cache
        # if we recomputed now, the degenerate faces
        # would lead some of these vertex normals to be zero
        # assert g.np.allclose(
        #    1.0, g.np.linalg.norm(mesh.vertex_normals, axis=1))


def simple_load(text):
    # we're going to load faces in a basic text way
    # and compare the order from this method to the
    # trimesh loader, to see if we get the same thing
    f = []
    v = []
    vt = []
    for line in str.splitlines(text):
        line = line.strip()
        if len(line) < 2:
            continue
        elif line.startswith('f '):
            if '/' in line:
                f.append([int(i.split('/', 1)[0])
                          for i in line[1:].strip().split()])
            else:
                f.append(line[1:].strip().split())
        elif line.startswith('v '):
            v.append(line[1:].strip().split())
        elif line.startswith('vt '):
            vt.append(line[2:].strip().split())

    # get faces as basic numpy array
    f = g.np.array(f, dtype=g.np.int64) - 1
    v = g.np.array(v, dtype=g.np.float64)
    vt = g.np.array(vt, dtype=g.np.float64)

    return f, v, vt


if __name__ == '__main__':
    g.trimesh.util.attach_to_log()
    g.unittest.main()
