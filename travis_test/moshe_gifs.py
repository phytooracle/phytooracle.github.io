import pandas as pd
import open3d as o3d
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import os
import bs4
import shutil

def getIndexes(dfObj, value):
    ''' Get index positions of value in dataframe i.e. dfObj.'''
    listOfPos = list()
    # Get bool dataframe with True at positions where the given value exists
    result = dfObj.isin([value])
    # Get list of columns that contains the value
    seriesObj = result.any()
    columnNames = list(seriesObj[seriesObj == True].index)
    # Iterate over list of columns and fetch the rows indexes where value exists
    for col in columnNames:
        rows = list(result[col][result[col] == True].index)
        for row in rows:
            listOfPos.append((row, col))
    # Return a list of tuples indicating the positions of value in the dataframe
    return listOfPos

root_list = []
# for (root, dirs, file) in os.walk('/home/travis/data/season_10/last_day_100_test_moshe'):
#     if 'combined_mulltiway_registered.npy' in file:
#         root_list.append(str(root))

import glob

root_list = glob.glob('/home/travis/data/season_10/last_day_100_test_moshe/*')

pcd_filepaths = []
numpy_filepaths = []
for root in root_list:
    pcd_filepaths.append(str(root + '/combined_multiway_registered.ply'))
    numpy_filepaths.append(str(root + '/combined_multiway_registered.npy'))
pcd_filepaths.sort()
numpy_filepaths.sort()

def generate_date(path):
    file_name = os.path.basename(os.path.dirname(os.path.dirname(path)))
    date = file_name.split('_')[2]
    return date

def generate_pointcloud_ID(pcd_path, array_path):
    plant_id = os.path.basename(os.path.dirname(pcd_path))
    plant_id_split = plant_id.rsplit('_', 1) 
    plant_genotype = plant_id_split[0]
    plant_number = plant_id_split[1]
    # date = generate_date(pcd_path)
    # date_split = date.split('-')
    # year = date_split[2]
    # month = date_split[0]
    # day = date_split[1]
    # date_reordered = str(year + '-' + month + '-' + day)
    return [plant_genotype, plant_number, pcd_path, array_path]

path_list = [generate_pointcloud_ID(i,j) for i,j in zip(pcd_filepaths, numpy_filepaths)]

paths_DF = pd.DataFrame(path_list)
paths_DF.columns = ['Genotype', 'Plant Number', 'PCD Filepath', 'Array Filepath']

import random

# change n to whatever number of images you'd like to return

n = 50
desired_pointclouds_row_numbers = []

for i in range(n):
    desired_pointclouds_row_numbers.append(random.randint(0, len(paths_DF)))

desired_pcd_paths_list = []
desired_array_paths_list = []
for number in desired_pointclouds_row_numbers:
    desired_pcd_paths_list.append(paths_DF.iloc[number]['PCD Filepath'])
    desired_array_paths_list.append(paths_DF.iloc[number]['Array Filepath'])

def convert_plant_ground_assignment_to_color_array(array):
    color_list = []
    for i in array:
        if i == 1:
            color_list.append([0.227450980392, 0.133333333333, 0.133333333333])
        else:
            color_list.append([0.509803921569, 1, 0])
    return np.asarray(color_list)

def generate_pointcloud_array_from_path(pcd_path, array_path):
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(np.asarray(o3d.io.read_point_cloud(pcd_path).points))
    read_array = np.load(array_path)
    total_array = np.c_[np.asarray(pcd.points), read_array]
    return total_array

def generate_rotating_gif(array, gif_save_path, n_points=None, force_overwrite=False, scan_number=None):

    fig = plt.figure(figsize=(9,9))
    ax = fig.add_subplot(111, projection='3d')
    x = array[:,0]
    y = array[:,1]
    z = array[:,2]
    c = array[:,3]
    cmap = 'Greens'
    ax.scatter(x, y, z,
               zdir='z',
               c = c,
               cmap = 'Dark2_r',
               marker='.',
               s=1,
    )
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.set_zticklabels([])
    ax.grid(False)
    ax.xaxis.pane.fill = False # Left pane
    ax.yaxis.pane.fill = False # Right pane
    ax.w_xaxis.line.set_color((1.0, 1.0, 1.0, 0.0))
    ax.w_yaxis.line.set_color((1.0, 1.0, 1.0, 0.0))
    ax.w_zaxis.line.set_color((1.0, 1.0, 1.0, 0.0))
    # Transparent panes
    ax.w_xaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    ax.w_yaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    # No ticks
    ax.set_xticks([]) 
    ax.set_yticks([]) 
    ax.set_zticks([])
    ax.set_box_aspect([max(x)-min(x),max(y)-min(y),max(z)-min(z)])
    def rotate(angle):
        ax.view_init(azim=angle)
    #rot_animation = animation.FuncAnimation(fig, rotate, frames=np.arange(0, 361, 2), interval=30)
    rot_animation = animation.FuncAnimation(fig, rotate, frames=np.arange(0, 361, 15), interval=300)
    #rot_animation.save('rotation.gif', dpi=80, writer='imagemagick')
    rot_animation.save(gif_save_path, dpi=80)


def make_html_entry(gif_path):
    genotype_name = '_'.join([str(i) for i in os.path.basename(gif_path).replace('.gif', '').split('_')[:-1]])

    geno_link = './geno_pages/'+genotype_name+'.html'

    if os.path.exists(geno_link):

        # load the file
        with open(geno_link) as inf:
            txt = inf.read()
            soup = bs4.BeautifulSoup(txt)

        outfile = geno_link


    # Geno specific html
    else:
        # load the file
        shutil.copy('test_html.html', geno_link)
        with open("test_html.html") as inf:
            txt = inf.read()
            soup = bs4.BeautifulSoup(txt)
        outfile = geno_link

    new_link = soup.new_tag("img", src='.' + gif_path, height= '20%', width = '40%')
    new_captian = soup.new_tag("figcaption")
    new_captian.string = os.path.basename(gif_path).replace('.gif', '')
    soup.head.append(new_link)
    soup.head.append(new_captian)

    # save the file again
    with open(geno_link, "w") as outf:
        outf.write(str(soup))


    # do index
    with open("index.html") as inf:
        txt = inf.read()
        isoup = bs4.BeautifulSoup(txt)




    new_link = isoup.new_tag("option", value='./geno_pages/'+genotype_name + '.html')
    print(genotype_name)
    new_link.string = genotype_name
    # print(soup)
    isoup.find('select').append(new_link)
    # .append(new_link)
    
    # save the file again
    with open("index.html", "w") as outf:
        outf.write(str(isoup))



print(desired_pcd_paths_list[0])
gif_path_list = []
for i in range(0, len(desired_pcd_paths_list)):
    plant_name = desired_pcd_paths_list[i].split('/')[-2]
    gif_path_list.append(f'./test_png/{plant_name}' + '.gif')

for pcd_path, array_path, gif_path in zip(desired_pcd_paths_list, desired_array_paths_list, gif_path_list):
    pcd_array = generate_pointcloud_array_from_path(pcd_path, array_path)
    generate_rotating_gif(pcd_array, gif_path)
    make_html_entry(gif_path)
