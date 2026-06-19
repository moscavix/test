from __future__ import annotations

from word_a11y_fixer import gui


def test_gui_module_exposes_main_entrypoint() -> None:
    assert callable(gui.main)
    assert gui.AccessibilityFixerApp.__name__ == "AccessibilityFixerApp"
