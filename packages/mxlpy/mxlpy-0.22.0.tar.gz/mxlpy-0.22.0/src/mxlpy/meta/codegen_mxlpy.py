"""Generate mxlpy code from a model."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from mxlpy.meta.sympy_tools import fn_to_sympy, list_of_symbols, sympy_to_python_fn
from mxlpy.types import Derived

if TYPE_CHECKING:
    import sympy

    from mxlpy.model import Model

__all__ = [
    "generate_mxlpy_code",
]

_LOGGER = logging.getLogger()


def generate_mxlpy_code(model: Model) -> str:
    """Generate a mxlpy model from a model."""
    functions: dict[str, tuple[sympy.Expr, list[str]]] = {}

    # Variables and parameters
    variables = model.get_raw_variables()
    parameters = model.get_parameter_values()

    # Derived
    derived_source = []
    for k, der in model.get_raw_derived().items():
        fn = der.fn
        fn_name = fn.__name__
        if (
            expr := fn_to_sympy(fn, origin=k, model_args=list_of_symbols(der.args))
        ) is None:
            msg = f"Unable to parse fn for derived value '{k}'"
            raise ValueError(msg)

        functions[fn_name] = (expr, der.args)

        derived_source.append(
            f"""        .add_derived(
                "{k}",
                fn={fn_name},
                args={der.args},
            )"""
        )

    # Reactions
    reactions_source = []
    for k, rxn in model.get_raw_reactions().items():
        fn = rxn.fn
        fn_name = fn.__name__
        if (
            expr := fn_to_sympy(fn, origin=k, model_args=list_of_symbols(rxn.args))
        ) is None:
            msg = f"Unable to parse fn for reaction '{k}'"
            raise ValueError(msg)

        functions[fn_name] = (expr, rxn.args)
        stoichiometry: list[str] = []
        for var, stoich in rxn.stoichiometry.items():
            if isinstance(stoich, Derived):
                if (
                    expr := fn_to_sympy(
                        fn, origin=var, model_args=list_of_symbols(stoich.args)
                    )
                ) is None:
                    msg = f"Unable to parse fn for stoichiometry '{var}'"
                    raise ValueError(msg)
                functions[fn_name] = (expr, rxn.args)
                args = ", ".join(f'"{k}"' for k in stoich.args)
                stoich = (  # noqa: PLW2901
                    f"""Derived(fn={fn.__name__}, args=[{args}])"""
                )
            stoichiometry.append(f""""{var}": {stoich}""")

        reactions_source.append(
            f"""        .add_reaction(
                "{k}",
                fn={fn_name},
                args={rxn.args},
                stoichiometry={{{",".join(stoichiometry)}}},
            )"""
        )

    # Surrogates
    if len(model._surrogates) > 0:  # noqa: SLF001
        msg = "Generating code for Surrogates not yet supported."
        _LOGGER.warning(msg)

    # Combine all the sources
    functions_source = "\n\n".join(
        sympy_to_python_fn(fn_name=name, args=args, expr=expr)
        for name, (expr, args) in functions.items()
    )
    source = [
        "from mxlpy import Model\n",
        functions_source,
        "def create_model() -> Model:",
        "    return (",
        "        Model()",
    ]
    if len(parameters) > 0:
        source.append(f"        .add_parameters({parameters})")
    if len(variables) > 0:
        source.append(f"        .add_variables({variables})")
    if len(derived_source) > 0:
        source.append("\n".join(derived_source))
    if len(reactions_source) > 0:
        source.append("\n".join(reactions_source))

    source.append("    )")

    return "\n".join(source)
