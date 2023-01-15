"""
Copy snippet files that R Studio currently uses to this directory (safe).
"""

## --------------------------------------------------------
## PREAMBLE
## --------------------------------------------------------

import os

## --------------------------------------------------------
## HELPERS
## --------------------------------------------------------

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

## --------------------------------------------------------
## MAIN
## --------------------------------------------------------

if __name__ == '__main__':
    load_dot_env()

    local_dirpath = os.path.join(os.path.dirname(os.path.realpath(__file__)))
    rstud_snips = os.listdir(os.environ["RSTUDIO_SNIPPETS_PATH"])
    for fn in rstud_snips:
        print("Copying R Studio's `%s`" % fn)
        src_fp = os.path.join(os.environ["RSTUDIO_SNIPPETS_PATH"], fn)
        dest_fp = os.path.join(local_dirpath, fn)        
        if os.path.exists(dest_fp):
            print("* making backup (`%s`)" % dest_fp + ".bak")            
            os.rename(dest_fp, dest_fp + ".bak")
        os.system("cp %s %s" % (src_fp, dest_fp))

    print("\nDONE.")

