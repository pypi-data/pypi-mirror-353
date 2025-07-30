import tempfile
from pathlib import Path
from typer.testing import CliRunner
from src.renpy_assets.cli import app

runner = CliRunner()

def test_generate_command():
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        # Create some dummy image files
        (base / "bg_menu.png").write_text("dummy")
        (base / "hero.png").write_text("dummy")

        result = runner.invoke(app, ["generate", "images", "--path", str(base)])
        assert result.exit_code == 0
        assert "Wrote 2 images declarations" in result.stdout

        generated_file = base / "generated_assets.rpy"
        assert generated_file.exists()
        content = generated_file.read_text()
        assert 'image bg_menu = "bg_menu.png"' in content
        assert 'image hero = "hero.png"' in content
