import subprocess
import re
import tempfile
import logging
import argparse
from pathlib import Path

from processor import reader, writer

PANDOC_FILTERS = ["utils/pandoc-tex-numbering.py"]
PANDOC_ARGS = []

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main(input_file, output_file, metadata_file):
    if output_file == '':
        output_file = re.sub(r'\.tex$', '.docx', input_file)
    logging.info(f'Converting {input_file} to {output_file}')

    logger.info('Start reading tex file')
    tex_content = reader(input_file)

    with tempfile.NamedTemporaryFile(mode='w+', suffix='.tex',delete=False,delete_on_close=False) as f:
        tmp_texfile = f.name
        f.write(tex_content)
        logger.info(f"Temporary tex written to file: {tmp_texfile}")
    
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.docx',delete=False,delete_on_close=False) as f:
        tmp_docxfile = f.name
        logger.info(f"Temporary docx file created: {tmp_docxfile}")
    
    logger.info('Start pandoc conversion')
    filter_args = [cmd for filter in PANDOC_FILTERS for cmd in ["-F", filter]]
    subprocess.run(['pandoc','--metadata-file',metadata_file,*filter_args,*PANDOC_ARGS,"-o",tmp_docxfile, tmp_texfile])

    logger.info('Start writing docx file')
    writer(tmp_docxfile,output_file)
    
    Path(tmp_texfile).unlink(missing_ok=True)
    Path(tmp_docxfile).unlink(missing_ok=True)
    logger.info(f"Temporary files deleted: {tmp_texfile}, {tmp_docxfile}")
    logging.info('Finish converting tex to docx')
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert latex to word')
    parser.add_argument('-I', '--input', type=str, help='The tex file to be converted',default='tex_source/main.tex')
    parser.add_argument('-M', '--metadata', type=str, help='The metadata file',default='tex_source/metadata.yaml')
    parser.add_argument('-O', '--output', type=str, help='The output file',default='')
    args = parser.parse_args()
    main(args.input, args.output, args.metadata)