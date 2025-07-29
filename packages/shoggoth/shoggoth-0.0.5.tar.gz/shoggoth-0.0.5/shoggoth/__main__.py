import argparse
import os

os.environ["KIVY_NO_ARGS"] = "1"

parser = argparse.ArgumentParser(description='Shoggoth Card Creator')
parser.add_argument('-v', '--view', metavar='FILE', help='Open in viewer mode with specified file')
args = parser.parse_args()


if args.view:
    # Start in viewer mode
    from shoggoth.viewer import ViewerApp
    app = ViewerApp(args.view)
else:
    # Start in normal mode
    from shoggoth.main import ShoggothApp
    app = ShoggothApp()
app.run()
