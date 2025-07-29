from pathlib import Path

import sphinx_genai as core


def save_embeddings(app, exception):
    path = Path(app.outdir) / Path("embeddings.json")
    core.save_embeddings(path, "huggingface")


def setup(app):
    app.connect("build-finished", save_embeddings)
    return {
        "version": "0.0.1",
        "parallel_read_safe": True,
        "parallel_read_safe": True
    }
