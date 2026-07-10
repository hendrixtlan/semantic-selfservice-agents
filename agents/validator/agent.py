"""Validator: gate de calidad. Compila (determinístico) + dry-run (EUC).

Expuesto como servicio HTTP simple, no conversacional: lo invocan Modeler
y Dashboarder. Es el mismo gate que corre el CI (scripts/compile_gate.mjs),
garantizando que 'compila en validación' == 'compila en CI' == 'sirve en Publisher'.
"""
import os
import subprocess
import tempfile

from flask import Flask, jsonify, request

from shared.euc import UserContext, dry_run_as_user

app = Flask(__name__)


@app.post("/validate")
def validate():
    payload = request.get_json()
    malloy, package = payload["malloy"], payload["package"]

    # 1. Gate determinístico: compilar con @malloydata/malloy
    with tempfile.NamedTemporaryFile(suffix=".malloy", mode="w", delete=False) as f:
        f.write(malloy)
        path = f.name
    compile_proc = subprocess.run(
        ["node", "scripts/compile_gate.mjs", "--single", path],
        capture_output=True, text=True, timeout=120,
    )
    if compile_proc.returncode != 0:
        return jsonify({"compiles": False, "error": compile_proc.stderr[-2000:]})

    result = {"compiles": True}

    # 2. Dry-run con la identidad del usuario (si el compile emitió SQL)
    sql = compile_proc.stdout.strip()
    if sql:
        try:
            ctx = UserContext.from_a2a_headers(dict(request.headers))
            result["estimated_bytes_processed"] = dry_run_as_user(
                ctx, os.environ["GOOGLE_CLOUD_PROJECT"], sql
            )
            result["dry_run_ok"] = True
            result["validated_as"] = ctx.email
        except Exception as e:  # noqa: BLE001 — el motivo viaja al spec
            result["dry_run_ok"] = False
            result["error"] = str(e)

    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
