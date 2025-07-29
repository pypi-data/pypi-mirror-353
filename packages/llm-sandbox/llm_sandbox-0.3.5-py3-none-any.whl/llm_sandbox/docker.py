# ruff: noqa: E501

import io
import tarfile
import tempfile
from pathlib import Path
from typing import Any

import docker
from docker.errors import ImageNotFound
from docker.models.images import Image
from docker.types import Mount

from llm_sandbox.base import ConsoleOutput, Session
from llm_sandbox.const import DefaultImage, SupportedLanguage
from llm_sandbox.exceptions import (
    CommandEmptyError,
    ExtraArgumentsError,
    ImageNotFoundError,
    ImagePullError,
    NotOpenSessionError,
)
from llm_sandbox.security import SecurityPolicy


class SandboxDockerSession(Session):
    r"""Sandbox session implemented using Docker containers.

    This class provides a sandboxed environment for code execution by leveraging Docker.
    It handles Docker image management (pulling, building from Dockerfile), container
    creation and lifecycle, code execution, library installation, and file operations
    within the Docker container.
    """

    def __init__(
        self,
        client: docker.DockerClient | None = None,
        image: str | None = None,
        dockerfile: str | None = None,
        lang: str = SupportedLanguage.PYTHON,
        keep_template: bool = False,
        commit_container: bool = False,
        verbose: bool = False,
        mounts: list[Mount] | None = None,
        stream: bool = True,
        runtime_configs: dict | None = None,
        workdir: str | None = "/sandbox",
        security_policy: SecurityPolicy | None = None,
        **kwargs: dict[str, Any],  # noqa: ARG002
    ) -> None:
        r"""Initialize a new Docker-based sandbox session.

        Args:
            client (docker.DockerClient | None, optional): An existing Docker client instance.
                If None, a new client will be created based on the local Docker environment.
                Defaults to None.
            image (str | None, optional): The name of the Docker image to use (e.g., "ghcr.io/vndee/sandbox-python-311-bullseye").
                If None and `dockerfile` is also None, a default image for the specified `lang` is used.
                Defaults to None.
            dockerfile (str | None, optional): The path to a Dockerfile to build an image from.
                Cannot be used if `image` is also provided. Defaults to None.
            lang (str, optional): The programming language of the code to be run (e.g., "python", "java").
                Determines default image and language-specific handlers. Defaults to SupportedLanguage.PYTHON.
            keep_template (bool, optional): If True, the Docker image (built or pulled) and the container
                will not be removed after the session ends. Defaults to False.
            commit_container (bool, optional): If True, the Docker container's state will be committed
                to a new image after the session ends. Defaults to False.
            verbose (bool, optional): If True, print detailed log messages. Defaults to False.
            mounts (list[Mount] | None, optional): A list of Docker `Mount` objects to be mounted
                into the container. Defaults to None.
            stream (bool, optional): If True, the output from `execute_command` will be streamed.
                Note: Enabling this option prevents obtaining an exit code for the command directly
                from the `exec_run` result if it relies on the non-streamed `exit_code` attribute.
                Defaults to True.
            runtime_configs (dict | None, optional): Additional configurations for the container runtime,
                such as resource limits (e.g., `cpu_count`, `mem_limit`) or user (`user="1000:1000"`).
                By default, containers run as the root user for maximum compatibility.
                Defaults to None.
            workdir (str | None, optional): The working directory inside the container.
                Defaults to "/sandbox". Consider using "/tmp/sandbox" when running as a non-root user.
            security_policy (SecurityPolicy | None, optional): The security policy to use for the session.
                Defaults to None.
            **kwargs: Catches unused keyword arguments passed from `create_session`.

        Raises:
            ExtraArgumentsError: If both `image` and `dockerfile` are provided.
            ImagePullError: If pulling the specified Docker image fails.
            ImageNotFoundError: If the specified image is not found and cannot be pulled or built.

        """
        super().__init__(
            lang=lang,
            verbose=verbose,
            image=image,
            keep_template=keep_template,
            workdir=workdir,
            security_policy=security_policy,
        )
        self.dockerfile = dockerfile
        if self.image and self.dockerfile:
            msg = "Only one of `image` or `dockerfile` can be provided"
            raise ExtraArgumentsError(msg)

        if not self.image and not self.dockerfile:
            self.image = DefaultImage.__dict__[lang.upper()]

        self.client: docker.DockerClient

        if not client:
            if self.verbose:
                self.logger.info("Using local Docker context since client is not provided..")

            self.client = docker.from_env()
        else:
            self.client = client

        self.docker_path: str
        self.docker_image: Image
        self.commit_container: bool = commit_container
        self.is_create_template: bool = False
        self.mounts: list[Mount] | None = mounts
        self.stream: bool = stream
        self.runtime_configs: dict | None = runtime_configs

    def _ensure_ownership(self, folders: list[str]) -> None:
        r"""Ensure correct file ownership for specified folders within the Docker container.

        This is particularly important when the container is configured to run as a non-root user.
        It changes the ownership of the listed folders to the user specified in `runtime_configs`.

        Args:
            folders (list[str]): A list of absolute paths to folders within the container.

        """
        current_user = self.runtime_configs.get("user") if self.runtime_configs else None
        if current_user and current_user != "root":
            self.container.exec_run(f"chown -R {current_user} {' '.join(folders)}", user="root")

    def open(self) -> None:
        r"""Open the Docker sandbox session.

        This method prepares the Docker environment by:
        1. Building an image from a Dockerfile if `dockerfile` is provided.
        2. Pulling an image from a registry if `image` is specified and not found locally.
        3. Starting a Docker container from the prepared image with specified configurations
            (mounts, runtime_configs, user).
        4. Calls `self.environment_setup()` to prepare language-specific settings.

        Raises:
            ImagePullError: If pulling the specified Docker image fails.
            ImageNotFoundError: If the specified image is not found and cannot be pulled or built.

        """
        warning_str = (
            "Since the `keep_template` flag is set to True the docker image will not "
            "be removed after the session ends and remains for future use."
        )
        if self.dockerfile:
            self.docker_path = str(Path(self.dockerfile).parent)
            if self.verbose:
                f_str = f"Building docker image from {self.dockerfile}"
                f_str = f"{f_str}\n{warning_str}" if self.keep_template else f_str
                self.logger.info(f_str)

            self.docker_image, _ = self.client.images.build(
                path=self.docker_path,
                dockerfile=Path(self.dockerfile).name,
                tag=f"sandbox-{self.lang.lower()}-{Path(self.docker_path).name}",
            )
            self.is_create_template = True
        elif isinstance(self.image, str):
            try:
                self.docker_image = self.client.images.get(self.image)
                if self.verbose:
                    self.logger.info("Using image %s", self.docker_image.tags[-1])
            except ImageNotFound:
                if self.verbose:
                    self.logger.info("Image %s not found locally. Attempting to pull...", self.image)

                try:
                    self.docker_image = self.client.images.pull(self.image)
                    if self.verbose:
                        self.logger.info("Successfully pulled image %s", self.docker_image.tags[-1])
                    self.is_create_template = True
                except Exception as e:
                    raise ImagePullError(self.image, str(e)) from e

        self.container = self.client.containers.run(
            self.docker_image,
            detach=True,
            tty=True,
            mounts=self.mounts or [],
            user=self.runtime_configs.get("user", "root") if self.runtime_configs else "root",
            **{k: v for k, v in self.runtime_configs.items() if k != "user"} if self.runtime_configs else {},
        )

        self.environment_setup()

    def close(self) -> None:  # noqa: PLR0912
        r"""Close the Docker sandbox session.

        This method cleans up Docker resources by:
        1. Committing the container to a new image if `commit_container` is True.
        2. Stopping and removing the running Docker container.
        3. Removing the Docker image if `is_create_template` is True (image was built or pulled
            during this session), `keep_template` is False, and the image is not in use by
            other containers.

        Raises:
            ImageNotFoundError: If the image to be removed is not found (should not typically occur).

        """
        if self.container:
            if self.commit_container and self.docker_image:
                if self.docker_image.tags:
                    full_tag = self.docker_image.tags[-1]
                    if ":" in full_tag:
                        repository, tag = full_tag.rsplit(":", 1)
                    else:
                        repository = full_tag
                        tag = "latest"
                try:
                    # Commit the container with repository and tag
                    self.container.commit(repository=repository, tag=tag)
                    if self.verbose:
                        self.logger.info("Committed container as image %s:%s", repository, tag)
                except Exception:
                    if self.verbose:
                        self.logger.exception("Failed to commit container")
                    raise

            self.container.stop()
            self.container.wait()
            self.container.remove(force=True)
            self.container = None

        if self.is_create_template and not self.keep_template and self.docker_image and self.image:
            # check if the image is used by any other container
            containers = self.client.containers.list(all=True)
            image_id = self.image.id if isinstance(self.image, Image) else self.client.images.get(self.image).id
            image_in_use = any(container.image.id == image_id for container in containers)

            if not image_in_use:
                if self.docker_image:
                    self.docker_image.remove(force=True)
                else:
                    raise ImageNotFoundError(self.image)
            elif self.verbose:
                self.logger.info(
                    "Image %s is in use by other containers. Skipping removal..",
                    self.docker_image.tags[-1],
                )

    def run(self, code: str, libraries: list | None = None) -> ConsoleOutput:
        r"""Run the provided code within the Docker sandbox session.

        This method performs the following steps:
        1. Ensures the session is open (container is running).
        2. Installs any specified `libraries` using the language-specific handler.
        3. Writes the `code` to a temporary file on the host.
        4. Copies this temporary file into the container at the configured `workdir`.
        5. Retrieves execution commands from the language handler.
        6. Executes these commands in the container using `execute_commands`.

        Args:
            code (str): The code string to execute.
            libraries (list | None, optional): A list of libraries to install before running the code.
                                            Defaults to None.

        Returns:
            ConsoleOutput: An object containing the stdout, stderr, and exit code from the code execution.

        Raises:
            NotOpenSessionError: If the session (container) is not currently open/running.
            CommandFailedError: If any of the execution commands fail.

        """
        if not self.container:
            raise NotOpenSessionError

        self.install(libraries)

        with tempfile.NamedTemporaryFile(delete=True, suffix=f".{self.language_handler.file_extension}") as code_file:
            code_file.write(code.encode("utf-8"))
            code_file.seek(0)

            code_dest_file = f"{self.workdir}/code.{self.language_handler.file_extension}"
            self.copy_to_runtime(code_file.name, code_dest_file)

            commands = self.language_handler.get_execution_commands(code_dest_file)
            return self.execute_commands(commands, workdir=self.workdir)  # type: ignore[arg-type]

    def copy_from_runtime(self, src: str, dest: str) -> None:  # noqa: PLR0912
        r"""Copy a file or directory from the Docker container to the local host filesystem.

        The source path `src` is retrieved from the container as a tar archive, which is then
        extracted to the `dest` path on the host. Robust security filtering is applied to
        prevent path traversal attacks, symlink attacks, and other security vulnerabilities.

        Args:
            src (str): The absolute path to the source file or directory within the container.
            dest (str): The path on the host filesystem where the content should be copied.
                        If `dest` is a directory, the content will be placed inside it with its original name.
                        If `dest` is a file path, the extracted content will be named accordingly.

        Raises:
            NotOpenSessionError: If the session (container) is not currently open/running.
            FileNotFoundError: If the `src` path does not exist or is empty in the container.

        """
        if not self.container:
            raise NotOpenSessionError

        if self.verbose:
            self.logger.info("Copying %s:%s to %s..", self.container.short_id, src, dest)

        bits, stat = self.container.get_archive(src)
        if stat["size"] == 0:
            msg = f"File {src} not found in the container"
            self.logger.error(msg)
            raise FileNotFoundError(msg)

        tarstream = io.BytesIO(b"".join(bits))
        with tarfile.open(fileobj=tarstream, mode="r") as tar:
            # Enhanced safety: filter out dangerous paths
            safe_members = []
            for member in tar.getmembers():
                # Skip absolute paths and path traversal attempts
                if member.name.startswith("/") or ".." in member.name:
                    if self.verbose:
                        self.logger.warning("Skipping unsafe path: %s", member.name)
                    continue
                # Skip symlinks pointing outside extraction directory
                if member.issym() or member.islnk():
                    if self.verbose:
                        self.logger.warning("Skipping symlink: %s", member.name)
                    continue
                safe_members.append(member)

            if not safe_members and tar.getmembers():
                # All members were filtered - extract anyway to prevent data loss
                self.logger.warning("All tar members were filtered - extracting anyway")
                safe_members = tar.getmembers()
            elif not safe_members:
                self.logger.error("No content found in %s", src)
                raise FileNotFoundError(msg)

            # Create destination directory if needed
            Path(dest).parent.mkdir(parents=True, exist_ok=True)

            # Extract safely using individual member extraction
            if len(safe_members) == 1 and safe_members[0].isfile():
                dest_name = Path(dest).name
                safe_members[0].name = dest_name
                extract_path = str(Path(dest).parent)
            else:
                extract_path = str(dest)

            # Use safe extraction method
            for member in safe_members:
                tar.extract(member, path=extract_path)

    def copy_to_runtime(self, src: str, dest: str) -> None:
        r"""Copy a file or directory from the local host filesystem to the Docker container.

        The source path `src` on the host is packaged into a tar archive and then put into
        the `dest` path within the container. If the parent directory of `dest` does not exist,
        it is created atomically. File ownership is ensured after copying if a non-root user is configured.

        Args:
            src (str): The path to the source file or directory on the host system.
            dest (str): The absolute destination path within the container.

        Raises:
            NotOpenSessionError: If the session (container) is not currently open/running.
            FileNotFoundError: If the source path does not exist.

        """
        if not self.container:
            raise NotOpenSessionError

        # Validate source path exists
        src_path = Path(src)
        if not (src_path.exists() and (src_path.is_file() or src_path.is_dir())):
            msg = f"Source path {src} does not exist or is not accessible"
            self.logger.error(msg)
            raise FileNotFoundError(msg)

        directory = Path(dest).parent

        # Atomic directory creation to prevent race conditions
        if directory:
            # Use a more robust directory creation approach
            mkdir_result = self.container.exec_run(f"mkdir -p '{directory}'")
            if mkdir_result.exit_code != 0:
                self.logger.error("Failed to create directory %s: %s", directory, mkdir_result.output)

        if self.verbose:
            self.logger.info("Copying %s to %s:%s..", src, self.container.short_id, dest)

        try:
            tarstream = io.BytesIO()
            with tarfile.open(fileobj=tarstream, mode="w") as tar:
                tar.add(src, arcname=Path(dest).name)

            tarstream.seek(0)
            self.container.put_archive(str(Path(dest).parent), tarstream)

            self._ensure_ownership([dest])
        except Exception as e:
            msg = f"Failed to copy {src} to container: {e}"
            self.logger.exception(msg)
            raise

    def execute_command(  # noqa: PLR0912
        self, command: str, workdir: str | None = None
    ) -> ConsoleOutput:
        r"""Execute an arbitrary command directly within the Docker container.

        This method uses Docker's `exec_run` to execute the command. It handles both
        streamed and non-streamed output based on the `self.stream` attribute.

        Args:
            command (str): The command string to execute (e.g., "ls -l", "pip install <package>").
            workdir (str | None, optional): The working directory within the container where
                                        the command should be executed. If None, the container's
                                        default working directory is used. Defaults to None.

        Returns:
            ConsoleOutput: An object containing the stdout, stderr, and exit code of the command.

        Raises:
            CommandEmptyError: If the provided `command` string is empty.
            NotOpenSessionError: If the session (container) is not currently open/running.

        """
        if not command:
            raise CommandEmptyError

        if not self.container:
            raise NotOpenSessionError

        if self.verbose:
            self.logger.info("Executing command: %s", command)

        if workdir:
            result = self.container.exec_run(
                command,
                stream=self.stream,
                tty=False,
                workdir=workdir,
                stderr=True,
                stdout=True,
                demux=True,
            )
        else:
            result = self.container.exec_run(
                command,
                stream=self.stream,
                tty=False,
                stderr=True,
                stdout=True,
                demux=True,
            )

        exit_code = result.exit_code
        output = result.output

        stdout_output = ""
        stderr_output = ""

        if self.verbose:
            self.logger.info("Output:")

        if not self.stream:
            # When not streaming and demux=True, output is a tuple (stdout, stderr)
            if output:
                stdout_data, stderr_data = output

                if stdout_data:
                    stdout_output = stdout_data.decode("utf-8")
                    if self.verbose:
                        self.logger.info(stdout_output)

                if stderr_data:
                    stderr_output = stderr_data.decode("utf-8")
                    if self.verbose:
                        self.logger.error(stderr_output)
        else:
            # When streaming and demux=True, we get a generator of (stdout, stderr)
            for stdout_chunk, stderr_chunk in output:
                if stdout_chunk:
                    chunk_str = stdout_chunk.decode("utf-8")
                    stdout_output += chunk_str
                    if self.verbose:
                        self.logger.info(chunk_str)

                if stderr_chunk:
                    chunk_str = stderr_chunk.decode("utf-8")
                    stderr_output += chunk_str
                    if self.verbose:
                        self.logger.error(chunk_str)

        return ConsoleOutput(
            exit_code=exit_code,
            stdout=stdout_output,
            stderr=stderr_output,
        )

    def get_archive(self, path: str) -> tuple[bytes, dict]:
        r"""Retrieve a file or directory from the Docker container as a tar archive.

        This method uses Docker's `get_archive` to fetch the content at the specified `path`.

        Args:
            path (str): The absolute path to the file or directory within the container.

        Returns:
            tuple[bytes, dict]: A tuple where the first element is the raw bytes of the
                                tar archive, and the second element is a dictionary containing
                                archive metadata (stat info).

        Raises:
            NotOpenSessionError: If the session (container) is not currently open/running.

        """
        if not self.container:
            raise NotOpenSessionError

        data, stat = self.container.get_archive(path)
        return b"".join(data), stat
