"""Make versioned snapshots of a directory tree, symlinking between versions.

This targets a fairly simple case of regular files which may be created or
deleted. It does not specially deal with moved files, symlinks, etc.
"""

import datetime
import filecmp
import logging
import os
import shutil
import stat
import sys


_SNAPSHOT_DIR_NAME_FORMAT = '%Y-%m-%d_%H:%M:%S.%f'


def AddSnapshot(source_dir_path, snapshot_base_dir_path):
	"""Creates a new snapshot of the source files in the snapshot directory.

	Args:
		source_dir_path: Directory to read from.
		snapshot_base_dir_path: Path to a directory which will contain snapshots.
				The directory will be created if it does not exist.

	Returns: The path of the newly-created snapshot directory.
	"""
	_CheckSnapshotDir(snapshot_base_dir_path)
	_CheckSourceDir(source_dir_path)

	old_snapshot_dir_name = _FindNewestSnapshot(snapshot_base_dir_path)
	new_snapshot_dir_name = datetime.datetime.utcnow().strftime(
			_SNAPSHOT_DIR_NAME_FORMAT)
	new_snapshot_dir_path = os.path.join(
			snapshot_base_dir_path, new_snapshot_dir_name)
	os.mkdir(new_snapshot_dir_path)

	for source_subdir_path, local_dir_names, local_file_names in os.walk(
			source_dir_path):
		_CopyOrSymlinkFiles(
				snapshot_base_dir_path,
				old_snapshot_dir_name,
				new_snapshot_dir_name, 
				source_dir_path,
				source_subdir_path,
				local_dir_names,
				local_file_names)

	return new_snapshot_dir_path


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


def _FindNewestSnapshot(dir_path):
	path = None
	path_time = None
	for local_name in os.listdir(dir_path):
		try:
			t = datetime.datetime.strptime(local_name, _SNAPSHOT_DIR_NAME_FORMAT)
		except ValueError:
			continue
		if path_time is None or path_time < t:
			path_time = t
			path = local_name
	return path or '/dev/null'


def _CopyOrSymlinkFiles(
		snapshot_base_dir_path,
		old_snapshot_dir_name,
		new_snapshot_dir_name, 
		source_dir_path,
		source_subdir_path,
		local_dir_names,
		local_file_names):
	# Find the relative path of the directory (in the source, old snapshot, and
	# new snapshot) being processed. Due to the recursive nature of walk, this
	# will always already exist in source and new snapshot.
	relative_subdir_path = os.path.relpath(source_subdir_path, source_dir_path)

	for local_dir_name in local_dir_names:
		os.mkdir(os.path.join(
				snapshot_base_dir_path, new_snapshot_dir_name,
				relative_subdir_path, local_dir_name))
	for local_file_name in local_file_names:
		relative_file_path = os.path.join(relative_subdir_path, local_file_name)
		src_path = os.path.join(source_dir_path, relative_file_path)
		old_path = os.path.join(
				snapshot_base_dir_path, old_snapshot_dir_name, relative_file_path)
		new_path = os.path.join(
				snapshot_base_dir_path, new_snapshot_dir_name, relative_file_path)
		if _IsSameFile(src_path, old_path):
			shutil.move(old_path, new_path)
			os.symlink(
					os.path.relpath(
							new_path,
							os.path.join(
									snapshot_base_dir_path,
									old_snapshot_dir_name,
									relative_subdir_path)),
					old_path)
		else:
			shutil.copy2(src_path, new_path)


def _IsSameFile(new_file_path, possible_old_file_path):
	if not os.path.isfile(possible_old_file_path):
		return False
	return filecmp.cmp(new_file_path, possible_old_file_path)


if __name__ == '__main__':
	AddSnapshot(*sys.argv[1:])
