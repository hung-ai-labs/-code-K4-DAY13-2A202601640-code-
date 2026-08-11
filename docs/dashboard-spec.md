# Dashboard Spec — Day 13 AI Observability

Contract máy chấm: [`config/dashboard.yaml`](../config/dashboard.yaml)  
Hướng dẫn runtime: [DASHBOARD_SETUP.md](DASHBOARD_SETUP.md)  
Công cụ sử dụng: **Streamlit** (`scripts/dashboard_app.py`) đọc live từ `GET /metrics`, đối chiếu thêm `data/logs.jsonl` (nguồn contract).

- Khoảng thời gian mặc định: **60 phút**
- Refresh: **30 giây** (nút Reload / rerun)
- SLO line / threshold: lấy từ `config/dashboard.yaml` và `config/slo.yaml`

Kiểm tra contract:

```bash
python scripts/validate_dashboard.py
```

Chạy dashboard:

```bash
streamlit run scripts/dashboard_app.py
```

Xem metrics hiện tại:

```bash
curl http://localhost:8000/metrics
```

---

## 6 panel bắt buộc

| # | Panel | Nguồn `/metrics` | Đơn vị | Loại hiển thị | Threshold / SLO line |
|---|---|---|---|---|---|
| 1 | Latency percentiles | `latency_p50`, `latency_p95`, `latency_p99` | ms | Single value P50/P95/P99 + line theo thời gian (từ logs) | P95 ≤ **3000** ms |
| 2 | Request traffic | `traffic` | requests (counter) / requests_per_minute | Counter tổng request + rate | rate ≥ **1** req/min |
| 3 | Error rate & breakdown | `error_rate_pct`, `error_breakdown` | percent | Gauge error % + bảng/bar theo loại lỗi | error_rate ≤ **2%** (SLO); alert critical khi > **5%** |
| 4 | Cost | `total_cost_usd`, `avg_cost_usd` | USD | Tổng chi phí vs ngân sách + avg/request | total ≤ **2.5** USD |
| 5 | Tokens | `tokens_in_total`, `tokens_out_total` | tokens | Hai single value input/output | tổng ≤ **50000** tokens |
| 6 | Quality proxy | `quality_avg` | score 0–1 | Single value mean quality | mean ≥ **0.75** |

---

## Chi tiết từng panel

### 1. Latency percentiles
- **Tên:** Latency percentiles
- **Fields:** `latency_p50`, `latency_p95`, `latency_p99`
- **Đơn vị:** ms
- **Time range:** 60 phút
- **SLO line:** P95 = 3000 ms (`config/slo.yaml` → `latency_p95_ms`)

### 2. Request traffic
- **Tên:** Request traffic
- **Fields:** `traffic`
- **Đơn vị:** requests / requests_per_minute
- **Time range:** 60 phút
- **Threshold:** ≥ 1 request/phút (dashboard contract)

### 3. Error rate and breakdown
- **Tên:** Error rate and breakdown
- **Fields:** `error_rate_pct`, `error_breakdown`
- **Đơn vị:** percent
- **Time range:** 60 phút
- **SLO:** ≤ 2%; **Alert critical:** > 5% trong 3 phút

### 4. Cost over time
- **Tên:** Cost over time
- **Fields:** `total_cost_usd`, `avg_cost_usd`
- **Đơn vị:** USD
- **Time range:** 60 phút (budget ngày tham chiếu `daily_cost_usd`)
- **SLO / budget line:** total ≤ 2.5 USD

### 5. Input and output tokens
- **Tên:** Input and output tokens
- **Fields:** `tokens_in_total`, `tokens_out_total`
- **Đơn vị:** tokens
- **Time range:** 60 phút
- **Threshold:** tổng ≤ 50000

### 6. Quality proxy
- **Tên:** Quality proxy
- **Fields:** `quality_avg`
- **Đơn vị:** score_0_to_1
- **Time range:** 60 phút
- **SLO line:** ≥ 0.75

---

## Evidence

- Kết quả `python scripts/validate_dashboard.py` → `HỢP LỆ: 6/6 panel`
- Ảnh dashboard Streamlit (đủ 6 nhóm + time range + threshold) → `submission/evidence/`
- File này (`docs/dashboard-spec.md`) là spec đầy đủ khi chưa/ không dùng Grafana/Langfuse dashboard
