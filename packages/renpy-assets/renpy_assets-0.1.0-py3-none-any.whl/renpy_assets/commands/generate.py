from pathlib import Path
import typer
from src.renpy_assets.utils.file_utilities import find_files_by_patterns

app = typer.Typer(help="Generate Ren'Py declarations for assets.")

ASSET_TYPES = {
    "images": [r"\.png$", r"\.jpg$", r"\.jpeg$", r"\.webp$"],
    "audio": [r"\.ogg$", r"\.mp3$", r"\.wav$"],
    "fonts": [r"\.ttf$", r"\.otf$"],
}


def generate_declaration(asset_type: str, file_path: Path, base_path: Path) -> str:
    """Create a Ren'Py declaration using relative paths based on asset type."""
    name = file_path.stem.replace(" ", "_").lower()
    rel_path = file_path.relative_to(base_path).as_posix()

    if asset_type == "images":
        return f"image {name} = \"{rel_path}\""
    elif asset_type == "audio":
        return f"define audio.{name} = \"{rel_path}\""
    elif asset_type == "fonts":
        return f"define {name}_font = \"{rel_path}\""
    return ""


@app.command()
def generate(
    asset_type: str = typer.Argument(..., help="The asset type to generate declarations for (images, audio, fonts, or all)."),
    path: Path = typer.Option("game", "--path", "-p", help="Directory to search assets in"),
    output: Path = typer.Option("asset_declarations.rpy", "--output", "-o", help="Output file for generated declarations")
):
    """
    Generate Ren'Py declarations for assets of a specific type or all types.

    Usage:
        renpy-assets generate images --path game/assets --output images.rpy
        renpy-assets generate all --output all_assets.rpy
    """
    if asset_type != "all" and asset_type not in ASSET_TYPES:
        typer.echo(f"Unsupported asset type: '{asset_type}'. Choose from: {', '.join(ASSET_TYPES.keys())}, all.")
        raise typer.Exit(code=1)

    resolved_path = path.resolve()
    typer.echo(f"\n🔍 Searching assets in: {resolved_path}")

    declarations = []
    type_counts = {}

    if asset_type == "all":
        for kind, patterns in ASSET_TYPES.items():
            files = find_files_by_patterns(str(resolved_path), patterns)
            if files:
                header = f"\n# --- {kind.capitalize().removesuffix('s')} Assets ---"
                declarations.append(header)
                count = 0
                for f in files:
                    decl = generate_declaration(kind, f, resolved_path)
                    if decl:
                        declarations.append(decl)
                        count += 1
                type_counts[kind] = count
    else:
        patterns = ASSET_TYPES[asset_type]
        files = find_files_by_patterns(str(resolved_path), patterns)
        if files:
            header = f"# --- {asset_type.capitalize().removesuffix('s')} Assets ---"
            declarations.append(header)
            count = 0
            for f in files:
                decl = generate_declaration(asset_type, f, resolved_path)
                if decl:
                    declarations.append(decl)
                    count += 1
            type_counts[asset_type] = count

    if declarations:
        output.parent.mkdir(parents=True, exist_ok=True)
        with open(output, "w", encoding="utf-8") as f:
            f.write("\n".join(declarations))

        typer.echo("📁 Generating declarations...")
        for t, count in type_counts.items():
            label = t.capitalize().removesuffix("s")
            typer.echo(f" ─ {label:<15} {count} declaration{'s' if count != 1 else ''}")

        typer.echo(f"\n✅ Done! Total declarations written: {sum(type_counts.values())}")
        typer.echo(f"📝 Output saved to: {output.resolve()}")
    else:
        typer.echo("No matching assets found to generate declarations.")
