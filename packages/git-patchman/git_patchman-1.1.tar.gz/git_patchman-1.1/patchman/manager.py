import os
import subprocess


class PatchManager:
    def __init__(self, repo_path="."):
        """
        Initialize the PatchManager class.

        Args:
            repo_path (str): The path to the Git repository.
            Defaults to the current directory.
        """
        self.repo_path = os.path.abspath(repo_path)
        self.patch_dir = os.path.join(self.repo_path, ".git", "patchman")
        os.makedirs(self.patch_dir, exist_ok=True)

    def list(self):
        files = os.listdir(self.patch_dir)
        return [self._to_name(path) for path in files]

    def add(self, name: str, commit: str, from_changes: bool):
        """
        Generate a patch from a commit or uncommitted changes
        and save it as a file.

        Args:
            name (str): The name of the patch file (without extension).
            commit (str): The Git commit identifier.
            from_changes (bool): Whether to use uncommitted changes
            instead of a commit.

        Raises:
            ValueError: If the repository path is invalid
            or the Git command fails.
        """
        patch_file_path = self._to_path(name)
        if from_changes:
            # Generate a patch for uncommitted changes
            command = ["diff"]
        else:
            # Generate a patch for the specified commit
            command = ["format-patch", "-1", "--stdout", commit]

        result = self.__execute_git_command(command)
        if not result:
            return

        with open(patch_file_path, "w") as patch_file:
            patch_file.write(result)

    def rename(self, old_name: str, new_name: str):
        """
        Rename a patch file.

        Args:
            old_name (str): The current name of the patch file (without extension).
            new_name (str): The new name for the patch file (without extension).

        Raises:
            FileNotFoundError: If the original patch file does not exist.
            FileExistsError: If a patch with the new name already exists.
        """
        old_path = self._to_path(old_name)
        new_path = self._to_path(new_name)
        if not os.path.exists(old_path):
            raise FileNotFoundError(f"No such patch: {old_name}")
        if os.path.exists(new_path):
            raise FileExistsError(f"Patch with name '{new_name}' already exists.")
        os.rename(old_path, new_path)

    def delete(self, name: str):
        """
        Delete a patch file with the given name.

        Args:
            name (str): The name of the patch file (without extension).

        Raises:
            FileNotFoundError: If the specified patch file does not exist.
        """
        patch_file_path = os.path.join(self.patch_dir, f"{name}.patch")
        if os.path.exists(patch_file_path):
            os.remove(patch_file_path)
        else:
            raise FileNotFoundError(f"No such patch: {name}")

    def apply(self, name: str, revert: bool = False):
        """
        Apply or revert a patch with the given name.

        Args:
            name (str): The name of the patch file (without extension).
            revert (bool): Whether to revert the patch instead of applying it.
                           Defaults to False.

        Raises:
            FileNotFoundError: If the specified patch file does not exist.
            ValueError: If the Git command fails.
        """
        patch_file_path = self._to_path(name)
        if not os.path.exists(patch_file_path):
            raise FileNotFoundError(f"No such patch: {name}")

        # Prepare the git apply command
        command = ["apply"]
        if revert:
            command.append("--reverse")
        command.append(patch_file_path)

        self.__execute_git_command(command)

    def diff(self, name: str, revert: bool = False):
        """
        Print a patch's diff with the given name.

        Args:
            name (str): The name of the patch file (without extension).

        Raises:
            FileNotFoundError: If the specified patch file does not exist.
            ValueError: If the Git command fails.
        """
        patch_file_path = self._to_path(name)
        if not os.path.exists(patch_file_path):
            raise FileNotFoundError(f"No such patch: {name}")

        subprocess.run(["less", patch_file_path], check=True)

    def edit(self, name: str):
        """
        Open the patch file in vim for editing.

        Args:
            name (str): The name of the patch file (without extension).

        Raises:
            FileNotFoundError: If the specified patch file does not exist.
            subprocess.CalledProcessError: If vim fails to open the file.
        """
        patch_file_path = self._to_path(name)
        if not os.path.exists(patch_file_path):
            raise FileNotFoundError(f"No such patch: {name}")
        
        subprocess.run(["vim", patch_file_path], check=True)

    def __execute_git_command(self, cmd) -> (str, str):
        try:
            result = subprocess.run(
                ["git"] + cmd,
                cwd=self.repo_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True,
            )

            return result.stdout
        except subprocess.CalledProcessError as e:
            print(e.stderr.strip())

    def _to_path(self, name):
        return os.path.join(self.patch_dir, f"{name}.patch")

    def _to_name(self, path):
        return os.path.splitext(path)[0]
