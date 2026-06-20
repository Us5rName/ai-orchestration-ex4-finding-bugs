"""Architecture boundary tests.

Enforces the service composition rules documented in ADR-005 and
docs/plan-wiki/03-Module-Design.md:

- Concrete service construction is allowed only in sdk/_wiring.py.
- Package-local __init__.py re-exports of the package's own facade are allowed.
- sdk/sdk.py imports only service interfaces (not concrete facades).
- The CLI (__main__.py) imports only the public SDK, not domain services.
- Domain service modules must not import another service package's concrete facade.

Uses AST inspection so that rules are enforced without executing the modules.
"""

from __future__ import annotations

import ast
from pathlib import Path

SRC_ROOT = Path(__file__).parent.parent.parent / "src" / "ex04"

# Each service package's own __init__.py is allowed to re-export its facade.
_SERVICE_PACKAGES = {"agent", "analysis", "comparison", "graph", "vault"}


def _ast_imports(path: Path) -> list[tuple[str, str | None]]:
    """Return (module, name_or_None) pairs for every import in a Python file.

    For ``from A import B`` the entry is (A, B).
    For ``import A`` the entry is (A, None).
    """
    tree = ast.parse(path.read_text(encoding="utf-8"))
    results: list[tuple[str, str | None]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            for alias in node.names:
                results.append((node.module, alias.name))
        elif isinstance(node, ast.Import):
            for alias in node.names:
                results.append((alias.name, None))
    return results


def _concrete_service_imports(imports: list[tuple[str, str | None]]) -> list[str]:
    """Return import strings that reference a concrete (non-interface) service facade.

    An import is considered 'concrete' when it names a service package directly
    (e.g. ``ex04.services.agent``) rather than its ``.interface`` sub-module.
    Package-local __init__ re-exports are excluded separately by the callers.
    """
    flagged: list[str] = []
    for module, name in imports:
        if not module.startswith("ex04.services."):
            continue
        # Allow interface modules
        if module.endswith(".interface"):
            continue
        # Allow sub-modules of a service (not the facade itself)
        parts = module.split(".")
        # ex04.services.<pkg> or ex04.services.<pkg>.<sub>
        if len(parts) < 3:
            continue
        flagged.append(f"{module}.{name}" if name else module)
    return flagged


class TestSDKImportBoundary:
    """sdk/sdk.py must import only service interfaces."""

    def test_sdk_imports_only_interfaces(self) -> None:
        sdk_py = SRC_ROOT / "sdk" / "sdk.py"
        imports = _ast_imports(sdk_py)
        violations = _concrete_service_imports(imports)
        assert not violations, (
            f"sdk/sdk.py imports concrete service facades: {violations}. "
            "Use service interfaces instead."
        )


class TestWiringAllowed:
    """sdk/_wiring.py is the permitted composition root for concrete imports."""

    def test_wiring_may_import_concrete_services(self) -> None:
        wiring_py = SRC_ROOT / "sdk" / "_wiring.py"
        imports = _ast_imports(wiring_py)
        # Verify _wiring.py has at least one concrete service import (it is the composition root)
        concrete = [m for m, _ in imports if m.startswith("ex04.services.") and not m.endswith(".interface")]
        assert concrete, "_wiring.py should import concrete services (it is the composition root)"


class TestCLIImportBoundary:
    """The CLI must not import domain services directly."""

    def test_cli_does_not_import_domain_services(self) -> None:
        main_py = SRC_ROOT / "__main__.py"
        imports = _ast_imports(main_py)
        violations = [
            m for m, _ in imports
            if m.startswith("ex04.services.")
        ]
        assert not violations, (
            f"CLI imports domain services directly: {violations}. "
            "Route through the SDK instead."
        )


class TestCrossServiceImportBoundary:
    """Domain service modules must not import another service package's concrete facade."""

    def _is_package_local(self, source_pkg: str, import_module: str) -> bool:
        """Return True when import_module is within the same service package as source_pkg."""
        prefix = f"ex04.services.{source_pkg}"
        return import_module.startswith(prefix)

    def test_no_cross_service_concrete_imports(self) -> None:
        services_dir = SRC_ROOT / "services"
        violations: list[str] = []

        for pkg_dir in sorted(services_dir.iterdir()):
            if not pkg_dir.is_dir() or pkg_dir.name.startswith("_"):
                continue
            pkg_name = pkg_dir.name

            for py_file in sorted(pkg_dir.rglob("*.py")):
                # Allow the package's own __init__.py to re-export its facade
                if py_file.name == "__init__.py":
                    continue
                imports = _ast_imports(py_file)
                for module, name in imports:
                    if not module.startswith("ex04.services."):
                        continue
                    if module.endswith(".interface"):
                        continue
                    if self._is_package_local(pkg_name, module):
                        continue
                    # Concrete cross-service import detected
                    violations.append(
                        f"{py_file.relative_to(SRC_ROOT)} imports {module}"
                        + (f".{name}" if name else "")
                    )

        assert not violations, (
            "Cross-service concrete imports found:\n"
            + "\n".join(f"  {v}" for v in violations)
        )


class TestPackageLocalExportsAllowed:
    """Package __init__.py re-exports of own facade are explicitly permitted."""

    def test_service_init_files_are_not_flagged(self) -> None:
        """Each service __init__.py re-exports its own facade — this is intentional."""
        services_dir = SRC_ROOT / "services"
        for pkg_dir in services_dir.iterdir():
            if not pkg_dir.is_dir() or pkg_dir.name.startswith("_"):
                continue
            init_py = pkg_dir / "__init__.py"
            if not init_py.exists():
                continue
            imports = _ast_imports(init_py)
            for module, _name in imports:
                if not module.startswith("ex04.services."):
                    continue
                # Must be within same package (local re-export)
                assert module.startswith(f"ex04.services.{pkg_dir.name}"), (
                    f"{init_py.relative_to(SRC_ROOT)} imports from another package: {module}"
                )
