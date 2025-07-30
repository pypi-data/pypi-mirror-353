use cow_utils::CowUtils;
use std::path::Path;

/// Convert a relative path to a Python module name, handling .py extension and __init__.py
pub fn module_name_from_relative(relative_path: &Path) -> Option<String> {
    let mut parts: Vec<String> = relative_path
        .components()
        .map(|c| c.as_os_str().to_string_lossy().into_owned())
        .collect();

    if parts.is_empty() {
        return None;
    }

    let last_part = parts.last_mut()?;
    // Remove .py extension
    if last_part.ends_with(".py") {
        *last_part = last_part[..last_part.len() - 3].to_owned();
    }

    // Handle __init__.py files
    if last_part == "__init__" {
        parts.pop();
    }

    // Skip files that don't map to a module
    if parts.is_empty() {
        return None;
    }

    Some(parts.join("."))
}

/// Convert a file system path to a Python module name, handling .py extension and __init__.py
/// Strips the `src_dir` prefix before processing.
pub fn path_to_module_name(src_dir: &Path, file_path: &Path) -> Option<String> {
    let relative_path = match file_path.strip_prefix(src_dir) {
        Ok(path) => path,
        Err(_) => return None,
    };
    // Handle root __init__.py specially
    if relative_path.components().count() == 1
        && relative_path.file_name().and_then(|n| n.to_str()) == Some("__init__.py")
    {
        return src_dir
            .file_name()
            .and_then(|os| os.to_str())
            .map(|s| s.to_owned());
    }
    module_name_from_relative(relative_path)
}

/// Normalize line endings to LF (\n) for cross-platform consistency
/// This ensures reproducible builds regardless of the platform where bundling occurs
pub fn normalize_line_endings(content: String) -> String {
    // Replace Windows CRLF (\r\n) and Mac CR (\r) with Unix LF (\n)
    content
        .cow_replace("\r\n", "\n")
        .cow_replace('\r', "\n")
        .into_owned()
}
