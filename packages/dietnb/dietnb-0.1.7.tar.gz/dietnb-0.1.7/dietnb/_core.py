import hashlib
from pathlib import Path
from typing import Optional
import time
import os

# Removed imports for notebook and requests
# import matplotlib.pyplot as plt # This should be kept
# from IPython import get_ipython # This should be kept
# from matplotlib.figure import Figure # This should be kept

import matplotlib.pyplot as plt
from IPython import get_ipython
from matplotlib.figure import Figure

# Global state
_state = {}  # Stores {cell_key: last_exec_count}
_patch_applied = False

DEFAULT_FOLDER_NAME = "dietnb_imgs"

def _get_notebook_image_dir(ip_instance, base_folder_name=DEFAULT_FOLDER_NAME) -> Path:
    """Determines the target image directory.
    Priority:
    1. Auto-detected notebook name.
    2. Default directory.
    """
    default_dir_for_fallback = Path(os.getcwd()) / base_folder_name
    notebook_path_str: Optional[str] = None

    if ip_instance and hasattr(ip_instance, 'kernel') and ip_instance.kernel and \
       hasattr(ip_instance.kernel, 'session') and ip_instance.kernel.session:
        notebook_path_attr = getattr(ip_instance.kernel.session, 'path', None)
        if isinstance(notebook_path_attr, str) and notebook_path_attr.strip():
            notebook_path_str = notebook_path_attr.strip()

    if not notebook_path_str and ip_instance and hasattr(ip_instance, 'user_global_ns'):
        vsc_path = ip_instance.user_global_ns.get("__vsc_ipynb_file__")
        if isinstance(vsc_path, str) and vsc_path.strip():
            notebook_path_str = vsc_path.strip()

    if not notebook_path_str:
        jpy_session_name = os.environ.get("JPY_SESSION_NAME")
        if isinstance(jpy_session_name, str) and jpy_session_name.strip():
            potential_path = jpy_session_name.strip()
            if not os.path.isabs(potential_path):
                 potential_path = os.path.join(os.getcwd(), potential_path)
            if os.path.isfile(potential_path) and potential_path.lower().endswith('.ipynb'):
                 notebook_path_str = potential_path

    if notebook_path_str:
        try:
            notebook_path = Path(notebook_path_str)
            notebook_fname = notebook_path.name
            notebook_name_without_ext, _ = os.path.splitext(notebook_fname)

            if not notebook_name_without_ext:
                 target_dir = default_dir_for_fallback
            else:
                 notebook_dir_name_part = f"{notebook_name_without_ext}_{base_folder_name}"
                 target_dir_base = notebook_path.parent
                 target_dir = target_dir_base / notebook_dir_name_part
        except Exception:
            target_dir = default_dir_for_fallback
    else:
        target_dir = default_dir_for_fallback

    try:
        target_dir.mkdir(parents=True, exist_ok=True)
        return target_dir
    except OSError:
        default_dir_for_fallback.mkdir(parents=True, exist_ok=True)
        return default_dir_for_fallback

def _get_cell_key(ip) -> str:
    """Generates a unique key for the current cell execution."""
    if not ip:
        # Fallback if IPython is not available (e.g., plain Python script)
        # Use a simple counter or random hash, less ideal but functional
        # For now, stick to figure number if possible, but this is unreliable outside IPython
        fig = plt.gcf()
        return hashlib.sha1(str(id(fig)).encode()).hexdigest()[:12] # Less stable fallback

    # Prefer cellId from metadata (JupyterLab >= 3, VS Code, etc.)
    meta = ip.parent_header.get("metadata", {})
    cell_id = meta.get("cellId") or meta.get("cell_id")

    if cell_id:
        return hashlib.sha1(cell_id.encode()).hexdigest()[:12]

    # Fallback to hashing the raw cell content (less reliable)
    try:
        # Ensure history manager and raw history are available
        if hasattr(ip, 'history_manager') and hasattr(ip.history_manager, 'input_hist_raw') and ip.history_manager.input_hist_raw:
             raw_cell = ip.history_manager.input_hist_raw[-1]
             return hashlib.sha1(raw_cell.encode()).hexdigest()[:12]
        else:
             raise AttributeError("History manager or raw input history not available.")
    except (AttributeError, IndexError):
        # Fallback if history is not available or empty
        fig = plt.gcf()
        fallback_key = hashlib.sha1(str(id(fig)).encode()).hexdigest()[:12]
        return fallback_key

