from threading import Thread, Event

from hardware import hw_config as hwc
from utils.log import get_logger

log = get_logger(__name__)

if hwc.Simulation.show_gui:
    if hwc.Simulation.enabled:
        event_started = Event()


        def start_gui():
            log.info('Creating SimulationGUI...')
            from hardware.generator import HW_GENERATOR
            from utils.hardware.simulation.gui import WorldGui
            bricks_controllers = HW_GENERATOR.environment_simulator.bricks_controllers
            word_gui = WorldGui(bricks_controllers.world, bricks_controllers, bricks_controllers.bricks)

            log.info('Showing SimulationGUI...')
            event_started.set()
            word_gui.mainloop()


        Thread(target=start_gui, name='GuiThread', daemon=True).start()
        event_started.wait()
    else:
        log.info('Skipped creating of SimulationGUI: Simulation is disabled')
