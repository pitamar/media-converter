import json
import sys
from tqdm import tqdm
from multiprocessing import Pool 
from glob import glob
import argparse
import os
import re


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-dir', '-i', type=str, help='Input directory to search for files.', required=True)
    parser.add_argument('--output-dir', '-o', type=str, help='Output directory to search for files.', required=True)
    parser.add_argument('--input-filetype', type=str, help='Input file extensions.')
    parser.add_argument('--output-filetype', type=str, help='Ouptut file extensions.')
    parser.add_argument('--processes', '-p', type=int, help='Number of processes for parallel execution.', default=1)
    parser.add_argument('--ffmpeg-args', '-a', type=str, help='FFMPEG arguments', default='')
    parser.add_argument('--verbose', help='Verbose output', action='store_true')
    parser.add_argument('--dry-run', help='Print the commands to be executed', action='store_true')
    args = parser.parse_args()


    input_filetype = args.input_filetype
    output_filetype = args.output_filetype
    input_directory = os.path.realpath(args.input_dir)
    output_directory = os.path.realpath(args.output_dir)
    num_processes = args.processes
    ffmpeg_args = args.ffmpeg_args
    dry_run = args.dry_run
    verbose = args.verbose

    input_pattern = os.path.join(input_directory, '**', f'*.{input_filetype}')
    input_files = glob(input_pattern, recursive=True)
    print(f'Found {len(input_files)} files.')

    def handler(input_file_path):
        input_rel_path = input_file_path[len(input_directory) + 1:]
        output_file_path = os.path.join(output_directory, input_rel_path)
        output_file_path = re.sub(rf'.{input_filetype}$', f'.{output_filetype}', output_file_path)
        output_file_dirname = os.path.dirname(output_file_path)
        
        verbosity_flags = '' if verbose else '-hide_banner -loglevel panic'
        command = f'ffmpeg {verbosity_flags} -i "{input_file_path}" {ffmpeg_args} "{output_file_path}"'
        
        if dry_run:
            print(command)
        else:
            os.makedirs(output_file_dirname, exist_ok=True)
            os.system(command)


    with Pool(processes=num_processes) as pool:
        list(tqdm(pool.imap(handler, input_files), total=len(input_files)))
