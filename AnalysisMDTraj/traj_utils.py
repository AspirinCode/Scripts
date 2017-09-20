import mdtraj
import numpy as np


def write_cpptraj_script(traj, top, frame1=1, frame2=1, outfile=None, write=True):
    """
    Create a cpptraj script to load specific range of frames from a trajectory and write them out to a file

    :param traj: str, Location in disk of trajectories to load
    :param top: str, Location in disk of the topology file
    :param frame1: int, The first frame to load
    :param frame2: int, The last frame to load
    :param outfile: str, Name (with file format extension) of the output trajectory
    :param write: bool, Whether to write the script to a file in disk

    :return cmds: str, the string representing the cpptraj script
    """
    if outfile is None:
        outfile = 'pdbs/' + traj.split('.')[0] + '.pdb'
    commands = [
        'parm {}'.format(top),
        'trajin {} {} {}'.format(traj, frame1, frame2),
        'trajout {}'.format(outfile),
        'run'
    ]
    cmds = '\n'.join(commands)
    if write:
        with open('script.cpptraj', 'w') as f:
            f.write(cmds)
    return cmds


def load_Trajs(trajfiles_list, prmtop_file, stride=1, chunk=1000):
    """
    Iteratively loads a list of NetCDF files and returns them
    as a list of mdtraj.Trajectory objects

    Parameters
    ----------
    trajfiles_list: list of str
            List with the names of trajectory files
    prmtop_file:  str
            Name of the prmtop file
    stride: int
            Frames to be used when loading the trajectories
    chunk:  int
            Number of frames to load at once from disk per iteration.
            If 0, load all.

    Returns
    -------
    list_chunks: list
            List of mdtraj.Trajectory objects, each of 'chunk' lenght
    """
    list_chunks = []
    for traj in trajfiles_list:
        for frag in mdtraj.iterload(traj, chunk=chunk, top=prmtop_file,
                                    stride=stride):
            list_chunks.append(frag)
    return(list_chunks)


def load_Trajs_generator(trajfiles_list, prmtop_file, stride=1, chunk=1000, verbose=False):
    """
    Iteratively loads a list of NetCDF files and returns them
    as an iterable of mdtraj.Trajectory objects
    Parameters
    ----------
    trajfiles_list: list of str
            List with the names of trajectory files
    prmtop_file:  str
            Name of the prmtop file
    stride: int
            Frames to be used when loading the trajectories
    chunk:  int
            Number of frames to load at once from disk per iteration.
            If 0, load all.
    Yields
    ------
    frag: mdtraj.Trajectory
    """
    for traj in trajfiles_list:
        if verbose:
            print("Loading {}".format(traj))
        for frag in mdtraj.iterload(traj, chunk=chunk, top=prmtop_file,
                                    stride=stride):
            yield frag


def traj_list_to_dict(trajfiles_list, prmtop_file, stride=1):
    """
    Loads a list of trajs passed as a list of strings into a
    dictionary with keys as integers from 0
    """
    trajs_dict = {}
    for i, traj in enumerate(trajfiles_list):
        trajs_dict[i] = mdtraj.load(traj, top=prmtop_file, stride=stride)
    return trajs_dict


def split_trajs_by_type(traj_dict, meta):
    """
    Find the kind of types of simulations inside the meta object
    and build a dictionary that has them as keys. Then, build a dictionary
    of the trajs inside traj_dict that belong to each type.
    """

    if len(traj_dict) != len(meta):
        raise ValueError('Lengths of traj_dict and meta do not match.')

    type_set = set(meta['type'])
    # dict which stores each subtype dict of trajs
    type_dict = dict.fromkeys(type_set)

    for t in type_set:
        new_dict = {}
        for i, row in meta.iterrows():
            if row['type'] == t:
                new_dict[i] = traj_dict[i]
        type_dict[t] = new_dict
    return type_dict


def trim_centers_by_region(clusterer, x1=None, x2=None, y1=None, y2=None, obs=(0, 1)):
    """
    Find the cluster centers that fall within a user-defined region.

    :param clusterer: an msmbuilder cluster object
    :param x1: float The low limit of the x axis
    :param x2: float The high limit of the x axis
    :param y1: float The low limit of the y axis
    :param y2: float The high limit of the y axis
    :param obs: tuple, the dimensions to sample
    :return trimmed: np.array, Cluster centers that are within the region
    """
    if not hasattr(clusterer, 'cluster_centers_'):
        raise AttributeError('The provided clusterer object has no cluster_centers_ property.')
    centers = clusterer.cluster_centers_
    pruned = centers[:, obs]
    if x1 is None:
        x1 = np.min(pruned[:, 0])
    if y1 is None:
        y1 = np.min(pruned[:, 1])
    if x2 is None:
        x2 = np.max(pruned[:, 0])
    if y2 is None:
        y2 = np.max(pruned[:, 1])

    trimmed = centers[
        ((pruned[:, 0] > x1) & (pruned[:, 0] < x2)) &
        ((pruned[:, 1] > y1) & (pruned[:, 1] < y2))
    ]
    return trimmed


def cartesian_product(x, y):
    return np.transpose([np.tile(x, len(y)), np.repeat(y, len(x))])
