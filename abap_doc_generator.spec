# -*- mode: python ; coding: utf-8 -*-
#
# abap_doc_generator.spec
# PyInstaller spec file for ABAP Documentation Generator
#
# Build with:   pyinstaller abap_doc_generator.spec --clean
# Output:       dist/ABAPDocGenerator/ABAPDocGenerator.exe

# ── Fix: Windows native stack overflow (0xC00000FD) occurs when PyInstaller
# ── recursively processes hundreds of submodules from torch/transformers/scipy.
# ── Solution: raise Python recursion limit AND avoid collect_submodules() for
# ── any heavy ML library — list only what is actually used instead.
import sys ; sys.setrecursionlimit(sys.getrecursionlimit() * 10)

import os
from PyInstaller.utils.hooks import collect_data_files, copy_metadata

# ── Paths ────────────────────────────────────────────────────────────────────
ROOT = os.path.dirname(os.path.abspath(SPEC))

# ── Data files to bundle ──────────────────────────────────────────────────────
# collect_data_files only gathers non-Python assets (JSON, HTML, etc.) — safe.
# collect_submodules is NOT used for heavy libs to avoid stack overflow.
datas = [
    # Main app
    (os.path.join(ROOT, "app.py"),                    "."),
    (os.path.join(ROOT, "app_pipeline.py"),           "."),

    # Core module
    (os.path.join(ROOT, "core"),                      "core"),

    # Assets (logo, etc.)
    (os.path.join(ROOT, "assets"),                    "assets"),

    # Streamlit theme config
    (os.path.join(ROOT, ".streamlit"),                ".streamlit"),

    # Static knowledge base
    (os.path.join(ROOT, "sap_knowledge_base.json"),   "."),

    # Streamlit static web assets (JS, HTML, CSS) — data only, no submodules
    *collect_data_files("streamlit"),

    # Altair/Vega schemas used by Streamlit charts
    *collect_data_files("altair"),

    # Package metadata (.dist-info) for packages that call
    # importlib.metadata.version() at import time — required in frozen .exe
    *copy_metadata("streamlit"),
    *copy_metadata("altair"),
    *copy_metadata("click"),
    *copy_metadata("packaging"),
    # importlib_metadata not needed — Python 3.10+ has importlib.metadata built-in
]

# ── Hidden imports ────────────────────────────────────────────────────────────
# Listed explicitly — NO collect_submodules() for heavy ML packages.
# collect_submodules("transformers") has 500+ entries and causes
# a Windows native stack overflow (0xC00000FD) during PyInstaller analysis.
hidden_imports = [

    # ── Streamlit core (explicit, no collect_submodules) ──────────────────
    "streamlit",
    "streamlit.web",
    "streamlit.web.cli",
    "streamlit.web.server",
    "streamlit.web.server.server",
    "streamlit.runtime",
    "streamlit.runtime.scriptrunner",
    "streamlit.runtime.scriptrunner.magic_funcs",
    "streamlit.runtime.state",
    "streamlit.runtime.caching",
    "streamlit.runtime.media_file_manager",
    "streamlit.runtime.metrics_util",
    "streamlit.components",
    "streamlit.components.v1",
    "streamlit.elements",

    # ── ChromaDB — client/embedded mode only (no server/fastapi) ──────────
    "chromadb",
    "chromadb.api",
    "chromadb.api.client",
    "chromadb.api.models",
    "chromadb.api.segment",
    "chromadb.api.types",
    "chromadb.config",
    "chromadb.db",
    "chromadb.db.impl",
    "chromadb.db.impl.sqlite",
    "chromadb.db.mixins",
    "chromadb.errors",
    "chromadb.execution",
    "chromadb.execution.executor",
    "chromadb.execution.executor.local",
    "chromadb.quota",
    "chromadb.rate_limiting",
    "chromadb.segment",
    "chromadb.segment.impl",
    "chromadb.segment.impl.manager",
    "chromadb.segment.impl.metadata",
    "chromadb.segment.impl.vector",
    "chromadb.telemetry",
    "chromadb.telemetry.product",
    "chromadb.telemetry.product.events",
    "chromadb.types",
    "chromadb.utils",

    # ── Sentence Transformers (explicit subset — no collect_submodules) ────
    "sentence_transformers",
    "sentence_transformers.models",
    "sentence_transformers.losses",
    "sentence_transformers.evaluation",
    "sentence_transformers.util",
    "sentence_transformers.cross_encoder",

    # ── HuggingFace Transformers (explicit subset — NOT full collect) ──────
    # collect_submodules("transformers") = 500+ modules = stack overflow
    "transformers",
    "transformers.modeling_utils",
    "transformers.tokenization_utils",
    "transformers.tokenization_utils_fast",
    "transformers.configuration_utils",
    "transformers.models",
    "transformers.models.auto",
    "transformers.models.bert",
    "transformers.models.roberta",
    "transformers.models.distilbert",
    "transformers.pipelines",
    "transformers.file_utils",
    "transformers.utils",

    # ── PyTorch ───────────────────────────────────────────────────────────
    "torch",
    "torch.nn",
    "torch.nn.functional",
    "torchvision",

    # ── FAISS ─────────────────────────────────────────────────────────────
    "faiss",

    # ── PDF parsing ───────────────────────────────────────────────────────
    "fitz",
    "pymupdf",

    # ── Data / ML ─────────────────────────────────────────────────────────
    "numpy",
    "pandas",
    "regex",
    "tqdm",
    "scipy",
    "sklearn",

    # ── API clients ───────────────────────────────────────────────────────
    "ollama",
    "requests",

    # ── Standard library extras ───────────────────────────────────────────
    "email.mime.multipart",
    "email.mime.text",
    "pkg_resources",
    "importlib.metadata",
    "importlib.resources",
    "sqlite3",
]

# ── Analysis ──────────────────────────────────────────────────────────────────
a = Analysis(
    [os.path.join(ROOT, "run_app.py")],
    pathex=[ROOT],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Heavy optional ML packages not used by this app
        "tensorboard",
        "tensorflow",
        "keras",
        "jax",
        "flax",
        # Dev tools
        "pytest",
        "black",
        "isort",
        "mypy",
        "IPython",
        "notebook",
        "jupyter",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# ── EXE ───────────────────────────────────────────────────────────────────────
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="ABAPDocGenerator",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    icon=os.path.join(ROOT, "assets", "icon.ico"),
)

# ── COLLECT — output folder ───────────────────────────────────────────────────
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="ABAPDocGenerator",
)
