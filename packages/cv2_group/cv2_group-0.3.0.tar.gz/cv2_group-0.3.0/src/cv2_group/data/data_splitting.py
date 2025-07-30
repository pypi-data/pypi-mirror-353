# Imports
import os
from typing import List, Tuple

from azure.ai.ml import MLClient
from azure.identity import InteractiveBrowserCredential
from azureml.core import Dataset, Workspace
from azureml.core.authentication import InteractiveLoginAuthentication


def authenticate_clients() -> Tuple[Workspace, MLClient]:
    """
    Authenticate and initialize Azure ML Workspace and MLClient.

    This function performs interactive authentication using Azure credentials,
    and returns both the legacy `Workspace` object and the newer `MLClient`.

    Returns
    -------
    ws : Workspace
        AzureML legacy Workspace object.
    ml_client : MLClient
        AzureML MLClient object used for interacting with Azure ML resources.
    """
    auth = InteractiveLoginAuthentication()

    ws = Workspace(
        subscription_id="0a94de80-6d3b-49f2-b3e9-ec5818862801",
        resource_group="buas-y2",
        workspace_name="CV2-2025",
        auth=auth,
    )

    ml_client = MLClient(
        credential=InteractiveBrowserCredential(),
        subscription_id="0a94de80-6d3b-49f2-b3e9-ec5818862801",
        resource_group_name="buas-y2",
        workspace_name="CV2-2025",
    )

    return ws, ml_client


def list_image_files(ws: Workspace) -> List[str]:
    """
    List all unique image file names in the 'raw_img/' directory default datastore.

    This function retrieves a dataset from the default AzureML datastore
    and filters it to return the base filenames of image files only.

    Parameters
    ----------
    ws : Workspace
        AzureML Workspace object from which to access the default datastore.

    Returns
    -------
    List[str]
        A list of unique image file names with supported extensions.
    """
    ds = Dataset.File.from_files(path=(ws.get_default_datastore(), "raw_img/"))
    paths = ds.to_path()

    valid_extensions = [".png", ".jpg", ".jpeg", ".tif", ".tiff"]
    image_files = [
        os.path.basename(p)
        for p in paths
        if os.path.splitext(p)[1].lower() in valid_extensions
    ]

    return list(set(image_files))
