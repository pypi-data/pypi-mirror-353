"""Main module."""

# Python
from typing import Union, List, Tuple, Any
import numpy as np
from scipy.spatial.transform import Rotation as R


def check_input_format_quaternion(*args, **kwargs) -> Tuple[Any, Any, Any, Any]:
    """
    Check if the input format is valid.

    Args:
        1. A single list or tuple containing [x, y, z, w].
        2. Four individual arguments x, y, z, w.
        3. Keyword arguments x=x, y=y, z=z, w=w.

    Returns:
        bool: True if the input format is valid, False otherwise.
    """
    # Case 1: Single list or tuple

    if len(args) == 1 and isinstance(args[0], (list, tuple)):
        x, y, z, w = args[0]
        return x, y, z, w

    # Case 2: Four individual arguments
    elif len(args) == 4:
        x, y, z, w = args
        return x, y, z, w

    # Case 3: Keyword arguments
    elif all(k in kwargs for k in ("x", "y", "z", "w")):
        x = kwargs["x"]
        y = kwargs["y"]
        z = kwargs["z"]
        w = kwargs["w"]
        return x, y, z, w

    # Invalid input format
    raise ValueError(
        "Invalid input format. Provide [x, y, z, w], x, y, z, w, or x=x, y=y, z=z, w=w."
    )


def check_input_format_euler(*args, **kwargs) -> Tuple[Any, Any, Any]:
    """
    Check if the input format is valid for Euler angles.

    Args:
        1. A single list or tuple containing [roll, pitch, yaw].
        2. Three individual arguments roll, pitch, yaw.
        3. Keyword arguments roll=roll, pitch=pitch, yaw=yaw.

    Returns:
        Tuple: A tuple containing roll, pitch, yaw.
    """
    # Case 1: Single list or tuple
    if len(args) == 1 and isinstance(args[0], (list, tuple)):
        roll, pitch, yaw = args[0]
        return roll, pitch, yaw

    # Case 2: Three individual arguments
    elif len(args) == 3:
        roll, pitch, yaw = args
        return roll, pitch, yaw

    # Case 3: Keyword arguments
    elif all(k in kwargs for k in ("roll", "pitch", "yaw")):
        roll = kwargs["roll"]
        pitch = kwargs["pitch"]
        yaw = kwargs["yaw"]
        return roll, pitch, yaw

    # Invalid input format
    raise ValueError(
        "Invalid input format. Provide [roll, pitch, yaw], roll, pitch, yaw, or roll=roll, pitch=pitch, yaw=yaw."
    )


def check_input_format_rotation_matrix(rotation_matrix: np.ndarray) -> np.ndarray:
    """
    Check if the input rotation matrix is valid.
    """

    if not isinstance(rotation_matrix, np.ndarray):
        raise ValueError("Input must be a numpy array.")

    if rotation_matrix.shape != (3, 3):
        raise ValueError("Input rotation matrix must be a 3x3 numpy array.")

    return rotation_matrix


def euler_from_quaternion(*args, **kwargs) -> Tuple[float, float, float]:
    """
    Transform quaternion to roll, pitch, yaw.

    Args:
        1. A single list or tuple containing [x, y, z, w].
        2. Four individual arguments x, y, z, w.
        3. Keyword arguments x=x, y=y, z=z, w=w.

    Returns:
        A tuple containing roll, pitch, yaw in radians.
    """

    x, y, z, w = check_input_format_quaternion(*args, **kwargs)

    quat = R.from_quat([x, y, z, w])
    roll, pitch, yaw = quat.as_euler("xyz", degrees=False)

    return roll, pitch, yaw


def euler_from_rotation_matrix(
    rotation_matrix: np.ndarray,
) -> Tuple[float, float, float]:
    """
    Transform rotation matrix to roll, pitch, yaw.

    Args:
        rotation_matrix (np.ndarray): A 3x3 rotation matrix.

    Returns:
        Tuple[float, float, float]: A tuple containing roll, pitch, yaw in radians.
    """

    rotation_matrix = check_input_format_rotation_matrix(rotation_matrix)

    rotation = R.from_matrix(rotation_matrix)
    roll, pitch, yaw = rotation.as_euler("xyz", degrees=False)

    return roll, pitch, yaw


def quaternion_from_euler(*args, **kwargs) -> Tuple[float, float, float, float]:
    """
    Transform roll, pitch, yaw to quaternion.
    Args:
        1. A single list or tuple containing [roll, pitch, yaw].
        2. Three individual arguments roll, pitch, yaw.
        3. Keyword arguments roll=roll, pitch=pitch, yaw=yaw.

    Returns:
        A tuple containing qx, qy, qz, qw

    """

    roll, pitch, yaw = check_input_format_euler(*args, **kwargs)

    euler = R.from_euler("xyz", [roll, pitch, yaw], degrees=False)
    qx, qy, qz, qw = euler.as_quat()

    return qx, qy, qz, qw


