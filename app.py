import requests
import streamlit as st

# Địa chỉ Production URL của webhook n8n (workflow phải được bật Active)
N8N_WEBHOOK_URL = "https://n8n.n2nai.io/webhook/chan-doan-sau-rieng"

st.set_page_config(page_title="Chẩn đoán bệnh lá sầu riêng", page_icon="🌿")


def hien_thi_ket_qua(kq: dict) -> None:
    """Hiển thị kết quả chẩn đoán mà n8n trả về."""
    trang_thai = kq.get("trang_thai")
    do_tin_cay = float(kq.get("do_tin_cay") or 0)
    do_tin_cay = min(max(do_tin_cay, 0.0), 1.0)

    if trang_thai == "ok":
        ten_benh = kq.get("ten_benh", "Không rõ")
        if kq.get("ma_benh") == "Leaf_Healthy":
            st.success(f"✅ Kết quả: **{ten_benh}**")
        else:
            st.error(f"🦠 Phát hiện: **{ten_benh}**")

        st.write(f"**Độ tin cậy:** {do_tin_cay:.1%}")
        st.progress(do_tin_cay)

        st.subheader("🔎 Nguyên nhân")
        st.write(kq.get("nguyen_nhan", ""))

        st.subheader("🍂 Triệu chứng")
        st.write(kq.get("trieu_chung", ""))

        st.subheader("💊 Cách xử lý")
        st.write(kq.get("cach_xu_ly", ""))

        st.subheader("🛡️ Phòng ngừa")
        st.write(kq.get("phong_ngua", ""))
    else:
        st.warning(
            kq.get(
                "thong_bao",
                "Ảnh chưa đủ rõ hoặc không phải lá sầu riêng. Vui lòng chụp lại.",
            )
        )
        st.caption(f"Độ tin cậy của mô hình: {do_tin_cay:.1%}")

    st.divider()
    st.caption(
        "⚠️ Kết quả chỉ mang tính tham khảo. Khi dùng thuốc bảo vệ thực vật, "
        "hãy đọc kỹ hướng dẫn trên nhãn và hỏi ý kiến cán bộ kỹ thuật nông nghiệp."
    )


st.title("🌿 Chẩn đoán bệnh trên lá sầu riêng")
st.write(
    "Tải lên hoặc chụp ảnh **một chiếc lá sầu riêng** để hệ thống nhận diện bệnh "
    "và gợi ý cách xử lý."
)

tab_tai_len, tab_chup = st.tabs(["📁 Tải ảnh lên", "📷 Chụp ảnh"])
with tab_tai_len:
    anh_tai_len = st.file_uploader("Chọn ảnh lá (JPG, PNG)", type=["jpg", "jpeg", "png"])
with tab_chup:
    anh_chup = st.camera_input("Chụp ảnh lá")

anh = anh_tai_len or anh_chup

if anh is not None:
    st.image(anh, caption="Ảnh đã chọn")

    if st.button("🔍 Chẩn đoán", type="primary"):
        with st.spinner("Đang phân tích ảnh..."):
            try:
                files = {
                    "file": (
                        anh.name or "anh_la.jpg",
                        anh.getvalue(),
                        anh.type or "image/jpeg",
                    )
                }
                phan_hoi = requests.post(N8N_WEBHOOK_URL, files=files, timeout=60)
                phan_hoi.raise_for_status()
                ket_qua = phan_hoi.json()
            except requests.exceptions.Timeout:
                st.error("Máy chủ phản hồi quá lâu. Vui lòng thử lại sau.")
                st.stop()
            except requests.exceptions.RequestException as loi:
                st.error(f"Không kết nối được tới máy chủ chẩn đoán: {loi}")
                st.stop()
            except ValueError:
                st.error("Máy chủ trả về dữ liệu không hợp lệ.")
                st.stop()

        hien_thi_ket_qua(ket_qua)
else:
    st.info("👆 Hãy tải lên hoặc chụp một ảnh lá để bắt đầu.")
