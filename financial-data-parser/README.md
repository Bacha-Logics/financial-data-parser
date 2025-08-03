# 🧾 Financial Data Parser

A robust financial data parsing system that processes Excel files, intelligently detects data types, handles various currency/date formats, and stores data in optimized structures for fast querying and aggregation.

---

## 📌 Features

- 📁 Load Excel files with multiple sheets
- 🔍 Detect column types (number, date, string) intelligently
- 💵 Parse diverse financial amount formats:
  - `$1,234.56`, `(2,500.00)`, `€1.234,56`, `1.5M`, `₹1,23,456.78`
- 📆 Handle various date formats:
  - `MM/DD/YYYY`, `DD/MM/YYYY`, `Q4 2023`, Excel serial (e.g. `44927`)
- 🚀 Optimized storage using:
  - Pandas MultiIndex, dictionary indexes
- 🔎 Fast lookup and query by criteria
- 📊 Easy aggregation for reporting

---

## 📂 Folder Structure


