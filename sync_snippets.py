"""
Sync code snippets between different IDEs (e.g. R Studio and Sublime Text).

Author: Soubhik Barari

Environment:
- must use Python 3+

Runtime: a few seconds 

Input:
- config.env:
    - must have `SUBLIME_SNIPPETS_PATH` and `RSTUDIO_SNIPPETS_PATH` variables set
    - `RSTUDIO_SNIPPETS_PATH` is usually by default `~/.config/rstudio/snippets/`

Output:
- `SUBLIME_SNIPPETS_PATH` populated with new `.sublime-snippet` files
- `RSTUDIO_SNIPPETS_PATH` populated with new `.snippets` files
"""

## --------------------------------------------------------
## PREAMBLE
## --------------------------------------------------------

import datetime as dt
import json
import os
import re
import sys
import time

## --------------------------------------------------------
## GLOBALS
## --------------------------------------------------------

SUBLIME_SOURCE_VALUES_TO_R_SNIPPET_FILES = {
    "source.python" : ["python.snippets"],
    "source.r" : ["r.snippets"],
    "text.tex.latex" : ["tex.snippets"],
    "text.tex" : ["tex.snippets"]
}

SUBLIME_SNIPPET_TEMPLATE = """
<snippet>
    <content><![CDATA[
%s
]]></content>
    <tabTrigger>%s</tabTrigger>
    <scope>%s</scope>
</snippet>
"""

R_SNIPPETS_SECTION_TEMPLATE = """
##-------------------------------------
## %s
##-------------------------------------
"""

## --------------------------------------------------------
## HELPERS
## --------------------------------------------------------

def make_filename_safe(text):
    return("".join([c for c in text if re.match(r'\w', c)]))

def load_dot_env(verbose=0):
    print("\nLoading `config.env`"); time.sleep(0.5)
    config_fpath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "config.env")
    if not os.path.exists(config_fpath):
        sys.exit("Please create `config.env`")
    with open(config_fpath, "r") as f:
        config_lines = f.readlines()
        for line in config_lines:
            if line.strip().startswith("#"):
                next
            else:
                kv = line.split("=")
                k = kv[0].strip().strip("'").strip('"')
                v = kv[1].strip().strip("'").strip('"')
                os.environ[k] = v
                if verbose == 1:
                    print("%s = %s" % (k, v))

def get_sublime_snippets():
    print("\nGetting Sublime Text snippets"); time.sleep(0.5)
    subl_snips = {}
    subl_snip_files = os.listdir(os.environ["SUBLIME_SNIPPETS_PATH"])
    subl_snip_files = list(filter(lambda fn: fn.endswith(".sublime-snippet"), subl_snip_files))
    for f, file in enumerate(subl_snip_files):
        file_path = os.path.join(os.environ["SUBLIME_SNIPPETS_PATH"], file)
        snip_code = ""
        snip_name = ""
        snip_section = make_filename_safe(re.search("( [A-Z ]* )", file_path)[1].strip() if re.match("( [A-Z ]* )", file_path) else "")
        with open(file_path, "r") as fp:
            snip_lines = fp.readlines()
            r = False
            for i in range(len(snip_lines)):
                if "<content>" in snip_lines[i]:
                    r = True
                    continue
                if "</content>" in snip_lines[i]:
                    r = False
                    continue
                if "<tabTrigger>" in snip_lines[i]:
                    snip_name = re.search("<tabTrigger>(.*)</tabTrigger>", snip_lines[i])[1]
                if "<scope>" in snip_lines[i]:
                    snip_lang = re.search("<scope>(.*)</scope>", snip_lines[i])[1]
                    if not snip_lang in subl_snips.keys():
                        subl_snips[snip_lang] = {}                  
                if r == True:
                    snip_code += snip_lines[i]                  
            if snip_code == "":
                print("Warning: `%s` is malformed -- couldn't extract code" % file)
                next
            elif snip_name == "":
                print("Warning: `%s` is malformed -- couldn't extract name" % file)
                next
            elif snip_lang == "":
                print("Warning: `%s` is malformed -- couldn't extract language" % file)
                next                
            else:
                if snip_section not in subl_snips[snip_lang].keys():
                    subl_snips[snip_lang][snip_section] = {}
                subl_snips[snip_lang][snip_section][snip_name] = snip_code
                print("[%i/%i] %s : %s (%s)" % (f+1, len(subl_snip_files), file, snip_name, snip_section))                

    return(subl_snips)

