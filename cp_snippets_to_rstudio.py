"""
Copy snippets in this directory to R Studio snippets directory (safe).
"""

## --------------------------------------------------------
## PREAMBLE
## --------------------------------------------------------

import os
import time

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
    local_snips = list(filter(lambda fn: fn.endswith(".snippets"), os.listdir(local_dirpath)))

    if not os.path.exists(os.path.join(os.environ["RSTUDIO_SNIPPETS_PATH"], "backups")):
        os.makedirs(os.path.join(os.environ["RSTUDIO_SNIPPETS_PATH"], "backups"))

    for fn in local_snips:
        print("Copying local `%s`" % fn)
        dest_fp = os.path.join(os.environ["RSTUDIO_SNIPPETS_PATH"], fn)
        src_fp = os.path.join(local_dirpath, fn)
        if fn in rstud_snips:
            print("* making backup (`%s`)" % (os.path.join(os.environ["RSTUDIO_SNIPPETS_PATH"], "backups", fn)))
            if os.path.exists(os.path.join(os.environ["RSTUDIO_SNIPPETS_PATH"], "backups", fn)):
                os.remove(os.path.join(os.environ["RSTUDIO_SNIPPETS_PATH"], "backups", fn))
            os.rename(dest_fp, os.path.join(os.environ["RSTUDIO_SNIPPETS_PATH"], "backups", fn))            
        os.system("cp '%s' '%s'" % (src_fp, os.environ["RSTUDIO_SNIPPETS_PATH"]))

    print("\nDONE.")
