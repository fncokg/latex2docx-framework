import shutil
def reader(input_file):
    with open(input_file, 'r') as f:
        tex = f.read()
    return tex

def writer(tmp_docxfile, output_file):
    shutil.copy(tmp_docxfile, output_file)
    return output_file