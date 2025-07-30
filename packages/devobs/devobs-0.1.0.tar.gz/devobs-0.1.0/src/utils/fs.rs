use std::{fs::create_dir_all,
          path::{Path, PathBuf}};

use anyhow::Result;
use glob::glob;

/// Create the file if it does not exist, including its parent directories.
pub(crate) fn touch_file(path: &Path) -> Result<()> {
    if path.exists() {
        log::debug!("File already exists: {}", path.display());
        return Ok(());
    }

    create_dir_all(
        path.parent()
            .expect("Failed to get parent directory for file creation."),
    )?;
    std::fs::File::create(path)?;
    log::debug!("Created file: {}", path.display());

    Ok(())
}

/// List files in the `from` directory based on the include and exclude patterns.
pub(crate) fn list_files(from: &Path, include: &[String], exclude: &[String]) -> Vec<PathBuf> {
    let mut include = expand_glob(from, include);
    let exclude = expand_glob(from, exclude);

    // Filter out files that match the exclude patterns
    include.retain(|path| {
        // Exclude files that match any of the exclude patterns
        !exclude.iter().any(|ex| path == ex)
    });

    include
}

/// Expand glob patterns in the given directory, returning a flat list of paths.
pub(crate) fn expand_glob(from: &Path, patterns: &[String]) -> Vec<PathBuf> {
    patterns
        .iter()
        .flat_map(|s| {
            glob(
                from.join(s)
                    .to_str()
                    .expect("Failed to convert path to string"),
            )
            .expect("Failed to create glob pattern")
        })
        .filter_map(Result::ok)
        .collect()
}

#[cfg(test)]
mod tests {
    use anyhow::Result;
    use sugars::hmap;

    use super::*;
    use crate::helpers::get_temp_dir;

    #[test]
    fn test_touch_file() -> Result<()> {
        // Arrange
        let temp_dir = get_temp_dir(hmap! {});
        let file_path = temp_dir.path().join("test.txt");
        assert!(!file_path.exists());

        // Act
        touch_file(&file_path)?;

        // Assert
        assert!(file_path.exists());
        Ok(())
    }

    #[test]
    fn test_touch_file_nested_directory() -> Result<()> {
        // Arrange
        let temp_dir = get_temp_dir(hmap! {});
        let nested_file_path = temp_dir.path().join("nested/dir/test.txt");
        assert!(!nested_file_path.exists());

        // Act
        touch_file(&nested_file_path)?;

        // Assert
        assert!(nested_file_path.exists());
        Ok(())
    }

    #[test]
    fn test_touch_existing_file() -> Result<()> {
        // Arrange
        let temp_dir = get_temp_dir(hmap! {"test.txt" => ""});
        let file_path = temp_dir.path().join("test.txt");
        assert!(file_path.exists());

        // Act
        touch_file(&file_path)?;

        // Assert
        assert!(file_path.exists());
        Ok(())
    }

    #[test]
    fn test_expand_glob_simple() -> Result<()> {
        // Arrange
        let temp_dir = get_temp_dir(hmap! {
            "file1.txt" => "",
            "file2.txt" => "",
            "other.log" => "",
        });
        let dir_path = temp_dir.path();

        // Act
        let mut txt_files = expand_glob(dir_path, &["*.txt".to_string()]);
        txt_files.sort();

        // Assert
        assert_eq!(
            txt_files,
            &[dir_path.join("file1.txt"), dir_path.join("file2.txt")]
        );
        Ok(())
    }

    #[test]
    fn test_expand_glob_multiple_patterns() -> Result<()> {
        // Arrange
        let temp_dir = get_temp_dir(hmap! {
            "file1.txt" => "",
            "file2.txt" => "",
            "other.log" => "",
        });
        let dir_path = temp_dir.path();

        // Act
        let mut all_files = expand_glob(dir_path, &["*.txt".to_string(), "*.log".to_string()]);
        all_files.sort();

        // Assert
        assert_eq!(
            all_files,
            &[
                dir_path.join("file1.txt"),
                dir_path.join("file2.txt"),
                dir_path.join("other.log"),
            ]
        );
        Ok(())
    }

    #[test]
    fn test_expand_glob_recursive() -> Result<()> {
        // Arrange
        let temp_dir = get_temp_dir(hmap! {
            "file1.txt" => "",
            "file2.txt" => "",
            "subdir/nested.txt" => "",
        });
        let dir_path = temp_dir.path();

        // Act
        let mut all_nested = expand_glob(dir_path, &["**/*.txt".to_string()]);
        all_nested.sort();

        // Assert
        assert_eq!(
            all_nested,
            &[
                dir_path.join("file1.txt"),
                dir_path.join("file2.txt"),
                dir_path.join("subdir/nested.txt"),
            ]
        );
        Ok(())
    }

    #[test]
    fn test_list_files_with_exclude() -> Result<()> {
        // Arrange
        let temp_dir = get_temp_dir(hmap! {
            "file1.txt" => "",
            "file2.txt" => "",
            "file3.txt" => "",
        });
        let dir_path = temp_dir.path();

        // Act
        let mut files = list_files(dir_path, &["*.txt".to_string()], &["file2.txt".to_string()]);
        files.sort();

        // Assert
        assert_eq!(
            files,
            &[dir_path.join("file1.txt"), dir_path.join("file3.txt")]
        );
        Ok(())
    }

    #[test]
    fn test_list_files_recursive_with_exclude() -> Result<()> {
        // Arrange
        let temp_dir = get_temp_dir(hmap! {
            "file1.txt" => "",
            "file2.txt" => "",
            "file3.txt" => "",
            "other.log" => "",
            "subdir/nested.txt" => "",
            "subdir/nested.log" => "",
        });
        let dir_path = temp_dir.path();

        // Act
        let mut files = list_files(
            dir_path,
            &["**/*.txt".to_string()],
            &["**/*.log".to_string()],
        );
        files.sort();

        // Assert
        assert_eq!(
            files,
            &[
                dir_path.join("file1.txt"),
                dir_path.join("file2.txt"),
                dir_path.join("file3.txt"),
                dir_path.join("subdir/nested.txt"),
            ]
        );
        Ok(())
    }

    #[test]
    fn test_list_files_empty_patterns() -> Result<()> {
        // Arrange
        let temp_dir = get_temp_dir(hmap! {
            "file1.txt" => "",
            "file2.txt" => "",
        });
        let dir_path = temp_dir.path();

        // Act
        let files = list_files(dir_path, &[], &[]);

        // Assert
        assert_eq!(files, &[] as &[PathBuf]);
        Ok(())
    }
}
