use anyhow::Result;
use assert_cmd::Command;
use insta::assert_snapshot;
use sugars::hmap;

use crate::{helpers::{first_line, get_temp_dir, list_dir, normalize_console_output, parse_output},
            to_str};

#[test]
fn test_empty_directory_no_error_no_output() -> Result<()> {
    // Arrange
    let temp_dir = get_temp_dir(hmap! {});

    // Act
    let mut cmd = Command::cargo_bin(env!("CARGO_PKG_NAME"))?;
    let assert = cmd
        .arg("--no-colors")
        .arg("check-file-pair")
        .args(&["--from", to_str!(temp_dir.path().join("src"))])
        .args(&["--to", to_str!(temp_dir.path().join("tests"))])
        .assert();

    // Assert
    let result = assert.success().code(0);
    let (stdout, stderr) = parse_output(result.get_output());
    assert_snapshot!(normalize_console_output(
        stdout,
        hmap! {
            to_str!(temp_dir.path()) => "<temp_dir>"
        }
    ));
    assert_eq!(stderr, "");
    assert_eq!(list_dir(temp_dir.path()), &[] as &[&str]);
    Ok(())
}

#[test]
fn test_forward_matching() -> Result<()> {
    // Arrange
    let temp_dir = get_temp_dir(hmap! {
        "src/__init__.py" => "",
        "src/main.py" => "",
        "src/utils/logger.py" => "",
        "src/utils/slack/template.py" => "",
    });

    // Act
    let mut cmd = Command::cargo_bin(env!("CARGO_PKG_NAME"))?;
    let assert = cmd
        .arg("--no-colors")
        .arg("check-file-pair")
        .args(&["--from", to_str!(temp_dir.path().join("src"))])
        .args(&["--to", to_str!(temp_dir.path().join("tests"))])
        .args(&["--include", "**/*.py"])
        .args(&["--expect", "{to}/{relative_from}/test_{filename}"])
        .assert();

    // Assert
    let result = assert.failure().code(1);
    let (stdout, stderr) = parse_output(result.get_output());
    assert_snapshot!(normalize_console_output(
        stdout,
        hmap! {
            to_str!(temp_dir.path()) => "<temp_dir>"
        }
    ));
    assert_eq!(
        first_line(stderr),
        "Error: There are 4 missing files. Use `--create-if-not-exists` to create them."
    );
    assert_eq!(
        list_dir(temp_dir.path()),
        &[
            "src/__init__.py",
            "src/main.py",
            "src/utils/logger.py",
            "src/utils/slack/template.py",
        ]
    );
    Ok(())
}

#[test]
fn test_backward_matching() -> Result<()> {
    // Arrange
    let temp_dir = get_temp_dir(hmap! {
        "src/__init__.py" => "",
        "src/main.py" => "",
        "tests/test_main.py" => "",
        "tests/conftest.py" => "",
        "tests/_helpers.py" => "",
        "tests/utils/slack/test_template.py" => "",
        "tests/utils/test_logger.py" => "",
    });

    // Act
    let mut cmd = Command::cargo_bin(env!("CARGO_PKG_NAME"))?;
    let assert = cmd
        .arg("--no-colors")
        .arg("check-file-pair")
        .args(&["--from", to_str!(temp_dir.path().join("tests"))])
        .args(&["--to", to_str!(temp_dir.path().join("src"))])
        .args(&["--include", "**/*.py"])
        .args(&["--filename-regex", "^test_(?P<filename>.*)$"])
        .assert();

    // Assert
    let result = assert.failure().code(1);
    let (stdout, stderr) = parse_output(result.get_output());
    assert_snapshot!(normalize_console_output(
        stdout,
        hmap! {
            to_str!(temp_dir.path()) => "<temp_dir>"
        }
    ));
    assert_eq!(
        first_line(stderr),
        "Error: There are 4 missing files. Use `--create-if-not-exists` to create them."
    );
    assert_eq!(
        list_dir(temp_dir.path()),
        &[
            "src/__init__.py",
            "src/main.py",
            "tests/_helpers.py",
            "tests/conftest.py",
            "tests/test_main.py",
            "tests/utils/slack/test_template.py",
            "tests/utils/test_logger.py"
        ]
    );
    Ok(())
}

