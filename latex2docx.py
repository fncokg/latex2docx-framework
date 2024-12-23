import subprocess
import re
import shutil
import tempfile
import logging
import argparse
from pathlib import Path

from processor import reader, writer

PANDOC_FILTERS = ["utils/pandoc-tex-numbering.py"]
PANDOC_ARGS = []
IMPORT_MACRONAMES = ["input","include","import","subfile"]

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import_macro_re = re.compile(r'\\(' + '|'.join(IMPORT_MACRONAMES) + r')\{(.*?)\}')

def full_path(path):
    return Path(path).resolve()

def get_latex_imported_files(tex):
    files = [file for cmd,file in import_macro_re.findall(tex)]
    return files

def main(input_file, output_file, metadata_file,project_dir):
    
    logging.info(f'Converting {input_file} to {output_file}')

    with tempfile.TemporaryDirectory(delete=True) as tmpdir:
        root_dir = Path(tmpdir)
        logger.info(f'Creating temporary directory {root_dir}')
        if project_dir:
            logger.info(f'Copying project directory {project_dir} to {root_dir}')
            shutil.copytree(project_dir, str(root_dir), dirs_exist_ok=True)
        tmp_texfile = root_dir / Path(input_file).name
        tmp_docxfile = root_dir / Path(output_file).name

        logger.info('Start reading tex file')
        files_queue = [tmp_texfile]
        while files_queue:
            file = files_queue.pop(0)
            with file.open("r") as f:
                tex = f.read()
            imported_files = get_latex_imported_files(tex)
            if imported_files:
                files_queue.extend([root_dir / f for f in imported_files])
            with file.open("w") as f:
                f.write(reader(tex))
    
        logger.info('Start pandoc conversion')
        filter_args = []
        for filter in PANDOC_FILTERS:
            if "." in filter:
                filter_args.extend(["-F",full_path(filter)])
            else:
                filter_args.extend(["-F",filter])
        subprocess.run(['pandoc','--metadata-file',metadata_file,*filter_args,*PANDOC_ARGS,"-o",tmp_docxfile, tmp_texfile],cwd=root_dir)

        logger.info('Start writing docx file')
        writer(tmp_docxfile,output_file)

    if root_dir.exists():
        logger.warning(f'Temporary directory {root_dir} still exists, this does not impact the output file, but you may want to delete it manually')
    logger.info(f"Temporary directory {root_dir} deleted")    
    logging.info('Finish converting tex to docx')
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert latex to word')
    parser.add_argument('-I', '--input', type=str, help='The tex file to be converted',default='tex_source/main.tex')
    parser.add_argument('-M', '--metadata', type=str, help='The metadata file',default='tex_source/metadata.yaml')
    parser.add_argument('-O', '--output', type=str, help='The output file',default='')
    parser.add_argument('-P', '--project', type=str, help='The project directory',default='tex_source')
    args = parser.parse_args()
    if args.output == '':
        output_file = Path(args.input).with_suffix('.docx').resolve()
    # We gonna use temp dir in the real conversion, so we need to make sure the path is absolute
    main(full_path(args.input), output_file, full_path(args.metadata), full_path(args.project))