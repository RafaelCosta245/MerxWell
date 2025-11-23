"""
Storage manager for handling output directory selection and persistence.
"""
import flet as ft
from pathlib import Path
from typing import Optional, Callable


STORAGE_KEY = "merx_output_directory"


def get_output_directory(page: ft.Page) -> Optional[str]:
    """
    Get the configured output directory from storage.
    
    Args:
        page: Flet page object
        
    Returns:
        str: Path to output directory, or None if not configured
    """
    if page.client_storage.contains_key(STORAGE_KEY):
        return page.client_storage.get(STORAGE_KEY)
    return None


def set_output_directory(page: ft.Page, directory_path: str) -> None:
    """
    Save the output directory to storage.
    
    Args:
        page: Flet page object
        directory_path: Path to the output directory
    """
    page.client_storage.set(STORAGE_KEY, directory_path)
    print(f"[STORAGE] Output directory set to: {directory_path}")


def prompt_folder_selection(
    page: ft.Page,
    on_selected: Optional[Callable[[str], None]] = None,
    on_cancel: Optional[Callable[[], None]] = None
) -> None:
    """
    Show folder picker dialog to select output directory.
    
    Args:
        page: Flet page object
        on_selected: Callback function called with selected path
        on_cancel: Callback function called if user cancels
    """
    def handle_result(e: ft.FilePickerResultEvent):
        if e.path:
            set_output_directory(page, e.path)
            if on_selected:
                on_selected(e.path)
            
            # Show success message
            snackbar = ft.SnackBar(
                ft.Text(f"Pasta de saída configurada: {e.path}"),
                bgcolor=ft.Colors.GREEN_600
            )
            page.overlay.append(snackbar)
            snackbar.open = True
            page.update()
        else:
            if on_cancel:
                on_cancel()
    
    picker = ft.FilePicker(on_result=handle_result)
    page.overlay.append(picker)
    page.update()
    picker.get_directory_path(dialog_title="Selecione a pasta para salvar os arquivos")


def ensure_output_directory_configured(
    page: ft.Page,
    on_configured: Optional[Callable[[str], None]] = None
) -> bool:
    """
    Ensure output directory is configured, prompting user if not.
    
    Args:
        page: Flet page object
        on_configured: Callback called when directory is configured
        
    Returns:
        bool: True if already configured, False if prompting user
    """
    output_dir = get_output_directory(page)
    
    if output_dir:
        # Verify directory still exists
        if Path(output_dir).exists():
            if on_configured:
                on_configured(output_dir)
            return True
        else:
            # Directory no longer exists, prompt for new one
            print(f"[STORAGE] Configured directory no longer exists: {output_dir}")
            page.client_storage.remove(STORAGE_KEY)
    
    # Not configured or directory doesn't exist, prompt user
    prompt_folder_selection(page, on_selected=on_configured)
    return False
