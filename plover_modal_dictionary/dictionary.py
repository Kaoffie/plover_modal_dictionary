from plover.steno_dictionary import StenoDictionary
from plover.dictionary.base import _get_dictionary_class
from typing import Union, Tuple, Callable

import json


# Dictionary options

EXCLUDE_ENTRY = "exclude_entry"
EXIT_ON_MISMATCH = "exit_on_mismatch"
EXIT_ON_MATCH = "exit_on_match"
IGNORE_FOLDING = "ignore_folding"


CONFIG_DEFAULTS = {
    EXCLUDE_ENTRY: False, 
    EXIT_ON_MISMATCH: True, 
    EXIT_ON_MATCH: False,
    IGNORE_FOLDING: True
}


# Dictionary options

ENTRY = "entry"
MAIN_DICT = "dict"
EXIT = "exit"

DICT_LIST = [ENTRY, MAIN_DICT, EXIT]


class ModalDictionary(StenoDictionary):

    readonly = True

    def __init__(self) -> None:
        super().__init__()
        self._reverse_lookup = None
        self.readonly = True

        self._options = {}
        self._lookup_funcs = {}

        self._longest_key = 0

        self._new_stroke = True
        self._current_stroke = ""
        self._ignore = False
        self._to_activate = False
        self._matched = False
        self._to_deactivate = False

        self._activated = False
        self._dormant = False
        self._dormant_buffer = 0

        self._json_data = {}
    
    def _get_json_lookup_func(self, dict_name: str) -> Callable:
        def dict_get(stroke_tup: Tuple[str, ...]) -> str:
            return self._json_data[dict_name].get("/".join(stroke_tup), None)
        
        return dict_get

    def _load(self, filename: str) -> None:
        with open(filename, "r", encoding="utf-8") as fp:
            self._json_data = json.load(fp)
        
        for key, default in CONFIG_DEFAULTS.items():
            self._options[key] = self._json_data.get(key, default)
        
        for dict_name in DICT_LIST:
            sub_dict_data = self._json_data.get(dict_name, None)

            if sub_dict_data is None:
                self._lookup_funcs[dict_name] = lambda _: None

            elif isinstance(sub_dict_data, dict):
                self._lookup_funcs[dict_name] = self._get_json_lookup_func(dict_name)
                longest = max(len(key.split("/")) for key in sub_dict_data.keys())
                self._longest_key = max(self._longest_key, longest)

            elif isinstance(sub_dict_data, str):
                sub_dict = _get_dictionary_class(sub_dict_data).load(sub_dict_data)
                self._longest_key = max(self._longest_key, sub_dict.longest_key)
                self._lookup_funcs[dict_name] = sub_dict.get
            
            else:
                raise ValueError(f"Invalid dictionary: {dict_name}")
    
    def _lookup(self, key: Tuple[str, ...]) -> str:
        key_len = len(key)

        if self._ignore or not key:
            raise KeyError

        if self._new_stroke:
            self._new_stroke = False
            self._current_stroke = key[-1]
        else:
            self._matched = False

            if key[-1] != self._current_stroke and self._options[IGNORE_FOLDING]:
                self._ignore = True
                raise KeyError

        if (
            self._activated 
            or (self._dormant and key_len > self._dormant_buffer)
        ):
            output = self._lookup_funcs[EXIT](key)

            if output is not None:
                self._to_deactivate = True
            else:
                output = self._lookup_funcs[MAIN_DICT](key)

            if output is not None:
                self._matched = True

                if not self._activated:
                    self._to_activate = True

                return output
            
        if (not self._activated) or (not self._options[EXCLUDE_ENTRY]):
            entry_output = self._lookup_funcs[ENTRY](key)

            if entry_output is not None:
                self._matched = True
                self._to_activate = True
                return entry_output
        
        raise KeyError

    def __contains__(self, key: Tuple[str, ...]) -> bool:
        if len(key) > self.longest_key:
            return False
        try:
            self._lookup(key)
        except KeyError:
            return False
        return True

    def __getitem__(self, key: Tuple[str, ...]) -> str:
        if len(key) > self.longest_key:
            raise KeyError
        return self._lookup(key)

    def get(self, key: Tuple[str, ...], fallback: str = None) -> str:
        if len(key) > self.longest_key:
            return fallback
        try:
            return self._lookup(key)
        except KeyError:
            return fallback

    def update_state(self) -> None:
        if self._activated:
            if (
                self._to_deactivate
                or (self._options[EXIT_ON_MISMATCH] and not self._matched)
                or (self._options[EXIT_ON_MATCH] and self._matched)
            ):
                self._activated = False
                self._dormant = True
                self._dormant_buffer = 1

        elif self._to_activate:
            if not self._to_deactivate:
                self._activated = True
            
        elif self._dormant:
            self._dormant_buffer += 1
            if self._dormant_buffer >= self.longest_key:
                self._dormant = False
                self._dormant_buffer = 0
        
        self._new_stroke = True
        self._ignore = False
        self._to_activate = False
        self._matched = False
        self._to_deactivate = False 
    
    @property
    def longest_key(self) -> int:
        return self._longest_key
