from threading import Thread, Event

from hardware import hw_config as hwc
from utils.log import get_logger

log = get_logger(__name__)


def show(force=False):
    if force or hwc.Simulation.show_gui:
        if force or hwc.Simulation.enabled:
            event_started = Event()

            def start_gui():
                try:
                    log.info('Creating SimulationGUI...')
                    from hardware.generator import HW_GENERATOR
                    from utils.hardware.simulation.gui import WorldGui
                    word_gui = WorldGui(HW_GENERATOR)

                    log.info('Showing SimulationGUI...')
                    event_started.set()
                    word_gui.mainloop()
                except:
                    log.exception('Failed creating of SimulationGUI.')
                    event_started.set()

            Thread(target=start_gui, name='GuiThread', daemon=True).start()
            event_started.wait()
        else:
            log.info('Skipped creating of SimulationGUI: Simulation is disabled')
