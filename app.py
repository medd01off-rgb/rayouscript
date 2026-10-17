import base64
from decimal import Decimal, getcontext
import math
import numpy as np
import pandas as pd
from scipy.stats import nbinom, poisson
import streamlit as st

getcontext().prec = 60

# --- أود كود المحرك والقواعد كاملين ---
_ENCODED_DATA = "Rk9SIE1PUkUgSU5GT1JNQVRJT04sIFBMRUFTRSBDT05UQUNUIFVTIFZJQSBXSEFUU0FQUCArMjEyIDcgNjAgNDAgMjYgODI="
_ENCODED_PHONE = "KzIxMiA3IDYwIDQwIDI2IDgy"
_ENCODED_TITLE = "U0NSSVBUIEJZIFJBWU9VIC0gVjIuMQ=="
_ENCODED_WARN_TITLE = "V0FSUklORyAmIERJU0NMQUlNRVI="
_ENCODED_WARN1_TEXT = "VEhJUyBTQ1JJUFQgVVNFUyBNQVRIRU1BVElDQUwgRVFVQVRJT05TIEFORCBQUk9HUkFNTUVEIEFMR09SSVRITVMgVE8gR0VORVJBVEUgUFJFRElDVElPTlM="
_ENCODED_WARN2_TEXT = "UFJFRElDVElPTlMgTUFZIENPTlRBSU4gQSBNQVJHSU4gT0YgRVJST1IgQU5EIEFSRSBOT1QgR1VBUkFOVEVFRCBSRVNVTFRT"
_ENCODED_WARN3_TEXT = "VVNFIFRIRVNFIFBSRURJQ1RJT05TIEZPUiBBTkFMWVNJUzBQVVJQT1NFUyBPTkxZ"


def _decode_data(s):
  return base64.b64decode(s).decode("utf-8")


_SEC_HEX = "646566205f765f736563286d632c20707764293a0a202020207472793a0a202020202020202070203d20737472286d63292e73706c697428272e27290a202020202020202078692c207864203d20696e7428705b305d292c20696e7428705b315d290a202020202020202072203d20287864202a202834383030202b2078692929202f2f203130300a202020202020202072657475726e207374722872295b2d343a5d203d3d2073747228707764292e737472697028290a202020206578636570743a0a202020202020202072657475726e2046616c7365"
exec(bytes.fromhex(_SEC_HEX).decode("utf-8"))


