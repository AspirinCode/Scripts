#!/usr/bin/env python
"""RUN THE SCRIPT AS:
   $ ./clustering.py "../nameofTrajs*.nc" "../../topology.prmtop"
"""

import mdtraj as md
import sys
import glob
import numpy as np
import os
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from itertools import combinations

def load_Trajs(names, topology):
    filenames = sorted(glob.glob(names))
    trajectories = md.load(filenames, top = topology)
    return trajectories

def plot_PCA1(trajectory):
	pca1 = PCA(n_components = 2)
	trajectory.superpose(trajectory, 0)
	reduced_cartesian = pca1.fit_transform(trajectory.xyz.reshape(trajectory.n_frames, trajectory.n_atoms * 3))
	plt.figure()
	plt.scatter(reduced_cartesian[:, 0], reduced_cartesian[:,1], marker = 'x', c = trajectory.time)
	plt.xlabel('PC1')
	plt.ylabel('PC2')
	plt.title('Cartesian coordinate PCA')
	cbar = plt.colorbar()
	cbar.set_label('Time [ps]')



def plot_PCA2(trajectory):
	pca2 = PCA(n_components=2)
	atom_pairs = list(combinations(range(trajectory.n_atoms), 2))
	pairwise_distances = md.geometry.compute_distances(trajectory, atom_pairs)
	reduced_distances = pca2.fit_transform(pairwise_distances)
	plt.figure()
	plt.scatter(reduced_distances[:, 0], reduced_distances[:,1], marker='x', c=trajectory.time)
	plt.xlabel('PC1')
	plt.ylabel('PC2')
	plt.title('Pairwise distance PCA: alanine dipeptide')
	cbar = plt.colorbar()
	cbar.set_label('Time [ps]')




def main():
	trajectory = load_Trajs(sys.argv[1], sys.argv[2])
	plot1 = plot_PCA1(trajectory)
	#plot2 = plot_PCA2(trajectory)

if __name__ == "__main__":
    import sys
    main()