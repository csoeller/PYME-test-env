import logging
logging.basicConfig(level=logging.INFO)

def pythran_cleanup():
    import site
    from pathlib import Path
    import os
    __pythran_loc = None
    for dir in site.getsitepackages():
        __pythran_path = Path(dir) / '__pythran'
        if __pythran_path.exists():
            __pythran_loc = __pythran_path
            logging.info('__pythran is in site packages at "%s"' % __pythran_path)
    if __pythran_loc is not None:
        logging.info("moving __pythran back to pythran")
        try:
            os.rename(__pythran_loc,__pythran_loc.parent / 'pythran')
        except PermissionError:
            logging.warn("could not rename __pythran directory, pythran install may be non-functional now")
        except OSError as error:
            logging.warn("error trying to rename __pythran: %s" % error)

if __name__ == "__main__":
    pythran_cleanup()

