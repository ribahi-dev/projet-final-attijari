// Types miroir des schemas Pydantic du backend — LE contrat de l'API.
export type Role = "admin" | "director" | "advisor";

export interface User {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  role: Role;
  is_active: boolean;
  phone: string | null;
  telegram_chat_id: string | null;
  created_at: string;
}

export interface Client {
  id: number;
  first_name: string;
  last_name: string;
  cin: string;
  phone: string | null;
  address: string | null;
  profession: string | null;
  monthly_income: string | null;
  is_active: boolean;
  created_at: string;
  // Profil de risque (calibrage du scoring par client — directeur).
  frequent_traveler: boolean;
  high_net_worth: boolean;
  business_account: boolean;
  risk_profile_note: string | null;
}

export interface Account {
  id: number;
  account_number: string;
  account_type: "current" | "savings";
  balance: string;
  status: "active" | "blocked" | "closed";
  client_id: number;
  created_at: string;
}

export interface RiskScore {
  score: number;
  confidence_level: string;
  explanation: string;
  model_version: string;
  shap_values: Record<string, number> | null;
}

export interface Transaction {
  id: number;
  transaction_type: "deposit" | "withdrawal" | "transfer";
  amount: string;
  city: string | null;
  description: string | null;
  account_id: number;
  destination_account_id: number | null;
  created_by_id: number;
  created_at: string;
  risk_score: RiskScore | null;
}

export interface Alert {
  id: number;
  alert_type: "transaction_risk" | "login_security";
  level: "low" | "medium" | "high" | "critical";
  message: string;
  status: "open" | "in_progress" | "closed";
  // Qualification du directeur à la clôture — c'est l'étiquette qui
  // alimente le réentraînement du modèle (boucle de feedback).
  resolution: "confirmed_fraud" | "false_positive" | null;
  transaction_id: number | null;
  created_at: string;
  closed_at: string | null;
  transaction: Transaction | null;
}

// Surveillance de la fraude INTERNE : profil d'activité de chaque
// conseiller, calculé depuis les transactions et le journal d'audit.
export interface AdvisorActivity {
  user_id: number;
  name: string;
  tx_count: number;
  total_amount: string;
  night_count: number;
  high_risk_count: number;
  max_ops_same_account: number;
  failed_logins: number;
  flags: string[];
  is_anomalous: boolean;
}

export interface InternalMonitoring {
  advisors: AdvisorActivity[];
  peer_avg_amount: string;
}

// Suivi de la fraude & santé du modèle (MLOps) : métriques calculées sur
// les qualifications humaines (boucle de feedback), pas sur le jeu de test.
export interface ModelHealth {
  model_version: string | null;
  total_scored: number;
  open_alerts: number;
  alerts_processed: number;
  confirmed_fraud: number;
  false_positives: number;
  precision_production: number | null;
  false_positive_rate: number | null;
  feedback_available: number;
  avg_processing_hours: number | null;
  score_distribution: { range_start: number; count: number }[];
}

export interface Kpi {
  total_clients: number;
  total_accounts: number;
  total_transactions: number;
  open_alerts: number;
  total_deposits: string;
  total_withdrawals: string;
  average_risk_score: number | null;
}

export interface TrendPoint {
  day: string;
  transaction_count: number;
  total_amount: string;
}

export interface TypeDistribution {
  transaction_type: string;
  count: number;
  total_amount: string;
}

export interface AuditLog {
  id: number;
  user_id: number | null;
  action: string;
  entity_type: string | null;
  entity_id: number | null;
  ip_address: string | null;
  success: boolean;
  details: string | null;
  created_at: string;
}
