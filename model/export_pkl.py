"""Gói mỗi mô hình (kèm bộ tiền xử lý) thành một file .pkl độc lập.

Chạy từ bất kỳ đâu:  python export_pkl.py
Nạp lại:
    import sys, pickle
    sys.path.insert(0, "<đường dẫn tới thư mục model>")   # để pickle tìm thấy module price_model
    with open("random_forest_sklearn.pkl", "rb") as f:
        model = pickle.load(f)
    from price_model import predict_price
    predict_price(model, df)
"""
import pickle
import sys
from pathlib import Path

DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(DIR))
import price_model  # noqa: E402  (phải import để pickle ghi đúng tên module, không phải __main__)

for name in price_model.MODELS:
    path = DIR / f"{name}.pkl"
    with open(path, "wb") as f:
        pickle.dump(price_model.load_model(name), f, protocol=pickle.HIGHEST_PROTOCOL)
    print(f"{path.name:32s} {path.stat().st_size / 1e6:8.2f} MB")
