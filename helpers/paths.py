"""
Helper module for resolving paths in both development and frozen (cx_Freeze) environments.
"""
import sys
import os
from pathlib import Path


def get_base_path() -> Path:
    """
    Get the base path of the application.
    
    Returns the directory of the executable when frozen (built with cx_Freeze),
    or the project root directory when running in development.
    
    Returns:
        Path: The base path of the application
    """
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        base_path = Path(sys.executable).parent
    else:
        # Running in development
        # Go up from helpers/ to project root
        base_path = Path(__file__).resolve().parent.parent
    
    return base_path


def get_asset_path(*path_parts: str) -> Path:
    """
    Get the full path to an asset file (READ-ONLY).
    
    Use this ONLY for reading template files, images, icons, etc.
    NEVER use this for saving generated files.
    
    Args:
        *path_parts: Path components relative to the assets folder
        
    Returns:
        Path: Full path to the asset
        
    Example:
        get_asset_path("documents", "template.docx")
        # Returns: C:/path/to/app/assets/documents/template.docx
    """
    base = get_base_path()
    return base / "assets" / Path(*path_parts)


def get_icon_path(icon_name: str) -> str:
    """
    Get the full path to an icon file as a string.
    
    Args:
        icon_name: Name of the icon file
        
    Returns:
        str: Full path to the icon
    """
    return str(get_asset_path("icons", icon_name))


def get_output_path(output_dir: str, *path_parts: str) -> Path:
    """
    Get the full path for saving generated files (WRITE).
    
    Use this for ALL file generation (DOCX, PDF, etc.).
    Creates the directory if it doesn't exist.
    
    Args:
        output_dir: Base output directory (from client_storage)
        *path_parts: Path components relative to output_dir
        
    Returns:
        Path: Full path for the output file
        
    Example:
        output_dir = page.client_storage.get("merx_output_directory")
        get_output_path(output_dir, "proposals", "customer.docx")
        # Returns: C:/Users/user/Documents/MerxWell/proposals/customer.docx
    
    Raises:
        ValueError: If output_dir is None, empty, or invalid
    """
    # ⚠️ VALIDAÇÃO 1: Verificar se output_dir existe
    if not output_dir:
        raise ValueError(
            "Output directory not configured. "
            "Please configure the output folder in Backoffice settings."
        )
    
    # ⚠️ VALIDAÇÃO 2: Verificar se é string válida
    if not isinstance(output_dir, str):
        raise ValueError(f"Output directory must be a string, got {type(output_dir)}")
    
    # ⚠️ VALIDAÇÃO 3: Verificar se não é apenas espaços em branco
    if not output_dir.strip():
        raise ValueError("Output directory cannot be empty or whitespace")
    
    try:
        output_path = Path(output_dir)
        
        # ⚠️ VALIDAÇÃO 4: Criar diretório se não existir
        output_path.mkdir(parents=True, exist_ok=True)
        
        if path_parts:
            full_path = output_path / Path(*path_parts)
            # Garantir que diretórios pai existam
            full_path.parent.mkdir(parents=True, exist_ok=True)
            return full_path
        
        return output_path
        
    except (OSError, PermissionError) as e:
        raise ValueError(
            f"Cannot create or access output directory '{output_dir}': {e}"
        )


