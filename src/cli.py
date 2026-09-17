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
                # Testlərin gözlədiyi dəqiq [CACHE] formatı
                typer.echo(f"[CACHE] {cached.response_text}")
                return

        # Testlərin gözlədiyi: Sorğunu ekrana çap edirik
        typer.echo(query)
        typer.echo("🤖 Süni intellekt düşünür (Bu bir az vaxt apara bilər)...")
        
        # Asinxron orchestrator ilə cavab alırıq
        answer_obj = asyncio.run(answer_question(query, sources, use_cache=not no_cache))
        
        response_text = answer_obj.answer if hasattr(answer_obj, "answer") else str(answer_obj)

        # Nəticəni bazaya yazırıq
        save_response(db, query, response_text, sources or "")

        if sources:
            typer.echo(f"Mənbələr: {sources}")
            
        typer.echo(f"\n[🎯 AI Nəticəsi]:\n{response_text}")
        
    except Exception as e:
        typer.echo(f"❌ Xəta baş verdi: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    app()