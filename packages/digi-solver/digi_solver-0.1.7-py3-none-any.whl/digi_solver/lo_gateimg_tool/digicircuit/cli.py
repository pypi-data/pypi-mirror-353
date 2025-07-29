import argparse
import os

# Để import generate_logic_diagrams, chúng ta cần điều chỉnh sys.path một chút
# khi chạy file này trực tiếp, hoặc dựa vào việc Python tìm thấy package
# khi cài đặt qua entry point. Cách tốt nhất là gọi hàm từ package đã cài.
# Tuy nhiên, để file này có thể chạy (ví dụ, để test đơn giản từ thư mục digicircuit),
# chúng ta có thể làm như sau, nhưng cách chuẩn hơn là dựa vào cấu trúc package.
# import sys
# script_dir = os.path.dirname(os.path.abspath(__file__))
# lo_gateimg_tool_dir = os.path.dirname(script_dir) # Lùi lại một cấp để đến lo_gateimg_tool
# digi_solver_dir = os.path.dirname(lo_gateimg_tool_dir) # Lùi lại hai cấp để đến digi_solver
# if digi_solver_dir not in sys.path:
# sys.path.insert(0, digi_solver_dir)

from digi_solver.lo_gateimg_tool import generate_logic_diagrams

def main():
    parser = argparse.ArgumentParser(
        description="Generate LaTeX circuit diagrams from Boolean expressions.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "input_file", 
        help="Path to the input file containing Boolean expressions (e.g., data.txt).\nEach line should be a Boolean expression, optionally preceded by a number and space."
    )
    parser.add_argument(
        "-o", "--output_dir", 
        default="latex_circuit_output_cli", 
        help="Directory to save the generated .tex files (default: latex_circuit_output_cli)."
    )
    parser.add_argument(
        "-s", "--scale", 
        type=float, 
        default=1.0, 
        help="Scale factor for the circuit diagrams in LaTeX output (default: 1.0)."
    )

    args = parser.parse_args()

    print(f"Input file: {os.path.abspath(args.input_file)}")
    print(f"Output directory: {os.path.abspath(args.output_dir)}")
    print(f"Scale: {args.scale}")

    # Đảm bảo output_dir là đường dẫn tuyệt đối hoặc tương đối từ vị trí chạy lệnh
    # Hàm generate_logic_diagrams đã xử lý việc tạo thư mục nếu chưa có.

    generated_files = generate_logic_diagrams(
        input_file_path=args.input_file, 
        output_dir=args.output_dir, 
        scale=args.scale
    )

    if generated_files:
        print("\nSuccessfully generated the following LaTeX files:")
        for f_path in generated_files:
            print(f"- {f_path}")
        print(f"\nOutput files are in: {os.path.abspath(args.output_dir)}")
    else:
        print("\nNo LaTeX files were generated. Please check for errors above.")

if __name__ == "__main__":
    main() 