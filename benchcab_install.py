import yaml
import subprocess
import tempfile
import time
import string

CONFIG_FILE_NAME = "config.yaml"
TEMPDIR_PREFIX = "benchcab_install_"

def interpolate_string(input, mapping):
    return string.Template(input).substitute(mapping)

def fetch_repo(spec):
    src_path = tempfile.mkdtemp(prefix=TEMPDIR_PREFIX)
    if "git" in spec:
        url = spec["git"]["url"]
        subprocess.run(f"git clone {url} {src_path}", shell=True, check=True)
        ref = spec["git"].get("ref")
        if ref:
            time.sleep(0.01)
            subprocess.run(f"cd {src_path} && git reset --hard {ref}", shell=True, check=True)
    return src_path

def benchcab_install():

    with open(CONFIG_FILE_NAME) as file:
        config = yaml.safe_load(file)

    for model_config in config["models"]:
        template_mapping = dict()
        if "fetch_from" in model_config:
            template_mapping["MODEL_SOURCE"] = fetch_repo(model_config["fetch_from"])

        install_command = interpolate_string(
            model_config["install_command"], template_mapping
        )
        subprocess.run(install_command, shell=True, check=True)

        if "prefix_path" in model_config:
            prefix_path = interpolate_string(
                model_config["prefix_path"], template_mapping
            )
        else:
            prefix_path_command = interpolate_string(
                model_config["prefix_path_command"], template_mapping
            )
            prefix_path = subprocess.check_output(
                prefix_path_command, shell=True
            )
        print(f"prefix_path: {prefix_path}")

        version = model_config["version"]
        print(f"version: {version}")

if __name__ == "__main__":
    benchcab_install()
