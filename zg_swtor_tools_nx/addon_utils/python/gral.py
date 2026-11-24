# ----------------------------------------------------------------------------

def get_documents_dir():
    """
    Retrieve the absolute path to the current user's Documents directory.

    This function supports Windows, macOS, and Linux, accounting for
    differences in how each operating system handles user directories.

    Platform-specific behavior:
        Windows:
            Uses the USERPROFILE environment variable to locate the
            user's home directory, then appends the Documents folder.
            Example: C:\\Users\\john\\Documents
            
            (Windows installations with redirected or customized
             Documents folders would require the Windows
             Known Folders API for complete accuracy, though.)

        macOS:
            Uses the user's home directory, typically located under
            /Users/<username>, then appends the Documents folder.
            Example: /Users/john/Documents

        Linux:
            Attempts to retrieve the Documents directory using the
            xdg-user-dir utility. This respects the user's XDG
            configuration, which allows Documents to be located
            somewhere other than the default $HOME/Documents path.

            If xdg-user-dir is unavailable, fails, or returns a
            directory that does not exist, the function falls back
            to $HOME/Documents.

    Returns:
        pathlib.Path:
            An absolute Path object representing the user's
            Documents directory.

    Notes:
        - The function does not create the Documents directory.
        - Linux systems may require the xdg-user-dirs package.
        - If the configured Linux Documents directory does not exist,
          the default $HOME/Documents path is returned.
        - The returned path is not guaranteed to exist.
    """

    import os
    import platform
    import subprocess
    from pathlib import Path


    # Identify the operating system so that the appropriate
    # platform-specific method can be used.
    system = platform.system()

    # Resolve the current user's home directory.
    # This avoids hardcoding usernames or home directory locations.
    home = Path.home()

    if system == "Linux":
        # Linux supports configurable standard user directories
        # through the XDG User Directory specification.
        #
        # Use xdg-user-dir to retrieve the configured Documents
        # directory rather than assuming it is always located at
        # $HOME/Documents.
        try:
            result = subprocess.run(
                ["xdg-user-dir", "DOCUMENTS"],
                capture_output=True,
                text=True,
                check=True,
                timeout=5
            )

            # Convert the command output into a pathlib.Path object.
            # Remove any surrounding whitespace or newline characters.
            path = Path(result.stdout.strip())

            # Only accept an absolute path that points to an existing
            # directory. Otherwise, continue to the fallback behavior.
            if path.is_absolute() and path.is_dir():
                return path

        except (FileNotFoundError, subprocess.SubprocessError):
            # FileNotFoundError:
            #   The xdg-user-dir executable is not installed or
            #   cannot be found in the system PATH.
            #
            # SubprocessError:
            #   The command failed, timed out, or returned a
            #   non-zero exit status.
            #
            # In either case, fall back to the conventional
            # Documents directory under the user's home directory.
            pass

    elif system == "Windows":
        # Windows stores user-specific files under USERPROFILE.
        # Append Documents to obtain the conventional Documents path.
        #
        # Example:
        #   USERPROFILE = C:\Users\john
        #   Result      = C:\Users\john\Documents
        return Path(os.environ["USERPROFILE"]) / "Documents"

    # macOS uses /Users/<username> as the conventional home directory.
    # Linux also conventionally uses /home/<username>.
    #
    # For both platforms, Documents is normally a subdirectory
    # of the user's home directory.
    #
    # This also serves as the fallback for Linux if the XDG lookup
    # fails or the configured directory does not exist.
    return home / "Documents"

# ----------------------------------------------------------------------------

def load_xml_file(file_path):
    """
    Open an XML file and return its contents as an ElementTree object.

    Parameters:
    file_path (str): The path to the XML file to be opened.

    Returns:
    ElementTree: The contents of the XML file as an ElementTree object.

    Raises:
    FileNotFoundError: If the specified file does not exist.
    ET.ParseError: If the file contains invalid XML.
    Exception: For any other exceptions that may occur.
    """

    import xml.etree.ElementTree as ET


    try:
        # Parse the XML file
        tree = ET.parse(file_path)
        
        return tree

    except FileNotFoundError:
        # Raise an error if the file is not found
        print(f"Error: The file '{file_path}' does not exist.")
        raise

    except ET.ParseError:
        # Raise an error if the file contains invalid XML
        print(f"Error: The file '{file_path}' contains invalid XML.")
        raise

    except Exception as e:
        # Raise any other exceptions that may occur
        print(f"An unexpected error occurred: {e}")
        raise

# ----------------------------------------------------------------------------

def load_json_file(file_path):
    """
    Open a JSON file and return its contents as a Python dictionary.

    Parameters:
    file_path (str): The path to the JSON file to be opened.

    Returns:
    dict: The contents of the JSON file as a dictionary.

    Raises:
    FileNotFoundError: If the specified file does not exist.
    json.JSONDecodeError: If the file contains invalid JSON.
    Exception: For any other exceptions that may occur.
    """

    import json


    try:
        # Open the file in read mode
        with open(file_path, 'r') as file:
            # Load the JSON data from the file
            data = json.load(file)
        
        return data

    except FileNotFoundError:
        # Raise an error if the file is not found
        print(f"Error: The file '{file_path}' does not exist.")
        raise

    except json.JSONDecodeError:
        # Raise an error if the file contains invalid JSON
        print(f"Error: The file '{file_path}' contains invalid JSON.")
        raise

    except Exception as e:
        # Raise any other exceptions that may occur
        print(f"An unexpected error occurred: {e}")
        raise

# ----------------------------------------------------------------------------

