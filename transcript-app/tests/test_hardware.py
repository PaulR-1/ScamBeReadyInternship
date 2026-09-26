from app.core.hardware import HardwareInfo, plan_compute


def info(**overrides) -> HardwareInfo:
    base = {
        "cuda_available": True,
        "cuda_device_count": 1,
        "gpu_name": "NVIDIA GeForce RTX 3050 Laptop GPU",
        "vram_total_gb": 4.0,
        "vram_free_gb": 3.5,
        "ram_total_gb": 40.0,
        "cpu_threads": 8,
        "notes": [],
    }
    base.update(overrides)
    return HardwareInfo(**base)


def test_four_gb_gpu_uses_quantised_large_v3():
    plan = plan_compute("large-v3", info())
    assert (plan.device, plan.compute_type) == ("cuda", "int8_float16")


def test_large_gpu_uses_float16():
    plan = plan_compute("large-v3", info(vram_total_gb=12.0))
    assert (plan.device, plan.compute_type) == ("cuda", "float16")


def test_tiny_gpu_falls_back_to_cpu():
    plan = plan_compute("large-v3", info(vram_total_gb=2.0))
    assert plan.device == "cpu"


def test_small_model_still_fits_the_four_gb_gpu_at_float16():
    plan = plan_compute("medium", info())
    assert (plan.device, plan.compute_type) == ("cuda", "float16")


def test_no_cuda_means_cpu():
    plan = plan_compute("large-v3", info(cuda_available=False, gpu_name=None, vram_total_gb=None))
    assert (plan.device, plan.compute_type) == ("cpu", "int8")


def test_explicit_cpu_preference_wins():
    assert plan_compute("large-v3", info(), "cpu").device == "cpu"


def test_unknown_vram_prefers_the_safe_precision():
    plan = plan_compute("large-v3", info(vram_total_gb=None))
    assert (plan.device, plan.compute_type) == ("cuda", "int8_float16")