class QuantumFootballEngineFull:

  def __init__(self, league_avg_home=1.55, league_avg_away=1.18):
    self.prior_home = league_avg_home
    self.prior_away = league_avg_away
    self.weights = np.array([0.35, 0.25, 0.20, 0.12, 0.08])

  def parse_scores(self, scores_str):
    matches = scores_str.strip().split()
    if len(matches) != 5:
      raise ValueError("يجب إدخال 5 نتائج مباريات بالضبط.")
    scored, conceded = [], []
    for m in matches:
      s, c = map(int, m.split("-"))
      scored.append(s)
      conceded.append(c)
    return np.array(scored), np.array(conceded)

  def _dynamic_momentum(self, scored, conceded):
    trend_s = scored[0] - scored[-1]
    trend_c = conceded[0] - conceded[-1]
    momentum_xg_boost = 0.05 if trend_s > 0 else (-0.05 if trend_s < 0 else 0)
    momentum_def_boost = -0.05 if trend_c < 0 else (0.05 if trend_c > 0 else 0)
    return momentum_xg_boost, momentum_def_boost

  def _bayesian_xg(self, scored, conceded, is_home=True):
    weighted_scored = np.sum(scored * self.weights)
    weighted_conceded = np.sum(conceded * self.weights)
    prior = self.prior_home if is_home else self.prior_away
    mom_att, mom_def = self._dynamic_momentum(scored, conceded)
    xg = (weighted_scored * 0.70) + (prior * 0.30) + mom_att
    defensive_shock = (weighted_conceded * 0.60) + (prior * 0.40) + mom_def
    return max(0.1, xg), max(0.1, defensive_shock)

  def _engine_zero_inflated_dixon_coles(
      self, lambda_h, lambda_a, max_goals=14, rho=-0.13
  ):
    matrix = np.zeros((max_goals + 1, max_goals + 1))
    for x in range(max_goals + 1):
      for y in range(max_goals + 1):
        px = poisson.pmf(x, lambda_h)
        py = poisson.pmf(y, lambda_a)
        tau = 1.0
        if x == 0 and y == 0:
          tau = 1.0 - (lambda_h * lambda_a * rho) * 1.15
        elif x == 0 and y == 1:
          tau = 1.0 + (lambda_h * rho)
        elif x == 1 and y == 0:
          tau = 1.0 + (lambda_a * rho)
        elif x == 1 and y == 1:
          tau = 1.0 - rho * 1.05
        matrix[x, y] = px * py * tau
    return np.clip(matrix, 0, None) / np.sum(np.clip(matrix, 0, None))

  def _engine_negative_binomial(
      self, lambda_h, lambda_a, max_goals=14, dispersion=1.25
  ):
    matrix = np.zeros((max_goals + 1, max_goals + 1))
    for x in range(max_goals + 1):
      for y in range(max_goals + 1):
        n_h = lambda_h / (dispersion - 1) if dispersion > 1 else 10
        p_h = n_h / (n_h + lambda_h)
        n_a = lambda_a / (dispersion - 1) if dispersion > 1 else 10
        p_a = n_a / (n_a + lambda_a)
        matrix[x, y] = nbinom.pmf(x, n_h, p_h) * nbinom.pmf(y, n_a, p_a)
    return matrix / np.sum(matrix)

  def _engine_stochastic_monte_carlo(
      self, lambda_h, lambda_a, sims=50000, max_goals=14
  ):
    np.random.seed(42)
    noise_h = np.random.normal(1.0, 0.12, sims)
    noise_a = np.random.normal(1.0, 0.12, sims)
    sim_h = np.random.poisson(np.maximum(0.05, lambda_h * noise_h))
    sim_a = np.random.poisson(np.maximum(0.05, lambda_a * noise_a))
    matrix = np.zeros((max_goals + 1, max_goals + 1))
    for h, a in zip(sim_h, sim_a):
      if h <= max_goals and a <= max_goals:
        matrix[h, a] += 1
    return matrix / np.sum(matrix)

  def predict_match(self, home_str, away_str):
    h_s, h_c = self.parse_scores(home_str)
    a_s, a_c = self.parse_scores(away_str)

    h_att, h_def = self._bayesian_xg(h_s, h_c, is_home=True)
    a_att, a_def = self._bayesian_xg(a_s, a_c, is_home=False)

    lambda_h = max(0.15, ((h_att * 1.1 + a_def * 0.9) / 2.0) * 1.08)
    lambda_a = max(0.15, (a_att * 0.9 + h_def * 1.1) / 2.0)

    m_dc = self._engine_zero_inflated_dixon_coles(lambda_h, lambda_a)
    m_nb = self._engine_negative_binomial(lambda_h, lambda_a)
    m_mc = self._engine_stochastic_monte_carlo(lambda_h, lambda_a)

    stacked_matrix = (m_dc * 0.50) + (m_nb * 0.25) + (m_mc * 0.25)
    stacked_matrix /= np.sum(stacked_matrix)

    scores = []
    for h in range(stacked_matrix.shape[0]):
      for a in range(stacked_matrix.shape[1]):
        prob_raw = stacked_matrix[h, a] * 100
        if prob_raw > 0:
          prob_dec = Decimal(f"{prob_raw:.20f}")
          odds_dec = (
              Decimal("100") / prob_dec if prob_dec > 0 else Decimal("999")
          )

          scores.append({
              "Rank": 0,
              "Exact_Score": f"{h} - {a}",
              "Probability_%": f"{prob_dec:f}",
              "Implied_Odds": f"{odds_dec:f}",
              "_sort_key": float(prob_raw),
          })

    df = (
        pd.DataFrame(scores)
        .sort_values(by="_sort_key", ascending=False)
        .reset_index(drop=True)
    )
    df["Rank"] = df.index + 1
    return df

  def extract_fipa_predictions(self, df_predictions):
    fipa_records = []
    for idx, row in df_predictions.iterrows():
      prob_float = float(row["_sort_key"])
      if prob_float < 0.001000:
        continue
      odds_str = str(row["Implied_Odds"])
      if "e" in odds_str.lower():
        odds_str = f"{Decimal(odds_str):f}"
      if "." not in odds_str:
        continue
      dec_part = odds_str.split(".")[1]
      dec_digits = "".join(c for c in dec_part if c.isdigit())
      if len(dec_digits) < 12:
        continue
      b1_pairs = [dec_digits[0:2], dec_digits[2:4], dec_digits[4:6]]
      b2_pairs = [dec_digits[6:8], dec_digits[8:10], dec_digits[10:12]]
      is_valid = False
      reason_str = ""

      if "00" in b1_pairs:
        zero_idx = b1_pairs.index("00") + 1
        is_valid = True
        reason_str = (
            f"FIPA MATCH (Zero Pair '00' at Pair {zero_idx} -> Product equals"
            " 0)"
        )

      if not is_valid:
        for pos_idx in range(3):
          if b1_pairs[pos_idx] == b2_pairs[pos_idx]:
            is_valid = True
            reason_str = (
                "FIPA MATCH (Positional Pair Match at index"
                f" {pos_idx+1}: .{b1_pairs[pos_idx]})"
            )
            break

      if not is_valid:
        p1 = int(b1_pairs[0])
        p2 = int(b1_pairs[1])
        p3 = int(b1_pairs[2])
        if p1 > 0:
          prod = p1 * p2 * p3
          surd = prod ** (1 / 3)
          val = surd / p1
          p1_str = f"{p1:02d}"

          if 1.0 <= val < 10.0:
            val_unscaled_str = f"{Decimal(val):.30f}"
            dec_unscaled = val_unscaled_str.split(".")[1][:12]
            u_pairs = [dec_unscaled[i : i + 2] for i in range(0, 12, 2)]
            u_p0, u_p1 = u_pairs[0], u_pairs[1]
            if u_p0 in u_pairs[1:]:
              is_valid = True
              reason_str = (
                  f"FIPA MATCH (Unscaled First Decimal Pair .{u_p0} Repeated:"
                  f" {u_pairs})"
              )
            elif p1_str == u_p0 or p1_str == u_p1:
              is_valid = True
              reason_str = (
                  f"FIPA MATCH (Surd Divisor Pair .{p1_str} Matches Unscaled"
                  f" Decimal Pair: {u_pairs[:2]})"
              )

            if not is_valid:
              val_scaled = val * 10.0
              val_scaled_str = f"{Decimal(val_scaled):.30f}"
              int_part = int(val_scaled_str.split(".")[0])
              dec_scaled = val_scaled_str.split(".")[1][:12]
              s_pairs = [dec_scaled[i : i + 2] for i in range(0, 12, 2)]
              s_p0, s_p1 = s_pairs[0], s_pairs[1]
              s_p0_int = int(s_p0)
              diff0 = abs(int_part - s_p0_int)

              if diff0 <= 1:
                is_valid = True
                reason_str = (
                    f"FIPA MATCH (Int-Dec Diff Rule [Pair 1]: |{int_part} -"
                    f" {s_p0_int}| = {diff0} <= 1)"
                )
              elif p1_str == s_p0 or p1_str == s_p1:
                is_valid = True
                reason_str = (
                    f"FIPA MATCH (Surd Divisor Pair .{p1_str} Matches Scaled"
                    f" Decimal Pair: {s_pairs[:2]})"
                )
              elif s_p0 == s_p1:
                is_valid = True
                reason_str = (
                    f"FIPA MATCH (Direct Match: Initial Pairs .{s_p0} == .{s_p1})"
                )
              elif s_p0 in s_pairs[2:] or s_p1 in s_pairs[2:]:
                matched_pair = s_p0 if s_p0 in s_pairs[2:] else s_p1
                reason_str = (
                    f"FIPA MATCH (Repeated Pair .{matched_pair} in Scaled"
                    f" Decimals: {s_pairs})"
                )
                is_valid = True

          elif val < 1.0:
            val_str = f"{Decimal(val):.30f}"
            dec_after = val_str.split(".")[1][:12]
            pairs = [dec_after[i : i + 2] for i in range(0, 12, 2)]
            pair0_int = int(pairs[0])
            pair1_int = int(pairs[1])
            target_derived_int = (
                pair0_int - 1 if pair1_int < pair0_int else pair0_int + 1
            )
            target1_str = f"{pair0_int:02d}"
            target2_str = f"{target_derived_int:02d}"

            if p1_str == pairs[0] or p1_str == pairs[1]:
              is_valid = True
              reason_str = (
                  f"FIPA MATCH (Surd Divisor Pair .{p1_str} Matches Decimal Pair"
                  f" (< 1.0): {pairs[:2]})"
              )
            elif target1_str in pairs[1:] or target2_str in pairs[1:]:
              matched = target1_str if target1_str in pairs[1:] else target2_str
              reason_str = (
                  f"FIPA MATCH (Target Pair .{matched} Repeated in Decimals:"
                  f" {pairs})"
              )
              is_valid = True

      if is_valid:
        rec = dict(row)
        rec["FIPA_Reason"] = reason_str
        fipa_records.append(rec)

    df_fipa = pd.DataFrame(fipa_records)
    if df_fipa.empty:
      return df_fipa

    df_fipa = df_fipa.sort_values(
        by="_sort_key", ascending=False
    ).reset_index(drop=True)

    indices_to_remove = set()
    records_to_add = []

    i = 0
    while i < len(df_fipa) - 1:
      row1 = df_fipa.iloc[i]
      row2 = df_fipa.iloc[i + 1]
      sc1 = str(row1["Exact_Score"])
      sc2 = str(row2["Exact_Score"])
      h1, a1 = map(int, sc1.replace(" ", "").split("-"))
      h2, a2 = map(int, sc2.replace(" ", "").split("-"))

      if h1 != a1 and h1 == a2 and a1 == h2:
        r1 = float(row1["Rank"])
        r2 = float(row2["Rank"])
        avg_rank = (r1 + r2) / 2.0
        if avg_rank % 1 != 0:
          target_rank = int(avg_rank / 2.0)
          div_used = 2
        else:
          divisor = 2
          while True:
            res = avg_rank / divisor
            if res % 1 != 0:
              target_rank = int(res)
              div_used = divisor
              break
            divisor += 1

        match = df_predictions[df_predictions["Rank"] == target_rank]
        if not match.empty:
          rec = dict(match.iloc[0])
          rec["FIPA_Reason"] = (
              f"FIPA CONSECUTIVE RECIPROCAL RULE (Replaced {sc1} & {sc2} [Ranks"
              f" {int(r1)}, {int(r2)}] -> Avg Rank {avg_rank:.1f} / {div_used} ="
              f" General Rank {target_rank})"
          )
          records_to_add.append(rec)

        indices_to_remove.add(i)
        indices_to_remove.add(i + 1)
        i += 2
      else:
        i += 1

    if indices_to_remove:
      keep_indices = [
          idx for idx in range(len(df_fipa)) if idx not in indices_to_remove
      ]
      df_fipa = df_fipa.iloc[keep_indices].copy()

    if records_to_add:
      df_add = pd.DataFrame(records_to_add)
      df_fipa = pd.concat([df_fipa, df_add], ignore_index=True)

    if not df_fipa.empty:
      df_fipa = (
          df_fipa.sort_values(by="_sort_key", ascending=False).reset_index(
              drop=True
          )
      )
      df_fipa["FIPA_Rank"] = range(1, len(df_fipa) + 1)

    return df_fipa

  def extract_vfipa_and_surprise_predictions(self, df_fipa, df_predictions):
    if df_fipa.empty:
      return pd.DataFrame(), pd.DataFrame()

    odds_2nd = (
        float(df_fipa.iloc[1]["Implied_Odds"])
        if len(df_fipa) >= 2
        else float(df_fipa.iloc[0]["Implied_Odds"])
    )
    limit_odds = odds_2nd * 2.0

    vfipa_records = []
    for idx, row in df_fipa.iterrows():
      odds_val = float(row["Implied_Odds"])
      if odds_val <= limit_odds:
        rec = dict(row)
        rec["VFIPA_Reason"] = (
            f"VFIPA MATCH (Implied_Odds {odds_val:.2f} <= Max Limit"
            f" {limit_odds:.2f} [2 * 2nd FIPA Odds])"
        )
        vfipa_records.append(rec)

    df_vfipa = pd.DataFrame(vfipa_records)
    if df_vfipa.empty:
      return df_vfipa, pd.DataFrame()

    # Rule 2
    records_r2 = df_vfipa.to_dict("records")
    to_remove_idx = set()
    scores_to_add = []

    for i in range(len(records_r2)):
      if i in to_remove_idx:
        continue
      for j in range(i + 1, len(records_r2)):
        if j in to_remove_idx:
          continue
        rA, rB = records_r2[i], records_r2[j]
        probA_str, probB_str = str(rA["Probability_%"]), str(rB["Probability_%"])
        decA = (
            probA_str.split(".")[1][:6].ljust(6, "0")
            if "." in probA_str
            else "000000"
        )
        decB = (
            probB_str.split(".")[1][:6].ljust(6, "0")
            if "." in probB_str
            else "000000"
        )

        has_positional_pair_match = any(
            decA[k : k + 2] == decB[k : k + 2] for k in range(5)
        )
        if has_positional_pair_match:
          to_remove_idx.add(i)
          to_remove_idx.add(j)
          scA = [int(x) for x in rA["Exact_Score"].replace(" ", "").split("-")]
          scB = [int(x) for x in rB["Exact_Score"].replace(" ", "").split("-")]
          sum_sc = f"{scA[0] + scB[0]} - {scA[1] + scB[1]}"
          max_sc = scA if (scA[0] + scA[1]) >= (scB[0] + scB[1]) else scB
          div_sc = f"{max_sc[0] // 2} - {max_sc[1] // 2}"
          scores_to_add.extend([sum_sc, div_sc])
          break

    if to_remove_idx:
      df_vfipa = pd.DataFrame([
          records_r2[idx]
          for idx in range(len(records_r2))
          if idx not in to_remove_idx
      ])
      for sc in scores_to_add:
        match = df_predictions[df_predictions["Exact_Score"] == sc]
        if not match.empty:
          rec_add = dict(match.iloc[0])
          rec_add["VFIPA_Reason"] = (
              f"VFIPA RULE 2 (Derived Score {sc} from Strict Vertical Prob%"
              " Decimal Overlap)"
          )
          df_vfipa = pd.concat(
              [df_vfipa, pd.DataFrame([rec_add])], ignore_index=True
          )
      df_vfipa = df_vfipa.drop_duplicates(subset=["Exact_Score"]).reset_index(
          drop=True
      )

    # Rule 5 (Duplicate)
    while True:
      dup_mask = df_vfipa.duplicated(subset=["Exact_Score"], keep=False)
      if not dup_mask.any():
        break
      dup_scores = df_vfipa[dup_mask]
      dup_score = dup_scores.iloc[0]["Exact_Score"]
      dup_indices = df_vfipa[
          df_vfipa["Exact_Score"] == dup_score
      ].index.tolist()
      first_dup_idx = dup_indices[0]
      best_neigh_idx, min_dist = None, float("inf")

      for idx, row in df_vfipa.iterrows():
        if idx not in dup_indices:
          dist = abs(idx - first_dup_idx)
          if dist < min_dist:
            min_dist, best_neigh_idx = dist, idx

      if best_neigh_idx is not None:
        neigh_score = df_vfipa.loc[best_neigh_idx, "Exact_Score"]
        h_dup, a_dup = map(int, dup_score.replace(" ", "").split("-"))
        h_nei, a_nei = map(int, neigh_score.replace(" ", "").split("-"))
        avg_score = f"{(h_dup + h_nei) // 2} - {(a_dup + a_nei) // 2}"

        remove_indices = [dup_indices[0], best_neigh_idx]
        df_vfipa = df_vfipa.drop(index=remove_indices).reset_index(drop=True)
        match = df_predictions[df_predictions["Exact_Score"] == avg_score]
        if not match.empty:
          rec_add = dict(match.iloc[0])
          rec_add["VFIPA_Reason"] = (
              f"VFIPA DUPLICATE RULE (Replaced Duplicate {dup_score} & Neighbor"
              f" {neigh_score} with Avg {avg_score})"
          )
          df_vfipa = pd.concat(
              [df_vfipa, pd.DataFrame([rec_add])], ignore_index=True
          )
        df_vfipa = df_vfipa.drop_duplicates(subset=["Exact_Score"]).reset_index(
            drop=True
        )
      else:
        df_vfipa = df_vfipa.drop_duplicates(subset=["Exact_Score"]).reset_index(
            drop=True
        )
        break

    # Rule 1 (Sequences)
    if not df_vfipa.empty:
      df_sorted = df_vfipa.sort_values(by="Rank").reset_index(drop=True)
      ranks = [int(r) for r in df_sorted["Rank"]]
      seqs, cur_seq = [], [ranks[0]]
      for r in ranks[1:]:
        if r == cur_seq[-1] + 1:
          cur_seq.append(r)
        else:
          if len(cur_seq) >= 3:
            seqs.append(cur_seq)
          cur_seq = [r]
      if len(cur_seq) >= 3:
        seqs.append(cur_seq)

      if seqs:
        ranks_to_remove, ranks_to_add = set(), set()
        for seq in seqs:
          ranks_to_remove.update(seq)
          ranks_to_add.add(seq[0] * 2)
          ranks_to_add.add(max(1, seq[-1] // 2))

        df_vfipa = df_vfipa[
            ~df_vfipa["Rank"].astype(int).isin(ranks_to_remove)
        ].copy()
        for r in ranks_to_add:
          match = df_predictions[df_predictions["Rank"] == r]
          if not match.empty:
            rec_add = dict(match.iloc[0])
            rec_add["VFIPA_Reason"] = (
                f"VFIPA RULE 1 (Added General Rank {r} from Sequence"
                " Replacement)"
            )
            df_vfipa = pd.concat(
                [df_vfipa, pd.DataFrame([rec_add])], ignore_index=True
            )
        df_vfipa = df_vfipa.drop_duplicates(subset=["Exact_Score"]).reset_index(
            drop=True
        )

    # Rule 3 (Reciprocals)
    if not df_vfipa.empty:
      rec_step = []
      for rec in df_vfipa.to_dict("records"):
        sc = str(rec["Exact_Score"]).replace(" ", "")
        h, a = map(int, sc.split("-"))
        if h != a:
          recip_sc = f"{a} - {h}"
          match_orig = df_predictions[
              df_predictions["Exact_Score"] == f"{h} - {a}"
          ]
          match_recip = df_predictions[
              df_predictions["Exact_Score"] == recip_sc
          ]
          p_orig = (
              float(match_orig.iloc[0]["_sort_key"])
              if not match_orig.empty
              else 0.0
          )
          p_recip = (
              float(match_recip.iloc[0]["_sort_key"])
              if not match_recip.empty
              else 0.0
          )

          if p_recip > p_orig:
            rec_new = dict(match_recip.iloc[0])
            rec_new["VFIPA_Reason"] = (
                f"VFIPA MATCH (Replaced {h}-{a} with Reciprocal {a}-{h} [Higher"
                " Prob])"
            )
            rec_step.append(rec_new)
          else:
            rec_step.append(rec)
        else:
          rec_step.append(rec)
      df_vfipa = (
          pd.DataFrame(rec_step)
          .sort_values(by="_sort_key", ascending=False)
          .drop_duplicates(subset=["Exact_Score"])
          .reset_index(drop=True)
      )

    # Rule 4
    if 1 <= len(df_vfipa) < 3:
      avg_rank = int(df_vfipa["Rank"].astype(float).mean()) + 1
      match = df_predictions[df_predictions["Rank"] == avg_rank]
      if not match.empty:
        rec_add = dict(match.iloc[0])
        rec_add["VFIPA_Reason"] = (
            f"VFIPA RULE 4 (Added Average General Rank {avg_rank} [VFIPA Count"
            " < 3])"
        )
        df_vfipa = pd.concat(
            [df_vfipa, pd.DataFrame([rec_add])], ignore_index=True
        )
        df_vfipa = df_vfipa.drop_duplicates(subset=["Exact_Score"]).reset_index(
            drop=True
        )

    if not df_vfipa.empty:
      df_vfipa = df_vfipa.sort_values(
          by="_sort_key", ascending=False
      ).reset_index(drop=True)
      df_vfipa["VFIPA_Rank"] = range(1, len(df_vfipa) + 1)

    # Surprise Section
    surprise_records = []
    N_fipa = len(df_fipa)
    if N_fipa >= 1:
      K = int(N_fipa / 2)
      if K >= 1:
        use_avg_replacement = False
        if K >= 3:
          row_above1 = df_fipa.iloc[K - 2]
          row_above2 = df_fipa.iloc[K - 3]
          sc_above1, sc_above2 = str(row_above1["Exact_Score"]), str(
              row_above2["Exact_Score"]
          )
          vfipa_scores = (
              set(df_vfipa["Exact_Score"]) if not df_vfipa.empty else set()
          )

          if (sc_above1 not in vfipa_scores) and (sc_above2 not in vfipa_scores):
            use_avg_replacement = True
            r1, r2 = float(row_above1["Rank"]), float(row_above2["Rank"])
            avg_target_rank = int((r1 + r2) / 2.0)
            match_pred = df_predictions[
                df_predictions["Rank"] == avg_target_rank
            ]
            if not match_pred.empty:
              row_k = dict(match_pred.iloc[0])
              row_k["Surprise_Reason"] = (
                  f"SURPRISE MATCH (Replaced Mid FIPA Rank {K} with Avg General"
                  f" Rank {avg_target_rank} from missing top 2 FIPA Ranks"
                  f" [{sc_above1}, {sc_above2}])"
              )
              surprise_records.append(row_k)
            else:
              use_avg_replacement = False

        if not use_avg_replacement:
          row_k = dict(df_fipa.iloc[K - 1])
          row_k["Surprise_Reason"] = (
              f"SURPRISE MATCH (Mid FIPA Rank {K} of Total {N_fipa} FIPA"
              " Predictions)"
          )
          surprise_records.append(row_k)

      row_n = dict(df_fipa.iloc[N_fipa - 1])
      row_n["Surprise_Reason"] = (
          f"SURPRISE MATCH (Final FIPA Rank {N_fipa} of Total {N_fipa} FIPA"
          " Predictions)"
      )
      if row_n["Exact_Score"] not in [
          r["Exact_Score"] for r in surprise_records
      ]:
        surprise_records.append(row_n)

    df_surprise = pd.DataFrame(surprise_records)
    if not df_surprise.empty:
      df_surprise["Surprise_Rank"] = range(1, len(df_surprise) + 1)

    return df_vfipa, df_surprise


def calculate_averages(df):
  total_preds = Decimal(len(df))
  if total_preds == 0:
    return Decimal("0"), Decimal("0")
  total_prob = sum(Decimal(p) for p in df["Probability_%"])
  total_odds = sum(Decimal(o) for o in df["Implied_Odds"])
  return total_prob / total_preds, total_odds / total_preds


# --- STREAMLIT UI WITH CUSTOM LUXURY DARK THEME ---
st.set_page_config(
    page_title="Quantum Football Engine Pro",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Custom CSS Styles
st.markdown(
    """
    <style>
    /* Background and main container */
    .stApp {
        background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
        color: #c9d1d9;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    
    /* Main Title Styling */
    .main-header {
        text-align: center;
        padding: 20px 0;
        background: linear-gradient(90deg, #10b981 0%, #3b82f6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: 1px;
    }
    
    /* Card Container */
    .custom-card {
        background-color: #1e2631;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.4);
    }
    
    /* Input Box Styles */
    .stTextInput input {
        background-color: #0d1117 !important;
        color: #e6edf3 !important;
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
    }
    .stTextInput input:focus {
        border-color: #10b981 !important;
        box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2) !important;
    }

    /* Primary Button Style */
    .stButton>button {
        background: linear-gradient(90deg, #10b981 0%, #059669 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 12px 24px !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3) !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(16, 185, 129, 0.5) !important;
    }
    
    /* Result Prediction Cards */
    .prediction-box {
        background: linear-gradient(90deg, #1a2332 0%, #0f172a 100%);
        border-left: 4px solid #10b981;
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .prediction-box-surprise {
        border-left-color: #f59e0b !important;
    }
    .prediction-rank {
        color: #10b981;
        font-weight: 800;
        font-size: 1.1rem;
        margin-right: 10px;
    }
    .prediction-match {
        color: #f8fafc;
        font-weight: 700;
        font-size: 1.05rem;
    }
    .prediction-prob {
        background-color: rgba(16, 185, 129, 0.15);
        color: #34d399;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.9rem;
    }
    .match-code-badge {
        background: linear-gradient(90deg, #3b82f6 0%, #1d4ed8 100%);
        color: #white;
        text-align: center;
        padding: 12px;
        border-radius: 8px;
        font-size: 1.2rem;
        font-weight: 800;
        letter-spacing: 2px;
        margin: 15px 0;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Header Title
st.markdown(
    '<div class="main-header">⚡ QUANTUM FOOTBALL ENGINE V2.1</div>',
    unsafe_allow_html=True,
)

# Input Form in Card
with st.container():
  st.markdown('<div class="custom-card">', unsafe_allow_html=True)

  col1, col2 = st.columns(2)
  with col1:
    h_name = st.text_input("🏠 Home Team Name", "TEAM A")
    h_input = st.text_input(
        f"Last 5 Results ({h_name})", "2-1 1-1 3-0 0-1 2-0", key="h_res"
    )
  with col2:
    a_name = st.text_input("✈️ Away Team Name", "TEAM B")
    a_input = st.text_input(
        f"Last 5 Results ({a_name})", "0-1 2-2 1-0 1-1 0-0", key="a_res"
    )

  st.markdown("</div>", unsafe_allow_html=True)

engine = QuantumFootballEngineFull()

# Prediction Action
if st.button("🚀 GENERATE ANALYTICAL PREDICTIONS", use_container_width=True):
  try:
    df_predictions = engine.predict_match(h_input, a_input)
    df_fipa = engine.extract_fipa_predictions(df_predictions)
    df_vfipa, df_surprise = engine.extract_vfipa_and_surprise_predictions(
        df_fipa, df_predictions
    )

    target_df_for_avg = df_vfipa if not df_vfipa.empty else df_fipa
    avg_prob, _ = calculate_averages(target_df_for_avg)
    avg_str = f"{float(avg_prob):.6f}"
    dec_part = avg_str.split(".")[1]
    match_code = f"{dec_part[:2]}.{dec_part[2:]}"

    st.session_state["match_code"] = match_code
    st.session_state["df_vfipa"] = df_vfipa
    st.session_state["df_surprise"] = df_surprise
    st.session_state["h_name"] = h_name
    st.session_state["a_name"] = a_name
    st.session_state["computed"] = True
  except Exception as e:
    st.error(f"❌ Error: {e}")

# Security & Results Display
if st.session_state.get("computed", False):
  st.markdown(
      f'<div class="match-code-badge">🔑 MATCH CODE: [{st.session_state["match_code"]}]</div>',
      unsafe_allow_html=True,
  )

  pwd_input = st.text_input(
      "🔒 Enter Match Security Password:", type="password"
  )

  if pwd_input:
    if _v_sec(st.session_state["match_code"], pwd_input):
      st.success("✅ ACCESS GRANTED")

      st.markdown(
          f"<h3 style='text-align: center; color: #f8fafc; margin-top: 20px;'>MATCH: {st.session_state['h_name'].upper()} VS {st.session_state['a_name'].upper()}</h3>",
          unsafe_allow_html=True,
      )
      st.caption(
          f"<p style='text-align: center;'>{_decode_data(_ENCODED_TITLE)} | {_decode_data(_ENCODED_PHONE)}</p>",
          unsafe_allow_html=True,
      )

      # VIP Predictions Section
      st.markdown(
          "<h4 style='color: #10b981; margin-top: 20px;'>⭐ VIP PREDICTIONS</h4>",
          unsafe_allow_html=True,
      )
      df_v = st.session_state["df_vfipa"]
      if not df_v.empty:
        for idx, row in df_v.iterrows():
          st.markdown(
              f"""
                    <div class="prediction-box">
                        <div>
                            <span class="prediction-rank">#{idx+1:02d}</span>
                            <span class="prediction-match">{st.session_state['h_name'].upper()} {row['Exact_Score']} {st.session_state['a_name'].upper()}</span>
                        </div>
                        <div class="prediction-prob">[{float(row['Probability_%']):.4f}%]</div>
                    </div>
                    """,
              unsafe_allow_html=True,
          )

      # Surprise Predictions Section
      st.markdown(
          "<h4 style='color: #f59e0b; margin-top: 20px;'>🎁 SURPRISE PREDICTIONS</h4>",
          unsafe_allow_html=True,
      )
      df_s = st.session_state["df_surprise"]
      if not df_s.empty:
        for idx, row in df_s.iterrows():
          st.markdown(
              f"""
                    <div class="prediction-box prediction-box-surprise">
                        <div>
                            <span class="prediction-rank" style="color:#f59e0b;">#{idx+1:02d}</span>
                            <span class="prediction-match">{st.session_state['h_name'].upper()} {row['Exact_Score']} {st.session_state['a_name'].upper()}</span>
                        </div>
                        <div class="prediction-prob" style="background-color:rgba(245, 158, 11, 0.15); color:#fbbf24;">[{float(row['Probability_%']):.4f}%]</div>
                    </div>
                    """,
              unsafe_allow_html=True,
          )

      st.markdown("<hr style='border-color: #30363d;'/>", unsafe_allow_html=True)
      st.caption(
          f"<p style='text-align: center; color: #6e7681;'>{_decode_data(_ENCODED_DATA)}<br/>{_decode_data(_ENCODED_WARN1_TEXT)}<br/>{_decode_data(_ENCODED_WARN2_TEXT)}</p>",
          unsafe_allow_html=True,
      )
    else:
      st.error("❌ INCORRECT PASSWORD! ACCESS DENIED.")
