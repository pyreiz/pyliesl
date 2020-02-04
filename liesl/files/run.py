"""
Runfile
-------
"""
from pathlib import Path


class Run(Path):
    """a runfile automatically increasing its runcount during instantiation

    args
    ----
    fname:str
        the filename, requires the suffix .xdf


    Example::

        run = Run("test")
        print(run.name) # prints test_R001.xdf    


    """

    def __new__(cls, fname: str):
        fname = Path(str(fname)).expanduser().absolute()
        if fname.suffix == "":
            fname = fname.with_suffix(".xdf")
        if fname.suffix != ".xdf":
            raise ValueError("Filename must end in .xdf")

        count = 0
        base_stem = fname.stem.split("_R")[0]
        for f in fname.parent.glob(fname.stem + "*.xdf"):
            base_stem, run_counter = f.stem.split("_R")
            count = max(int(run_counter), count)
        count += 1
        run_str = "_R{0:03d}".format(count)

        final_name = fname.with_name(base_stem + run_str).with_suffix(".xdf")
        return Path(final_name)
