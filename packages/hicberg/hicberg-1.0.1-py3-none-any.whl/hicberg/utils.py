import time
import uuid
import subprocess as sp
from glob import glob
import subprocess as sp
import shutil as sh
from os import getcwd, mkdir
from pathlib import Path
import multiprocessing
from functools import partial
import itertools

from typing import Iterator, Tuple, List

import numpy as np
from numpy.random import choice
import pandas as pd
import scipy.stats as st
from scipy.stats import median_abs_deviation

import pysam
from Bio import SeqIO
import cooler

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

import hicberg.io as hio
import hicberg.statistics as hst
from hicberg import logger

def sum_mat_bins(matrix : np.array) -> np.array:
    """
    Adapted from : https://github.com/koszullab/hicstuff/tree/master/hicstuff
    Compute the sum of matrices bins (i.e. rows or columns) using
    only the upper triangle, assuming symmetrical matrices.

    Parameters
    ----------
    mat : scipy.sparse.coo_matrix
        Contact map in sparse format, either in upper triangle or
        full matrix.

    Returns
    -------
    numpy.ndarray :
        1D array of bin sums.
    """
    # Equivalaent to row or col sum on a full matrix
    # Note: mat.sum returns a 'matrix' object. A1 extracts the 1D flat array
    # from the matrix

    if matrix.shape[0] == matrix.shape[1]:

        return matrix.sum(axis=0) + matrix.sum(axis=1) - matrix.diagonal(0)
    
    else :

        return matrix.sum(axis=0), matrix.sum(axis=1)

def generate_gaussian_kernel(size : int = 1, sigma : int = 2) -> np.array:
    """
    Generate a 2D Gaussian kernel of a given size and standard deviation.

    Parameters
    ----------
    size : int, optional
        Size of the kernel, by default 1
    sigma : int, optional
        Standard deviation to use for the kernel build, by default 2

    Returns
    -------
    np.array
        2D Gaussian kernel.
    """    

    x = np.linspace(-sigma, sigma, size + 1)
    kern1d = np.diff(st.norm.cdf(x))
    kern2d = np.outer(kern1d, kern1d)

    return kern2d / kern2d.sum()

def detrend_matrix(matrix : np.array) -> np.array:
    """
    Detrend a matrix by P(s).

    Parameters
    ----------
    matrix : np.array
        Hi-C matrix to detrend.

    Returns
    -------
    np.array
        Detrended Hi-C matrix.
    """
    zeros_indexes = np.where(matrix == 0)
    matrix[zeros_indexes] = np.nan

    # Cis case
    if matrix.shape[0] == matrix.shape[1]:

        detrended_matrix = np.zeros(matrix.shape)

        np.fill_diagonal(detrended_matrix, np.diag(matrix) / np.nanmean(np.diag(matrix)))

        for i in range(1, matrix.shape[0]):
            diagonal_mean = np.nanmean(np.diagonal(matrix, i))
            np.fill_diagonal(detrended_matrix[i:, 0:-i], np.diag(matrix[i:, 0:-i]) / diagonal_mean)
            np.fill_diagonal(detrended_matrix[0:-i, i:], np.diag(matrix[0:-i, i:]) / diagonal_mean)

    # Trans case
    else:   
        expected_value = np.nanmedian(matrix)
        detrended_matrix = matrix / expected_value

    return detrended_matrix

def get_bad_bins(matrix : np.array = None, n_mads : int = 2) -> np.array:
    """
    Detect bad bins (poor interacting bins) in a normalized Hi-C matrix and return their indexes.
    Bins where the nan sum of interactions is zero  are considered as bad bins.

    Parameters
    ----------
    matrix : Normalized Hi-C matrix to detect bad bins from, by default None.
        
    n_mads : int, optional
        Number of median absolute deviations to set poor interacting bins threshold, by default 2

    Returns
    -------
    np.array
        Indexes of bad bins.
    """   

    # Cis case
    if matrix.shape[0] == matrix.shape[1]:

        nan_sum_bins = np.nansum(matrix, axis = 0)
        bad_indexes = np.where(nan_sum_bins == 0)

        return (bad_indexes)
    
    # Trans case
    else :

        x_sum_bins = np.nansum(matrix, axis = 0)
        y_sum_bins = np.nansum(matrix, axis = 1)

        x_bad_indexes = np.where(x_sum_bins == 0)
        y_bad_indexes = np.where(y_sum_bins == 0) 

        return (x_bad_indexes, y_bad_indexes)
    