#[test]
fn test_on_fully_populated_directory() -> Result<()> {
    // Arrange
    let temp_dir = get_temp_dir(hmap! {
        "src/__init__.py" => "",
        "src/apps/posts/migrations/__init__.py" => "",
        "src/apps/posts/migrations/0001_initial.py" => "",
        "src/main.py" => "",
        "src/utils/logger.py" => "",
        "src/utils/slack/template.py" => "",
        "tests/test_main.py" => "",
        "tests/conftest.py" => "",
        "tests/_helpers.py" => "",
        "tests/utils/slack/test_template.py" => "",
        "tests/utils/test_logger.py" => "",
    });

    // Act
    let mut cmd = Command::cargo_bin(env!("CARGO_PKG_NAME"))?;
    let assert = cmd
        .arg("--no-colors")
        .arg("check-file-pair")
        .args(&["--from", to_str!(temp_dir.path().join("src"))])
        .args(&["--to", to_str!(temp_dir.path().join("tests"))])
        .args(&["--include", "**/*.py"])
        .args(&["--exclude", "**/migrations/*.py", "**/_*.py"])
        .args(&["--expect", "{to}/{relative_from}/test_{filename}"])
        .assert();

    // Assert
    let result = assert.success().code(0);
    let (stdout, stderr) = parse_output(result.get_output());
    assert_snapshot!(normalize_console_output(
        stdout,
        hmap! {
            to_str!(temp_dir.path()) => "<temp_dir>"
        }
    ));
    assert_eq!(stderr, "");
    assert_eq!(
        list_dir(temp_dir.path()),
        &[
            "src/__init__.py",
            "src/apps/posts/migrations/0001_initial.py",
            "src/apps/posts/migrations/__init__.py",
            "src/main.py",
            "src/utils/logger.py",
            "src/utils/slack/template.py",
            "tests/_helpers.py",
            "tests/conftest.py",
            "tests/test_main.py",
            "tests/utils/slack/test_template.py",
            "tests/utils/test_logger.py"
        ]
    );
    Ok(())
}

#[test]
fn test_create_if_not_exists() -> Result<()> {
    // Arrange
    let temp_dir = get_temp_dir(hmap! {
        "src/__init__.py" => "",
        "src/main.py" => "",
        "src/utils/logger.py" => "",
        "src/utils/slack/template.py" => "",
        "tests/test_main.py" => "",
    });

    // Act
    let mut cmd = Command::cargo_bin(env!("CARGO_PKG_NAME"))?;
    let assert = cmd
        .arg("--no-colors")
        .arg("check-file-pair")
        .args(&["--from", to_str!(temp_dir.path().join("src"))])
        .args(&["--to", to_str!(temp_dir.path().join("tests"))])
        .args(&["--include", "**/*.py"])
        .args(&["--exclude", "**/_*.py"])
        .args(&["--expect", "{to}/{relative_from}/test_{filename}"])
        .args(&["--create-if-not-exists"])
        .assert();

    // Assert
    let result = assert.failure().code(1);
    let (stdout, stderr) = parse_output(result.get_output());
    assert_snapshot!(normalize_console_output(
        stdout,
        hmap! {
            to_str!(temp_dir.path()) => "<temp_dir>"
        }
    ));
    assert_eq!(first_line(stderr), "Error: Created 2 missing files.");
    assert_eq!(
        list_dir(temp_dir.path()),
        &[
            "src/__init__.py",
            "src/main.py",
            "src/utils/logger.py",
            "src/utils/slack/template.py",
            "tests/test_main.py",
            "tests/utils/slack/test_template.py",
            "tests/utils/test_logger.py",
        ]
    );
    Ok(())
}

/// Test for `--create-if-not-exists` with `--dry-run` option.
///
/// If the files do not exist, they should not be created,
/// but the output should indicate they would be created.
#[test]
fn test_create_if_not_exists_dry_run() -> Result<()> {
    // Arrange
    let temp_dir = get_temp_dir(hmap! {
        "src/__init__.py" => "",
        "src/main.py" => "",
        "src/utils/logger.py" => "",
        "src/utils/slack/template.py" => "",
        "tests/test_main.py" => "",
    });

    // Act
    let mut cmd = Command::cargo_bin(env!("CARGO_PKG_NAME"))?;
    let assert = cmd
        .arg("--no-colors")
        .arg("--dry-run")
        .arg("check-file-pair")
        .args(&["--from", to_str!(temp_dir.path().join("src"))])
        .args(&["--to", to_str!(temp_dir.path().join("tests"))])
        .args(&["--include", "**/*.py"])
        .args(&["--exclude", "**/_*.py"])
        .args(&["--expect", "{to}/{relative_from}/test_{filename}"])
        .args(&["--create-if-not-exists"])
        .assert();

    // Assert
    let result = assert.failure().code(1);
    let (stdout, stderr) = parse_output(result.get_output());
    assert_snapshot!(normalize_console_output(
        stdout,
        hmap! {
            to_str!(temp_dir.path()) => "<temp_dir>"
        }
    ));
    assert_eq!(first_line(stderr), "Error: Created 2 missing files.");
    assert_eq!(
        list_dir(temp_dir.path()),
        &[
            "src/__init__.py",
            "src/main.py",
            "src/utils/logger.py",
            "src/utils/slack/template.py",
            "tests/test_main.py",
        ]
    );
    Ok(())
}
