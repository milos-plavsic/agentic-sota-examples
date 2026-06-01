"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import {
  DEFAULT_SERVICES,
  healthUrl,
  serviceUrl,
  type ServiceDef,
} from "../lib/services";

type HealthState = "unknown" | "up" | "down";

export default function Page() {
  const [host, setHost] = useState("127.0.0.1");
  const [health, setHealth] = useState<Record<string, HealthState>>({});
  const [filter, setFilter] = useState<"all" | ServiceDef["category"]>("all");

  const services = useMemo(() => {
    if (filter === "all") return DEFAULT_SERVICES;
    return DEFAULT_SERVICES.filter((s) => s.category === filter);
  }, [filter]);

  const probe = useCallback(async () => {
    const next: Record<string, HealthState> = {};
    await Promise.all(
      DEFAULT_SERVICES.map(async (service) => {
        const url = healthUrl(host, service);
        if (!url) {
          next[service.id] = "unknown";
          return;
        }
        try {
          const ctrl = new AbortController();
          const timer = setTimeout(() => ctrl.abort(), 2500);
          const res = await fetch(url, { signal: ctrl.signal, mode: "cors" });
          clearTimeout(timer);
          next[service.id] = res.ok ? "up" : "down";
        } catch {
          next[service.id] = "down";
        }
      }),
    );
    setHealth(next);
  }, [host]);

  useEffect(() => {
    probe();
    const id = setInterval(probe, 15000);
    return () => clearInterval(id);
  }, [probe]);

  return (
    <main>
      <h1 style={{ marginTop: 0 }}>Service Console</h1>
      <p style={{ color: "var(--muted)" }}>
        Start services on the documented ports, then open UIs or OpenAPI docs. Health probes run every 15s.
      </p>

      <div className="panel" style={{ marginBottom: "1.25rem", display: "flex", gap: "1rem", flexWrap: "wrap" }}>
        <label>
          Host{" "}
          <input value={host} onChange={(e) => setHost(e.target.value.trim() || "127.0.0.1")} />
        </label>
        <label>
          Filter{" "}
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value as typeof filter)}
            style={{
              background: "var(--bg)",
              color: "var(--text)",
              border: "1px solid var(--border)",
              borderRadius: 6,
              padding: "0.35rem 0.55rem",
            }}
          >
            <option value="all">All</option>
            <option value="agent">Agents</option>
            <option value="ml">ML</option>
            <option value="platform">Platform</option>
          </select>
        </label>
        <button
          type="button"
          onClick={probe}
          style={{
            background: "var(--accent)",
            color: "#0d1117",
            border: 0,
            borderRadius: 6,
            padding: "0.45rem 0.9rem",
            fontWeight: 600,
            cursor: "pointer",
          }}
        >
          Refresh health
        </button>
      </div>

      <div className="grid">
        {services.map((service) => {
          const url = serviceUrl(host, service);
          const state = health[service.id] ?? "unknown";
          const badge =
            state === "up" ? (
              <span className="badge ok">healthy</span>
            ) : state === "down" ? (
              <span className="badge down">offline</span>
            ) : (
              <span className="badge warn">n/a</span>
            );
          return (
            <article key={service.id} className="panel">
              <div style={{ display: "flex", justifyContent: "space-between", gap: "0.5rem" }}>
                <strong>{service.name}</strong>
                {badge}
              </div>
              <div style={{ fontSize: 14, color: "var(--muted)", margin: "0.35rem 0 0.6rem" }}>
                :{service.port} · {service.category}
              </div>
              <a href={url}>{url}</a>
            </article>
          );
        })}
      </div>
    </main>
  );
}
