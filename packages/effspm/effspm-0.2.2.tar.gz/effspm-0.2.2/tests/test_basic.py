import time
from effspm import PrefixProjection,LargePrefixProjection, BTMiner,LargeHTMiner,HTMiner

DATAFILE    = "/Users/yeswanthvootla/Desktop/final_kosarak_s.txt"
OUTPUT_BASE = "/Users/yeswanthvootla/Desktop/final_kosarak_s_"
COMMON_ARGS = dict(
    data       = DATAFILE,
    minsup     = 0.01,
    time_limit = 36000,
    preproc    = 1,
    use_dic    = 0,
    verbose    = 0,
)

def run_and_report(name, fn):
    out_file = OUTPUT_BASE + name + ".txt"
    print(f"\n--- {name} miner ---")
    start = time.time()
    res   = fn(**COMMON_ARGS, out_file=out_file)
    took  = time.time() - start

    pats = res.get("patterns", [])
    wall = res.get("time", took)
    print(f"  → Found {len(pats)} patterns in {wall:.3f}s (wall: {took:.3f}s)")
    print(f"  → Sample patterns: {pats[:5]!r}")

if __name__ == "__main__":
    run_and_report("PrefixProjection", PrefixProjection)
    run_and_report("BTMiner",BTMiner)
    
    #run_and_report("LargeBTMiner",LargeBTMiner)
    run_and_report("LargeHTMiner",LargeHTMiner)

    run_and_report("LargePrefixProjection",LargePrefixProjection)
    
    run_and_report("HTMiner",HTMiner)
    
