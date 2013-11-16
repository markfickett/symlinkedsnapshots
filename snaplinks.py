"""Make versioned snapshots of a directory tree, symlinking between versions."""

def AddSnapshot(snapshot_dir_path, source_dir_path):
	"""Creates a new snapshot of the source files in the snapshot directory.

	Args:
		snapshot_dir_path: Path to a directory which will contain snapshots. The
				directory will be created if it does not exist.
		source_dir_path: Directory to read from.

	Returns: The path of the newly-created snapshot directory.
	"""
	check args: must be paths to directories, etc
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
