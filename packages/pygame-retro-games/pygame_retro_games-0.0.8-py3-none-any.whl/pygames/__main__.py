from argparse import ArgumentParser
from pygames.bounce.main import run as bounce
from pygames.invaders.main import run as invaders


parser = ArgumentParser(description='PyGame Retro Games')
parser.add_argument('cmd', choices=['bounce', 'invaders'])
args = parser.parse_args()
if args.cmd == 'bounce':
    bounce()
elif args.cmd == 'invaders':
    invaders()

