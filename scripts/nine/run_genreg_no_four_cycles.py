"""Run the checkpointed GENREG search with the quartic codegree restriction."""
import run_genreg_treewidth
from build_genreg_no_four_cycles import build

if __name__=='__main__':
    run_genreg_treewidth.build=build
    run_genreg_treewidth.main()
