"""Single SDK entry point with dependency injection.

All business logic flows through this module. CLI, GUI, and REST layers
delegate here — they never import internal domain services directly.
"""
