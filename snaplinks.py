"""Make versioned snapshots of a directory tree, symlinking between versions."""

import logging
import os
import stat
import sys


def AddSnapshot(snapshot_dir_path, source_dir_path):
	"""Creates a new snapshot of the source files in the snapshot directory.

	Args:
		snapshot_dir_path: Path to a directory which will contain snapshots. The
				directory will be created if it does not exist.
		source_dir_path: Directory to read from.

	Returns: The path of the newly-created snapshot directory.
	"""
	_CheckSnapshotDir(snapshot_dir_path)
	_CheckSourceDir(source_dir_path)

	"""
	find the latest snapshot directory (if missing, use a bogus base path)
	make a new directory for the new snapshot
	walk all the files in the source directory:
		if it's a directory, create it in the new snapshot directory
		if it does not exist in the old snapshot,
				or exists but is different,
			just copy it to the new snapshot
		otherwise it exists and is the same, so
				move the old snapshot's file to the new snapshot location
				and symlink from the old snapshot to the new snapshot location
	"""


def _CheckSnapshotDir(path):
	if not os.path.exists(path):
		logging.info('creating base snapshot directory %r', path)
		os.makedirs(path)
	if not os.path.isdir(path):
		raise ValueError('path for snapshot directory not a directory: %r' % path)
	stat_result = os.stat(path)
	for mode, description in (
			(stat.S_IRUSR, 'readable'),
			(stat.S_IWUSR, 'writable'),
			(stat.S_IXUSR, 'traversable')):
		if not stat_result.st_mode & mode:
			raise ValueError(
					'snapshot directory %r not user-%s' % (path, description))


def _CheckSourceDir(path):
	if not os.path.exists(path):
		raise ValueError('source path does not exist: %r' % path)
	if not os.path.isdir(path):
		raise ValueError('source path exists but is not a directory: %r' % path)
	stat_result = os.stat(path)
	for mode, description in (
			(stat.S_IRUSR, 'readable'),
			(stat.S_IXUSR, 'traversable')):
		if not stat_result.st_mode & mode:
			raise ValueError(
					'source directory %r not user-%s' % (path, description))


if __name__ == '__main__':
	AddSnapshot(*sys.argv[1:])
