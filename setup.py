from pathlib import Path

def setup_project():
    """Set up project directory structure and files."""
    # Create base directories
    base_dir = Path(__file__).parent
    data_dir = base_dir / "geonames_data"
    app_dir = base_dir / "app"
    
    # Create directories
    for directory in [data_dir, app_dir]:
        directory.mkdir(parents=True, exist_ok=True)
    
    # Ensure database directory is writable
    try:
        test_file = data_dir / "test.txt"
        test_file.touch()
        test_file.unlink()
    except Exception as e:
        print(f"Error: Data directory is not writable: {e}")
        return False
    
    return True

if __name__ == "__main__":
    if setup_project():
        print("Project setup completed successfully")
    else:
        print("Project setup failed")