def nan_conv(matrix : np.array = None, kernel : np.array = None, nan_threshold : bool = False) -> np.array:
    """
    Custom convolution function that takes into account nan values when convolving.
    Used to compute the local density of a Hi-C matrix.

    Parameters
    ----------
    matrix : np.array, optional
        Hi-C matrix to detect bad bins from, by default None
    kernel : np.array, optional
        Kernel to use for convolution (dimension must be odd), by default None
    nan_threshold : bool, optional
        Set wether or not convolution return nan if not enough value are caught, by default False

    Returns
    -------
    np.array
        Convolution product of the matrix and the kernel.
    """

    mat_cp = matrix.copy().astype(float)
    half_kernel = (kernel.shape[0] // 2)
    density_threshold = (kernel.shape[0] - half_kernel + 1) ** 2

    # Cis case
    if matrix.shape[0] == matrix.shape[1]:

        for i in range(half_kernel , (mat_cp.shape[0] - half_kernel), 1): 
            for j in range(half_kernel , (mat_cp.shape[1] - half_kernel), 1): 

                patch = matrix[i - (half_kernel) : (i +  half_kernel + 1) , j - (half_kernel) : j + half_kernel + 1]

                # Disrupt the kernel if too many nan values
                if nan_threshold:
                    nb_nan = np.count_nonzero(np.isnan(patch))
                    if nb_nan > density_threshold:

                        mat_cp[i, j] = np.nan
                        continue

                masked_patch = np.ma.MaskedArray(patch, mask = np.isnan(patch))
                mat_cp[i, j] = np.ma.average(masked_patch, weights = kernel)

    # Trans case
    else : 

        mean_value = np.nanmean(matrix)

        for i in range(half_kernel , (mat_cp.shape[0] - half_kernel), 1): 
            for j in range(half_kernel , (mat_cp.shape[1] - half_kernel), 1): 

                patch = matrix[i - (half_kernel) : (i +  half_kernel + 1) , j - (half_kernel) : j + half_kernel + 1]
                nb_nan = np.count_nonzero(np.isnan(patch))

                # Disrupt the kernel if too many nan values
                if nan_threshold:
                    if nb_nan > density_threshold:

                        mat_cp[i, j] = np.nan
                        continue

                masked_patch = np.ma.MaskedArray(patch, mask = np.isnan(patch))
                conv = np.ma.average(masked_patch, weights = kernel)

                if np.isnan(conv):

                    mat_cp[i, j] = mean_value
                else:
                    mat_cp[i, j] = conv

    return mat_cp


def get_local_density(cooler_file : str = None, chrom_name : tuple = (None, None), size : int = 11, sigma : int = 0.2, n_mads : int = 2, nan_threshold : bool = False) -> np.array:
    """
    Create density map from a Hi-C matrix. Return a dictionary where keys are chromosomes names and values are density maps.
    Density is obtained by getting the local density of each pairwise bin using a gaussian kernel convolution.

    Parameters
    ----------
    cooler_file : str, optional
        Path to Hi-C matrix (or sub-matrix) to dget density from, by default None, by default None
    chrom_name : tuple, optional
        Tuple containing the sub-matrix to fetch, by default (None, None)
    size : int, optional
        Size of the gaussian kernel to use, by default 5
    sigma : int, optional
        Standard deviation to use for the kernel, by default 2
    n_mads : int, optional
        Number of median absolute deviations to set poor interacting bins threshold, by default 2
    nan_threshold : bool, optional
        Set wether or not convolution return nan if not enough value are caught, by default None

    Returns
    -------
    np.array
        Map of local contact density.
    """

    if size % 2 == 0:
        raise ValueError("Kernel size must be odd")
    
    print(f"Cooler file : {cooler_file}")

    #Load cooler file
    matrix = cooler.Cooler(cooler_file).matrix(balance = True).fetch(chrom_name[0], chrom_name[1])


    mat_cp = matrix.copy().astype(float)

    if mat_cp.shape[0] < size:
        size = size - 2 * (size // 2)

    bad_bins = get_bad_bins(mat_cp, n_mads = n_mads)
    
    detrended_matrix = detrend_matrix(mat_cp)


    log_detrended_matrix = np.log(detrended_matrix)

    if detrended_matrix.shape[0] == detrended_matrix.shape[1]:

        log_detrended_matrix[bad_bins, :] = np.nan
        log_detrended_matrix[:, bad_bins] = np.nan

    else :

        log_detrended_matrix[bad_bins[1], :] = np.nan
        log_detrended_matrix[:, bad_bins[0]] = np.nan


    kernel = generate_gaussian_kernel(size = size, sigma = sigma)
    log_density = nan_conv(matrix = log_detrended_matrix, kernel = kernel, nan_threshold = nan_threshold)

    density = np.exp(log_density)

    # Edge cases correction
    if density.shape[0] == density.shape[1]:

        edges = np.where(np.isnan(density))

        for i, j in zip(edges[0], edges[1]):

            # TODO : replace by 1 ?
            density[i, j] =  np.nanmean(np.diag(density, k = i - j)) if ~np.isnan(np.nanmean(np.diag(density, k = i - j ))) else np.nanmean(density)

    else : 
        edges = np.where(np.isnan(density))

        for i, j in zip(edges[0], edges[1]):

            density[i, j] =  np.nanmedian(density)
            
    return (chrom_name, density)


def get_chromosomes_sizes(genome : str = None, output_dir : str = None) -> None:
    """
    Generate a dictionary save in .npy format where keys are chromosome name and value are size in bp.

    Parameters
    ----------
    genome : str, optional
        Path to the genome, by default None

    output_dir : str, optional
        Path to the folder where to save the dictionary, by default None
    """

    logger.info(f"Start getting chromosome sizes")

    genome_path = Path(genome)

    if not genome_path.is_file():

        raise IOError(f"Genome file {genome_path.name} not found. Please provide a valid path.")

    if output_dir is None:

        folder_path = Path(getcwd())

    else:

        folder_path = Path(output_dir)

    chrom_sizes = {}

    output_file = folder_path / "chromosome_sizes.npy"

    for rec in SeqIO.parse(genome_path,"fasta"):

        chrom_sizes[rec.id] = len(rec.seq)

    np.save(output_file, chrom_sizes)

    logger.info(f"Chromosome sizes have been saved in {output_file}")


def get_bin_table(chrom_sizes_dict : str = "chromosome_sizes.npy", bins : int = 2000, output_dir : str = None) -> None:
    """
    Create bin table containing start and end position for fixed size bin per chromosome.

    Parameters
    ----------
    chrom_sizes_dict : str
        Path to a dictionary containing chromosome sizes as {chromosome : size} saved in .npy format. By default chromosome_sizes.npy
    bins : int
        Size of the desired bin, by default 2000.
    output_dir : str, optional
        Path to the folder where to save the dictionary, by default None
    """

    logger.info(f"Start getting bin table")

    chrom_sizes_dict_path = Path(output_dir, chrom_sizes_dict)

    if not chrom_sizes_dict_path.is_file():

        raise IOError(f"Genome file {chrom_sizes_dict_path.name} not found. Please provide a valid path.")

    if output_dir is None:

        folder_path = Path(getcwd())

    else:

        folder_path = Path(output_dir)

    output_file = folder_path / "fragments_fixed_sizes.txt"

    chrom_size_dic = np.load(chrom_sizes_dict_path, allow_pickle=True).item()
    chr_count = 0

    with open (output_file, "w") as f_out:
        
        for chrom, length in zip(chrom_size_dic.keys(), chrom_size_dic.values()):

            curr_chr, curr_length = chrom, length
            chr_count += 1

            if (curr_length % bins) == 0:
                    interval_end = curr_length
            else:
                interval_end = (int((curr_length + bins) / bins)) * bins

                for val in range(0, interval_end, bins):
                    curr_start = val

                    if val + bins > curr_length:

                        curr_end = curr_length
                    else:
                        curr_end = val + bins
                    if (chr_count > 1) or (val > 0):
                        f_out.write("\n")
                    f_out.write(
                        str(curr_chr)
                        + "\t"
                        + str(curr_start)
                        + "\t"
                        + str(int(curr_end))
                        + "\t"
                    )

        # close the output fragment file
        f_out.close()

def is_duplicated(read : pysam.AlignedSegment) -> bool:
    """
    Check if read from pysam AlignmentFile is mapping more than once along the genome.

    Parameters
    ----------
    read : pysam.AlignedSegment
        pysam AlignedSegment object.

    Returns
    -------
    bool
        True if the read is duplicated i.e. mapping to more than one position.
    """    

    if "XS" in [x[0] for x in read.get_tags()]:
        return True

    else:
        return False

def is_poor_quality(read : pysam.AlignedSegment, mapq : int) -> bool:
    """
    Check if read from pysam AlignmentFile is under mapping quality threshold

    Parameters
    ----------
    read : pysam.AlignedSegment
        pysam AlignedSegment object.
    mapq : int
        Mapping quality threshold.

    Returns
    -------
    bool
        True if the read quality is below mapq threshold.
    """    
    if 0 < read.mapping_quality < mapq:
        return True

    else:
        return False

def is_unqualitative(read : pysam.AlignedSegment) -> bool:
    """
    Check if the read is not qualitative.

    Parameters
    ----------
    read : pysam.AlignedSegment
        pysam AlignedSegment object.

    Returns
    -------
    bool
        True if the read is not qualitative, False otherwise.
    """

    if read.mapping_quality == 0:

        return True

    else:

        return False

def is_unmapped(read : pysam.AlignedSegment) -> bool:
    """
    Check if read from pysam AlignmentFile is unmapped

    Parameters
    ----------
    read : pysam.AlignedSegment
        pysam AlignedSegment object.

    Returns
    -------
    bool
        True if the read is unmapped.
    """    
    if read.flag == 4:
        return True

    else:
        return False

def is_reverse(read : pysam.AlignedSegment) -> bool:
    """
    Check if read from pysam AlignmentFile is reverse

    Parameters
    ----------
    read : pysam.AlignedSegment
        pysam AlignedSegment object.

    Returns
    -------
    bool
        True if the read is reverse.
    """ 

    if read.flag == 16 or read.flag == 272:
        return True

    else:
        return False

def classify_reads(bam_couple : tuple[str, str] = ("1.sorted.bam", "2.sorted.bam"), chromosome_sizes : str = "chromosome_sizes.npy", mapq : int = 35, output_dir : str = None) -> None:
    """
    Classification of pairs of reads in 2 different groups:
        Group 0) --> (Unmappable) - files :group0.1.bam and group0.2.bam
        Group 1) --> (Uniquely Mapped  Uniquely Mapped) - files :group1.1.bam and group1.2.bam
        Group 2) --> (Uniquely Mapped Multi Mapped) or (Multi Mapped  Multi Mapped).- files :group2.1.bam and group2.2.bam

    Parameters
    ----------
    bam_couple : tuple[str, str]
        Tuple containing the paths to the forward and reverse alignment files. By default ("1.sorted.bam", "2.sorted.bam")
    chromosome_sizes : str, optional
        Path to a chromosome size dictionary save in .npy format, by default chromosome_sizes.npy
    mapq : int, optional
        Minimal read quality under which a Hi-C read pair will not be kept, by default 30
    output_dir : str, optional
        Path to the folder where to save the classified alignment files, by default None
    """

    forward_bam_file_path, reverse_bam_file_path = Path(output_dir, bam_couple[0]), Path(output_dir, bam_couple[1])

    chromosome_sizes_path = Path(output_dir, chromosome_sizes)

    if not forward_bam_file_path.is_file():

        raise IOError(f"Forward alignment file {forward_bam_file_path.name} not found. Please provide a valid path.")

    if not reverse_bam_file_path.is_file():
            
            raise IOError(f"Reverse alignment file {reverse_bam_file_path.name} not found. Please provide a valid path.")
    
    if not chromosome_sizes_path.is_file():
            
            raise IOError(f"Chromosome sizes file {chromosome_sizes_path.name} not found. Please provide a valid path.")
    
    if output_dir is None:
            
            output_dir = Path(getcwd())
    else:

        output_dir = Path(output_dir)

    chromosome_sizes_dic = hio.load_dictionary(chromosome_sizes_path)

    #opening files to parse
    forward_bam_file = pysam.AlignmentFile(forward_bam_file_path, "rb")
    reverse_bam_file = pysam.AlignmentFile(reverse_bam_file_path, "rb")

    #retrieve headers
    forward_header = forward_bam_file.header
    reverse_header = reverse_bam_file.header

    # create iterators
    forward_bam_file_iter = bam_iterator(forward_bam_file_path)
    reverse_bam_file_iter = bam_iterator(reverse_bam_file_path)

    unmapped_bam_file_foward = pysam.AlignmentFile(output_dir / f"group0.1.bam", "wb", template = forward_bam_file, header = forward_header)
    unmapped_bam_file_reverse = pysam.AlignmentFile(output_dir / f"group0.2.bam", "wb", template = reverse_bam_file, header = reverse_header)

    uniquely_mapped_bam_file_foward = pysam.AlignmentFile(output_dir / f"group1.1.bam", "wb", template = forward_bam_file, header = forward_header)
    uniquely_mapped_bam_file_reverse = pysam.AlignmentFile(output_dir / f"group1.2.bam", "wb", template = reverse_bam_file, header = reverse_header)

    multi_mapped_bam_file_foward = pysam.AlignmentFile(output_dir / f"group2.1.bam", "wb", template = forward_bam_file, header = forward_header)
    multi_mapped_bam_file_reverse = pysam.AlignmentFile(output_dir / f"group2.2.bam", "wb", template = reverse_bam_file, header = reverse_header)

    nb_unmapped_reads_forward, nb_unmapped_reads_reverse = 0, 0
    nb_uniquely_mapped_reads_forward, nb_uniquely_mapped_reads_reverse = 0, 0
    nb_multi_mapped_reads_forward, nb_multi_mapped_reads_reverse = 0, 0

    for forward_block, reverse_block in zip(forward_bam_file_iter, reverse_bam_file_iter):

        unmapped_couple, multi_mapped_couple = False, False

        forward_reverse_combinations = list(itertools.product(tuple(forward_block), tuple(reverse_block)))

        for combination in forward_reverse_combinations:

            if  is_unmapped(combination[0])  or is_unmapped(combination[1]):

                unmapped_couple = True

                break

            if is_duplicated(combination[0]) or is_poor_quality(combination[0], mapq) or is_duplicated(combination[1]) or is_poor_quality(combination[1], mapq):

                multi_mapped_couple = True
                
                break

        for forward_read in forward_block:

            if unmapped_couple :

                unmapped_bam_file_foward.write(forward_read)
                nb_unmapped_reads_forward += 1

            elif multi_mapped_couple:

                forward_read.set_tag("XG", chromosome_sizes_dic[forward_read.reference_name])
                multi_mapped_bam_file_foward.write(forward_read)
                nb_multi_mapped_reads_forward += 1

            else: 

                forward_read.set_tag("XG", chromosome_sizes_dic[forward_read.reference_name])
                uniquely_mapped_bam_file_foward.write(forward_read)
                nb_uniquely_mapped_reads_forward += 1

        for reverse_read in reverse_block:

            if unmapped_couple:

                unmapped_bam_file_reverse.write(reverse_read)
                nb_unmapped_reads_reverse += 1

            elif multi_mapped_couple:

                reverse_read.set_tag("XG", chromosome_sizes_dic[reverse_read.reference_name])
                multi_mapped_bam_file_reverse.write(reverse_read)
                nb_multi_mapped_reads_reverse += 1

            else : 

                reverse_read.set_tag("XG", chromosome_sizes_dic[reverse_read.reference_name])
                uniquely_mapped_bam_file_reverse.write(reverse_read)
                nb_uniquely_mapped_reads_reverse += 1

    #closing files
    forward_bam_file.close()
    reverse_bam_file.close()
    unmapped_bam_file_foward.close()
    unmapped_bam_file_reverse.close()
    uniquely_mapped_bam_file_foward.close()
    uniquely_mapped_bam_file_reverse.close()
    multi_mapped_bam_file_foward.close()
    multi_mapped_bam_file_reverse.close()

    logger.info(f"Files for the different groups have been saved in {output_dir}")
    logger.info(f"Number of unmapped reads in forward file : {nb_unmapped_reads_forward}")
    logger.info(f"Number of unmapped reads in reverse file : {nb_unmapped_reads_reverse}")
    logger.info(f"Number of uniquely mapped reads in forward file : {nb_uniquely_mapped_reads_forward}")
    logger.info(f"Number of uniquely mapped reads in reverse file : {nb_uniquely_mapped_reads_reverse}")
    logger.info(f"Number of multi mapped reads in forward file : {nb_multi_mapped_reads_forward}")
    logger.info(f"Number of multi mapped reads in reverse file : {nb_multi_mapped_reads_reverse}")


    # Cleaning files after classification
    # forward_bam_file_path.unlink()
    # reverse_bam_file_path.unlink()

def is_intra_chromosome(read_forward : pysam.AlignedSegment, read_reverse : pysam.AlignedSegment) -> bool:
    """
    Return True if two reads of a pair came from the same chromosome.

    Parameters
    ----------
    read_forward : pysam.AlignedSegment
        Forward read of the pair.
    read_reverse : pysam.AlignedSegment
        Reverse read of the pair.

    Returns
    -------
    bool
        True if the pair is intra-chromosomic, False otherwise.
    """    

    if read_forward.query_name != read_reverse.query_name:
        raise ValueError("Reads are not coming from the same pair")

    if read_forward.reference_name == read_reverse.reference_name:
        return True
    else:
        return False 

def get_ordered_reads(read_forward : pysam.AlignedSegment, read_reverse : pysam.AlignedSegment) -> Tuple[pysam.AlignedSegment, pysam.AlignedSegment]:
    """
    Returns the ordered pair of reads in the same chromosome as the two reads .

    Parameters
    ----------
    read_forward : pysam.AlignedSegment
        Forward read to compare with the reverse read.
    read_reverse : pysam.AlignedSegment
        Reverse read to compare with the forward read.

    Returns
    -------
    Tuple[pysam.AlignedSegment, pysam.AlignedSegment]
        The ordered pair of reads in the same chromosome as the two reads.
    """

    if read_forward.query_name != read_reverse.query_name:
            
        raise ValueError("The two reads must come from the same pair.")
        
    if is_reverse(read_forward):

        forward_start = read_forward.reference_end
    
    elif not is_reverse(read_forward):
                
        forward_start = read_forward.reference_start

    if is_reverse(read_reverse):
            
        reverse_start = read_reverse.reference_end

    elif not is_reverse(read_reverse):
    
        reverse_start = read_reverse.reference_start

    
    if forward_start <= reverse_start:
        
        return (read_forward, read_reverse)
    
    elif forward_start > reverse_start:

        return (read_reverse, read_forward)

def is_weird(read_forward : pysam.AlignedSegment, read_reverse : pysam.AlignedSegment) -> bool:
    """
    Check if two reads are forming a weird pattern .

    Parameters
    ----------
    read_forward : pysam.AlignedSegment
        Forward read of the pair
    read_reverse : pysam.AlignedSegment
        Reverse read of the pair

    Returns
    -------
    bool
        True if the two reads are forming a weird pattern, False otherwise.
    """
    
    if read_forward.query_name != read_reverse.query_name:

        raise ValueError("The two reads must be mapped on the same chromosome.")

    read_forward, read_reverse = get_ordered_reads(read_forward, read_reverse)

    if (
        (read_forward.flag == read_reverse.flag == 0)
        or (read_forward.flag == read_reverse.flag == 16)
        or (read_forward.flag == read_reverse.flag == 272)
        or (read_forward.flag == read_reverse.flag == 256)
        or (read_forward.flag == 256 and read_reverse.flag == 0)
        or (read_forward.flag == 0 and read_reverse.flag == 256)
        or (read_forward.flag == 16 and read_reverse.flag == 272)
        or (read_forward.flag == 272 and read_reverse.flag == 16)
    ):
        return True
    
    else:
        return False

def is_uncut(read_forward : pysam.AlignedSegment, read_reverse : pysam.AlignedSegment) -> bool:
    """
    Check if two reads are forming an uncut pattern .

    Parameters
    ----------
    read_forward : pysam.AlignedSegment
        Forward read of the pair
    read_reverse : pysam.AlignedSegment
        Reverse read of the pair

    Returns
    -------
    bool
        True if the two reads are forming an uncut pattern, False otherwise.
    """
        
    if read_forward.query_name != read_reverse.query_name:

        raise ValueError("The two reads must be mapped on the same chromosome.")
    
    read_forward, read_reverse = get_ordered_reads(read_forward, read_reverse)

    if (
        (read_forward.flag == 0 and read_reverse.flag == 16)
        or (read_forward.flag == 256 and read_reverse.flag == 16)
        or (read_forward.flag == 0 and read_reverse.flag == 272)
        or (read_forward.flag == 256 and read_reverse.flag == 272)
    ):
        return True
    else:
        return False

    

def is_circle(read_forward : pysam.AlignedSegment, read_reverse : pysam.AlignedSegment) -> bool:
    """
    Check if two reads are forming a loop pattern .

    Parameters
    ----------
    read_forward : pysam.AlignedSegment
        Forward read of the pair
    read_reverse : pysam.AlignedSegment
        Reverse read of the pair

    Returns
    -------
    bool
        True if the two reads are forming a loop pattern, False otherwise.
    """

    if read_forward.query_name != read_reverse.query_name:
        raise ValueError("Reads are not coming from the same pair")

    read_forward, read_reverse = get_ordered_reads(read_forward, read_reverse)

    if (
        (read_forward.flag == 16 and read_reverse.flag == 0)
        or (read_forward.flag == 272 and read_reverse.flag == 0)
        or (read_forward.flag == 16 and read_reverse.flag == 256)
        or (read_forward.flag == 272 and read_reverse.flag == 256)
    ):
        return True
    else:
        return False

def get_cis_distance(read_forward : pysam.AlignedSegment, read_reverse : pysam.AlignedSegment, circular : str = "") -> int:
    """
    Calculate the distance between two reads in the same pairwise alignment .

    Parameters
    ----------
    read_forward : pysam.aligned_segment
        Forward read of the pair
    read_reverse : pysam.AlignedSegment
        Reverse read of the pair
    circular : str, optional
        Name of the chromosomes to consider as circular, by default None, by default "".

    Returns
    -------
    int
        Genomic distance separating the two reads (bp).

    """    
    if read_forward.query_name != read_reverse.query_name:
        raise ValueError("Reads are not coming from the same pair")

    if is_intra_chromosome(read_forward, read_reverse):

        read_forward, read_reverse = get_ordered_reads(read_forward, read_reverse)

        if is_weird(read_forward, read_reverse):
            distance = np.abs(
                np.subtract(read_forward.reference_start, read_reverse.reference_start)
            )

        elif is_uncut(read_forward, read_reverse):
            distance = np.abs(np.subtract(read_forward.reference_start, read_reverse.reference_end))

        elif is_circle(read_forward, read_reverse):
            distance = np.abs(np.subtract(read_forward.reference_end, read_reverse.reference_start))

        # circular mode
        if read_forward.reference_name in circular:

            clockwise_distance = distance
            anti_clockwise_distance = np.subtract(read_forward.get_tag("XG"), distance)
            return np.min([clockwise_distance, anti_clockwise_distance])

        # linear mode
        else:
            return distance


def bam_iterator(bam_file : str = None) -> Iterator[pysam.AlignedSegment]:
    """
    Returns an iterator for the given SAM/BAM file (must be query-sorted).
    In each call, the alignments of a single read are yielded as a 3-tuple: (list of primary pysam.AlignedSegment, list of supplementary pysam.AlignedSegment, list of secondary pysam.AlignedSegment).

    Parameters
    ----------
    bam : [str]
        Path to alignment file in .sam or .bam format.

    Yields
    -------
    Iterator[pysam.AlignedSegment]
        Yields a list containing pysam AlignmentSegment objects, within which all the reads have the same id.
    """

    bam_path = Path(bam_file)

    if not bam_path.is_file():

        raise IOError(f"BAM file {bam_path.name} not found. Please provide a valid path.")

    with pysam.AlignmentFile(bam_path, "rb") as bam_handler:
    
        alignments = bam_handler.fetch(until_eof=True)
        current_aln = next(alignments)
        current_read_name = current_aln.query_name

        block = []
        block.append(current_aln)

        while True:
            try:
                next_aln = next(alignments)
                next_read_name = next_aln.query_name
                if next_read_name != current_read_name:
                    yield (block)
                    current_read_name = next_read_name
                    block = []
                    block.append(next_aln)

                else:
                    block.append(next_aln)
            except StopIteration:
                break

        yield (block)

def block_counter(forward_bam_file : str, reverse_bam_file : str) -> Tuple[int, int] : 
    """
    Return as a tuple the number of blocks in the forward and reverse bam files.

    Parameters
    ----------
    forward_bam_file : str, optional
        Path to forward .bam alignment file.
    reverse_bam_file : str, optional
        Path to reverse .bam alignment file.

    Returns
    -------
    Tuple[int, int]
        Number of blocks in the forward and reverse bam files.
    """    
    
    forward_bam_path = Path(forward_bam_file)
    reverse_bam_path = Path(reverse_bam_file)

    if not forward_bam_path.is_file():
            
        raise IOError(f"BAM file {forward_bam_path.name} not found. Please provide a valid path.")
    
    if not reverse_bam_path.is_file():
                
        raise IOError(f"BAM file {reverse_bam_path.name} not found. Please provide a valid path.")

    iterator_for, iterator_rev = bam_iterator(forward_bam_path), bam_iterator(reverse_bam_path)
    nb_blocks_for, nb_blocks_rev = 0, 0

    for forward_block, reverse_block in zip(iterator_for, iterator_rev):

        nb_blocks_for += 1
        nb_blocks_rev += 1
    
    return (nb_blocks_for, nb_blocks_rev)

def chunk_bam(forward_bam_file : str = "group2.1.bam", reverse_bam_file : str = "group2.2.bam", nb_chunks : int = 2, output_dir : str = None) -> None:
    """
    Split a .bam file into chunks .bam files.
    Parameters
    ----------
    forward_bam_file : str, optional
        Path to forward .bam alignment file, by default group2.1.bam
    reverse_bam_file : str, optional
        Path to reverse .bam alignment file, by default group2.2.bam
    nb_chunks : int, optional
        Number of chunks to create, by default 2
    output_dir : str, optional
        Path to the folder where to save the classified alignment files, by default None
    """
    logger.info(f"Start chunking BAM files")

    if output_dir is None:
            
            output_dir = Path(getcwd())
    else:

        output_dir = Path(output_dir)

    # Create folder for chunks
    chunks_path = output_dir / "chunks"

    if chunks_path.is_dir():
        sh.rmtree(chunks_path)

    mkdir(output_dir / "chunks")

    forward_bam_path, reverse_bam_path = Path(output_dir, forward_bam_file), Path(output_dir, reverse_bam_file)

    if not forward_bam_path.is_file():
            
        raise IOError(f"BAM file {forward_bam_path.name} not found. Please provide a valid path.")
    
    if not reverse_bam_path.is_file():
                
        raise IOError(f"BAM file {reverse_bam_path.name} not found. Please provide a valid path.")
    
    forward_bam_handler = pysam.AlignmentFile(forward_bam_path, "rb")
    reverse_bam_handler = pysam.AlignmentFile(reverse_bam_path, "rb")

    #retrieve headers
    forward_header = forward_bam_handler.header
    reverse_header = reverse_bam_handler.header

    # Create placeholder for chunks

    output_chunk_for = chunks_path / "chunk_for_%d.bam"
    output_chunk_rev = chunks_path / "chunk_rev_%d.bam"

    nb_forward_block, nb_reverse_blocks = block_counter(forward_bam_path, reverse_bam_path)

    # Compute euclidean division to know chunks sizes
    size_cut = np.divmod(nb_forward_block, (nb_chunks - 1))

    # Create list of chunk sizes
    cut_list = [size_cut[0]] * (nb_chunks - 1)
    cut_list.append(size_cut[1])

    # Instanciate index for list of chunks sizes
    chunk_size_index = 0

    # Instanciate generators to yield blocks of multi-mapping reads
    for_iterator, rev_iterator = bam_iterator(forward_bam_path), bam_iterator(reverse_bam_path)

    # Create empty lists to store blocks of reads
    read_stack_for = []
    read_stack_rev = []

    # Set first output file
    outfile_for = pysam.AlignmentFile(
        str(output_chunk_for) % chunk_size_index, "wb", template = forward_bam_handler, header = forward_header
    )
    outfile_rev = pysam.AlignmentFile(
        str(output_chunk_rev) % chunk_size_index, "wb", template = reverse_bam_handler, header = reverse_header
    )

    # Parse alignment file to yield reads blocks
    for block_for_, block_rev_ in zip(for_iterator, rev_iterator):

        # Fill containers with blocks
        if len(read_stack_for) < cut_list[chunk_size_index]:

            read_stack_for.append(block_for_)
            read_stack_rev.append(block_rev_)

        # Write reads alignment in chunks once the container is full
        elif len(read_stack_for) == cut_list[chunk_size_index]:

            for block_for in read_stack_for:
                for read_for in block_for:

                    outfile_for.write(read_for)

            for block_rev in read_stack_rev:
                for read_rev in block_rev:

                    outfile_rev.write(read_rev)
            
            # Close current chunk
            outfile_for.close()
            outfile_rev.close()

            # Switch to next chunk
            chunk_size_index += 1

            # Free containers
            read_stack_for = []
            read_stack_rev = []

            # Save current block
            read_stack_for.append(block_for_)
            read_stack_rev.append(block_rev_)

            # Update output chunk file
            outfile_for = pysam.AlignmentFile(
                str(output_chunk_for) % chunk_size_index, "wb", template = forward_bam_handler, header = forward_header
            )
            outfile_rev = pysam.AlignmentFile(
                str(output_chunk_rev) % chunk_size_index, "wb", template = reverse_bam_handler, header = reverse_header
            )

    # Fill last chunk
    for block_for in read_stack_for:
        for read_for in block_for:

            outfile_for.write(read_for)

    for block_rev in read_stack_rev:
        for read_rev in block_rev:

            outfile_rev.write(read_rev)
    
    # Close last chunk
    outfile_for.close()
    outfile_rev.close()

    forward_bam_handler.close()
    reverse_bam_handler.close()

    logger.info(f"Chunks saved in {output_dir / 'chunks'}")


def subsample_restriction_map(restriction_map : dict = None, rate : float = 1.0) -> dict[str, np.ndarray[int]]:
    """
    Subsample a restriction map by a given rate.

    Parameters
    ----------
    restriction_map : dict, optional
        Restriction map saved as a dictionary like chrom_name : list of restriction sites' position, by default None
    rate : float, optional
        Set the proportion of restriction sites to consider. Avoid memory overflow when restriction maps are very dense, by default 1.0

    Returns
    -------
    dict[str, np.ndarray[int]]
        Dictionary of sub-sampled restriction map with keys as chromosome names and values as lists of restriction sites' position.

    """

    if (0.0 > rate) or (rate > 1.0):
        raise ValueError("Sub-sampling rate must be between 0.0 and 1.0.")
    

    subsampled_restriction_map = {}

    for chromosome in restriction_map:
            
        if int(len(restriction_map.get(str(chromosome))) * rate) < 5:

            subsampled_restriction_map[str(chromosome)] = restriction_map[str(chromosome)]

            continue

        size_sample = int(len(restriction_map.get(str(chromosome))) * rate)

        subsampled_restriction_map[str(chromosome)] = np.random.choice(
            restriction_map.get(str(chromosome)), size_sample, replace=False
        )
        
        subsampled_restriction_map[str(chromosome)] = np.sort(subsampled_restriction_map[str(chromosome)])

        if subsampled_restriction_map[str(chromosome)][0] != 0:
            subsampled_restriction_map[str(chromosome)][0] = 0

        if (
            subsampled_restriction_map[str(chromosome)][-1]
            != restriction_map.get(str(chromosome))[-1]
        ):
            subsampled_restriction_map[str(chromosome)][-1] = restriction_map.get(str(chromosome))[-1]        

    return subsampled_restriction_map


def max_consecutive_nans(vector : np.ndarray) -> int:
    """
    Return the maximum number of consecutive NaN values in a vector.

    Parameters
    ----------
    vector : np.ndarray
        Vector to get the maximum number of consecutive NaN values from.

    Returns
    -------
    int
        Number of maximum consecutive NaN values.
    """

    mask = np.concatenate(([False], np.isnan(vector), [False]))
    if ~mask.any():
        return 0
    else:
        idx = np.nonzero(mask[1:] != mask[:-1])[0]
        return (idx[1::2] - idx[::2]).max()

def mad_smoothing(vector : np.ndarray[int] = None, window_size : int | str = "auto", nmads : int = 1) -> np.ndarray[int]:
    """
    Apply MAD smoothing to an vector .

    Parameters
    ----------
    vector : np.ndarray[int], optional
        Data to smooth, by default None
    window_size : int or str, optional
        Size of the window to perform mean sliding average in. Window is center on current value as [current_value - window_size/2] U [current_value + window_size/2], by default "auto"
    nmads : int, optional
        number of median absolute deviation tu use, by default 1

    Returns
    -------
    np.ndarray[int]
        MAD smoothed vector.
    """

    mad = median_abs_deviation(vector)
    threshold = np.median(vector) - nmads * mad
    # threshold = 0
    imputed_nan_data = np.where(vector <= threshold, np.nan, vector)

    if window_size == "auto":
        # due to centered window, selected windows for rolling mean is :
        # [window_size / 2 <-- center_value --> window_size / 2]
        window_size = (max_consecutive_nans(imputed_nan_data) * 2) + 1

    averaged_data = (
        pd.Series(imputed_nan_data)
        .rolling(window=window_size, min_periods=1, center=True)
        .apply(lambda x: np.nanmean(x))
        .to_numpy()
    )

    return averaged_data


def replace_consecutive_zeros_with_mean(vector : np.ndarray[float]) -> np.ndarray[float]:
    """
    Replace consecutive zeros in a vector with the mean of the flanking values.

    Parameters
    ----------
    vector : np.ndarray[float]
        Array to replace consecutive zeros in.

    Returns
    -------
    np.ndarray[float]
        Array with consecutive zeros replaced by the mean of the flanking values.
    """    
    
    # Initialize variables
    start = None
    end = None
    i = 0
    
    # Iterate through the array
    while i < len(vector):
        # Check for the start of a sequence of zeros
        if vector[i] == 0 and start is None:
            start = i
        # Check for the end of a sequence of zeros
        elif vector[i] != 0 and start is not None:
            end = i
            # Calculate the mean of the values flanking the sequence of zeros
            mean_value = (vector[start-1] + vector[end]) / 2 if start > 0 else vector[end]
            # Replace zeros with the mean value
            vector[start:end] = mean_value
            # Reset start and end for the next sequence
            start = None
            end = None
        i += 1
    
    # Handle case where sequence of zeros goes till the end of the array
    if start is not None:
        mean_value = vector[start-1] if start > 0 else 0  # Use the preceding value or 0 if at the start
        vector[start:] = mean_value
    
    return vector


def get_chunks(output_dir : str = None) -> tuple([List[str], List[str]]):
    """
    Return a tuple containing the paths to the forward and reverse chunks.

    Parameters
    ----------
    output_dir : str, optional
        Path to get chunks from, by default None


    Returns
    -------
    tuple([List[str], List[str]]
        Tuple containing the paths to the forward and reverse chunks.
    """

    forward_chunks = sorted(glob(output_dir + '/chunks/chunk_for_*.bam'))
    reverse_chunks = sorted(glob(output_dir + '/chunks/chunk_rev_*.bam'))

    return (forward_chunks, reverse_chunks)

def is_empty_alignment(alignment_file : str) -> bool:
    """
    Check if an alignment file is empty.
    If empty, return True, else return False.

    Parameters
    ----------
    alignment_file : str
        Path to the alignment file to check.

    Returns
    -------
    bool
        Return True if the file is empty, False otherwise.
    """    
    try:
        # Open the SAM/BAM file
        with pysam.AlignmentFile(alignment_file, "rb") as alignment:
            # Attempt to fetch the first read
            try:
                alignment.__next__()
                # If we can fetch a read, the file is not empty
                return False
            except StopIteration:
                # If StopIteration is raised, the file is empty
                return True
    except FileNotFoundError:
        print(f"File not found: {filepath}")
        return True  # Assuming file is "empty" if it doesn't exist

def format_blacklist(blacklist : str = None) -> dict[str, Tuple[int, int]]:
    """
    Format a blacklist file into a dictionary.

    Parameters
    ----------
    blacklist : str, optional
        Path to the blacklist file. If set to -1 this is equivalent to None for workflow managers purpose, by default None

    Returns
    -------
    dict[str, Tuple[int, int]]
        Dictionary with chromosome name as key and tuple of start and end as value.
    """

    if blacklist is None or blacklist == "-1":
        return None
    
    if not isinstance(blacklist, str):
        raise TypeError("Blacklist should be a string")

    if not Path(blacklist).exists():
        pieces = blacklist.split(',')
        chromosomes_found = np.unique([blacklist.split(':')[0] for p in pieces])
        indexes_dict = {chrom: 0 for chrom in chromosomes_found}

        result = {}
        for piece in pieces:
            key, value = piece.split(':')
            if key in result:
                index = indexes_dict[key]
                new_key = f'{key}_{index}'
                indexes_dict[key] += 1

            else : 
                new_key = key
            result[new_key] = tuple([int(x) for x in value.split('-')])

        return result
    
    else:
        result = {}
        with open(blacklist, 'r') as f:
            for line in f:
                chrom, start, end = line.split()
                if chrom in result:
                    index = 0
                    while f"{chrom}_{index}" in result:
                        index += 1
                    result[f"{chrom}_{index}"] = (int(start), int(end))
                else:
                    result[chrom] = (int(start), int(end))
        return result


def is_blacklisted(read_forward : pysam.AlignedSegment, read_reverse : pysam.AlignedSegment, blacklist : dict[str, Tuple[int, int]] = None) -> bool:
    """
    Check if a read pair is blacklisted based on a list of coordiantes.

    Parameters
    ----------
    read_forward : pysam.AlignmentSegment
        Forward read of the pair.
    read_reverse : pysam.AlignedSegment
        Reverse read of the pair.
    blacklist : dict[str, Tuple[int, int]]
        Blacklist of coordinates to check against. Chromsome name as key and tuple of start and end as value.
        Chromosome names should be formatted as 'chr1_A', 'chr1_B', etc. With A and B being the index of the coordinates to blacklist in a given chromosome.

    Returns
    -------
    bool
        True if the read pair is blacklisted, False otherwise.
    """

    if blacklist is None:
        return False
    
    if read_forward.query_name != read_reverse.query_name:
        raise ValueError("Reads are not coming from the same chromosome")
    
    forward_start = read_forward.reference_start if not is_reverse(read_forward) else read_forward.reference_end
    reverse_start = read_reverse.reference_start if not is_reverse(read_reverse) else read_reverse.reference_end

    forward_check = [low < forward_start < high and read_forward.reference_name == chrom.split("_")[0] for chrom, (low, high) in blacklist.items()]
    reverse_check = [low < reverse_start < high and read_reverse.reference_name == chrom.split("_")[0] for chrom, (low, high) in blacklist.items()]

    return any([f_check or r_check for f_check, r_check in zip(forward_check, reverse_check)])