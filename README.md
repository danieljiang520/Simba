<img width="128px" src="https://user-images.githubusercontent.com/71047773/162661459-faad6b31-1436-47cf-b861-96878cd25a2e.png" alt="Logo" align="left" />

# Simba

Simba is a graphical user interface tool for processing 3D kinect scan files. It can automatically remove background points from 3D Kinect scans, create watertight body shape surfaces, and visualize final noise-free meshes, providing data to generate realistic body shape and dimension predictions.

Simba works on macOS Mojave 10.14 or higher.

* [Features](#features)
* [Install](#install)
* [Usage](#usage)
* [Motivation](#motivation)
* [Missing Functions](#missing-functions)

## Features
* Native UI
* Remove background points from Kinect 3D scans
* Reconstruct watertight surfaces using the Poisson method
* Merge body shapes with seat scans automatically
* Skip projects that have been previously processed

## Install
Download the latest version from the [releases](https://github.com/danieljiang520/UMTRI_3D_Scan_Processing/releases) page.
<img width="1224" alt="Screen Shot 2022-01-30 at 17 50 34" src="https://user-images.githubusercontent.com/71047773/151721252-e802b988-ec4e-4679-8beb-d805aa64b88c.png">

## Usage
#### Input Folder
Simba checks all paths underneath the input directory that contain the following files
* At least 1 .ply file with the naming pattern scan_*.py
* At least 1 joint file obtained from the Kinect Scanner with the naming pattern joint_*.csv

#### Seat Merging Input File
* Any .ply file

## Motivation
In 2014, the Bioscience Group at the University of Michigan Transportation Research Institute (UMTRI) developed a body shape and dimensions measurement method that can generate watertight realistic body shape along with predicted joint locations and anthropometric variables from a 3D scan of an individual (Park et al. 2014). Although this method works with the noisy point cloud data, it requires high computational power and is error-prone due to the noise and unnecessary scan points. The purpose of the current study is to develop an intuitive graphical user interface software that (1) automatically removes background points, (2) creates watertight surface from oriented point sets using Poisson surface reconstruction method and (3) visualizes final noise-free meshes. Using results generated by the program will improve the fitting performance and the body shape and dimension predictions.

![Jiang_Daniel_UMTRI_GUI_Portfolio](https://user-images.githubusercontent.com/71047773/178681186-dea9a604-2174-489d-afd1-8cb19f41fbd6.jpg)

#### Objectives
* Create noise-free meshes to improve the fitting performance and the accuracy of the established body shape and dimensions measurement method
* Visualize results in 3D using a graphical user interface
* The user should be able to work through multiple projects one at
a time, and set custom configuration for individual meshes

When fitting a body shape model to a noisy point cloud to measure body dimensions, the fitting method needs to decide the most feasible target location for each vertex of the model, which is computationally quite expensive. This program generates noise-free body shape meshes from noisy point cloud data, which greatly reduce fitting time (from 10 sec to 1 sec) and increase the accuracy of the body shape and dimension predictions.

#### References
Park, B. K., Lumeng, J. C., Lumeng, C. N., Ebert, S. M., & Reed, M. P. (2014). Child body shape measurement using depth cameras and a statistical body shape model. Ergonomics, 58(2), 301–309. https://doi.org/10.1080/00140139.2014.965754

## Missing functions
- Help page
- Help icons
