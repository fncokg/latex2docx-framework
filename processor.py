import shutil
import re
from pylatexenc.latexwalker import LatexWalker,get_default_latex_context_db,LatexMacroNode
from pylatexenc.macrospec import std_macro

LATEX_CONTEXT = get_default_latex_context_db()
LATEX_CONTEXT.add_context_category("hithesis",macros=[std_macro("longbionenumcaption",False,7),std_macro("bicaption",True,4)])

MACRO_RE = re.compile(r"(\\(bicaption|longbionenumcaption).*?)(\r|\n|\r\n)")

def get_argnode_content(argnode):
    return argnode.latex_verbatim()[1:-1]

def reader_replace_macros(macros):
    repl_pairs = []
    for macro in macros:
        repl_str = ""
        node = LatexWalker(macro,latex_context=LATEX_CONTEXT).get_latex_nodes(pos=0)[0][0]
        if isinstance(node, LatexMacroNode):
            arglist = node.nodeargd.argnlist
            if node.macroname == "bicaption":
                narg_offset = 0
                if "[" in arglist[0].delimiters:
                    label = get_argnode_content(arglist[0])
                    repl_str = f"\\label{{{label}}}\n"
                    narg_offset = 1
                cap_zh = get_argnode_content(arglist[1+narg_offset])
                repl_str += f"\\caption{{{cap_zh}}}"
            elif node.macroname == "longbionenumcaption":
                cap_zh = get_argnode_content(arglist[1])
                repl_str = f"\\caption{{{cap_zh}}}"
            repl_pairs.append((macro, repl_str))
    return repl_pairs

def reader(input_file:str)->str:
    with open(input_file, 'r') as f:
        tex = f.read()
    # Test string: \subsection{本硕论文题注}[Other picture example]
    tex = re.sub(r'\\(chapter|section|subsection|subsubsection)\{(.*?)\}\[(.*?)\]', r'\\\1{\2}', tex)

    # Test string: \bicaption[tumor]{}{肿瘤组织中各个子种群的进化示意图}{Fig.$\!$}{The diagram of tumor subpopulation evolution process}
    # Test string: \longbionenumcaption{}{{\wuhao 中国省级行政单位一览}\label{table2}}{Table$\!$}{}{{\wuhao Overview of the provincial administrative unit of China}}{-0.5em}{3.15bp}
    macros = list(map(lambda x:x[0],re.findall(MACRO_RE, tex+"\n")))
    replace_list = reader_replace_macros(macros)
    for string, repl in replace_list:
        tex = tex.replace(string, repl)
    return tex

def writer(tmp_docxfile:str, output_file:str)->None:
    shutil.copy(tmp_docxfile, output_file)