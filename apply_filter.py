import os, pymeshlab, glob, time, pathlib
import numpy as np
import pandas as pd
class ApplyFilter:
    def __init__(self, inputPath, outputPath, config):
        self.inputPath = inputPath
        self.outputPath = os.path.join(outputPath,'Results_SAS_Mesh')
        self.config = config

    def load_joint_points(self, subdir):
        # get filepaths for each of the joint file
        filepaths = glob.glob(os.path.join(subdir, "joints_*.csv"))  
        # combine the three files into one dataframe
        df_from_each_file = (pd.read_csv(f, header=None) for f in filepaths)
        concatenated_df = pd.concat(df_from_each_file, ignore_index=True)
        print("Joint points loaded successfully")
        # return a numpy array
        return concatenated_df.to_numpy()

    def load_meshes(self, subdir):
        # create a new MeshSet
        self.ms = pymeshlab.MeshSet()
        # load meshes
        filepaths = glob.glob(os.path.join(subdir, "scan_*.ply"))  
        for filepath in filepaths:
            self.ms.load_new_mesh(filepath)
        # flatten visible layers - combine all meshes
        self.ms.flatten_visible_layers(alsounreferenced = True)
        print("Scan meshes loaded successfully")

    def remove_background(self, joint_arr):
        # get a reference to the current mesh
        # store the scan mesh id and number of vertices for the hausdorff function
        m = self.ms.current_mesh()
        scan_mesh_id = self.ms.current_mesh_id()
        sample_num = m.vertex_number()
        print(f'Total vertices: {m.vertex_number()}')

        # create a new mesh with the joint points
        m = pymeshlab.Mesh(vertex_matrix = joint_arr)
        self.ms.add_mesh(m)
        joint_mesh_id = self.ms.current_mesh_id()

        # set current mesh back to the scan mesh
        self.ms.set_current_mesh(scan_mesh_id)
        m = self.ms.current_mesh()
        # Hausdorff Distance filter will store into the "quality" for each vertex of A the distance from the closest vertex of B; 
        # then use the conditional selection filter by testing against quality to remove background vertices.
        self.ms.hausdorff_distance(sampledmesh = scan_mesh_id, targetmesh = joint_mesh_id, samplenum = sample_num, maxdist = self.config['radius'])
        self.ms.conditional_vertex_selection(condselect = f"(q >= {self.config['radius']})")
        self.ms.delete_selected_vertices()
        print(f'Keeping {m.vertex_number()} vertices')

    def export_mesh(self, subdir):
        # compute normals for the points. use smooth iteration number 2.
        self.ms.compute_normals_for_point_sets(smoothiter = self.config['smoothiter'])
        # reconstruct points as a surface using the Poisson method. use default parameters for now. 
        self.ms.surface_reconstruction_screened_poisson()

        # print out default value for 'select_faces_with_edges_longer_than' function
        default_params = self.ms.filter_parameter_values('select_faces_with_edges_longer_than')
        print(f"Default threshold: {default_params['threshold']}")

        # select interpolated faces. use 15 mm as a selection criterion.
        self.ms.select_faces_with_edges_longer_than(threshold = self.config['edgeLength'])
        self.ms.delete_selected_faces()
        self.ms.remove_unreferenced_vertices()

        # save mesh
        basename = os.path.basename(os.path.normpath(subdir)) # extract last directory name
        complete_name = os.path.join(self.outputPath, basename + '_processed.ply')
        self.ms.save_current_mesh(complete_name)
        self.ms.clear()
        print("Saved!")

    def start(self):
        process_time_sum = .0 # process time for each scan
        processed_scans_num = 0 # total number of processed scans
        pathlib.Path(self.outputPath).mkdir(exist_ok=True) # create output directory if it doesn't exist
        for subdir, dirs, files in os.walk(self.inputPath):
            filepath = os.path.join(subdir, 'scan_0.ply')
            if os.path.isfile(filepath):
                tic = time.perf_counter()
                print(subdir)
                try:
                    # load joint ponts to a numpy array
                    joint_arr = self.load_joint_points(subdir)
                except ValueError:
                    # skip file if joint_arr is empty
                    print("No joint points! Skipped.\n")
                    continue
                # create a meshset with a single mesh that has been flattened
                self.load_meshes(subdir)
                # remove background vertices
                self.remove_background(joint_arr)
                # apply filters and save mesh
                self.export_mesh(subdir)

                toc = time.perf_counter()
                print(f"Process time = {toc - tic:0.4f} seconds\n")
                processed_scans_num = processed_scans_num + 1
                process_time_sum = process_time_sum + toc - tic

        print(f"Number of processed scans = {processed_scans_num}\n")
        try:
            averageProcessTime = process_time_sum/processed_scans_num
        except ZeroDivisionError:
            averageProcessTime = 0
        print(f"Avg process time = {averageProcessTime:0.4f} seconds\n")
