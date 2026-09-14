import os
from typer.testing import CliRunner
from src.cli import app
from src.storage.database import SessionLocal, init_db
from src.storage.repository import save_response

runner = CliRunner()

def setup_function():
    if os.path.exists("research_assistant.db"):
        try:
            os.remove("research_assistant.db")
        except PermissionError:
            pass

def test_cli_ask_basic():
    result = runner.invoke(app, ["Python nədir?"])
    assert result.exit_code == 0
    assert "Python nədir?" in result.stdout

def test_cli_ask_with_sources_and_no_cache():
    result = runner.invoke(app, ["Deep Learning nədir?", "--sources", "dl.pdf", "--no-cache"])
    assert result.exit_code == 0
    assert "dl.pdf" in result.stdout

def test_cli_ask_cache_hit():
    init_db()
    db = SessionLocal()
    try:
        save_response(db, "Unique Cache Test Query?", "Nəticə tədqiq olundu.")
    finally:
        db.close()

    result = runner.invoke(app, ["Unique Cache Test Query?"])
    assert result.exit_code == 0
    assert "[CACHE]" in result.stdout