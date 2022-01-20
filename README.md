## Simba
Simba is a graphical user interface tool for processing 3D kinect scan files. It can automatically remove background points from 3D scans, create watertight body shape surfaces, and visualize final noise-free meshes, providing data to generate realistic body shape and dimension predictions. 

## Install
Download the latest version from the [releases](https://github.com/danieljiang520/UMTRI_3D_Scan_Processing/releases) page.

## Mac Setup - for Working on the Project
1. Open terminal and locate a folder where you want to store the files. For example, type ```cd Documents```.
![Screen Shot 2021-10-08 at 10 02 53](https://user-images.githubusercontent.com/71047773/136570679-fb029f7a-6c15-49b9-aed7-663cd9e4f6c6.png)
2. Clone the Files ```git clone https://github.com/danieljiang520/UMTRI_3D_Scan_Processing.git```
4. Install required libraries: 
```
pip install pymeshlab
pip install numpy
pip install pandas
pip install pyqt5
pip install pyqt5-tools
pip install vtk
```
# To run the code
1. Open terminal and locate a folder where you stored the files for the application in Mac Setup Step 1. For example, type ```cd Documents```.
2. Type ```ls``` in the terminal to see the children directories of the current folder
3. Type ```cd UMTRI_3D_Scan_Processing```
4. Run the code: type ```python3 main.py```
5. You should see this window
![Screen Shot 2021-10-08 at 10 09 14](https://user-images.githubusercontent.com/71047773/136571692-2f0d567a-9927-4147-8fff-16169e12e52c.png)
6. Click on the monitor icon to open activity monitor

## Missing functions
- Help page
- Help icons
