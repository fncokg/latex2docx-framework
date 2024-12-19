import subprocess
import re
import tempfile
import logging
import argparse
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def prepare_tex(tex_file):
    with open(tex_file, 'r') as f:
        tex = f.read()
    return tex

def main(input_file, metadata_file, output_file):
    logging.info('Start to convert tex to docx')
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.tex',delete=False,delete_on_close=False) as f:
        tex_file = f.name
        tex_content = prepare_tex(input_file)
        f.write(tex_content)
        logger.info(f"Temporary tex file created: {tex_file}")
    subprocess.run(['pandoc','--metadata-file',metadata_file,"-F","pandoc-tex-numbering.py","-o",output_file, tex_file])
    Path(tex_file).unlink()
    logger.info("Temporary tex file deleted")
    logging.info('Finish converting tex to docx')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert hithesis2docx')
    parser.add_argument('-I', '--input', type=str, help='The tex file to be converted',default='test.tex')
    parser.add_argument('-M', '--metadata', type=str, help='The metadata file',default='test.yaml')
    parser.add_argument('-O', '--output', type=str, help='The output file',default='test.docx')
    args = parser.parse_args()
    main(args.input, args.metadata, args.output)