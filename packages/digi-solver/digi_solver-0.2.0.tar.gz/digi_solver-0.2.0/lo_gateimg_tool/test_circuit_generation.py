# test_circuit_generation.py
import os
import shutil

# Sử dụng import tương đối để trỏ đến __init__.py trong cùng package (lo_gateimg_tool)
from . import generate_logic_diagrams 

def run_circuit_generation_tests():
    print("--- Testing Circuit Generation (generate_logic_diagrams) ---")

    # Xác định đường dẫn dựa trên vị trí của script này
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(script_dir, "data.txt")
    output_dir = os.path.join(script_dir, "generated_circuit_tex_output")
    
    # Kiểm tra xem file data.txt có tồn tại không
    if not os.path.exists(input_file):
        print(f"LỖI: Không tìm thấy file đầu vào: {input_file}")
        print("Vui lòng đảm bảo file 'data.txt' tồn tại trong thư mục lo_gateimg_tool.")
        return

    print(f"Sử dụng file đầu vào: {input_file}")
    print(f"Thư mục đầu ra: {output_dir}")

    # Xóa thư mục output nếu đã tồn tại để kiểm thử lại từ đầu
    if os.path.exists(output_dir):
        print(f"Xóa thư mục output cũ: {output_dir}")
        shutil.rmtree(output_dir)
    
    # Gọi hàm chính để tạo sơ đồ logic
    # Mặc định scale=1.0
    generated_files = generate_logic_diagrams(input_file_path=input_file, output_dir=output_dir)

    if generated_files:
        print("\\nThành công! Các file LaTeX sau đã được tạo:")
        all_files_exist = True
        for tex_file in generated_files:
            print(f"- {tex_file}")
            if not os.path.exists(tex_file):
                print(f"  LỖI: File {tex_file} không tồn tại sau khi tạo!")
                all_files_exist = False
        
        if all_files_exist:
            print("\\nTất cả các file đã được kiểm tra và tồn tại.")
            print(f"Bạn có thể tìm thấy chúng trong thư mục: {os.path.abspath(output_dir)}")
        else:
            print("\\nLỖI: Một số file được báo cáo đã tạo nhưng không tìm thấy trên hệ thống.")

    else:
        print("\\nKhông có file LaTeX nào được tạo, hoặc đã có lỗi xảy ra trong quá trình xử lý.")
        print("Kiểm tra lại các thông báo lỗi ở trên (nếu có) từ hàm generate_logic_diagrams.")

    print("\\n--- Kết thúc kiểm thử Circuit Generation ---")

if __name__ == "__main__":
    # Để chạy script này trực tiếp từ dòng lệnh:
    # 1. Đảm bảo bạn đang ở thư mục `digi_solver` (thư mục cha của `lo_gateimg_tool`).
    # 2. Chạy lệnh: python -m lo_gateimg_tool.test_circuit_generation
    # Điều này cần thiết để Python xử lý đúng các import tương đối.

    # Kiểm tra xem có file __init__.py trong thư mục hiện tại của script không
    # (chủ yếu để đảm bảo lo_gateimg_tool là một package)
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    if not os.path.exists(os.path.join(current_script_dir, "__init__.py")):
        print("CẢNH BÁO: Không tìm thấy file __init__.py trong thư mục chứa script này.")
        print("Import tương đối có thể không hoạt động chính xác nếu thư mục này không phải là một package.")
        print(f"Thư mục hiện tại của script: {current_script_dir}")

    run_circuit_generation_tests() 