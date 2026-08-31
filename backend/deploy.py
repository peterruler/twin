import os
import shutil
import zipfile
import subprocess


def install_dependencies(package_dir: str):
    print("Installing dependencies for Lambda runtime...")

    docker_command = [
        "docker",
        "run",
        "--rm",
        "-v",
        f"{os.getcwd()}:/var/task",
        "--platform",
        "linux/amd64",
        "--entrypoint",
        "",
        "public.ecr.aws/lambda/python:3.12",
        "/bin/sh",
        "-c",
        f"pip install --target /var/task/{package_dir} -r /var/task/requirements.txt --platform manylinux2014_x86_64 --implementation cp --python-version 3.12 --abi cp312 --only-binary=:all: --upgrade",
    ]

    local_pip_command = [
        "uv",
        "pip",
        "install",
        "--target",
        package_dir,
        "-r",
        "requirements.txt",
        "--python-platform",
        "x86_64-manylinux2014",
        "--python-version",
        "3.12",
        "--only-binary=:all:",
        "--upgrade",
    ]

    if shutil.which("docker"):
        try:
            subprocess.run(docker_command, check=True)
            return
        except subprocess.CalledProcessError as exc:
            print(f"Docker packaging failed ({exc}). Falling back to local uv wheel install...")
    else:
        print("Docker not found. Falling back to local uv wheel install...")

    subprocess.run(local_pip_command, check=True)


def main():
    print("Creating Lambda deployment package...")

    # Clean up
    if os.path.exists("lambda-package"):
        shutil.rmtree("lambda-package")
    if os.path.exists("lambda-deployment.zip"):
        os.remove("lambda-deployment.zip")

    # Create package directory
    os.makedirs("lambda-package")

    install_dependencies("lambda-package")

    # Copy application files
    print("Copying application files...")
    for file in ["server.py", "lambda_handler.py", "context.py", "resources.py"]:
        if os.path.exists(file):
            shutil.copy2(file, "lambda-package/")
    
    # Copy data directory
    if os.path.exists("data"):
        shutil.copytree("data", "lambda-package/data")

    # Create zip
    print("Creating zip file...")
    with zipfile.ZipFile("lambda-deployment.zip", "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk("lambda-package"):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, "lambda-package")
                zipf.write(file_path, arcname)

    # Show package size
    size_mb = os.path.getsize("lambda-deployment.zip") / (1024 * 1024)
    print(f"✓ Created lambda-deployment.zip ({size_mb:.2f} MB)")


if __name__ == "__main__":
    main()
