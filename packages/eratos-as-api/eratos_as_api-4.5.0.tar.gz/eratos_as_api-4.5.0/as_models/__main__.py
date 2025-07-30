
from .log_levels import INFO

import argparse, os

def host(args):
    from .web_api import app

    app.config['model_path'] = args.pop('model')
    app.config['args'] = args

    host = os.environ.get('MODEL_HOST', '0.0.0.0')
    port = int(args.pop('port', os.environ.get('MODEL_PORT', 8080)))

    app.run(host=host, port=port)

# Create main arg parser.
parser = argparse.ArgumentParser(description='Analysis Services Model Integration Engine')
subparsers = parser.add_subparsers()

# Create the parser for the "host" command
install_model_parser = subparsers.add_parser('host', help='Host a model')
install_model_parser.add_argument('model', help='The path to the model\'s entrypoint file, its manifest, or the directory containing its manifest.')
install_model_parser.add_argument('-p', '--port', help='The port to run the web api on.', default=argparse.SUPPRESS)
install_model_parser.add_argument('-t', '--type', help='The model type.', default=argparse.SUPPRESS, type=str.lower)
install_model_parser.add_argument('-r', '--root', help='The model "root" directory.', default=argparse.SUPPRESS)
install_model_parser.add_argument('-d', '--debug', help='Run the model in debug mode?', action='store_true')
install_model_parser.add_argument('-l', '--log-level', help='Default log level (when not overridden on per-job basis).', default=INFO)
install_model_parser.set_defaults(func=host)

# TODO: install, validate, package commands?

# Parse command line.
namespace = parser.parse_args()
args = vars(namespace)

# Run selected function.
namespace.func(args)
