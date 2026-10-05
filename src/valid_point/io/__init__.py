"""Canonical small synthetic cloud I/O; no external data formats here."""

from .pointcloud import PointCloud, read_pointcloud, write_pointcloud

__all__ = ["PointCloud", "read_pointcloud", "write_pointcloud"]
