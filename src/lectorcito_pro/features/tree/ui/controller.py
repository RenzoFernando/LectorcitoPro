
from __future__ import annotations

from ..application.generate_tree import generate_tree_report


class TreeUIController:
    def generate(
        self,
        *,
        source_folder: str,
        output_path: str,
        use_config: bool,
        config: dict,
    ) -> tuple[str, str | None]:
        return generate_tree_report(
            source_folder=source_folder,
            output_path=output_path,
            use_config=use_config,
            config=config,
        )
