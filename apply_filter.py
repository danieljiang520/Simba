import os, pymeshlab, glob, time, pathlib, argparse
import numpy as np
import pandas as pd
    
def load_joint_points(subdir):
    # get filepaths for each of the joint file
    filepaths = glob.glob(os.path.join(subdir, "joints_*.csv"))  
    # combine the three files into one dataframe
    df_from_each_file = (pd.read_csv(f, header=None) for f in filepaths)
    concatenated_df = pd.concat(df_from_each_file, ignore_index=True)
    print("Joint points loaded successfully")
    # return a numpy array
    return concatenated_df.to_numpy()

def load_meshes(subdir):
    # create a new MeshSet
    ms = pymeshlab.MeshSet()
    # load meshes
    filepaths = glob.glob(os.path.join(subdir, "scan_*.ply"))  
    for filepath in filepaths:
        ms.load_new_mesh(filepath)
    # flatten visible layers - combine all meshes
    ms.flatten_visible_layers(alsounreferenced = True)
    print("Scan meshes loaded successfully")
    # return MeshSet
    return ms

def remove_background(joint_arr, ms, radius):
    # get a reference to the current mesh
    # store the scan mesh id and number of vertices for the hausdorff function
    m = ms.current_mesh()
    scan_mesh_id = ms.current_mesh_id()
    sample_num = m.vertex_number()
    print(f'Total vertices: {m.vertex_number()}')

    # create a new mesh with the joint points
    m = pymeshlab.Mesh(vertex_matrix = joint_arr)
    ms.add_mesh(m)
    joint_mesh_id = ms.current_mesh_id()

    # set current mesh back to the scan mesh
    ms.set_current_mesh(scan_mesh_id)
    m = ms.current_mesh()
    # Hausdorff Distance filter will store into the "quality" for each vertex of A the distance from the closest vertex of B; 
    # then use the conditional selection filter by testing against quality to remove background vertices.
    ms.hausdorff_distance(sampledmesh = scan_mesh_id, targetmesh = joint_mesh_id, samplenum = sample_num, maxdist = radius)
    ms.conditional_vertex_selection(condselect = f"(q >= {radius})")
    ms.delete_selected_vertices()
    print(f'Keeping {m.vertex_number()} vertices')

def export_mesh(subdir, ms, p):
    # compute normals for the points. use smooth iteration number 2.
    ms.compute_normals_for_point_sets(smoothiter = p.smoothiter)
    # reconstruct points as a surface using the Poisson method. use default parameters for now. 
    ms.surface_reconstruction_screened_poisson()

    # print out default value for 'select_faces_with_edges_longer_than' function
    default_params = ms.filter_parameter_values('select_faces_with_edges_longer_than')
    print(f"Default threshold: {default_params['threshold']}")

    # select interpolated faces. use 15 mm as a selection criterion.
    ms.select_faces_with_edges_longer_than(threshold = p.edgeLength)
    ms.delete_selected_faces()
    ms.remove_unreferenced_vertices()

    # save mesh
    basename = os.path.split(os.path.split(subdir)[0])[1] # extract second last directory name
    complete_name = os.path.join(p.output, basename + '_processed.ply')
    ms.save_current_mesh(complete_name)
    ms.clear()
    print("Saved!")

def walk_folder(p):
    process_time_sum = .0 # process time for each scan
    processed_scans_num = 0 # total number of processed scans
    pathlib.Path(p.output).mkdir(exist_ok=True) # create output directory if it doesn't exist
    for subdir, dirs, files in os.walk(p.input):
        filepath = os.path.join(subdir, 'scan_0.ply')
        if os.path.isfile(filepath):
            tic = time.perf_counter()
            print(subdir)
            try:
                # load joint ponts to a numpy array
                joint_arr = load_joint_points(subdir)
            except ValueError:
                # skip file if joint_arr is empty
                print("No joint points! Skipped.\n")
                continue
            # create a meshset with a single mesh that has been flattened
            ms = load_meshes(subdir)
            # remove background vertices
            remove_background(joint_arr, ms, p.radius)
            # apply filters and save mesh
            export_mesh(subdir, ms, p)

            toc = time.perf_counter()
            print(f"Process time = {toc - tic:0.4f} seconds\n")
            processed_scans_num = processed_scans_num + 1
            process_time_sum = process_time_sum + toc - tic
    
    print(f"Number of processed scans = {processed_scans_num:0.4f} seconds\n")
    print(f"Avg process time = {process_time_sum/processed_scans_num:0.4f} seconds\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', default = os.getcwd(),
                    help='Path to the input directory. Default: current working directory')
    parser.add_argument('--output', default = os.path.join(os.getcwd(),'Results_SAS_Mesh'),
                    help='Path to the output directory. Default: a folder called Result_SAS_Mesh in the current working directory')
    parser.add_argument('--radius', default=400, type=float,
                    help='Vertices within radius (mm) from joint points are kept. Default: 400')
    parser.add_argument('--smoothiter', default=2, type=int,
                    help='The number of smoothing iteration done on the point used to estimate and propagate normals. Default: 2')
    parser.add_argument('--edgeLength', default=15, type=float,
                    help='All the faces with an edge longer than this threshold will be deleted. Default: 15')
    p = parser.parse_args()
    walk_folder(p)
    print("Done!")