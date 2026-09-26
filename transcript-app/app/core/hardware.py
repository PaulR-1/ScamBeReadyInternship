"""Detects the available compute backend and picks a model precision that fits."""

from __future__ import annotations

import logging
import shutil
import subprocess
from dataclasses import asdict, dataclass

from app.core import cuda

logger = logging.getLogger(__name__)

# Half-precision weight size in GB. Runtime needs roughly this plus ~1.5 GB of
# activations and beam-search state, which is what the fit check below assumes.
_MODEL_FP16_GB = {
    "large-v3": 3.1,
    "large-v2": 3.1,
    "distil-large-v3": 1.5,
    "medium": 1.5,
    "small": 0.5,
    "base": 0.15,
    "tiny": 0.08,
}
_RUNTIME_OVERHEAD_GB = 1.5


@dataclass(frozen=True)
class HardwareInfo:
    cuda_available: bool
    cuda_device_count: int
    gpu_name: str | None
    vram_total_gb: float | None
    vram_free_gb: float | None
    ram_total_gb: float | None
    cpu_threads: int
    notes: list[str]

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class ComputePlan:
    device: str
    compute_type: str
    reason: str


def _query_nvidia_smi() -> tuple[str | None, float | None, float | None]:
    exe = shutil.which("nvidia-smi")
    if not exe:
        return None, None, None
    try:
        out = subprocess.run(
            [exe, "--query-gpu=name,memory.total,memory.free", "--format=csv,noheader,nounits"],
            capture_output=True,
            text=True,
            timeout=15,
            check=True,
        ).stdout.strip()
    except (subprocess.SubprocessError, OSError) as exc:
        logger.info("nvidia-smi query failed, continuing without VRAM detail: %s", exc)
        return None, None, None
    if not out:
        return None, None, None
    name, total, free = (part.strip() for part in out.splitlines()[0].split(",")[:3])
    return name, float(total) / 1024, float(free) / 1024


CUDA_LIBS_HINT = (
    "Install the CUDA runtime into this environment with: "
    "pip install nvidia-cublas-cu12 nvidia-cudnn-cu12"
)


def detect() -> HardwareInfo:
    notes: list[str] = []

    cuda_count = 0
    try:
        cuda.prepare()
        import ctranslate2

        cuda_count = ctranslate2.get_cuda_device_count()
    except Exception as exc:  # ctranslate2 raises various errors when CUDA libs are missing
        notes.append(f"CUDA unavailable: {exc}")

    gpu_name, vram_total, vram_free = _query_nvidia_smi()

    if cuda_count > 0 and not cuda.libraries_ready():
        cuda_count = 0
        notes.append(f"An NVIDIA GPU is present but its CUDA libraries are missing. {CUDA_LIBS_HINT}")
    elif cuda_count == 0 and gpu_name:
        notes.append(f"An NVIDIA GPU is present but CTranslate2 cannot use it. {CUDA_LIBS_HINT}")

    ram_total = None
    cpu_threads = 4
    try:
        import psutil

        ram_total = psutil.virtual_memory().total / 1024**3
        cpu_threads = psutil.cpu_count(logical=False) or psutil.cpu_count(logical=True) or 4
    except Exception as exc:
        notes.append(f"Could not read CPU/RAM details: {exc}")

    return HardwareInfo(
        cuda_available=cuda_count > 0,
        cuda_device_count=cuda_count,
        gpu_name=gpu_name,
        vram_total_gb=round(vram_total, 2) if vram_total else None,
        vram_free_gb=round(vram_free, 2) if vram_free else None,
        ram_total_gb=round(ram_total, 2) if ram_total else None,
        cpu_threads=cpu_threads,
        notes=notes,
    )


def plan_compute(model: str, info: HardwareInfo, device_preference: str = "auto") -> ComputePlan:
    """Choose device and precision for `model`, preferring accuracy that still fits in VRAM."""
    if device_preference == "cpu":
        return ComputePlan("cpu", "int8", "CPU was requested explicitly.")

    if not info.cuda_available:
        if device_preference == "cuda":
            return ComputePlan("cpu", "int8", "GPU was requested but CUDA is not available.")
        return ComputePlan("cpu", "int8", "No usable CUDA device detected.")

    weights = _MODEL_FP16_GB.get(model, 3.1)
    vram = info.vram_total_gb
    if vram is None:
        return ComputePlan(
            "cuda", "int8_float16", "GPU detected but VRAM size unknown; using the safer precision."
        )

    if vram >= weights + _RUNTIME_OVERHEAD_GB:
        return ComputePlan("cuda", "float16", f"{vram:.1f} GB VRAM fits {model} at full precision.")
    if vram >= weights / 2 + _RUNTIME_OVERHEAD_GB:
        return ComputePlan(
            "cuda",
            "int8_float16",
            f"{vram:.1f} GB VRAM is too small for float16 {model}, using 8-bit weights.",
        )
    return ComputePlan(
        "cpu", "int8", f"{vram:.1f} GB VRAM cannot hold {model}; running on CPU instead."
    )