def get_directory_rsnippets(dir_path):
    print("\nGetting R snippets from `%s`" % dir_path); time.sleep(0.5)
    rstd_snips = {}
    rstd_snip_files = os.listdir(dir_path)
    rstd_snip_files = list(filter(lambda fn: fn.endswith(".snippets"), rstd_snip_files))
    for f, file in enumerate(rstd_snip_files):
        file_path = os.path.join(dir_path, file)
        snip_lang = file
        if not snip_lang in rstd_snips.keys():
            rstd_snips[snip_lang] = {}
        with open(file_path, "r") as fp:
            snip_lines = fp.readlines()
            curr_snip_code = ""
            curr_snip_name = ""
            curr_snip_section = ""
            i = 0
            while i < (len(snip_lines)-1):
                i = i + 1
                # print(str(i) + curr_snip_section + " " + curr_snip_name)
                if snip_lines[i].startswith("#"):
                    curr_snip_section_cand = re.sub("(#|=|-|\n)", "", snip_lines[i]).strip()
                    if curr_snip_section_cand:
                        ### first, write the last snippet if there was one
                        if curr_snip_section != "" and curr_snip_name != "":
                            rstd_snips[snip_lang][curr_snip_section][curr_snip_name] = curr_snip_code
                            print("[%i/%i] %s : %s (%s)" % (f+1, len(rstd_snip_files), file, curr_snip_name, curr_snip_section))                        
                        ## then start new section
                        curr_snip_name = ""
                        curr_snip_code = ""
                        curr_snip_section = make_filename_safe(curr_snip_section_cand)
                        if curr_snip_section not in rstd_snips[snip_lang].keys():
                            rstd_snips[snip_lang][curr_snip_section] = {}          
                    else:
                        continue
                elif "snippet" in snip_lines[i]:
                    ### first, write the last snippet if there was one
                    if curr_snip_section != "" and curr_snip_name != "":
                        rstd_snips[snip_lang][curr_snip_section][curr_snip_name] = curr_snip_code
                        print("[%i/%i] %s : %s (%s)" % (f+1, len(rstd_snip_files), file, curr_snip_name, curr_snip_section))
                    ### start filling out this snippet
                    curr_snip_name = snip_lines[i].replace("snippet ", "").strip()
                    curr_snip_code = ""
                    continue                        
                elif curr_snip_name != "":
                    curr_snip_code += re.sub("^\t", "", snip_lines[i])

    return(rstd_snips)

def get_rstudio_snippets():
    return(get_directory_rsnippets(os.environ["RSTUDIO_SNIPPETS_PATH"]))

def backup_snippets(subl_snips, rstd_snips):
    bak_dirpath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "backups")
    if not os.path.exists(bak_dirpath):
        os.makedirs(bak_dirpath)
    ts_iso = dt.datetime.now().isoformat()
    print("\nBacking up snippets (%s)" % ts_iso); time.sleep(0.5)
    with open(os.path.join(bak_dirpath, ts_iso + "_sublime_snippets.json"), "w") as fp:
        json.dump(subl_snips, fp, indent=4)
    with open(os.path.join(bak_dirpath, ts_iso + "_rstudio_snippets.json"), "w") as fp:
        json.dump(rstd_snips, fp, indent=4)

def backup_curr_rstudio_snippets():
    print("\nBacking up current R Studio snippet files"); time.sleep(0.5)
    rstd_snip_files = os.listdir(os.environ["RSTUDIO_SNIPPETS_PATH"])
    for srcfile in rstd_snip_files:
        if srcfile.endswith(".snippets"):
            print("* " + srcfile)            
            destfile = srcfile
            os.system('cp %s %s' % (os.path.join(os.environ["RSTUDIO_SNIPPETS_PATH"], srcfile), destfile))

def combine_snippets(subl_snips, rstd_snips):
    ## recategorize snippets from blank section if possible
    print("\nRe-categorizing snippets from blank section"); time.sleep(0.5)
    for s in SUBLIME_SOURCE_VALUES_TO_R_SNIPPET_FILES.keys():
        for r in SUBLIME_SOURCE_VALUES_TO_R_SNIPPET_FILES[s]:
            ### look for uncategorized R Studio snippets
            r_none = list(rstd_snips[r][""].keys()) if r in rstd_snips.keys() and "" in rstd_snips[r].keys() else []
            if len(r_none) > 0 and s in subl_snips.keys():
                ### check if they exist and have been categorized on Sublime Text
                r_none_recat_options = dict([(snip_name, snip_sxn) for snip_sxn in subl_snips[s].keys() for snip_name in subl_snips[s][snip_sxn] if snip_sxn != ""])
                for k in r_none:
                    if k in r_none_recat_options.keys():
                        if r_none_recat_options[k] not in rstd_snips[r].keys():
                            rstd_snips[r][r_none_recat_options[k]] = {}
                        rstd_snips[r][r_none_recat_options[k]][k] = rstd_snips[r][""][k]
                        print("[rstudio][%s] %s: %s --> %s" % (r,k,"''",r_none_recat_options[k]))
                        del rstd_snips[r][""][k]
            ### look for uncategorized Sublime Text snippets
            s_none = list(subl_snips[s][""].keys()) if s in subl_snips.keys() and "" in subl_snips[s].keys() else []            
            if len(s_none) > 0 and r in rstd_snips.keys(): 
                ### check if they exist and have been categorized on R Studio
                s_none_recat_options = dict([(snip_name, snip_sxn) for snip_sxn in rstd_snips[r].keys() for snip_name in rstd_snips[r][snip_sxn] if snip_sxn != ""])                        
                for k in s_none:
                    if k in s_none_recat_options.keys():
                        if s_none_recat_options[k] not in subl_snips[s].keys():
                            subl_snips[s][s_none_recat_options[k]] = {}
                        subl_snips[s][s_none_recat_options[k]][k] = subl_snips[s][""][k]
                        print("[sublime][%s] %s: %s --> %s" % (s,k,"''",s_none_recat_options[k]))
                        del subl_snips[s][""][k]
    print("\nMerging Sublime Text and R snippets"); time.sleep(0.5)
    for s in SUBLIME_SOURCE_VALUES_TO_R_SNIPPET_FILES.keys():
        for r in SUBLIME_SOURCE_VALUES_TO_R_SNIPPET_FILES[s]:
            print("* %s -- %s" % (s,r))
            subl_snips[s] = subl_snips[s] if s in subl_snips.keys() else {}
            rstd_snips[r] = rstd_snips[r] if r in rstd_snips.keys() else {}
            for sxn in set(list(subl_snips[s].keys()) + list(rstd_snips[r].keys())):
                subl_snips[s][sxn] = subl_snips[s][sxn] if sxn in subl_snips[s].keys() else {}
                rstd_snips[r][sxn] = rstd_snips[r][sxn] if sxn in rstd_snips[r].keys() else {}     
                subl_snips[s][sxn].update(rstd_snips[r][sxn])
                rstd_snips[r][sxn].update(subl_snips[s][sxn])

    return((subl_snips, rstd_snips))