def _save_figure_and_get_html(fig: Figure, ip, fmt="png", dpi=150) -> Optional[str]:
    """Saves the figure to a file and returns an HTML img tag."""
    global _state
    if not ip:
        return None

    # Determine target directory dynamically (no folder_prefix)
    image_dir = _get_notebook_image_dir(ip)

    key = _get_cell_key(ip)
    # Use execution_count if available, otherwise fallback (e.g., timestamp for uniqueness)
    exec_count = getattr(ip, 'execution_count', None) or int(time.time())


    try:
        # Ensure the target directory exists
        image_dir.mkdir(parents=True, exist_ok=True)
    except OSError:
        return None # Indicate failure

    # Use a tuple (directory, cell_key) for state to handle multiple notebooks
    state_key = (str(image_dir), key)

    # Clean up images from previous execution of the same cell *in the same directory*
    if _state.get(state_key) != exec_count:
        for old_file in image_dir.glob(f"*_*_{key}.png"):
            try:
                old_file.unlink()
            except OSError:
                pass # Fail silently if old file removal fails
        _state[state_key] = exec_count
        idx = 1
    else:
        # Increment index for multiple figures in the same cell execution
        # The pattern must match the new filename format: {exec_count}_*_{key}.png
        # We need to find the max index for the current exec_count and key
        
        # A more robust way to find the next index
        existing_indices = [
            int(f.stem.split('_')[1])
            for f in image_dir.glob(f"{exec_count}_*_{key}.png")
            if f.stem.split('_')[1].isdigit()
        ]
        idx = max(existing_indices) + 1 if existing_indices else 1


    # Filename format: {exec_count}_{fig_index}_{cell_key}.png
    filename = f"{exec_count}_{idx}_{key}.png"
    filepath = image_dir / filename

    try:
        fig.savefig(filepath, dpi=dpi, bbox_inches="tight", format=fmt)
    except Exception:
        return None # Indicate failure

    img_src_base = f"{image_dir.name}/{filename}"
    
    final_img_src = img_src_base # Default: no query string for web Jupyter as per user feedback

    # Check if running in VS Code to add cache-busting query string specifically for it
    # ip is the IPython instance passed to _save_figure_and_get_html
    if ip and hasattr(ip, 'user_global_ns'):
        vsc_notebook_file_path_str = ip.user_global_ns.get("__vsc_ipynb_file__")
        if vsc_notebook_file_path_str and isinstance(vsc_notebook_file_path_str, str):
            # It's VS Code, add query string for cache busting
            final_img_src = f"{img_src_base}"
    
    # No /files/ prefix
    return f'<img src="{final_img_src}" alt="{filename}" style="max-width:100%;">'

def _no_op_repr_png(fig: Figure):
    """Prevents the default PNG representation."""
    return None

def _patch_figure_reprs(ip):
    """Applies the monkey-patches to the Figure class."""
    global _patch_applied
    if not ip:
        return

    # Disable default PNG embedding
    try:
        if hasattr(ip.display_formatter.formatters['image/png'], 'enabled'):
             ip.display_formatter.formatters['image/png'].enabled = False
    except KeyError:
        pass

    # Patch Figure methods
    Figure._repr_png_ = _no_op_repr_png
    # Use a lambda to capture the current ip
    Figure._repr_html_ = lambda fig_obj: _save_figure_and_get_html(fig_obj, ip)
    _patch_applied = True

def _restore_figure_reprs(ip):
    """Restores original Figure representations (best effort)."""
    global _patch_applied
    if not _patch_applied:
        return
    # This requires storing the original methods, which we aren't doing yet.
    # For now, just remove our patches if possible.
    if hasattr(Figure, '_repr_png_') and Figure._repr_png_ is _no_op_repr_png:
        del Figure._repr_png_ # Or try to restore original if saved
    # Cannot easily restore _repr_html_ due to lambda, so leave it for now
    try:
        if hasattr(ip.display_formatter.formatters['image/png'], 'enabled'):
             ip.display_formatter.formatters['image/png'].enabled = True
    except KeyError:
        pass # Ignore if formatter doesn't exist

    _patch_applied = False


def _post_cell_cleanup_and_repatch(ip):
    """Closes figures and re-applies patches after cell execution."""
    if not ip:
        return

    # Close all figures to prevent memory leaks and duplicate output
    # plt.close should be safe regardless of saving directory
    try:
        # Only close figures managed by plt.figure(), not necessarily all Figure objects
        # Check if there are any active pyplot figures
        if plt.get_fignums():
             plt.close('all')
    except Exception:
        pass

    # Re-apply patches in case the backend was changed or reset
    _patch_figure_reprs(ip)

def _clean_unused_images_logic() -> dict:
    """Deletes image files whose keys are not in the current state *for the current context*."""
    global _state
    deleted_files = []
    failed_deletions = []
    kept_files = []

    ip = get_ipython()
    if not ip:
        return {"deleted": [], "failed": [], "kept": [], "message": "Cleanup skipped: Not in IPython."}

    # Determine the directory for the *current* context (no folder_prefix)
    image_dir = _get_notebook_image_dir(ip)

    if not image_dir.exists():
        return {"deleted": [], "failed": [], "kept": [], "message": f"Image directory '{image_dir.name}' not found."}

    # Get keys relevant *only* to the current directory from the state
    current_dir_str = str(image_dir)
    current_keys_in_state = {cell_key for (dir_key, cell_key) in _state if dir_key == current_dir_str}

    cleaned_count = 0
    failed_count = 0
    kept_count = 0

    for img_file in image_dir.glob("*.png"):
        try:
            # Extract key from filename like 'exec_count_idx_key.png'
            parts = img_file.stem.split('_')
            if len(parts) >= 3:
                key_part = parts[-1] # Key is the last part
                if key_part not in current_keys_in_state:
                    try:
                        img_file.unlink()
                        deleted_files.append(str(img_file.relative_to(Path.cwd()) if img_file.is_relative_to(Path.cwd()) else img_file))
                        cleaned_count += 1
                    except OSError:
                        failed_deletions.append(str(img_file.relative_to(Path.cwd()) if img_file.is_relative_to(Path.cwd()) else img_file))
                        failed_count += 1
                else:
                    kept_files.append(str(img_file.relative_to(Path.cwd()) if img_file.is_relative_to(Path.cwd()) else img_file))
                    kept_count += 1
            else:
                # Filename doesn't match expected format, keep it
                kept_files.append(str(img_file.relative_to(Path.cwd()) if img_file.is_relative_to(Path.cwd()) else img_file))
                kept_count += 1

        except Exception:
            # Catch any other parsing errors and keep the file
            failed_deletions.append(str(img_file.relative_to(Path.cwd()) if img_file.is_relative_to(Path.cwd()) else img_file))
            failed_count += 1

    message = f"Cleaned directory '{image_dir.name}'. Deleted: {cleaned_count}, Failed: {failed_count}, Kept: {kept_count}."
    return {"deleted": deleted_files, "failed": failed_deletions, "kept": kept_files, "message": message} 