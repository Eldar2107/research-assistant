import typer
from typing import Optional
from src.storage.database import init_db, SessionLocal
from src.storage.repository import get_cached_response, save_response

app = typer.Typer()

@app.command()
def ask(
    query: str = typer.Argument(..., help="Veriləcək sorğu mətni"),
    sources: Optional[str] = typer.Option("", "--sources", "-s", help="Mənbələr"),
    no_cache: bool = typer.Option(False, "--no-cache", help="Keşi istifadə etmə")
):
    init_db()
    db = SessionLocal()
    try:
        if not no_cache:
            cached = get_cached_response(db, query)
            if cached:
                typer.echo(f"[CACHE] {cached.response_text}")
                return

        response_text = f"Nəticə: '{query}' üzrə tədqiqat aparıldı."
        save_response(db, query, response_text, sources or "")

        if sources:
            typer.echo(f"Mənbələr: {sources}")
        typer.echo(response_text)
    finally:
        db.close()

if __name__ == "__main__":
    app()