def save_rstudio_snippets(rstd_snips):
    ## write new snippet files
    print("\nSaving new R Studio snippets to `%s`" % os.environ["RSTUDIO_SNIPPETS_PATH"]); time.sleep(0.5)
    for l in rstd_snips.keys():
        rstd_snip_fpath = os.path.join(os.environ["RSTUDIO_SNIPPETS_PATH"], l)
        print("* " + rstd_snip_fpath)
        with open(rstd_snip_fpath, "w") as fp:
            for s in rstd_snips[l].keys():
                if len(rstd_snips[l][s]) > 0:
                    fp.write("\n" + (R_SNIPPETS_SECTION_TEMPLATE % s))
                    for (k, v) in rstd_snips[l][s].items():
                        fp.write("\n\nsnippet " + k)
                        v = v.strip()
                        for v_j in v.split("\n"):
                            fp.write("\n\t" + v_j)

def save_sublime_snippets(subl_snips):
    for fn in os.listdir(os.environ["SUBLIME_SNIPPETS_PATH"]):
        if fn.endswith(".sublime-snippet"):
            src = os.path.join(os.environ["SUBLIME_SNIPPETS_PATH"], fn)
            os.remove(src)

    # Note: making backups seems to interfere with snippets, so just removing old ones for now
    # ## move old snippet files to back-up folder
    # subl_bak_path = os.path.join(os.environ["SUBLIME_SNIPPETS_PATH"], "bak")
    # if not os.path.exists(subl_bak_path):
    #     os.makedirs(subl_bak_path)
    # print("\nMoving old Sublime snippets to `%s`" % subl_bak_path); time.sleep(0.5)
    # for fn in os.listdir(os.environ["SUBLIME_SNIPPETS_PATH"]):
    #     if fn.endswith(".sublime-snippet"):
    #         src = os.path.join(os.environ["SUBLIME_SNIPPETS_PATH"], fn)
    #         dest = os.path.join(subl_bak_path, fn)
    #         if os.path.exists(dest):
    #             os.remove(dest)
    #         os.rename(src, dest)
    ## write new snippet files
    print("\nSaving new Sublime snippets to `%s`" % os.environ["SUBLIME_SNIPPETS_PATH"]); time.sleep(0.5)   
    for l in subl_snips.keys():
        for s in subl_snips[l].keys():
            for (k, v) in subl_snips[l][s].items():
                snip_txt = SUBLIME_SNIPPET_TEMPLATE % (v, k, l)
                l1 = l.split(".")[-1].title()
                s1 = s.upper()
                subl_snip_fpath = os.path.join(os.environ["SUBLIME_SNIPPETS_PATH"], "%s %s %s.sublime-snippet" % (l1, s1, k))
                print("* " + subl_snip_fpath)
                with open(subl_snip_fpath, "w") as f:
                    f.write(snip_txt)

## --------------------------------------------------------
## MAIN
## --------------------------------------------------------

if __name__ == '__main__':
    load_dot_env()

    subl_snips = get_sublime_snippets()
    rstd_snips = get_rstudio_snippets()
    
    (subl_snips, rstd_snips) = combine_snippets(subl_snips, rstd_snips)

    backup_curr_rstudio_snippets()
    backup_snippets(subl_snips, rstd_snips)

    save_sublime_snippets(subl_snips)
    save_rstudio_snippets(rstd_snips)

    print("\nDONE.")
