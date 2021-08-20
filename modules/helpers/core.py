def get_args(args):
    damage = [int(arg) for arg in args if arg.isnumeric()]
    done = [True for arg in args if arg == 'd']

    if not damage:
        damage = [0]
    if not done:
        done = [False]

    return damage.pop(0), done.pop(0)