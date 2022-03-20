from threading import Thread
from typing import Tuple

from plover.engine import StenoEngine
from plover.steno_dictionary import StenoDictionary

from plover_modal_dictionary.dictionary import ModalDictionary


class ModalExtension():
    def __init__(self, engine: StenoEngine) -> None:
        self._engine = engine
        self._engine.hook_connect("stroked", self.on_stroke)

    def start(self):
        pass

    def stop(self):
        pass

    def on_stroke(self, _: Tuple[str, ...]) -> None:
        dict: StenoDictionary
        for dict in self._engine.dictionaries.dicts:
            if isinstance(dict, ModalDictionary):
                dict.update_state()
