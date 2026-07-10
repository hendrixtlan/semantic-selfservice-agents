# Evals

- `golden_routing.jsonl`: golden set de clasificación de intención del
  orquestador, incluyendo casos de rebote. Nota del diseño del hub: cuando el
  orquestador general exista, este golden set **se muda al hub** — el routing
  entre cuadrillas pertenece a quien rutea.
- El gate de compilación (`scripts/compile_gate.mjs`) es el eval permanente
  del modelo semántico: corre en Validator, CI y pre-deploy.
