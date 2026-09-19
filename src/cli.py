import typer
from typing import Optional
import asyncio
from src.storage.database import init_db, SessionLocal
from src.storage.repository import get_cached_response, save_response
from src.concurrency.orchestrator import answer_question

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
        # 1. Keşi yoxlayırıq
        if not no_cache:
            cached = get_cached_response(db, query)
            if cached:
                typer.echo(f"[CACHE] {cached.response_text}")
                return

        typer.echo(query)
        typer.echo("🤖 Süni intellekt düşünür (Bu bir az vaxt apara bilər)...")
        
        # Asinxron orchestrator ilə cavab və mənbələri alırıq
        result = asyncio.run(answer_question(query, sources, use_cache=not no_cache))
        
        response_text = result.get("answer", "")
        used_sources = result.get("sources", [])

        # Nəticəni bazaya yazırıq
        save_response(db, query, response_text, sources or "")

        if sources:
            typer.echo(f"Seçilən mənbələr: {sources}")
            
        typer.echo(f"\n[🎯 AI Nəticəsi]:\n{response_text}")

        # Mənbələri (başlıq və linkləri) ekranda səliqəli siyahı şəklində göstəririk
        if used_sources:
            typer.echo("\n📚 İstifadə olunan mənbələr (References):")
            for i, src in enumerate(used_sources, 1):
                title = getattr(src, "title", "Mənbə")
                url = getattr(src, "url", "#")
                typer.echo(f"  [{i}] {title} -> {url}")
        
    except Exception as e:
        typer.echo(f"❌ Xəta baş verdi: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    app()