import argparse, json
import util_common, util_reach



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='.')
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('--reach-move', type=str, help='Reachability move rules, from: ' + ','.join(util_reach.RMOVE_LIST) + '.')
    args = parser.parse_args()

    if args.reach_move is not None:
        move_template = util_reach.get_move_template(args.reach_move)

        out = []
        for dest, need_open_path, need_open_aux, need_closed_path, need_closed_aux in move_template:
            out.append({
                'dest': dest,
                'need_open_path': need_open_path,
                'need_open_aux': need_open_aux,
                'need_closed_path': need_closed_path,
                'need_closed_aux': need_closed_aux
            })

        print(json.dumps(out))
