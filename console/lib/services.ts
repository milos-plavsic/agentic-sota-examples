export type ServiceDef = {
  id: string;
  name: string;
  port: number;
  path: string;
  healthPath?: string;
  category: "agent" | "ml" | "platform";
};

export const DEFAULT_SERVICES: ServiceDef[] = [
  { id: "studio", name: "AutoML Studio", port: 8000, path: "/ui", healthPath: "/health", category: "ml" },
  { id: "research", name: "Research Analyst", port: 8001, path: "/docs", healthPath: "/health", category: "agent" },
  { id: "tutor", name: "Knowledge Tutor", port: 8002, path: "/ui", healthPath: "/health", category: "agent" },
  { id: "market", name: "Market Intel", port: 8003, path: "/ui", healthPath: "/health", category: "agent" },
  { id: "incident", name: "Incident Copilot", port: 8004, path: "/ui", healthPath: "/health", category: "agent" },
  { id: "refactor", name: "Refactor Agent", port: 8005, path: "/ui", healthPath: "/health", category: "agent" },
  { id: "rag", name: "Enterprise RAG", port: 8006, path: "/ui", healthPath: "/health", category: "agent" },
  { id: "learning", name: "Learning Paths", port: 8007, path: "/ui", healthPath: "/health", category: "agent" },
  { id: "tabular", name: "Tabular Arena", port: 8008, path: "/docs", healthPath: "/health", category: "ml" },
  { id: "boost", name: "Categorical Boost", port: 8009, path: "/docs", healthPath: "/health", category: "ml" },
  { id: "nn", name: "NN Predictor", port: 8010, path: "/docs", healthPath: "/health", category: "ml" },
  { id: "mlflow", name: "MLflow UI", port: 5000, path: "/", category: "platform" },
];

export function serviceUrl(host: string, service: ServiceDef): string {
  return `http://${host}:${service.port}${service.path}`;
}

export function healthUrl(host: string, service: ServiceDef): string | null {
  if (!service.healthPath) return null;
  return `http://${host}:${service.port}${service.healthPath}`;
}
