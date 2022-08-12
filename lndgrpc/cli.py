import os
from pathlib import Path
import code
import subprocess

import click
from yachalk import chalk

from lndgrpc.client import LNDClient

@click.group()
def cli():
    pass

@click.command(help="Enter a Python REPL with access to your node")
def shell():
    # LNDClient gets all configuration parameters from environment variables!
    lnd = LNDClient()

    # Enter a shell for interacting with LND
    code.interact(local=dict(globals(), **locals()))

@click.command(help="Input and save your credentials to disk")
@click.option('--input_format', default="base64", type=click.Choice(["hex", "base64"]), help="Input format")
@click.option('--credential_type', default="macaroon", type=click.Choice(["macaroon", "tls"]), help="Input Type")
def credentials(input_format, credential_type):
    credential_path = Path(os.getenv("LND_CRED_PATH", None))
    subprocess.check_call(["stty","-icanon"])
    print(f"Saving credentials to: {credential_path}")
    input_data = click.prompt(chalk.yellow.bold(f"Enter your node's {credential_type}"), type=str, default="")
    if input_format == "hex":
        data = bytes.fromhex(input_data)
    elif input_format == "base64":
        data = base64.b64decode(input_data)

    output_file = None
    if credential_type == "tls":
        output_file = credential_path.joinpath("tls.cert")
        with open(output_file, "wb") as f:
            f.write(data)

    if credential_type == "macaroon":
        macaroon_name = click.prompt(chalk.yellow.bold(f"Enter your macaroon name:"), type=str, default="admin")
        output_file = credential_path.joinpath(f"{macaroon_name}.macaroon")
        with open(output_file, "wb") as f:
            f.write(data)
        
        print(f"Enable this macaroon by running:\n", chalk.red.bg_yellow(f"export LND_MACAROON={output_file.name}"))

    subprocess.check_call(["stty","icanon"])
    print(f"Wrote file: {output_file}")

@click.command(help="Create an environment file")
def environment():
    print("Saving credentials!")
    node_uri = click.prompt(chalk.yellow.bold("Enter your node's IP Address"), type=str, default="127.0.0.1")
    print(chalk.white(node_uri))
    
    node_port = click.prompt(chalk.yellow.bold("Enter your node's Port"), type=str, default="10009")
    print(chalk.white(node_port))
    
    node_nickname = click.prompt(chalk.yellow.bold("Enter your node's Alias"), type=str, default="default-node-alias")
    print(chalk.white(node_nickname))

    default_root_path = Path.expanduser(Path("~")).joinpath("Documents").joinpath("lnd-creds").joinpath(node_nickname)
    default_path = default_root_path.joinpath("lnd")
    credential_path = Path(click.prompt(chalk.yellow.bold("Where do you want keep your node credentials? Macaroons and tls.cert?"), type=str, default=default_root_path))

    macaroon_filename = click.prompt(chalk.yellow.bold("Enter your macaroon filename"), type=str, default="admin.macaroon")

    save_env_file = click.prompt(chalk.yellow.bold(f"Build directory structure and save `node-env` file at location: {default_root_path}"), type=bool, default=True)
    env_file = f"""
export LND_CRED_PATH={credential_path}
export LND_NODE_IP={node_uri}
export LND_NODE_PORT={node_port}
export LND_MACAROON={macaroon_filename}"""
    print(chalk.red.bold("This environment file must be loaded to access your node!"))
    print(chalk.red.bg_yellow(env_file))
    if save_env_file:
        print("Writing file....")
        credential_path.joinpath("lnd").mkdir( parents=True, exist_ok=True)
        env_file_path = credential_path.joinpath("node-env")
        with open(env_file_path, "w") as f:
            f.write(env_file)

        print(f"Wrote environment file to location: {env_file_path}")
        print(f"Enable it by running:", chalk.red.bg_yellow(f"source {env_file_path}"))
    else:
        print("Not saving file...")


cli.add_command(shell)
cli.add_command(credentials)
cli.add_command(environment)


if __name__ == '__main__':
    cli()