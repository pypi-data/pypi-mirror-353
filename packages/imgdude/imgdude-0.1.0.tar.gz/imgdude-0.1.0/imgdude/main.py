"""Main FastAPI application for image resizing."""

import os
import re
from pathlib import Path
from typing import Optional, Dict, Any, List, Callable
import asyncio
import hashlib
from contextlib import asynccontextmanager
import time
import concurrent.futures
import multiprocessing

from fastapi import FastAPI, HTTPException, Query, Depends, Request, Response as FastAPIResponse
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from PIL import Image
import aiofiles
import aiofiles.os
import io
import logging
from functools import lru_cache

from .cache import CacheManager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("imgdude")

# Configuration
class Config:
    """Configuration for ImgDude. Values can be overridden by environment variables."""
    # Default values that can be overridden
    MEDIA_ROOT = os.environ.get("IMGDUDE_MEDIA_ROOT", "./media")
    CACHE_DIR = os.environ.get("IMGDUDE_CACHE_DIR", "./cache")
    CACHE_MAX_AGE = int(os.environ.get("IMGDUDE_CACHE_MAX_AGE", "604800"))  # 7 days in seconds
    MAX_WIDTH = int(os.environ.get("IMGDUDE_MAX_WIDTH", "2000"))
    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    # Default to allow all hosts, only filter when explicitly provided
    TRUSTED_HOSTS_PROVIDED = len(os.environ.get("IMGDUDE_TRUSTED_HOSTS", "").strip()) > 0
    TRUSTED_HOSTS = os.environ.get("IMGDUDE_TRUSTED_HOSTS", "*").split(",") if TRUSTED_HOSTS_PROVIDED else ["*"]
    # Default to allow all origins, only filter when explicitly provided
    ALLOWED_ORIGINS_PROVIDED = len(os.environ.get("IMGDUDE_ALLOWED_ORIGINS", "").strip()) > 0
    ALLOWED_ORIGINS = os.environ.get("IMGDUDE_ALLOWED_ORIGINS", "*").split(",") if ALLOWED_ORIGINS_PROVIDED else ["*"]
    CACHE_HEADERS = {
        "Cache-Control": f"public, max-age={CACHE_MAX_AGE}",
        "X-ImgDude-Cache": "HIT"
    }
    NO_CACHE_HEADERS = {
        "Cache-Control": "no-store, no-cache, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0"
    }
    # Thread pool configuration
    CPU_COUNT = multiprocessing.cpu_count()
    IMAGE_PROCESSING_WORKERS = int(os.environ.get("IMGDUDE_IMAGE_WORKERS", str(max(2, CPU_COUNT - 1))))
    FILE_IO_WORKERS = int(os.environ.get("IMGDUDE_IO_WORKERS", str(max(2, CPU_COUNT // 2))))
    # Async connection pool limits
    MAX_CONNECTIONS = int(os.environ.get("IMGDUDE_MAX_CONNECTIONS", "100"))

config = Config()

# Initialize cache manager
cache_manager = CacheManager(config.CACHE_DIR, config.CACHE_MAX_AGE)

# Thread pools will be initialized in lifespan context manager
image_processing_pool = None
file_io_pool = None

# Set a flag for testing mode (allows bypassing security checks in tests)
# This is explicitly set to False here and should only be modified by test code
TESTING_MODE = False

# Environment variable override for testing only - should never be used in production
if os.environ.get("IMGDUDE_TESTING_MODE", "").lower() in ("1", "true", "yes"):
    # Log a warning if this is enabled
    logger.warning("TESTING_MODE is enabled - security checks are bypassed! Never use this in production.")
    TESTING_MODE = True

# Security middleware to check trusted hosts
class TrustedHostMiddleware(BaseHTTPMiddleware):
    """Restricts access to trusted hosts only."
    """
    async def dispatch(self, request: Request, call_next: Callable) -> FastAPIResponse:
        if TESTING_MODE or not config.TRUSTED_HOSTS_PROVIDED or "*" in config.TRUSTED_HOSTS:
            start_time = time.time()
            response = await call_next(request)
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = f"{process_time:.4f} seconds"
            return response

        client_host = request.client.host if request.client else None
        if client_host not in config.TRUSTED_HOSTS:
            logger.warning(f"Blocked request from untrusted host: {client_host}")
            return Response(
                content=f"Access denied: {client_host} is not in trusted hosts list",
                status_code=403
            )
        
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = f"{process_time:.4f} seconds"
        return response

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles startup and shutdown events for the application."""
    # Startup
    global image_processing_pool, file_io_pool
    
    # Initialize thread pools here instead of at module level
    image_processing_pool = concurrent.futures.ThreadPoolExecutor(
        max_workers=config.IMAGE_PROCESSING_WORKERS, 
        thread_name_prefix="img_proc"
    )
    
    file_io_pool = concurrent.futures.ThreadPoolExecutor(
        max_workers=config.FILE_IO_WORKERS, 
        thread_name_prefix="file_io"
    )
    
    os.makedirs(config.MEDIA_ROOT, exist_ok=True)
    os.makedirs(config.CACHE_DIR, exist_ok=True)
    
    # Start cache cleanup task
    cleanup_task = asyncio.create_task(cache_manager.start_periodic_cleanup())
    
    logger.info(f"ImgDude started with:")
    logger.info(f"  MEDIA_ROOT: {config.MEDIA_ROOT}")
    logger.info(f"  CACHE_DIR: {config.CACHE_DIR}")
    logger.info(f"  TRUSTED_HOSTS: {config.TRUSTED_HOSTS}")
    logger.info(f"  ALLOWED_ORIGINS: {config.ALLOWED_ORIGINS}")
    logger.info(f"  IMAGE_PROCESSING_WORKERS: {config.IMAGE_PROCESSING_WORKERS}")
    logger.info(f"  FILE_IO_WORKERS: {config.FILE_IO_WORKERS}")
    logger.info(f"  MAX_CONNECTIONS: {config.MAX_CONNECTIONS}")
    
    try:
        yield
    finally:
        # Shutdown - this will execute even if an exception occurs during startup
        logger.info("Shutting down ImgDude")
        
        # Cancel cleanup task
        if cleanup_task:
            cleanup_task.cancel()
            try:
                await cleanup_task
            except asyncio.CancelledError:
                pass
        
        # Shutdown thread pools
        if image_processing_pool:
            image_processing_pool.shutdown(wait=True)
        if file_io_pool:
            file_io_pool.shutdown(wait=True)
        
        logger.info("ImgDude shutdown complete")

# Create app with middleware
app = FastAPI(
    title="ImgDude",
    description="Image resizing proxy for Nginx",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Add middlewares
app.add_middleware(TrustedHostMiddleware)

# Add CORS middleware with settings based on configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "HEAD"],
    allow_headers=["*"],
)

# Security: Validate path to prevent path traversal
def validate_path(filepath: str) -> Path:
    """Ensures the requested file path is safe and valid."""
    try:
        requested_path = Path(filepath)
        
        # Normalize path and check for path traversal attempts
        normalized_path = Path(os.path.normpath(filepath))
        if ".." in normalized_path.parts or normalized_path.is_absolute():
            logger.warning(f"Path traversal attempt detected: {filepath}")
            raise HTTPException(status_code=403, detail="Path traversal detected")
        
        # Validate file extension
        if requested_path.suffix.lower() not in config.ALLOWED_EXTENSIONS:
            logger.warning(f"Unsupported file extension: {requested_path.suffix}")
            raise HTTPException(status_code=400, detail="Unsupported file extension")
        
        # Construct absolute path
        abs_path = Path(config.MEDIA_ROOT) / requested_path
        
        # Ensure path doesn't escape MEDIA_ROOT
        try:
            abs_path.relative_to(Path(config.MEDIA_ROOT))
        except ValueError:
            logger.warning(f"Invalid path attempt: {filepath}")
            raise HTTPException(status_code=403, detail="Invalid path")
        
        return abs_path
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        logger.error(f"Path validation error: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid file path")

@lru_cache(maxsize=1000)  # Increased cache size for better performance
def get_cache_path(filepath: Path, width: Optional[int]) -> Path:
    """Generates a unique cache path for a resized image."""
    # Create a unique filename based on the original path and resize parameters
    original_path = str(filepath.relative_to(config.MEDIA_ROOT) if filepath.is_absolute() else filepath)
    cache_key = f"{original_path}_w{width}"
    hashed = hashlib.md5(cache_key.encode()).hexdigest()
    
    # Preserve original extension
    return Path(config.CACHE_DIR) / f"{hashed}{filepath.suffix}"

@lru_cache(maxsize=100)
def get_mime_type(file_extension: str) -> str:
    """Returns the mime type for a given file extension."""
    extension_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }
    return extension_map.get(file_extension.lower(), "application/octet-stream")

async def resize_image(img_data: bytes, width: int) -> bytes:
    """Resizes an image to the specified width, keeping the aspect ratio."""
    # Run in the dedicated thread pool to avoid blocking the event loop
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(image_processing_pool, _resize_image_sync, img_data, width)

async def read_file_async(file_path: Path) -> bytes:
    """Reads a file asynchronously using the file I/O thread pool."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(file_io_pool, _read_file_sync, file_path)

async def write_file_async(file_path: Path, data: bytes) -> None:
    """Writes a file asynchronously using the file I/O thread pool."""
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(file_io_pool, _write_file_sync, file_path, data)

def _read_file_sync(file_path: Path) -> bytes:
    """Synchronous version of read_file to run in a thread pool."""
    with open(file_path, "rb") as f:
        return f.read()

def _write_file_sync(file_path: Path, data: bytes) -> None:
    """Synchronous version of write_file to run in a thread pool."""
    os.makedirs(file_path.parent, exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(data)

def _resize_image_sync(img_data: bytes, width: int) -> bytes:
    """Synchronous version of resize_image to run in a thread pool."""
    try:
        start_time = time.time()
        img = Image.open(io.BytesIO(img_data))
        
        # Skip resize if the image is already the requested width or smaller
        if img.width <= width:
            logger.debug(f"Image already at or below requested width ({img.width} <= {width})")
            return img_data
        
        # Calculate new height maintaining aspect ratio
        ratio = width / float(img.width)
        height = int(ratio * img.height)
        
        # Resize the image with optimal quality/speed tradeoff
        img = img.resize((width, height), Image.LANCZOS)
        
        # Save to bytes - use original format if available, otherwise JPEG
        buffer = io.BytesIO()
        format_to_use = img.format if img.format else 'JPEG'
        
        # Use optimize=True for JPEG and PNG for smaller file sizes
        save_options = {}
        if format_to_use in ('JPEG', 'PNG'):
            save_options['optimize'] = True
        
        # Convert RGBA to RGB for JPEG format
        if format_to_use == 'JPEG' and img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
            
        img.save(buffer, format=format_to_use, **save_options)
        
        process_time = time.time() - start_time
        logger.debug(f"Image resized in {process_time:.4f} seconds")
        
        return buffer.getvalue()
    except Exception as e:
        logger.error(f"Image resize error: {str(e)}")
        raise HTTPException(status_code=500, detail="Error resizing image")

# Connection limits and semaphores for concurrent requests
# This prevents too many simultaneous connections
connection_semaphore = asyncio.Semaphore(config.MAX_CONNECTIONS)

@app.get("/image/{filepath:path}")
async def get_image(filepath: str, w: Optional[int] = Query(None, ge=1, le=config.MAX_WIDTH)):
    """Serve an image, optionally resizing it."""
    async with connection_semaphore:  # Limit concurrent connections
        try:
            start_time = time.time()
            
            # Validate path
            abs_path = validate_path(filepath)
            
            # Check if file exists
            if not os.path.exists(abs_path):  # Using synchronous check for better performance
                logger.warning(f"Image not found: {abs_path}")
                raise HTTPException(status_code=404, detail="Image not found")
            
            # Prepare response headers
            headers = {}
            
            # If no resize requested, serve original
            if w is None:
                image_data = await read_file_async(abs_path)
                
                logger.debug(f"Serving original image: {filepath}")
                return Response(
                    content=image_data,
                    media_type=get_mime_type(abs_path.suffix),
                    headers=headers
                )
            
            # Check cache for resized image
            cache_path = get_cache_path(abs_path, w)
            if os.path.exists(cache_path):  # Using synchronous check for better performance
                # Serve from cache
                cached_data = await read_file_async(cache_path)
                
                # Mark file as recently accessed in cache manager
                cache_manager.mark_accessed(str(cache_path))
                
                process_time = time.time() - start_time
                logger.debug(f"Cache hit for {filepath} (w={w}), served in {process_time:.4f} seconds")
                
                # Add cache hit headers
                headers.update(config.CACHE_HEADERS)
                
                return Response(
                    content=cached_data,
                    media_type=get_mime_type(abs_path.suffix),
                    headers=headers
                )
            
            # Read the original image
            image_data = await read_file_async(abs_path)
            
            # Resize the image
            resized_data = await resize_image(image_data, w)
            
            # Save to cache
            await write_file_async(cache_path, resized_data)
            
            process_time = time.time() - start_time
            logger.debug(f"Cache miss for {filepath} (w={w}), processed in {process_time:.4f} seconds")
            
            # Add cache miss headers
            headers.update({
                "Cache-Control": f"public, max-age={config.CACHE_MAX_AGE}",
                "X-ImgDude-Cache": "MISS"
            })
            
            return Response(
                content=resized_data,
                media_type=get_mime_type(abs_path.suffix),
                headers=headers
            )
            
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/cache/stats")
async def cache_stats() -> Dict[str, Any]:
    """Get cache statistics."""
    return await cache_manager.get_cache_stats()

@app.post("/cache/clean")
async def clean_cache() -> Dict[str, Any]:
    """Manually clean the cache."""
    result = await cache_manager.clean_cache()
    return result

# Health check endpoint
@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint."""
    from . import __version__
    return {
        "status": "healthy", 
        "version": __version__,
        "trusted_hosts": config.TRUSTED_HOSTS,
        "allowed_origins": config.ALLOWED_ORIGINS,
        "default_port": 12312,
        "workers": {
            "image_processing": config.IMAGE_PROCESSING_WORKERS,
            "file_io": config.FILE_IO_WORKERS,
            "max_connections": config.MAX_CONNECTIONS
        }
    } 