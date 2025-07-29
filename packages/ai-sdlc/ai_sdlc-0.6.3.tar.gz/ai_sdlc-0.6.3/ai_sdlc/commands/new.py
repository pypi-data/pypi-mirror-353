"""`aisdlc new` – start a work-stream from an idea title."""

from __future__ import annotations

import datetime
import sys

from ai_sdlc.utils import ROOT, load_config, slugify, write_lock


def run_new(args: list[str]) -> None:
    """Create the work-stream folder and first markdown file."""
    if not args:
        print('Usage: aisdlc new "Idea title"')
        sys.exit(1)

    # Load configuration to get the first step
    config = load_config()
    first_step = config["steps"][0]

    idea_text = " ".join(args)
    slug = slugify(idea_text)

    workdir = ROOT / "doing" / slug
    if workdir.exists():
        print(f"❌  Work-stream '{slug}' already exists.")
        sys.exit(1)

    try:
        workdir.mkdir(parents=True)
        idea_file = workdir / f"{first_step}-{slug}.md"
        idea_file.write_text(
            f"# {idea_text}\n\n## Problem\n\n## Solution\n\n## Rabbit Holes\n",
        )

        write_lock(
            {
                "slug": slug,
                "current": first_step,
                "created": datetime.datetime.utcnow().isoformat(),
            },
        )
        print(f"✅  Created {idea_file}.  Fill it out, then run `aisdlc next`.")
    except OSError as e:
        print(f"❌  Error creating work-stream files for '{slug}': {e}")
        sys.exit(1)
