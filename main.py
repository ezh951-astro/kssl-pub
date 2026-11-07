from flow_parametrizer import flow_generate_all_run_params
from flow_initializer import flow_submit_all_runs, flow_resubmit_existing_runs
from flow_monitor import monitor_and_process_all_runs



def run(set_name: str):

    flow_generate_all_run_params(set_name)
    flow_submit_all_runs(set_name)
    monitor_and_process_all_runs(set_name)

def restart(set_name: str):

    flow_resubmit_existing_runs(set_name)
    monitor_and_process_all_runs(set_name)   # always be looking for unconverted and unprocessed snapshots


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--set-name", help="name of the set of runs", required=True)
    parser.add_argument("-R", "--restart", action="store_true", help="restart the set of runs")
    args = parser.parse_args()

    if args.restart:
        restart(args.set_name)
    else:
        run(args.set_name)