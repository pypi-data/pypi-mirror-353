from __future__ import annotations

import os
import sys
from collections.abc import Sequence
from copy import copy
from typing import List

from ...client import Client
from .api import APIDriver
from .errors import handle_state_errors
from .file import FileDriver
from .models import (
    Action,
    CheckAction,
    LabelAction,
    State,
    TableConfigAction,
)


class StateMachine:
    def __init__(self, client: Client):
        self.client = client

    @handle_state_errors
    def pull(self, filename: str, table_refs: Sequence[str]) -> None:
        api_state = APIDriver(self.client)
        if not table_refs:
            table_refs = sorted(api_state.table_refs)
        for table_ref in table_refs:
            api_state.load_table(table_ref)
            api_state.load_all_checks(table_ref)
            print(f"Loaded table {table_ref}")
        output_file = FileDriver(api_state.state)
        output_file.write_file(filename)
        print(f'Configuration saved to "{filename}"')

    @handle_state_errors
    def examine(self, table_ref: str, check_ref: str | None = None) -> None:
        api_state = APIDriver(self.client)
        if check_ref:
            api_state.load_check(table_ref, check_ref)
        else:
            api_state.load_table(table_ref)
        output = FileDriver(api_state.state)
        print(output.to_string().strip())

    @handle_state_errors
    def apply(
        self,
        filename: str,
        dryrun: bool = False,
        noninteractive: bool = False,
        destroy: bool = False,
    ) -> None:
        input_file = FileDriver()
        input_file.load_file(filename)
        api_state = APIDriver(self.client)
        api_state.load_from_state(input_file.state)
        if destroy:
            actions = self._compute_actions(
                api_state.state, State(), permit_destroy=True
            )
        else:
            actions = self._compute_actions(api_state.state, input_file.state)
        if not actions:
            print("No changes detected")
            return
        self._display_diff(actions)
        print(f"Total changes count: {len(actions)}")
        if dryrun:
            return
        if not noninteractive:
            self._prompt_continue()
        errors = 0
        for i, action in enumerate(actions):
            print(f"({i + 1}/{len(actions)}) {action} ... ", end="", flush=True)
            try:
                api_state.apply_action(action)
                print("Success")
            except RuntimeError as e:
                errors += 1
                print(f"Error ({e})")
        if errors:
            print()
            print(f"Total errors count: {errors}")

    def _prompt_continue(self) -> None:
        print()
        try:
            value = input("Do you want to apply these changes? (y/N) ")
            print("")
            if value.lower() in {"y", "yes"}:
                return
        except (KeyboardInterrupt, EOFError) as e:
            print(os.linesep)
        print("Cancelled")
        sys.exit(0)

    def _display_diff(self, actions: List[Action]) -> None:
        for action in actions:
            print(action)
            print(action.diff())
            print("")

    def _compute_actions(
        self, from_state: State, to_state: State, permit_destroy: bool = False
    ) -> List[Action]:
        actions: List[Action] = []
        for table_ref in sorted(from_state.tables.keys() | to_state.tables.keys()):
            # Consider table configuration
            from_table = from_state.tables[table_ref]
            to_table = to_state.tables[table_ref]

            if from_table.config and not to_table.config:
                # On table deconfiguration, just unset check_cadence_type
                to_table.config = from_table.config | {"check_cadence_type": None}

            if (
                permit_destroy or to_table.config
            ) and from_table.config != to_table.config:
                actions.append(
                    TableConfigAction(
                        prev=from_table.config, new=to_table.config, table_ref=table_ref
                    )
                )

            if (
                to_table
                and to_table.labels is not None
                and to_table.labels != from_table.labels
            ):
                actions.append(
                    LabelAction(
                        prev=from_table.labels if from_table else None,
                        new=to_table.labels,
                        table_ref=table_ref,
                    )
                )

            # Consider checks
            for check_ref in sorted(from_table.checks.keys() | to_table.checks.keys()):
                from_check = from_table.checks.get(check_ref)
                to_check = to_table.checks.get(check_ref)

                if (
                    to_check
                    and from_check
                    and to_check.labels is not None
                    and to_check.labels != from_check.labels
                ):
                    actions.append(
                        LabelAction(
                            prev=from_check.labels if from_check else None,
                            new=to_check.labels,
                            table_ref=table_ref,
                            check_ref=check_ref,
                        )
                    )

                # Now that we've considered labels, set them to none so we can do the comparison
                # for updating the check
                if comparison_from_check := from_check:
                    comparison_from_check = copy(from_check)
                    comparison_from_check.labels = None

                if comparison_to_check := to_check:
                    comparison_to_check = copy(to_check)
                    comparison_to_check.labels = None

                if (
                    permit_destroy or to_check
                ) and comparison_to_check != comparison_from_check:
                    actions.append(
                        CheckAction(
                            prev=from_check,
                            new=to_check,
                            table_ref=table_ref,
                            check_ref=check_ref,
                        )
                    )

        return actions
