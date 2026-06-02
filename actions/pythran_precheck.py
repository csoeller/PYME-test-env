import logging
logging.basicConfig(level=logging.INFO)


def pythran_precheck_and_fix():
    try:
        import pythran
    except ImportError:
        pythran_import_fails = True
    else:
        pythran_import_fails = False

    if not pythran_import_fails:
        try:
            import Cython.Compiler.Pythran
        except:
            cython_pythran_error = True
        else:
            cython_pythran_error = False

    import site
    from pathlib import Path
    pythran_loc = None
    for dir in site.getsitepackages():
        pythran_path = Path(dir) / 'pythran'
        if pythran_path.exists():
            pythran_loc = pythran_path
            logging.info('pythran is in site packages at "%s"' % pythran_path)

    if not pythran_import_fails and cython_pythran_error:
        logging.info("we have the likely cython issue and need to do something about the cached pythran")
        logging.info("we temporarily move pythran to __pythran...")
        import os
        try:
            os.rename(pythran_loc,pythran_loc.parent / '__pythran')
        except PermissionError:
            logging.warn("could not rename pythran directory, expect issues when building")
        except OSError as error:
            logging.warn("error trying to rename pythran: %s" % error)


if __name__ == "__main__":
    pythran_precheck_and_fix()

