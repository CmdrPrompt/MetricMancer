# Data Model Class Descriptions (2025-09-24)

**RepoInfo**
- Represents the top-level object for a repository. Contains metadata about the repository, its root path, and collections of files, subdirectories, and KPIs.

**ScanDir**
- Represents a scanned directory within a repository. Can contain files, subdirectories (ScanDir), and KPIs. Inherits common directory attributes from BaseDir.

**BaseDir**
- Abstracts common directory attributes such as name, relative path, root path, and repository name. Used as a base for ScanDir and RepoInfo.

**File**
- Represents a single file in the repository. Stores the file's name, its relative path, associated KPIs, and a list of functions found in the file.

**Function**
- Represents a function or method within a file. Contains the function's name and any KPIs calculated for it.

**BaseKPI**
- Abstract base class for all Key Performance Indicators (KPIs). Stores metadata (name, description, unit), the calculated value, and any additional calculation details. All KPI implementations inherit from this class.
