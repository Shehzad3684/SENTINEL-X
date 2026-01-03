"""
Auto-BOT Build Script
Creates a standalone Windows executable using PyInstaller.

Usage:
    python build_exe.py

Output:
    dist/Auto-BOT.exe
"""

import os
import sys
import shutil
import subprocess


def get_project_root():
    """Get the project root directory."""
    return os.path.dirname(os.path.abspath(__file__))


def clean_build():
    """Remove previous build artifacts."""
    project_root = get_project_root()
    
    dirs_to_clean = [
        os.path.join(project_root, 'build'),
        os.path.join(project_root, 'dist'),
    ]
    
    files_to_clean = [
        os.path.join(project_root, 'Auto-BOT.spec'),
    ]
    
    print("🧹 Cleaning previous builds...")
    
    for dir_path in dirs_to_clean:
        if os.path.exists(dir_path):
            try:
                shutil.rmtree(dir_path)
                print(f"   Removed: {dir_path}")
            except PermissionError:
                print(f"   ⚠️ Could not remove {dir_path} (in use). Continuing...")
    
    for file_path in files_to_clean:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"   Removed: {file_path}")
            except PermissionError:
                print(f"   ⚠️ Could not remove {file_path}. Continuing...")
    
    print("   ✅ Clean complete.")


def create_icon_placeholder():
    """Create a placeholder icon if none exists."""
    project_root = get_project_root()
    icon_path = os.path.join(project_root, 'assets', 'icon.ico')
    
    if not os.path.exists(icon_path):
        print("⚠️ No icon.ico found in assets/. Building without custom icon.")
        return None
    
    return icon_path


def build_exe():
    """Build the executable using PyInstaller."""
    project_root = get_project_root()
    
    # Paths
    entry_point = os.path.join(project_root, 'app', 'gui.py')
    assets_dir = os.path.join(project_root, 'assets')
    icon_path = create_icon_placeholder()
    
    # Ensure entry point exists
    if not os.path.exists(entry_point):
        print(f"❌ Entry point not found: {entry_point}")
        sys.exit(1)
    
    print("\n🔨 Building Auto-BOT executable...")
    print(f"   Entry point: {entry_point}")
    print(f"   Assets: {assets_dir}")
    
    # Build PyInstaller command
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--name=Auto-BOT',
        '--onefile',                    # Single executable
        '--windowed',                   # No console window
        '--noconfirm',                  # Overwrite without asking
        f'--distpath={os.path.join(project_root, "dist")}',
        f'--workpath={os.path.join(project_root, "build")}',
        f'--specpath={project_root}',
    ]
    
    # Add icon if available
    if icon_path and os.path.exists(icon_path):
        cmd.append(f'--icon={icon_path}')
        print(f"   Icon: {icon_path}")
    
    # Add assets directory
    if os.path.exists(assets_dir):
        cmd.append(f'--add-data={assets_dir};assets')
    
    # Hidden imports for packages that PyInstaller might miss
    hidden_imports = [
        'pygame',
        'pygame.mixer',
        'speech_recognition',
        'pyautogui',
        'pygetwindow',
        'psutil',
        'edge_tts',
        'groq',
        'PIL',
        'PIL._tkinter_finder',  # Needed for PIL/Tkinter compatibility
        'pyttsx3',
        'aiohttp',
    ]
    
    for imp in hidden_imports:
        cmd.append(f'--hidden-import={imp}')
    
    # Collect all data for packages that need it
    collect_all = [
        'pygame',
        'edge_tts',
        'speech_recognition',
    ]
    
    for pkg in collect_all:
        cmd.append(f'--collect-all={pkg}')
    
    # Entry point
    cmd.append(entry_point)
    
    print(f"\n📦 Running PyInstaller...")
    print(f"   Command: {' '.join(cmd[:5])}...")
    
    # Run PyInstaller
    result = subprocess.run(cmd, cwd=project_root)
    
    if result.returncode != 0:
        print("\n❌ Build failed!")
        sys.exit(1)
    
    # Verify output
    exe_path = os.path.join(project_root, 'dist', 'Auto-BOT.exe')
    
    if os.path.exists(exe_path):
        size_mb = os.path.getsize(exe_path) / (1024 * 1024)
        print(f"\n✅ BUILD SUCCESSFUL!")
        print(f"   Output: {exe_path}")
        print(f"   Size: {size_mb:.1f} MB")
        print("\n📝 Next steps:")
        print("   1. Test the exe by double-clicking it")
        print("   2. If antivirus flags it, add an exclusion")
        print("   3. Distribute the exe to users")
    else:
        print(f"\n❌ Expected output not found: {exe_path}")
        sys.exit(1)


def main():
    """Main build process."""
    print("="*60)
    print("🤖 AUTO-BOT BUILD SYSTEM")
    print("="*60)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required.")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")
    
    # Check PyInstaller
    try:
        import PyInstaller
        print(f"✅ PyInstaller {PyInstaller.__version__}")
    except ImportError:
        print("❌ PyInstaller not found. Install with: pip install pyinstaller")
        sys.exit(1)
    
    # Clean and build
    clean_build()
    build_exe()
    
    print("\n" + "="*60)
    print("🎉 BUILD COMPLETE")
    print("="*60)


if __name__ == "__main__":
    main()
