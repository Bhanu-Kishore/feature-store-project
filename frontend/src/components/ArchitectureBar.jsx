import React from 'react';
import { ChevronRight, Database, GitBranch, Cpu, Server, CheckCircle2, Box } from 'lucide-react';

const PIPELINE_STEPS = [
  { label: 'Raw Data', sub: 'Parquet / DVC', icon: Box },
  { label: 'Feature ETL', sub: 'Definitions', icon: GitBranch },
  { label: 'Feast Store', sub: 'Online Registry', icon: Database },
  { label: 'FastAPI Gateway', sub: ':8000 /predict', icon: Server },
  { label: 'MLflow Model', sub: 'Scikit-Learn', icon: Cpu },
  { label: 'Real-time Output', sub: 'Inference', icon: CheckCircle2 },
];

export default function ArchitectureBar() {
  return (
    <div className="architecture-bar-container">
      <div className="architecture-header">
        <span className="architecture-title">End-to-End Feature Store Flow</span>
      </div>
      <div className="architecture-steps">
        {PIPELINE_STEPS.map((step, idx) => {
          const Icon = step.icon;
          return (
            <React.Fragment key={step.label}>
              <div className="architecture-step-item">
                <div className="step-icon-box">
                  <Icon size={14} />
                </div>
                <div className="step-text-box">
                  <span className="step-name">{step.label}</span>
                  <span className="step-sub">{step.sub}</span>
                </div>
              </div>
              {idx < PIPELINE_STEPS.length - 1 && (
                <ChevronRight size={14} className="architecture-arrow" />
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
}