def quaternion_from_rotation_matrix(rotation_matrix: np.ndarray) -> tuple:
    """
    Transform rotation matrix to quaternion.

    Parameters:
        rotation_matrix (np.ndarray): A 3x3 rotation matrix.

    Returns:
        tuple: A tuple containing qx, qy, qz, qw.
    """

    rotation_matrix = check_input_format_rotation_matrix(rotation_matrix)

    # 회전 행렬을 scipy의 Rotation 객체로 변환
    rotation = R.from_matrix(rotation_matrix)

    # Quaternion 추출
    qx, qy, qz, qw = rotation.as_quat()

    return qx, qy, qz, qw


def rotation_matrix_from_euler(*args, **kwargs) -> np.ndarray:
    """
    Transform roll, pitch, yaw to rotation matrix.

    Args:
        1. A single list or tuple containing [roll, pitch, yaw].
        2. Three individual arguments roll, pitch, yaw.
        3. Keyword arguments roll=roll, pitch=pitch, yaw=yaw.

    Returns:
        np.ndarray: A 3x3 rotation matrix.
    """

    roll, pitch, yaw = check_input_format_euler(*args, **kwargs)

    rotation = R.from_euler("xyz", [roll, pitch, yaw], degrees=False)
    return rotation.as_matrix()


def compose_transform(translation: np.ndarray, rotation: np.ndarray) -> np.ndarray:
    """
    Compose a 4x4 transformation matrix from translation and rotation.

    Parameters:
        translation (np.ndarray): A 3-element array representing translation (x, y, z).
        rotation (np.ndarray): A 3x3 rotation matrix.

    Returns:
        np.ndarray: A 4x4 transformation matrix.
    """

    assert isinstance(translation, np.ndarray), "Translation must be a numpy array."
    assert isinstance(rotation, np.ndarray), "Rotation must be a numpy array."

    assert translation.shape == (3,), "Translation must be a 3-element array."
    assert rotation.shape == (3, 3), "Rotation must be a 3x3 matrix."

    transform_matrix = np.eye(4)

    transform_matrix[:3, :3] = rotation
    transform_matrix[:3, 3] = translation

    return transform_matrix


def decompose_transform(transform_matrix: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Decompose a 4x4 transformation matrix into translation and rotation.

    Parameters:
        transform_matrix (np.ndarray): A 4x4 transformation matrix.

    Returns:
        Tuple[np.ndarray, np.ndarray]: A tuple containing:
            - translation (np.ndarray): A 3-element array representing translation (x, y, z).
            - rotation (np.ndarray): A 3x3 rotation matrix.
    """

    assert isinstance(transform_matrix, np.ndarray), "Input must be a numpy array."
    assert transform_matrix.shape == (4, 4), "Input must be a 4x4 matrix."

    translation = transform_matrix[:3, 3]
    rotation = transform_matrix[:3, :3]

    return translation, rotation


def invert_transform(matrix: np.ndarray) -> np.ndarray:
    """
    Invert a 4x4 transformation matrix in order to make it represent B > A from A > B.

    Parameters:
        matrix (np.ndarray): A 4x4 transformation matrix representing A > B.

    Returns:
        np.ndarray: The inverted transformation matrix representing B > A.
    """
    if matrix.shape != (4, 4):
        raise ValueError("Input matrix must be a 4x4 matrix.")

    # Extract rotation and translation components
    rotation = matrix[:3, :3]
    translation = matrix[:3, 3]

    # Invert the rotation (transpose for orthogonal matrix)
    rotation_inv = rotation.T

    # Invert the translation
    translation_inv = -np.dot(rotation_inv, translation)

    # Construct the inverted transformation matrix
    inverted_matrix = np.eye(4)
    inverted_matrix[:3, :3] = rotation_inv
    inverted_matrix[:3, 3] = translation_inv

    return inverted_matrix


def transform_realsense_to_ros(transform_matrix: np.ndarray) -> np.ndarray:
    """
    Transform a 4x4 transformation matrix from Realsense to ROS coordinate system.

    Parameters:
        transform_matrix (np.ndarray): A 4x4 transformation matrix representing Realsense coordinates.

    Returns:
        np.ndarray: A 4x4 transformation matrix representing ROS coordinates.
    """

    if transform_matrix.shape != (4, 4):
        raise ValueError("Input transformation matrix must be a 4x4 matrix.")

    # Rotation matrix to convert Realsense to ROS
    realsense_to_ros_rotation = np.array(
        [[0, 0, 1], [-1, 0, 0], [0, -1, 0]]  # X -> Z  # Y -> -X  # Z -> -Y
    )

    # Decompose the input transformation matrix
    rotation = transform_matrix[:3, :3]
    translation = transform_matrix[:3, 3]

    # Transform the rotation and translation
    rotation_ros = realsense_to_ros_rotation @ rotation
    translation_ros = realsense_to_ros_rotation @ translation

    # Construct the new transformation matrix in ROS format
    transform_matrix_ros = np.eye(4)
    transform_matrix_ros[:3, :3] = rotation_ros
    transform_matrix_ros[:3, 3] = translation_ros

    return transform_matrix_ros
