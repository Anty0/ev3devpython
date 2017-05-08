def _build_hw_generator():
    from hardware import hw_config as hwc
    from hardware.brick_main import BRICK_MAIN
    from hardware.bricks import BRICKS
    from hardware.ports import PORTS

    if hwc.Simulation.enabled:
        from utils.hardware.generator import build_simulated as _build_hw_generator_simulated
        from hardware.world_map import WORLD_MAP

        return _build_hw_generator_simulated(WORLD_MAP, BRICK_MAIN, *BRICKS, **PORTS)
    else:
        from utils.hardware.generator import build_real as _build_hw_generator_real

        return _build_hw_generator_real(BRICK_MAIN, *BRICKS, **PORTS)


HW_GENERATOR = _build_hw_generator()
